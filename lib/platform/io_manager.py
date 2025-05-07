import logging
import re
import time
import os
from lib.platform.remote_ssh_manager import RemoteConnect
from morpheus_api.settings import MorpheusSettings, ProxySettings, VDBenchSettings
from packaging import version as pver
from json import loads
from lib.platform.host.vdbench_config_models import (
    BasicParameters,
    StorageDefinitions,
    WorkloadDefinitions,
    RunDefinitions,
)

logger = logging.getLogger()

settings = MorpheusSettings()


class IOManager:
    def __init__(self, client: RemoteConnect, super_user: bool = True):
        """
        Class contains methods to run dmore on an HPE MVM VM (Linux)
        Provides support for generating checksum using cksum module and cksum validation.

        Args:
            client (RemoteConnect): Paramiko client object to the HPE MVM VM.
            super_user (bool, optional): Run commands as super user. Defaults to True.
        """
        self.client = client
        self.dmcore = settings.dmcore_settings.dmcore_binary
        self.home_directory = f"/home/{client.username}/"
        self.dmcore_directory, self.dmcore_filename = os.path.split(self.dmcore)
        self.super_user = super_user

    def copy_dmcore_binary_to_remote_host(self) -> bool:
        """
        Copy dmcore binary file to the HPE MVM VM (Linux)

        Returns:
            bool: True if the file is copied, False otherwise.
        """
        remote_file: str = os.path.join(self.home_directory, self.dmcore_filename)

        if not self.client.sftp_exists(remote_file):
            self.client.copy_file(local_path=self.dmcore, remote_path=remote_file)
            time.sleep(5)
            command = f"chmod +x {self.dmcore_filename}"
            stdout = self.client.execute_command(command=command, super_user=self.super_user)
            for line in stdout:
                logger.info(line)
            # Need to add wait time for copy dmcore to complete as it may lead to errors when running dmcore later
            time.sleep(40)
            stdout = self.client.execute_command(command="ls -al", super_user=self.super_user)
            logger.info(stdout)
            stdout = self.client.execute_command(command="du -sh", super_user=self.super_user)
            logger.info(stdout)
            return True
        return False

    def run_dmcore(
        self,
        export_filename: str,
        percentage_to_fill: int = 80,
        block_size: str = "4k",
        compression_ratio: int = 4,
        compression_method: int = 4,
        offset: int = 0,
        validation: bool = False,
        change_block_percentage: int = 20,
    ) -> bool:
        """
        Run DMCore on the HPE MVM VM (Linux)

        Args:
            export_filename (str): Export file name to write the data.
            percentage_to_fill (int, optional): Percentage of the drive to fill. Defaults to 80.
            block_size (str, optional): Block size. Defaults to "4k".
            compression_ratio (int, optional): Compression ratio. Defaults to 4.
            compression_method (int, optional): Compression method. Defaults to 4.
            offset (int, optional): Offset. Defaults to 0.
            validation (bool, optional): Validate the data. Defaults to False.
            change_block_percentage (int, optional): Change block percentage. Defaults to 20.

        Returns:
            bool: True if the DMCore is run successfully, False otherwise.
        """
        success = False
        for device in self.get_devices():
            device = device.rstrip("\r")
            success = self.run_dm_core_on_custom_drive(
                device=device,
                percentage_to_fill=percentage_to_fill,
                block_size=block_size,
                compression_ratio=compression_ratio,
                compression_method=compression_method,
                offset=offset,
                validation=validation,
                change_block_percentage=change_block_percentage,
                export_filename=export_filename,
            )
        logger.info(f"Dmcore success value is {success}")
        return success

    def ends_with_number(self, string: str) -> bool:
        """
        Check if the string ends with a number

        Args:
            string (str): string to check

        Returns:
            bool: True if the string ends with a number, False otherwise
        """
        return bool(re.search(r"\d$", string))

    def get_devices(self) -> list[str]:
        """
        Get the list of devices on the HPE MVM VM (Linux)

        Returns:
            list[str]: List of devices
        """
        # NOTE: Ubuntu MVM = ['loop0', 'loop1', 'loop2', 'sr0', 'vda', 'vda1', 'vda2', 'vda3', 'dm-0']
        # In Morpheus UI, this is with "root = vda" and "CD Drive = sda"
        # Added "data-2" drive --> "vdb"
        # ['loop0', 'loop1', 'loop2', 'sr0', 'vda', 'vda1', 'vda2', 'vda3', 'vdb', 'dm-0']
        #
        # ['vdb'] is the desired target
        devices = self.client.execute_command_sudo_passwd(command="lsblk --output KNAME -n")

        # Morpheus VMs have a specific naming convention for the drives: vdb, vdc, etc.
        # "vda" is the root drive, so we'll skip it.
        devices = [
            device
            for device in devices
            if device.startswith("vd") and not device.endswith("a") and not self.ends_with_number(device)
        ]
        return devices

    def run_dm_core_on_custom_drive(
        self,
        device: str,
        percentage_to_fill: int = 80,
        block_size: str = "4k",
        compression_ratio: int = 4,
        compression_method: int = 4,
        offset: int = 0,
        validation: bool = False,
        change_block_percentage: int = 20,
        export_filename: str = None,
    ) -> bool:
        """
        Run DMCore with given specifications, compression ratio and compression method is set to 4 by default.
        This will help us get around 4:1 dedupe ratio in store once appliance.
        Use offset to do the incremental backup

        Args:
            device (str): volume on which the data has to be written. Eg. vdb, vdc, etc.
            percentage_to_fill (int, optional): Defaults to 80.
            block_size (str, optional): Defaults to "4k".
            compression_ratio (int, optional): Defaults to 4.
            compression_method (int, optional): Defaults to 4.
            offset (int, optional): Defaults to 0.
            validation (bool, optional): Defaults to False.
            change_block_percentage (int, optional): Defaults to 20
            export_filename (str, option): Provide a value if data is supposed to be written to a file system. Defaults to None.

        Returns:
            bool: True for operation success else False
        """

        total_block_change = int(change_block_percentage * 2)
        self.client.change_directory(self.home_directory)
        command: str = ""
        success = False
        # Convert size from GB to MB and type integer
        size = int((self.get_volume_size(device) / 100) * percentage_to_fill)

        export_filename = export_filename if export_filename else f"/dev/{device}"

        if not validation:
            # Data write command
            command = f"./{self.dmcore_filename} Command=Write DMExecSet=Nas DMVerificationMode=MD5 ExportFileName={export_filename} WriteT={size}m seed=1 WriteI={block_size} Offset={str(offset)} CompressionRatio={str(compression_ratio)} CompressionMethod={str(compression_method)} InternalBlockChange=50 TotalBlockChange={total_block_change}"
        else:
            # Data Read and validate command
            command = f"./{self.dmcore_filename} Command=Read DMExecSet=Nas ImportFileName={export_filename} ReadT={size}m ReadI={block_size} Validation=1"

        stdout = self.client.execute_command_sudo_passwd(command=command, retry_count=5)

        for line in stdout:
            logger.info(line)
            if 'ReturnMessage="Success"' in line:
                success = True
                break
            elif 'ReturnMessage="Error"' in line:
                logger.error(stdout)
                break
        else:
            success = False

        logger.info(f"Dmcore success value is {success}")
        return success

    def get_volume_size(self, device: str) -> int:
        """
        Get the volume size in MB

        Args:
            device (str): volume on which the data has to be written. Eg. vdb, vdc, etc.

        Returns:
            int: volume size in MB
        """
        stdout = self.client.execute_command(f"lsblk -no SIZE /dev/{device}", super_user=self.super_user)
        # Get volume size in GB and convert to MB
        # eg: 8G -> 8 -> 8 * 1024 = 8096
        return self.str_gb_to_mb(stdout[0])

    def str_gb_to_mb(self, gb_str: str) -> int:
        """
        Convert GB string to MB integer

        Volume size in GB passed as string converted to MB (int)
        eg: 8G -> 8 -> 8 * 1024 = 8096

        Args:
            gb_str (str): GB string

        Returns:
            int: MB integer
        """
        return int(gb_str.strip()[:-1]) * 1024

    def create_vdbench_config_on_instance(self, remote_file: str, content: list[str]):
        """
        Creates a Vdbench configuration file on a remote instance.

        This method checks if the specified remote file exists. If it does not exist,
        it creates the necessary directories and writes the provided content to the file.

        Args:
            remote_file (str): The path to the remote file where the Vdbench configuration will be written.
            content (list[str]): The content to be written to the remote file.

        Raises:
            IOError: If writing the Vdbench configuration to the remote instance fails.
        """
        remote_directory, _ = os.path.split(remote_file)
        if not self.client.sftp_exists(remote_file):
            self.client.execute_command_sudo_passwd(f"mkdir -p {remote_directory}")
        success = self.client.write_data_to_remote_file(remote_file=remote_file, content=content, mode="w")
        if not success:
            raise IOError("Writing vdbench config to the remote ec2 instance failed.")

    def copy_vdbench_executable_to_remote_host(self, vdbench_settings: VDBenchSettings):
        """
        Copies the VDBench executable to a remote host.

        This method checks if the home directory exists on the remote host, creates it if it does not,
        and then copies the VDBench executable archive from the local resource directory to the remote host.
        Finally, it changes the current directory on the remote host to the home directory.

        Args:
            vdbench_settings (VDBenchSettings): An instance of VDBenchSettings containing the configuration
                                                for the VDBench executable, including the resource directory
                                                and the VDBench archive name.
        """
        if not self.client.sftp_exists(self.home_directory):
            self.client.execute_command(f"mkdir -p {self.home_directory}")
        self.client.copy_file(
            os.path.join(vdbench_settings.resource_directory, vdbench_settings.vdbench_archive),
            vdbench_settings.vdbench_archive,
        )
        self.client.change_directory(self.home_directory)

    def install_java_on_remote_host(self, vdbench_settings: VDBenchSettings):
        """
        Installs Java and unzip on a remote host and extracts the VDBench archive.

        This method checks the package manager available on the remote host (apt-get, yum, or zypper)
        and installs the default JDK and unzip package accordingly. It then verifies the installation
        and extracts the VDBench archive.

        Args:
            vdbench_settings (VDBenchSettings): An instance of VDBenchSettings containing the path to the VDBench archive.

        Raises:
            AssertionError: If any of the commands fail to execute or the expected output is not found in the command output.
        """
        if self.client.check_command("command -v apt-get"):
            self.install_java_on_debian_ubuntu_linux(vdbench_settings=vdbench_settings)
        elif self.client.check_command("command -v yum"):
            self.install_java_on_redhat_linux()
        else:
            self.install_java_on_suse_linux()

    def install_java_on_debian_ubuntu_linux(self, vdbench_settings: VDBenchSettings):
        """
        Installs Java and unzip utility on a Debian/Ubuntu Linux system and verifies the installation.

        This method performs the following steps:
        1. Updates the package list using `apt-get update`.
        2. Installs the default JDK using `apt-get -y install default-jdk`.
        3. Verifies the Java installation by checking the output of `java --version` for the string "openjdk".
        4. Installs the unzip utility using `apt-get -y install unzip`.
        5. Verifies the unzip installation by checking the output of `which unzip` for the path "/usr/bin/unzip".
        6. Unzips the specified VDBench archive and verifies the output for the strings "example5" or "Nothing to do".

        Args:
            vdbench_settings (VDBenchSettings): An instance of VDBenchSettings containing the path to the VDBench archive.

        Raises:
            AssertionError: If any of the verification steps fail.
        """
        self.client.execute_command_sudo_passwd("apt-get update")
        stdout = self.client.execute_command_sudo_passwd("apt-get -y install default-jdk")
        stdout = self.client.execute_command_sudo_passwd("java --version")
        assert self.client.check_for_string_in_stdout(
            stdout,
            ["openjdk"],
        )
        stdout = self.client.execute_command_sudo_passwd("apt-get -y install unzip")
        stdout = self.client.execute_command_sudo_passwd("which unzip")
        assert self.client.check_for_string_in_stdout(
            stdout,
            ["/usr/bin/unzip"],
        )
        stdout = self.client.execute_command_sudo_passwd(f"unzip -o {vdbench_settings.vdbench_archive}")
        assert self.client.check_for_string_in_stdout(stdout, ["example5", "Nothing to do"])

    def install_java_on_redhat_linux(self):
        """
        Installs Java on Red Hat Linux systems.

        This method performs the following steps:
        1. Lists all available Java packages using the `yum list java*` command.
        2. Parses the output to find the appropriate Java version to install.
        3. Installs the selected Java version using `yum install`.
        4. Installs the `unzip` utility if not already installed.
        5. Unzips the specified archive.

        Raises:
            AssertionError: If any of the installation steps fail.

        Note:
            This method assumes that the system is not registered with an entitlement server.
            It uses `yum` commands and expects the `self.client` object to have methods for
            executing commands and checking output.
        """
        # Amazon and Red Hat
        # On Amazon Linux and Suse -> yum install java-1.8.0-openjdk --assumeyes fails with:
        # Error: Unable to find a match: java-1.8.0-openjdk
        # Below command will list all the available java packages from which we are installing the first one
        # output example
        # [
        #     "Updating Subscription Management repositories.",
        #     "Unable to read consumer identity",
        #     "",
        #     "This system is not registered with an entitlement server. You can use subscription-manager to register.",
        #     "",
        #     "Last metadata expiration check: 0:02:10 ago on Wed 10 May 2023 08:50:36 PM UTC.",
        #     "Available Packages",
        #     "java-1.8.0-openjdk.x86_64             1:1.8.0.372.b07-2.el9 rhel-9-appstream-rhui-rpms",
        #     "java-1.8.0-openjdk-demo.x86_64        1:1.8.0.372.b07-2.el9 rhel-9-appstream-rhui-rpms",
        #     ...,
        # ]
        stdout = self.client.execute_command("yum list java*")
        logger.info(stdout)

        min_java_ver = pver.parse("1.6.999")
        java_versions = [java_version.split(" ")[0].strip() for java_version in stdout if "java" in java_version]
        java_version = [
            ver for ver in java_versions if (jv := re.search(r"\d.\d.\d", ver)) and pver.parse(jv[0]) >= min_java_ver
        ][0]
        logger.info(f"Java Version to be installed is {java_version}")

        stdout = self.client.execute_command_sudo_passwd(f"yum install {java_version} --assumeyes")
        assert self.client.check_for_string_in_stdout(stdout, ["Complete", "Nothing to do"])
        stdout = self.client.execute_command_sudo_passwd("yum install unzip --assumeyes")
        assert self.client.check_for_string_in_stdout(
            stdout,
            ["Complete", "Nothing to do"],
        )
        stdout = self.client.execute_command_sudo_passwd(f"unzip -o {self.archive}")
        assert self.client.check_for_string_in_stdout(stdout, ["example5", "Nothing to do"])

    def install_java_on_suse_linux(self):
        """
        Installs Java on a SUSE Linux system using zypper package manager.

        This method performs the following steps:
        1. Searches for available OpenJDK development packages using zypper.
        2. Logs the output of the search command.
        3. Selects a specific Java version to install (default is java-11-openjdk-devel).
        4. Installs the selected Java version using zypper.
        5. Verifies the installation by checking for specific strings in the command output.
        6. Installs the unzip package using zypper.
        7. Verifies the installation of unzip by checking for specific strings in the command output.
        8. Unzips a specified archive file.
        9. Verifies the unzipping process by checking for specific strings in the command output.

        Raises:
            AssertionError: If any of the verification checks fail.

        Returns:
            None
        """
        stdout = self.client.execute_command("zypper search-packages openjdk-devel")
        logger.info(stdout)

        # output example
        # [
        #     "Refreshing service 'Basesystem_Module_x86_64'.",
        #     "Loading repository data...",
        #     "Reading installed packages...",
        #     "",
        #     "S | Name                     | Summary                            | Type",
        #     "S | Name                     | Summary                            | Type",
        #     "--+--------------------------+------------------------------------+--------",
        #     "  | java-1_8_0-openjdk-devel | OpenJDK 8 Development Environment  | package",
        #     "  | java-11-openjdk-devel    | OpenJDK 11 Development Environment | package",
        #     "  | java-17-openjdk-devel    | OpenJDK 17 Development Environment | package",
        # ]

        # java_versions = [java_version for java_version in stdout if "java" in java_version]
        # java_version = java_versions[0].split("|")[1].strip()
        # logger.info(f"Java Version to be installed is {java_version}")

        java_version = "java-11-openjdk-devel"
        stdout = self.client.execute_command(f"zypper --non-interactive install {java_version}")
        assert self.client.check_for_string_in_stdout(
            stdout, ["done", "update-alternatives", f"Installing: {java_version}", "Nothing to do"]
        )
        stdout = self.client.execute_command("zypper --non-interactive install unzip")
        assert self.client.check_for_string_in_stdout(
            stdout,
            ["Complete", "Nothing to do"],
        )
        stdout = self.client.execute_command(f"unzip -o {self.archive}")
        assert self.client.check_for_string_in_stdout(stdout, ["example5", "Nothing to do"])

    def copy_vdbench_custom_config_file_to_remote_host(self, vdbench_custom_config_file: str):
        """
        Copies a Vdbench custom configuration file to a remote host.

        Args:
            vdbench_custom_config_file (str): The path to the Vdbench custom configuration file to be copied.
        """
        self.client.change_directory(self.home_directory)
        self.client.copy_file(
            vdbench_custom_config_file,
            vdbench_custom_config_file,
        )

    def create_vdbench_config_file_for_generating_files_and_dirs(
        self,
        vdbench_settings: VDBenchSettings,
        file_size: str = "1g",
        file_count: int = 2,
        dir_name: str = "/dir1",
        depth: int = 1,
        width: int = 2,
    ):
        """
        Creates a Vdbench configuration file for generating files and directories.

        Args:
            vdbench_settings (VDBenchSettings): Settings for Vdbench configuration.
            file_size (int): Size of each file to be generated. Defaults to "1g".
            file_count (int): Number of files to be generated. Defaults to 2.
            dir_name (str): Name of the directory where files will be generated. Defaults to "/dir1".
            depth (int): Depth of the directory structure. Defaults to 1.
            width (int): Width of the directory structure. Defaults to 2.

        Returns:
            None
        """
        devices = self.get_devices()
        config_path = f"{self.home_directory}/config"
        basic_content = list()
        fsd_content = list()
        fwd_content = list()
        frd_content = list()
        for serial in range(1, len(devices) + 1):
            config = {"basic": {}, "fsd": {}, "fwd": {}, "frd": {}}
            storage_definition = vdbench_settings.fsd % (serial, dir_name, depth, width, file_count, file_size)
            workload_definition = vdbench_settings.fwd % (serial, serial, "$operation")
            run_definition = vdbench_settings.frd % (serial, "$format")
            if serial == 1:
                config["basic"].update(
                    loads(
                        BasicParameters(
                            comp_ratio=f"compratio={vdbench_settings.comp_ratio}",
                            validate=f"validate={vdbench_settings.validate_vdbench}",
                            dedup_ratio=f"dedupratio={vdbench_settings.dedup_ratio}",
                            dedup_unit=f"dedupunit={vdbench_settings.dedup_unit}\n",
                        ).model_dump_json()
                    )
                )
                config["fsd"].update(loads(StorageDefinitions(storage_definition=storage_definition).model_dump_json()))
                config["fwd"].update(
                    loads(WorkloadDefinitions(workload_definition=workload_definition).model_dump_json())
                )
                config["frd"].update(loads(RunDefinitions(run_definition=run_definition).model_dump_json()))
                basic_content.extend(list(config["basic"].values()))
                fsd_content.extend(list(config["fsd"].values()))
                fwd_content.extend(list(config["fwd"].values()))
                frd_content.extend(list(config["frd"].values()))
            else:
                config["fsd"].update(loads(StorageDefinitions(storage_definition=storage_definition).model_dump_json()))
                config["fwd"].update(
                    loads(WorkloadDefinitions(workload_definition=workload_definition).model_dump_json())
                )
                config["frd"].update(loads(RunDefinitions(run_definition=run_definition).model_dump_json()))
                fsd_content.extend(list(config["fsd"].values()))
                fwd_content.extend(list(config["fwd"].values()))
                frd_content.extend(list(config["frd"].values()))
        content = basic_content + fsd_content + fwd_content + frd_content
        content = [line + "\n" for line in content]
        self.create_vdbench_config_on_instance(remote_file=config_path, content=content)

    def run_vdbench(self, validate=False, custom_config_file_name="config"):
        """
        Executes the Vdbench tool on a remote client.

        Parameters:
        validate (bool): If True, runs Vdbench in validation mode with read operation.
                         If False, runs Vdbench in normal mode with write operation.
        custom_config_file_name (str): The name of the custom configuration file to use. Default is "config".

        Returns:
        bool: True if the Vdbench execution completed successfully, False otherwise.
        """
        success_message = "Vdbench execution completed successfully"

        operation = "write" if not validate else "read"
        command = f"sudo ./vdbench -j -f {custom_config_file_name} format=no operation={operation} "
        logger.info(f"Running Vdbench with command: {command}")

        command_output = self.client.execute_command_sudo_passwd(command)
        logger.info(f"Vdbench execution output: {command_output}")

        result = False
        for output in command_output:
            if success_message in output:
                result = True
                break

        logger.info(f"Vdbench execution result: {result}")
        return result

    def add_proxy_to_instance(self, proxy_settings: ProxySettings):
        """
        Adds proxy settings to the instance by appending the proxy configuration
        to the /etc/apt/apt.conf.d/95proxies file.
        This function is necessary to make calls to internet. \n
        Commands like 'apt-get update' etc. need this proxy setting.

        Args:
            proxy_settings (ProxySettings): An object containing the HTTP and HTTPS
                                            proxy settings to be added.

        Raises:
            Exception: If the command execution fails.
        """
        command = f"""
        echo -e 'Acquire::http::Proxy "{proxy_settings.http_proxy}";\nAcquire::https::Proxy "{proxy_settings.https_proxy}";' | sudo tee -a /etc/apt/apt.conf.d/95proxies
        """
        logger.info(f"Adding proxy to the instance with command: {command}")
        self.client.execute_command_sudo_passwd(command)
