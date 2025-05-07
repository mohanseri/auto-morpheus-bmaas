import logging
import paramiko
import re
import sys
import threading
import time

from paramiko.ssh_exception import SSHException, BadHostKeyException, BadAuthenticationType

# default
COMMAND_WAIT: float = 2.0
CLEAR_LOGIN_WAIT: float = 6.0

SHELL_RECV_SIZE: int = 1024 * 3

ILO_PROMPT: str = "</>hpiLO->"

NODE_PROMPT: str = "hvadmin@hv-ubuntu:~$"

USERNAME_PROMPT: str = "hv-ubuntu login:"
PASSWORD_PROMPT: str = "Password:"


def install_dsc_vm_on_cluster(
    jumphost_ip: str,
    jumphost_user: str,
    jumphost_pass: str,
    cluster_node_data: list,
    dsc_qcow2_file_path: str,
    dsc_script_file_path: str,
    dsc_vm_ova_file_path: str = None,
    morpheus_ova_file_path: str = None,
    stdout: bool = False,
):
    """
    Install the DSC VM on a cluster of Nodes.

    Args:
        jumphost_ip (str): IP address of the CXO Jumphost.
        jumphost_user (str): Username for the CXO Jumphost.
        jumphost_pass (str): Password for the CXO Jumphost.
        cluster_node_data (list): The list of node data: iLO IP, iLO username & password, Node username & password.
            [["ilo_ip", "ilo_username", "ilo_password", "node_user", "node_pass"], ...]
        dsc_qcow2_file_path (str): Path to the DSC QCOW2 file.
        dsc_script_file_path (str): Path to the DSC install script.
        dsc_vm_ova_file_path (str, optional): Path to the DSC OVA file. Defaults to None.
            If present, it is copied to: /var/morpheus/ovas/dsc/
        morpheus_ova_file_path (str, optional): Path to the Morpheus OVA file. Defaults to None.
            If present, it is copied to: /var/morpheus/ovas/vme-manager/
        stdout (bool, optional): If True, log to stdout. Defaults to False.
    """
    # create the threads for the cluster nodes
    threads: list[threading.Thread] = []
    for ilo_ip, ilo_username, ilo_password, node_user, node_pass in cluster_node_data:
        dsc_install = DSCInstall(
            jumphost_ip=jumphost_ip,
            jumphost_user=jumphost_user,
            jumphost_pass=jumphost_pass,
            ilo_ip=ilo_ip,
            ilo_user=ilo_username,
            ilo_pass=ilo_password,
            node_user=node_user,
            node_pass=node_pass,
            stdout=stdout,
        )
        thread = threading.Thread(
            target=dsc_install.dsc_install,
            args=(
                dsc_qcow2_file_path,
                dsc_script_file_path,
                dsc_vm_ova_file_path,
                morpheus_ova_file_path,
            ),
        )
        threads.append(thread)

    # start the threads
    for thread in threads:
        thread.start()

    # wait for all threads to complete
    for thread in threads:
        thread.join()


