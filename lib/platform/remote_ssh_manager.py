import time
import paramiko
from paramiko.channel import ChannelFile
import urllib.parse
import logging
import httplib2

from morpheus_api.configuration.utils import proxies

logger = logging.getLogger()


class RemoteConnect:
    def __init__(
        self,
        host_ip: str,
        username: str,
        password: str,
        key_filename: str = None,
        pkey: paramiko.PKey = None,
        sock: bool = True,
        window_size: int = 52428800,
        packet_size: int = 327680,
    ):
        """
        Establish connection to an instance and open sftp connection

        Args:
            host_ip (str): Host IP of the instance. Can be obtained by instance.instance_details.connection_info[0].ip
            username (str): Username to connect to the instance
            password (str): Password to connect to the instance
            key_filename (str, optional): Key filename to connect to the instance. Defaults to None.
            pkey (PKey, optional): Private key to connect to the instance. Defaults to None.
            sock (bool, optional): Socket connection to the instance. Defaults to True.
            window_size (int, optional): Window size of the connection. Defaults to 52428800.
            packet_size (int, optional): Packet size of the connection. Defaults to 327680.

        Raises:
            e: Exception if connection fails
        """
        self.proxy_uri: str = proxies.get("http")
        self.port: int = 22
        self.host: str = host_ip
        self.username: str = username
        self.password: str = password
        logger.info("Create paramiko SSHClient")
        self.client: paramiko.SSHClient = paramiko.SSHClient()
        logger.info("Client created.")
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sock = None
        if sock:
            self.sock = self.set_sock_tunnel()

        logger.info(
            f"RemoteConnect: hostname={self.host}, port={self.port}, username={self.username}, \
            key_filename={key_filename}, sock={self.sock}, pkey={pkey}, \
            window_size={window_size}, packet_size={packet_size}, proxy={self.proxy_uri}"
        )

        try:
            logger.info("Paramiko client connecting")
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                key_filename=key_filename,
                pkey=pkey,
                sock=self.sock,
                banner_timeout=200,
            )
        except Exception as e:
            logger.warning(f"Paramiko client connection Failed. {e=}")
            raise e

        logger.info("Paramiko client connected")

        tr = self.client.get_transport()
        if packet_size:
            tr.default_max_packet_size = packet_size
        if window_size:
            tr.default_window_size = window_size

        logger.info("Opening paramiko client sftp")
        self.sftp = self.client.open_sftp()
        logger.info("Paramiko client sftp opened")

    def set_sock_tunnel(self):
        """
        Connect to the server specified

        Returns:
            obj: connection object
        """
        logger.info(f"Starting proxy connection to {self.proxy_uri}...")
        self.url = urllib.parse.urlparse(self.proxy_uri)
        # NOTE: Using import httplib2 instead of http.client to avoid the SSH protocol banner error when sock = True
        self.http_con = httplib2.HTTPConnectionWithTimeout(self.url.hostname, self.url.port)
        logger.info("Proxy connected.")
        return self.http_con.sock

    def execute_command(
        self,
        command: str,
        super_user: bool = True,
        check_status: bool = True,
        readline: bool = False,
        retry_count: int = 0,
    ):
        """
        Execute command on an instance

        Args:
            command (str): Command to be executed
            super_user (bool, optional): Run command as super user. Defaults to True.
            check_status (bool, optional): Check the status of the command. Defaults to True.
            readline (bool, optional): Read the output line by line. Defaults to False.
            retry_count (int, optional): Number of command retries. Defaults to 0.

        Returns:
            list: output of the command
        """
        command = f"sudo {command}" if super_user else command

        for i in range(retry_count + 1):
            stdin, stdout, stderr = self.client.exec_command(command)
            # recv_exit_status() will wait for the command completion
            logger.info(stdin)
            exit_status = stdout.channel.recv_exit_status()
            if check_status:
                logger.info(f"Exit Status: {exit_status}")
                if exit_status == 0:
                    return self._delete_newline_char(stdout, readline)
                else:
                    logger.info("Failed to execute command on instance")
                    logger.info(stderr)
                    if i == retry_count:
                        logger.debug(f"Failed to execute command on instance after {retry_count} retry attempts!")
                        raise Exception(f"Failed to execute command {command} on instance ; stdout: {stdout.read()}")
                    else:
                        logger.info(f"Failed to execute command {command} on instance ; stdout: {stdout.read()}")
                        logger.info(f"Retrying {i} . . .")
                        time.sleep(2)
                        continue

            else:
                return self._delete_newline_char(stdout, readline)

    def execute_command_sudo_passwd(
        self,
        command: str,
        check_status: bool = True,
        readline: bool = False,
        retry_count: int = 0,
    ) -> list[str]:
        """
        Execute command on an instance as super-user with password

        Args:
            command (str): Command to be executed
            check_status (bool, optional): Check the status of the command. Defaults to True
            readline (bool, optional): Read the output line by line. Defaults to False
            retry_count (int, optional): Number of command retries. Defaults to 0

        Returns:
            list: output of the command
        """
        command = f"sudo {command}"

        for i in range(retry_count + 1):
            # get pseudo-terminal
            stdin, stdout, stderr = self.client.exec_command(command=command, get_pty=True)
            # give password
            stdin.write(self.password + "\n")
            # recv_exit_status() will wait for the command completion
            logger.info(stdin)
            exit_status = stdout.channel.recv_exit_status()
            if check_status:
                logger.info(f"Exit Status: {exit_status}")
                if exit_status == 0:
                    return self._delete_newline_char(stdout, readline)
                else:
                    logger.info("Failed to execute command on instance")
                    logger.info(stderr)
                    if i == retry_count:
                        logger.debug(f"Failed to execute command on instance after {retry_count} retry attempts!")
                        raise Exception(f"Failed to execute command {command} on instance ; stdout: {stdout.read()}")
                    else:
                        logger.info(f"Failed to execute command {command} on instance ; stdout: {stdout.read()}")
                        logger.info(f"Retrying {i} . . .")
                        time.sleep(2)
                        continue

            else:
                return self._delete_newline_char(stdout, readline)

    def _delete_newline_char(self, stdout: ChannelFile, readline: bool) -> list[str]:
        """
        Format the output from exec_command

        Args:
            stdout (ChannelFile): stdout channel returned by exec_command()
            readline (bool): Read the output line by line

        Returns:
            list: command output
        """
        lines: list[str] = []
        if readline:
            while True:
                lines.append(stdout.readline())
                if stdout.channel.exit_status_ready():
                    break
        else:
            lines = stdout.readlines()
        return [line.strip("\n") for line in lines]

    def close_connection(self):
        """
        Close ssh and sftp connections
        """
        try:
            logger.info("SFTP - closing")
            self.sftp.close()
            logger.info("SFTP -  closed")
        except Exception as e_close:
            logger.warning(f"SFTP connection closing {e_close=}")
        try:
            logger.info("paramiko client -  closing")
            self.client.close()
            logger.info("paramiko client -  closed")
        except Exception as e_close:
            logger.warning(f"Paramiko client closing {e_close=}")
        # closing connection need time to close
        time.sleep(60)

    def sftp_exists(self, remote_path: str):
        """
        Check if a file or directory exists on the remote server

        Args:
            remote_path (str): Absolute path of the file or directory on the remote server

        Returns:
            bool: True if the file or directory exists, False otherwise
        """
        try:
            self.sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False

    def copy_file(self, local_path: str, remote_path: str):
        """
        Copy file from local to remote server

        Args:
            local_path (str): Absolute path of local file
            remote_path (str): Absolute path of remote file
        """
        try:
            self.sftp.put(local_path, remote_path)
        except (IOError, OSError) as e:
            logger.debug(f"Exeception while copying file to ec2 instance:: {e}")
            raise e

    def change_directory(self, path: str = "."):
        """
        Change working directory on the remote server

        Args:
            path (str, optional): Absolute path to set working directory. Defaults to '.'.
        """
        try:
            self.sftp.chdir(path)
        except IOError as e:
            logger.debug(f"Exeception while changing directory:: {e}")
            raise e

    def check_command(self, command: str, retry_count: int = 0):
        """Check whether the command exits or not

        Args:
            command (str): Command to be executed
            retry_count (int, optional): Number of command retries. Defaults to 0.

        Returns:
            Bool: Return True if command exists else return False
        """
        for _ in range(retry_count + 1):
            _, stdout, _ = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                return True
        return False

    def check_for_string_in_stdout(self, stdout: list[str], query_list: list[str]):
        """
        Checks if any of the strings in the query_list are present in the stdout.

        Args:
            stdout (list[str]): A list of strings representing the standard output.
            query_list (list[str]): A list of query strings to search for in the stdout.

        Returns:
            bool: True if any query string is found in the stdout, False otherwise.
        """
        for query in query_list:
            for line in stdout:
                if query in line:
                    return True
        else:
            return False

    def write_data_to_remote_file(self, remote_file: str, content: list[str], mode="a"):
        """
        Writes data to a remote file via SFTP.

        Args:
            remote_file (str): The path to the remote file where data will be written.
            content (list[str]): A list of strings to be written to the remote file.
            mode (str, optional): The mode in which the file is opened. Defaults to "a" (append mode).

        Returns:
            bool: True if the data was successfully written to the remote file, False otherwise.

        Raises:
            Exception: If there is an error during the file write operation, it will be logged.
        """
        try:
            file = self.sftp.file(remote_file, mode, -1)
            for line in content:
                file.write(line)
                file.flush()
            return True
        except Exception as e:
            logger.error("Fail to write data to the remote file, Please check the error message below.")
            logger.debug(e)
            return False
