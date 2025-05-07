import logging
import paramiko
import sys
import time

from lib.common.constants import cxo_cluster_console_ports as SwitchConsolePorts
from lib.common.constants import cxo_console_servers as CXOConsoles

from paramiko.ssh_exception import SSHException, BadHostKeyException, BadAuthenticationType

LOGIN_PROMPT = "login:"
ARRAY_PROMPT = "#"

PASSWORD_PROMPT: str = "Password:"

# default
COMMAND_WAIT = 2.0
LOGIN_WAIT = 4.0

SHELL_RECV_SIZE: int = 1024 * 3


class ArrayReinit:
    def __init__(
        self,
        console_username: str,
        console_password: str,
        console_port: str,
        array_serial_number: str,
        array_name: str,
        array_username: str,
        array_password: str,
        stdout: bool = False,
    ):
        """
        Initialize the ArrayReinit class.

        Args:
            console_username (str): Username for the console server.
            console_password (str): Password for the console server.
            console_port (str): Console port to connect to.
            array_serial_number (str): Serial number of the array.
            array_name (str): Name of the array.
            array_username (str): Admin username for the array.
            array_password (str): Admin password for the array.
            stdout (bool): If True, log to stdout. Default is False.
        """
        self.console_server = CXOConsoles.CXO_CONSOLE_SERVER_1
        self.console_username = console_username
        self.console_password = console_password
        self.console_port = console_port
        self.array_serial_number = array_serial_number
        self.array_name = array_name
        self.array_username = array_username
        self.array_password = array_password

        self.ssh: paramiko.SSHClient = None
        self.shell: paramiko.Channel = None

        # Create non-root logger, to allow stdout stream addition for manual execution
        self.logger = logging.getLogger("ArrayReinit")
        self.logger.setLevel(logging.INFO)
        if stdout:
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.logger.info("Array Reinit")
        self.logger.info(f"Console Port: {self.console_port}")

        # Connect to the Console Server
        self.logger.info(f"Connecting to Console Server: {self.console_server}")

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh.connect(
                hostname=self.console_server, username=self.console_username, password=self.console_password
            )
            self.logger.info(f"Successfully connected to Console Server: {self.console_server}")

            # invoke interactive shell to send() and recv() commands and output
            self.shell = self.ssh.invoke_shell()

            # flush current output from cxo-console connection
            output = self.shell.recv(SHELL_RECV_SIZE)
            self.logger.info(f"Console Server connection output: {output.decode()}")

        except BadAuthenticationType as ba:
            self.logger.error(f"Bad Authentication: {ba}")
            self.ssh = None
        except BadHostKeyException as bh:
            self.logger.error(f"Bad Host Key: {bh}")
            self.ssh = None
        except SSHException as e:
            self.logger.error(f"Failed to connect to Console Server: {self.console_server}: {e}")
            self.ssh = None

    def __del__(self):
        """
        Destructor for the ArrayReinit class.
        """
        if self.shell:
            self.logger.info("Closing Interactive Shell")
            self.shell.close()

        if self.ssh:
            self.logger.info(f"Closing SSH connection to Console Server: {self.console_server}")
            self.ssh.close()

    def _send_command(self, command: str, wait: float = COMMAND_WAIT):
        """
        Send a command and wait.

        NOTE: During testing, it was observed that some wait needs to be given after every command.
              We can send() data more quickly than it is ready to be received.

        Args:
            command (str): Command to send.
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
        # ignore decode errors:
        # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 2860: invalid start byte
        output_decode = self.shell.recv(SHELL_RECV_SIZE).decode(errors="ignore")
        self.logger.info(output_decode)

        return output_decode

    def _connect_and_login_to_array(self) -> bool:
        """
        Connect to the array via console.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        # Telnet to the Array Node console port
        command_str = f"telnet {SwitchConsolePorts.CXO_CONSOLE_SWITCH} {self.console_port}\n"
        self.logger.info(f"Executing Command: {command_str}")
        self._send_command(command_str)

        # send CR to obtain prompt
        self._send_command("\n")
        output_decode = self._get_output()

        # It's possible the prompt is "Password:". Send a \n to get to "login:" prompt
        if PASSWORD_PROMPT in output_decode:
            self._send_command("\n")
            # update output to get the login prompt
            output_decode = self._get_output()

        # It's possible the connection is already logged into the array
        if LOGIN_PROMPT in output_decode:
            # Log into array
            self._send_command(f"{self.array_username}\n")
            ####
            output_decode = self._get_output()
            while PASSWORD_PROMPT not in output_decode:
                self.logger.info("Wait for password prompt...")
                output_decode = self._get_output()
            # send password
            self._send_command(f"{self.array_password}\n", wait=LOGIN_WAIT)
            output_decode = self._get_output()

        # check for the array prompt
        if ARRAY_PROMPT not in output_decode:
            self.logger.error("Failed to login to Array")
            return False

        return True

    def _logout_and_disconnect_from_array(self, exit_array: bool = False):
        """
        Disconnect from the array via console.

        Args:
            exit_array (bool): If True, send "exit" to logout from the array before disconnecting from Console server. Default is False.
        """
        # logout from array
        if exit_array:
            self._send_command("exit\n")

        # send '^]' to end telnet connection
        # CTRL-] (ASCII code 29, represented as \x1d in hexadecimal).
        self._send_command("\x1d")
        # quit telnet
        self._send_command("q\n")
        self._get_output()

    def reinit_array(self) -> bool:
        """
        Reinitialize the array.

        Returns:
            bool: True if reinit is successful, False otherwise.
        """
        # login to array
        if not self._connect_and_login_to_array():
            self.logger.error("Failed to login to Array")
            return False

        # issue the "servicesys reinit" command
        command_str = "servicesys reinit\n"
        self.logger.info(f"Executing Command: {command_str}")
        self._send_command(command_str)

        self.output_decode = self._get_output()
        # The following error will be present if the Array has already had "servicesys reinit" executed:
        # Error: System manager state: executing manual startup
        # WARNING: servicesys has been aborted.
        if "System manager state: executing manual startup" in self.output_decode:
            self.logger.warning("The array is already in manual startup mode. Cannot proceed with reinit.")
            self._logout_and_disconnect_from_array(exit_array=True)  # ensure we logout from the array
            return False

        # provide the array serial number / array name to confirm
        command_str = f"{self.array_serial_number}/{self.array_name}\n"
        self.logger.info(f"Confirming with: {command_str}")
        self._send_command(command_str)

        self.output_decode = self._get_output()
        # the "reinit" process takes ~20 minutes to complete on both Nodes
        # timeout is set to 30 minutes
        reinit_complete: bool = False
        nodes_complete: int = 0
        timeout: float = 30 * 60  # 30 minutes
        start_time: float = time.time()

        # A complete log of the reinit process shows that the line containing
        # "iostack started" signifies a Node is completely reinitialized.
        # The complete log has 2 of these lines:
        # 1) iostack started (pid: 5267) 2025-04-07 14:46:59 MDT
        # 2) iostack started (pid: 5253) 2025-04-07 14:57:05 MDT
        while not reinit_complete:
            # check for timeout
            if time.time() - start_time > timeout:
                self.logger.error("Timeout waiting for reinit to complete (30 minutes)")
                break

            time.sleep(5)

            self.output_decode = self._get_output()
            # check for the "iostack started" line
            if "iostack started" in self.output_decode:
                nodes_complete += 1
                self.logger.info(f"Node reinit complete: {nodes_complete}")

            # check if both nodes are complete
            if nodes_complete == 2:
                reinit_complete = True
                self.logger.info("Reinit process complete")

        # logout from Console - after successful "reinit", we are at the "login:" prompt again.
        # no need to "exit_array"
        self._logout_and_disconnect_from_array()

        return reinit_complete