class DSCInstall:
    def __init__(
        self,
        jumphost_ip: str,
        jumphost_user: str,
        jumphost_pass: str,
        ilo_ip: str,
        ilo_user: str,
        ilo_pass: str,
        node_user: str,
        node_pass: str,
        stdout: bool = False,
    ):
        """
        Initialize the DSCInstall class.
        Args:
            jumphost_ip (str): IP address of the CXO Jumphost.
            jumphost_user (str): Username for the CXO Jumphost.
            jumphost_pass (str): Password for the CXO Jumphost.
            ilo_ip (str): IP address of the iLO.
            ilo_user (str): Username for the iLO.
            ilo_pass (str): Password for the iLO.
            node_user (str): Username for the Node.
            node_pass (str): Password for the Node.
            stdout (bool, optional): If True, log to stdout. Defaults to False.
        """
        self.jumphost_ip = jumphost_ip
        self.jumphost_user = jumphost_user
        self.jumphost_pass = jumphost_pass

        self.ilo_ip = ilo_ip
        self.ilo_user = ilo_user
        self.ilo_pass = ilo_pass
        self.node_user = node_user
        self.node_pass = node_pass

        self.ssh: paramiko.SSHClient = None
        self.shell: paramiko.Channel = None

        self.logger = logging.getLogger(f"DSCInstall-{ilo_ip}")
        self.logger.setLevel(logging.INFO)

        if stdout:
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

        # Connect to the CXO Jumphost
        self.logger.info(f"[{self.ilo_ip}] Connecting to CXO Jumphost: {self.jumphost_ip}")

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh.connect(hostname=self.jumphost_ip, username=self.jumphost_user, password=self.jumphost_pass)
            self.logger.info(f"[{self.ilo_ip}] Successfully connected to CXO Jumphost: {self.jumphost_ip}")

            # invoke interactive shell to send() and recv() commands and output
            self.shell = self.ssh.invoke_shell()

            # flush current output from cxo-console connection
            output = self.shell.recv(SHELL_RECV_SIZE)
            self.logger.info(f"[{self.ilo_ip}] cxo-jumphost connection output: {output.decode()}")

        except BadAuthenticationType as ba:
            self.logger.error(f"[{self.ilo_ip}] Bad Authentication: {ba}")
            self.ssh = None
        except BadHostKeyException as bh:
            self.logger.error(f"[{self.ilo_ip}] Bad Host Key: {bh}")
            self.ssh = None
        except SSHException as e:
            self.logger.error(f"[{self.ilo_ip}] Failed to connect to CXO Jumphost: {self.jumphost_ip}: {e}")
            self.ssh = None

    def __del__(self):
        """
        Destructor for the DSCInstall class.
        """
        if self.shell:
            self.logger.info(f"[{self.ilo_ip}] Closing Interactive Shell")
            self.shell.close()

        if self.ssh:
            self.logger.info(f"[{self.ilo_ip}] Closing SSH connection to CXO Jumphost: {self.jumphost_ip}")
            self.ssh.close()

    def _send_command(self, command: str, wait: float = COMMAND_WAIT):
        """
        Send a command and give wait for response.

        Args:
            command (str): Command to send to the switch.
            wait (float, optional): Wait time (seconds) after sending the command. Defaults to 2.0.
        """
        self.shell.send(command)
        time.sleep(wait)

    def _get_output(self) -> str:
        """
        Get the output from the shell.

        Returns:
            str: Output from the shell.
        """
        self.output_decode = self.shell.recv(SHELL_RECV_SIZE).decode()
        self.logger.info(f"[{self.ilo_ip}] {self.output_decode}")
        return self.output_decode

    def _connect_and_login_to_ilo(self) -> bool:
        """
        Connect to the iLO via SSH.

        Returns:
            bool: True if the iLO was connected successfully, False otherwise.
        """
        if not self.ssh:
            self.logger.error(f"[{self.ilo_ip}] No SSH connection to CXO Jumphost: {self.jumphost_ip}")
            return False

        # Connect to the iLO via SSH
        self.logger.info(f"[{self.ilo_ip}] Connecting to iLO via SSH: {self.ilo_ip}")

        self.command_str = f"ssh -oStrictHostKeyChecking=accept-new {self.ilo_user}@{self.ilo_ip}\n"
        self.logger.info(f"[{self.ilo_ip}] Executing Command: {self.command_str}")

        self._send_command(self.command_str)
        self._send_command(f"{self.ilo_pass}\n")
        # should be at iLO Prompt - check for "</>hpiLO->" in output
        self.output_decode = self._get_output()

        if ILO_PROMPT not in self.output_decode:
            self.logger.error(f"[{self.ilo_ip}] Failed to login to Host iLO: {self.ilo_ip}")
            return False

        return True

    def _get_node_link_local_via_ilo(self) -> str:
        """
        Get the link-local address of the Node via iLO.

        Returns:
            str: Link-local address of the Node.
        """
        self.link_local_ip: str = None

        # SSH into iLO
        self.logger.info(f"[{self.ilo_ip}] Logging into iLO: {self.ilo_ip}")
        if not self._connect_and_login_to_ilo():
            return self.link_local_ip

        # Start VSP
        self._send_command("vsp\n")
        self.output_decode = self._get_output()

        # It's possible the VSP is at "Password:". Send a \n to get to "hv-ubuntu login:" prompt
        if PASSWORD_PROMPT in self.output_decode:
            self._send_command("\n", wait=CLEAR_LOGIN_WAIT)
            # update output to get the login prompt
            self.output_decode = self._get_output()

        # It's possible the VSP is already logged into the HV Node
        if USERNAME_PROMPT in self.output_decode:
            # Log into Host as hvadmin
            self._send_command(f"{self.node_user}\n")
            self._send_command(f"{self.node_pass}\n")
            # clear buffer
            self._get_output()

        # execute "ip a" and grab address starting with "169.254."
        # color=never to prevent codes: "inet 169.254.\x1b[m\x1b[K217.211/16 metric 2048 brd 169.254.255.255 scope link mgmt"
        self._send_command("ip a | grep --color=never '169.254.'\n")
        self.output_decode = self._get_output()

        # The output will also contain the command and prompt
        #
        # ip a | grep --color=never '169.254.'
        # inet 169.254.222.56/16 metric 2048 brd 169.254.255.255 scope link ens224
        # hvadmin@hv-ubuntu:~$
        self.match = re.search(r"inet 169.254.(\d+\.\d+)", self.output_decode)
        self.ip = self.match.group(0) if self.match else None
        if self.ip:
            self.link_local_ip = self.ip.split()[1]
            self.logger.info(f"[{self.ilo_ip}] Link Local IP: {self.link_local_ip}")
        else:
            self.logger.error(f"[{self.ilo_ip}] No match for Node Link Local IP")

        # Log out of Host
        self._send_command("exit\n")

        # Exit VSP "ESC ("
        self._send_command("\033(")

        # Log out of iLO
        self._send_command("exit\n")
        # clear buffer
        self._get_output()

        return self.link_local_ip

    def _scp_file_from_jumphost_to_node(self, file_from_jumphost: str, target_file_path: str):
        """
        Copy a file from the jumphost to the Node.

        Args:
            file_from_jumphost (str): Path to the file on the jumphost.
            target_file (str): Path to the target file on the Node.
        """
        # save just the file portion of the target_file path
        self.target_filename = target_file_path.split("/")[-1]

        # Copy file function will:
        # scp file to Node /home/hvadmin directory
        self.logger.info(f"[{self.ilo_ip}] Copy file to node: {file_from_jumphost}")
        self.command_str: str = (
            f"scp -c aes256-ctr -oStrictHostKeyChecking=accept-new {file_from_jumphost} {self.node_user}@{self.link_local_ip}:/home/hvadmin/{self.target_filename}\n"
        )
        self._send_command(self.command_str)
        self._send_command(f"{self.node_pass}\n")
        self.output_decode = self._get_output()

        self.logger.info(f"[{self.ilo_ip}] Wait for copy to complete")
        while "100%" not in self.output_decode:
            time.sleep(5)
            self.output_decode = self._get_output()

        # log into Node, sudo su
        self.logger.info(f"[{self.ilo_ip}] Log into node")
        self._ssh_enter_node()

        # move file to target location
        self.logger.info(f"[{self.ilo_ip}] Move file to final location: {target_file_path}")
        self.command_str = f"mv /home/hvadmin/{self.target_filename} {target_file_path}\n"
        self._send_command(self.command_str)
        self.output_decode = self._get_output()

        # stay here until we have a prompt again
        self.logger.info(f"[{self.ilo_ip}] Wait for move to complete")
        while "root@" not in self.output_decode:
            time.sleep(5)
            self.output_decode = self._get_output()

        # log out of Node
        self.logger.info(f"[{self.ilo_ip}] Log out of node")
        self._ssh_exit_node()

    def _ssh_enter_node(self) -> bool:
        """
        SSH into the Node, and "sudo su".

        Returns:
            bool: True if the login was successful, False otherwise.
        """
        # log into node with link-local address
        self.logger.info(f"[{self.ilo_ip}] Connecting to Node: {self.link_local_ip}")

        self.command_str = (
            f"ssh -c aes256-ctr -oStrictHostKeyChecking=accept-new {self.node_user}@{self.link_local_ip}\n"
        )
        self.logger.info(f"[{self.ilo_ip}] Executing Command: {self.command_str}")

        self._send_command(self.command_str)
        self._send_command(f"{self.node_pass}\n")
        self.output_decode = self._get_output()

        # should be at Node Prompt - check for "hvadmin@hv-ubuntu:~$" in output
        if NODE_PROMPT not in self.output_decode:
            self.logger.error(f"[{self.ilo_ip}] Failed to login to Node: {self.link_local_ip}")
            return False

        # sudo su
        self._send_command("sudo su\n")
        # clear buffer
        self._get_output()

        return True

    def _ssh_exit_node(self):
        """
        Exit the Node.
        """
        # exit "sudo su"
        self._send_command("exit\n")

        # log out of Node
        self._send_command("exit\n")
        # clear buffer
        self._get_output()

    def _validate_and_create_directories(self) -> bool:
        """
        Validate and create the necessary directories on the Node.

        Returns:
            bool: True if the expected directory was found, False otherwise.
        """
        # /var/morpheus should already exist
        self._send_command("cd /var/morpheus\n")
        self.output_decode = self._get_output()

        if "No such file or directory" in self.output_decode:
            self.logger.error(f"[{self.ilo_ip}] /var/morpheus does not exist")
            return False

        # mkdir /var/morpheus/dsc-vm
        self._send_command("mkdir /var/morpheus/dsc-vm/\n")

        # chmod 777 /var/morpheus/dsc-vm/
        self._send_command("chmod 777 /var/morpheus/dsc-vm/\n")

        # mkdir -p /var/morpheus/kvm/local/
        self._send_command("mkdir -p /var/morpheus/kvm/local/\n")
        # clear buffer
        self._get_output()

        return True

    def _setup_dsc_on_node(
        self,
        dsc_qcow2_file_path: str,
        dsc_script_file_path: str,
        dsc_vm_ova_file_path: str = None,
        morpheus_ova_file_path: str = None,
    ) -> tuple[bool, str]:
        """
        Setup DSC VM on the Node.

        Args:
            dsc_qcow2_file_path (str): Path to the DSC QCOW2 file.
            dsc_script_file_path (str): Path to the DSC install script.
            dsc_vm_ova_file_path (str, optional): Path to the DSC OVA file. Defaults to None.
                If present, it is copied to: /var/morpheus/ovas/dsc/
            morpheus_ova_file_path (str, optional): Path to the Morpheus OVA file. Defaults to None.
                If present, it is copied to: /var/morpheus/ovas/vme-manager/

        Returns:
            bool: True if the DSC VM Setup is successfully, False otherwise.
            str: Link-local address of the DSC VM if successful, None otherwise.
        """
        self.dsc_vm_link_local: str = None

        # log into Node with link-local address
        if not self._ssh_enter_node():
            return False, self.dsc_vm_link_local

        # /var/morpheus should already exist
        if not self._validate_and_create_directories():
            return False, self.dsc_vm_link_local

        # log out of Node
        self._ssh_exit_node()

        # copy from jumphost "dsc-vm-ks.cfg" to /var/morpheus/dsc-vm/dcs-ks.sh
        self._scp_file_from_jumphost_to_node(
            file_from_jumphost=dsc_script_file_path, target_file_path="/var/morpheus/dsc-vm/dsc-ks.sh"
        )

        # copy from jumphost the MVM DSC QCOW2 file to /var/morpheus/kvm/local/
        self._scp_file_from_jumphost_to_node(
            file_from_jumphost=dsc_qcow2_file_path,
            target_file_path=f"/var/morpheus/kvm/local/{dsc_qcow2_file_path.split("/")[-1]}",
        )

        # Copy over OVA(s) if filenames are provided
        if dsc_vm_ova_file_path:
            self._scp_file_from_jumphost_to_node(
                file_from_jumphost=dsc_vm_ova_file_path,
                target_file_path=f"/scratch/ovas/dsc/{dsc_vm_ova_file_path.split("/")[-1]}",
            )

        if morpheus_ova_file_path:
            self._scp_file_from_jumphost_to_node(
                file_from_jumphost=morpheus_ova_file_path,
                target_file_path=f"/scratch/ovas/vme-manager/{morpheus_ova_file_path.split("/")[-1]}",
            )

        # log into Node
        self._ssh_enter_node()

        # Update the "dsc-ks.sh" file
        # DSC_QCOW2="{dsc_qcow2_filename...}" - just filename, no path
        self.command_str = f"sed -i 's/DSC_QCOW2=.*/DSC_QCOW2=\"{dsc_qcow2_file_path.split("/")[-1]}\"/' /var/morpheus/dsc-vm/dsc-ks.sh\n"
        self._send_command(self.command_str)
        # SKIP_DOWNLOAD=true
        self.command_str = "sed -i 's/SKIP_DOWNLOAD=.*/SKIP_DOWNLOAD=true/' /var/morpheus/dsc-vm/dsc-ks.sh\n"
        self._send_command(self.command_str)
        # PERSONA="kvm-alletramp-dhci"
        self.command_str = "sed -i 's/PERSONA=.*/PERSONA=\"kvm-alletramp-dhci\"/' /var/morpheus/dsc-vm/dsc-ks.sh\n"
        self._send_command(self.command_str)
        # clear buffer
        self._get_output()

        # chmod +x dsc-ks.sh
        self.command_str = "chmod +x /var/morpheus/dsc-vm/dsc-ks.sh\n"
        self._send_command(self.command_str)
        # clear buffer
        self._get_output()

        # execute the script
        self.command_str = "/var/morpheus/dsc-vm/dsc-ks.sh\n"
        self._send_command(self.command_str)
        self.output_decode = self._get_output()

        # stay here until we have a prompt again
        while "root@" not in self.output_decode:
            time.sleep(5)
            self.output_decode = self._get_output()

        # output some virsh data
        # virsh list
        # virsh domifaddr Data-Services-Connector --source agent
        self._send_command("virsh list\n")
        self.output_decode = self._get_output()
        # we should find the DSC in a "running" state
        if "running" not in self.output_decode:
            self.logger.error("DSC VM not running")
            return False, self.dsc_vm_link_local

        # it can take a momment for the DSC VM to get its link-local addresses assigned
        time.sleep(60)

        self._send_command("virsh domifaddr Data-Services-Connector --source agent\n")
        self.output_decode = self._get_output()

        # output such as:
        #  root@hv-ubuntu:/home/hvadmin# virsh domifaddr Data-Services-Connector --source agent
        #  Name       MAC address          Protocol     Address
        # -------------------------------------------------------------------------------
        #  lo         00:00:00:00:00:00    ipv4         127.0.0.1/8
        #  -          -                    ipv6         ::1/128
        #  enp1s0     52:54:00:d8:8c:7f    ipv4         10.157.232.244/22
        #  -          -                    ipv6         fe80::5054:ff:fed8:8c7f/64
        #  -          -                    ipv4         169.254.11.17/16
        #  docker0    02:42:7b:f7:6c:6f    ipv4         172.17.0.1/24
        #  br-a759116f5418 02:42:0b:a3:c9:0a    ipv4         172.18.0.1/24

        # parse output for link-local address of the DSC VM
        self.match = re.search(r"169.254.(\d+\.\d+)", self.output_decode)
        self.ip = self.match.group(0) if self.match else None
        if self.ip:
            self.dsc_vm_link_local = self.ip
            self.logger.info(f"[{self.ilo_ip}] DSC VM Link Local IP: {self.dsc_vm_link_local}")
        else:
            self.logger.error(f"[{self.ilo_ip}] No match for DSC VM link-local IP after 30 seconds")

        # log out of Node
        self._ssh_exit_node()

        return self.dsc_vm_link_local is not None, self.dsc_vm_link_local

    def dsc_install(
        self,
        dsc_qcow2_file_path: str,
        dsc_script_file_path: str,
        dsc_vm_ova_file_path: str = None,
        morpheus_ova_file_path: str = None,
    ) -> tuple[bool, str]:
        """
        Install the DSC on the Node.

        Args:
            dsc_qcow2_file_path (str): Path to the DSC QCOW2 file.
            dsc_script_file_path (str): Path to the DSC install script.
            dsc_vm_ova_file_path (str, optional): Path to the DSC OVA file. Defaults to None.
                If present, it is copied to: /var/morpheus/ovas/dsc/
            morpheus_ova_file_path (str, optional): Path to the Morpheus OVA file. Defaults to None.
                If present, it is copied to: /var/morpheus/ovas/vme-manager/

        Returns:
            bool: True if the DSC VM Setup is successfully, False otherwise.
            str: Link-local address of the DSC VM if successful, None otherwise.
        """
        self.logger.info(f"[{self.ilo_ip}] START {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}")

        self.logger.info(f"[{self.ilo_ip}] Starting DSC Install on Node")
        self.logger.info(f"[{self.ilo_ip}] Obtaining Node link-local IP via iLO")

        # get the link-local address of the Node via iLO
        self.link_local_ip = self._get_node_link_local_via_ilo()

        self.logger.info(f"[{self.ilo_ip}] link-local IP of Node: {self.link_local_ip}")

        self.result, self.dsc_vm_link_local = self._setup_dsc_on_node(
            dsc_qcow2_file_path=dsc_qcow2_file_path,
            dsc_script_file_path=dsc_script_file_path,
            dsc_vm_ova_file_path=dsc_vm_ova_file_path,
            morpheus_ova_file_path=morpheus_ova_file_path,
        )

        self.logger.info(f"[{self.ilo_ip}] END {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}")

        if not self.result:
            self.logger.error(f"[{self.ilo_ip}] DSC VM Setup failed on Node: {self.link_local_ip}")
            return False, None
        else:
            self.logger.info(f"[{self.ilo_ip}] DSC VM Setup success on Node: {self.link_local_ip}")
            if self.dsc_vm_link_local:
                self.logger.info(f"[{self.ilo_ip}] DSC VM link-local IP: {self.dsc_vm_link_local}")
            else:
                self.logger.error(f"[{self.ilo_ip}] No link-local IP for DSC VM")
            return True, self.dsc_vm_link_local
