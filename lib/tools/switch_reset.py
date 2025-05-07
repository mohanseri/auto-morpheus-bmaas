import logging
import paramiko
import socket
import sys
import threading
import time

from lib.common.constants import cxo_cluster_console_ports as SwitchConsolePorts
from lib.common.constants import cxo_console_servers as CXOConsoles
from lib.common.constants import switch_commands as Commands
from lib.common.constants import cxo_cluster_ip_addresses as IPs
from lib.common.constants import switch_interfaces as Ports

from paramiko.ssh_exception import SSHException, BadHostKeyException, BadAuthenticationType

# This class is used to reset the switch to the default state: "reset_switch()",
# and configure to default settings: "switch_setup()"
#
# The SwitchReset class requires CXO-Console Access:
#
# 10.157.16.12	cxo-console1.cxo.storage.hpecorp.net
# 10.157.16.13	cxo-console2.cxo.storage.hpecorp.net
#
# Console Access requires 3PAR Credentials
#
# From the CXO-Console, Telnet will be used to connect to the Switch.
# Requires a CR (\n) to obtain the login prompt
#   1) telnet c3l2-5113-c1 6047
#
# Current Switch Credentials
# New Switch Password
# If no New Password is provided, the Current Password will be used
#
# 1) reset_switch()
# Steps 1, 2 and 3 from:
# https://confluence.storage.hpecorp.net/pages/viewpage.action?pageId=478079992
#
# 2) switch_setup()
# Steps 4 thru 8 from:
# https://confluence.storage.hpecorp.net/pages/viewpage.action?pageId=478079992


LOGIN_PROMPT = "login:"
SWITCH_PROMPT = "#"
PASSWORD_PROMPT = "Password:"

DEFAULT_USERNAME = "admin"

ONE_MINUTE = 60.0
ONE_HOUR = 3600.0

# default
COMMAND_WAIT = 2.0
HOSTNAME_WAIT = 3.0
LOGIN_WAIT = 4.0
WRITE_MEMORY_WAIT = 5.0
CLEAR_LOGIN_WAIT = 6.0

SHELL_RECV_SIZE = 1024 * 2


def reset_setup_switch_pair(
    console_username: str,
    console_password: str,
    switch_pair_data: list,
    mgmt_vlan: str,
    reset_switch: bool = True,
    setup_switch: bool = True,
    set_mgmt_interface: bool = False,
    stdout: bool = False,
):
    """
    Reset and Setup a Switch Pair.

    Args:
        console_username (str): Console Server Username
        console_password (str): Console Server Password
        switch_pair_data (list): The Switch Pair data: Switch IP, Switch Hostname, Switch Console Port, Switch password, Primary Switch [True|False].
            [["switch_ip", "switch_hostname", "switch_console_port", "switch_password", primary_switch], ...]
        mgmt_vlan (str): Management VLAN
        reset_switch (bool, optional): If True, reset the switches. Defaults to True.
        setup_switch (bool, optional): If True, setup the switches. Defaults to True.
        set_mgmt_interface (bool, optional): If True, set the management IP data. Defaults to False.
        stdout (bool, optional): Enable stdout logging. Defaults to False.
    """
    # create the threads for the cluster nodes
    switches: list[SwitchReset] = []
    for switch_ip, switch_hostname, switch_console_port, switch_password, primary_switch in switch_pair_data:
        switch_reset = SwitchReset(
            console_username=console_username,
            console_password=console_password,
            switch_console_port=switch_console_port,
            switch_hostname=switch_hostname,
            switch_ip=switch_ip,
            switch_password=switch_password,
            mgmt_vlan=mgmt_vlan,
            primary_switch=primary_switch,
            set_mgmt_interface=set_mgmt_interface,
            stdout=stdout,
        )
        switches.append(switch_reset)

    # If we are to perform "reset" on the switches
    if reset_switch:
        reset_threads: list[threading.Thread] = []
        # create threads for "reset_switch()"
        for switch in switches:
            thread = threading.Thread(target=switch.reset_switch)
            reset_threads.append(thread)

        # start the threads
        for thread in reset_threads:
            thread.start()

        # wait for all threads to complete
        for thread in reset_threads:
            thread.join()

    # If we are to perform "setup" on the switches
    if setup_switch:
        setup_threads: list[threading.Thread] = []
        # create threads for "switch_setup()"
        for switch in switches:
            thread = threading.Thread(target=switch.switch_setup)
            setup_threads.append(thread)

        # start the threads
        for thread in setup_threads:
            thread.start()

        # wait for all threads to complete
        for thread in setup_threads:
            thread.join()


class SwitchReset:
    def __init__(
        self,
        console_username: str,
        console_password: str,
        switch_console_port: str,
        switch_hostname: str,
        switch_ip: str,
        switch_password: str,
        mgmt_vlan: str,
        primary_switch: bool,
        set_mgmt_interface: bool = False,
        stdout: bool = False,
    ):
        """
        Constructor for the SwitchReset class.

        Args:
            console_username (str): Console Server Username
            console_password (str): Console Server Password
            switch_console_port (str): Switch Console Port  (constants.cxo_cluster_console_ports)
            switch_hostname (str): Switch Hostname  (constants.cxo_cluster_hostnames)
            switch_ip (str): Switch IP Address  (constants.cxo_cluster_ip_addresses)
            switch_password (str): Switch Password
            mgmt_vlan (str): Management VLAN
            primary_switch (bool): True if the switch is the primary switch, False otherwise.
            set_mgmt_interface (bool, optional): If True, set the management IP data. Defaults to False.
            stdout (bool, optional): Enable stdout logging. Defaults to False.
        """
        self.console_server = CXOConsoles.CXO_CONSOLE_SERVER_1
        self.console_username = console_username
        self.console_password = console_password
        self.switch_console_port = switch_console_port
        self.switch_hostname = switch_hostname
        self.switch_ip = switch_ip
        self.switch_password = switch_password
        self.mgmt_vlan = mgmt_vlan
        self.primary_switch = primary_switch
        self.set_mgmt_interface = set_mgmt_interface
        self.ssh: paramiko.SSHClient = None
        self.shell: paramiko.Channel = None

        # Create non-root logger, to allow stdout stream addition for manual execution
        self.logger = logging.getLogger(f"SwitchReset-{self.switch_ip}")
        self.logger.setLevel(logging.INFO)
        if stdout:
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.logger.info(f"[{self.switch_ip}] Switch Reset: {self.switch_console_port}")

        # Connect to the Console Server
        self.logger.info(f"[{self.switch_ip}] Connecting to Console Server: {self.console_server}")

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh.connect(
                hostname=self.console_server, username=self.console_username, password=self.console_password
            )
            self.logger.info(f"[{self.switch_ip}] Successfully connected to Console Server: {self.console_server}")
        except BadAuthenticationType as ba:
            self.logger.error(f"[{self.switch_ip}] Bad Authentication: {ba}")
            self.ssh = None
        except BadHostKeyException as bh:
            self.logger.error(f"[{self.switch_ip}] Bad Host Key: {bh}")
            self.ssh = None
        except SSHException as e:
            self.logger.error(f"[{self.switch_ip}] Failed to connect to Console Server: {self.console_server}: {e}")
            self.ssh = None

    def __del__(self):
        """
        Destructor for the SwitchReset class.
        """
        if self.shell:
            self.logger.info(f"[{self.switch_ip}] Closing Interactive Shell")
            self.shell.close()

        if self.ssh:
            self.logger.info(f"[{self.switch_ip}] Closing SSH connection to Console Server: {self.console_server}")
            self.ssh.close()

    def _send_command(self, command: str, wait: float = COMMAND_WAIT):
        """
        Send a command to the switch and wait.

        NOTE: During testing, it was observed that some wait needs to be given after every command.
              We can send() data more quickly than the switch is ready to receive.

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
        self.logger.info(f"[{self.switch_ip}] {self.output_decode}")
        return self.output_decode

    def _connect_and_login_to_switch(self) -> bool:
        """
        Connect to the switch via console.

        Returns:
            bool: True if the switch was connected successfully, False otherwise.
        """
        if not self.ssh:
            self.logger.error(f"[{self.switch_ip}] No SSH connection to Console Server: {self.console_server}")
            return False

        # Connect to the Switch via Console
        self.logger.info(f"[{self.switch_ip}] Connecting to Console Switch Port: {self.switch_console_port}")

        # invoke interactive shell to send() and recv() commands and output
        self.shell = self.ssh.invoke_shell()

        # flush current output from cxo-console connection
        self._get_output()

        self.command_str = f"telnet {SwitchConsolePorts.CXO_CONSOLE_SWITCH} {self.switch_console_port}\n"
        self.logger.info(f"[{self.switch_ip}] Executing Command: {self.command_str}")

        self._send_command(self.command_str)
        # send CR to obtain login prompt
        self._send_command("\n")

        # should be at Login Prompt - check for "login:" in output
        self.output_decode = self._get_output()

        # It's possible the Console is at "Password:". Send a \n to get to LOGIN_PROMPT prompt
        if PASSWORD_PROMPT in self.output_decode:
            self._send_command("\n", wait=CLEAR_LOGIN_WAIT)
            # update output to get the login prompt
            self.output_decode = self._get_output()

        if LOGIN_PROMPT not in self.output_decode and SWITCH_PROMPT in self.output_decode:
            self.logger.info(f"[{self.switch_ip}] Already logged into Switch")
        else:
            # login
            self.logger.info(f"[{self.switch_ip}] Logging into Switch")

            self._send_command(f"{DEFAULT_USERNAME}\n")
            self._send_command(f"{self.switch_password}\n", wait=LOGIN_WAIT)

            # should be at Command Prompt
            self.output_decode = self._get_output()
            if SWITCH_PROMPT not in self.output_decode:
                self.logger.error(f"[{self.switch_ip}] Failed to login to Switch")
                return False

        return True

    def _logout_and_disconnect_from_switch(self) -> bool:
        """
        Disconnect from the switch via console.

        Returns:
            bool: True if the switch was disconnected successfully, False otherwise.
        """
        if not self.shell:
            self.logger.error(f"[{self.switch_ip}] No Interactive Shell")
            return False

        # logout from switch
        self._send_command(f"{Commands.EXIT}\n")

        # send '^]' to end telnet connection
        # CTRL-] (ASCII code 29, represented as \x1d in hexadecimal).
        self._send_command("\x1d")
        # quit telnet
        self._send_command("q\n")
        # flush output
        self._get_output()
        # close the shell
        self.shell.close()
        self.shell = None

        return True

    def reset_switch(self) -> bool:
        """
        Reset the switch to the default state.

        Returns:
            bool: True if the switch was reset successfully, False otherwise.
        """
        if not self._connect_and_login_to_switch():
            return False

        ##############################################################
        # 1. Reset the switches
        self.logger.info(f"[{self.switch_ip}] Resetting Switch: {Commands.ERASE_ALL_ZEROIZE}")
        self._send_command(f"{Commands.ERASE_ALL_ZEROIZE}\n")
        self._send_command("y\n")

        # The "erase all zeroize" operation states:
        # "This process will take several minutes to an hour to complete"
        # We'll set a timeout value of 1 hour for our .recv() call.
        # We're examining the output below, waiting for the "login:" prompt to appear.
        #
        # switch# erase all zeroize
        # This will securely erase all customer data and reset the switch to factory defaults.
        # This will initiate a reboot and render the switch unavailable until the zeroization is complete.
        # This should take several minutes to one hour to complete. Continue (y/n)? y
        # The system is going down for zeroization.
        # ...
        # ################ Preparing for zeroization #################
        # ################ Storage zeroization #######################
        # ################ WARNING: DO NOT POWER OFF UNTIL  ##########
        # ################          ZEROIZATION IS COMPLETE ##########
        # ################ This should take several minutes ##########
        # ################ to one hour to complete          ##########
        # ################ Restoring files ###########################
        # ...
        # We'd like to keep you up to date about:
        #   * Software feature updates
        #   * New product announcements
        #   * Special events
        # Please register your products now at: https://asp.arubanetworks.com
        #
        # switch login:
        #
        self.shell.settimeout(ONE_HOUR)

        process_complete = False

        while not process_complete:
            try:
                self.output_decode = self._get_output()
                if LOGIN_PROMPT in self.output_decode:
                    self.logger.info(f"[{self.switch_ip}] Switch has completed the reset process")
                    process_complete = True
                else:
                    self.logger.info(f"[{self.switch_ip}] Waiting for switch to complete the reset process...")
                    # sleep for a bit before checking again
                    time.sleep(ONE_MINUTE)
            except socket.timeout as e:
                self.logger.error(f"[{self.switch_ip}] Timeout Exception: {e}. Switch may not be fully reset.")
                return False

        ##############################################################
        # 2. Set admin password
        #
        # 8325 login: admin
        self._send_command(f"{DEFAULT_USERNAME}\n")
        # Password:
        # no password
        self._send_command("\n", wait=LOGIN_WAIT)

        # Please configure the 'admin' user account password.
        # Enter new password: *****
        self._send_command(f"{self.switch_password}\n")
        # Confirm new password: *****
        self._send_command(f"{self.switch_password}\n")
        # 8325#

        self.output_decode = self._get_output()
        if SWITCH_PROMPT not in self.output_decode:
            self.logger.error(f"[{self.switch_ip}] Failed to set admin password")
            return False

        ##############################################################
        # 3. Set the initial configuration
        #
        self._send_command(f"{Commands.CONFIGURE_TERMINAL}\n")

        self._send_command(f"{Commands.HTTPS_VRF_DEFAULT}\n")
        self._send_command(f"{Commands.SSH_VRF_DEFAULT}\n")

        # NOTE: This command will disable any transceivers in the group that do not support
        # the new speed and may disrupt the network.
        # Continue (y/n)? y
        self._send_command(f"{Commands.SYSTEM_INTERFACE_GROUP_.format("1", "10g")}\n")
        self._send_command("y\n")
        self._send_command(f"{Commands.SYSTEM_INTERFACE_GROUP_.format("2", "10g")}\n")
        self._send_command("y\n")
        self._send_command(f"{Commands.SYSTEM_INTERFACE_GROUP_.format("3", "10g")}\n")
        self._send_command("y\n")
        self._send_command(f"{Commands.SYSTEM_INTERFACE_GROUP_.format("4", "10g")}\n")
        self._send_command("y\n")

        # flush output
        self._get_output()

        self._send_command(f"{Commands.INTERFACE_.format('vlan 1')}\n")
        self._send_command(f"{Commands.IPV6_RA_MAX_INTERVAL_.format('30')}\n")
        self._send_command(f"{Commands.IPV6_RA_MIN_INTERVAL_.format('30')}\n")
        self._send_command(f"{Commands.IPV6_ADDRESS_AUTOCONFIG}\n")
        self._send_command(f"{Commands.NO_IPV6_SUPPRESS_RA}\n")
        self._send_command(f"{Commands.EXIT}\n")

        # flush output
        self._get_output()

        # NOTE: We configure the IP address assigned to the Switch by EngSup.
        # This allows direct SSH into the Switch for any further configuration/troubleshooting.
        # Following Network Automation, the MGMT Interface will be disabled, and the MGMT IP
        # will be set via: "lldp management-ipv4-address <IPV4-ADDR>"."
        self._send_command(f"{Commands.INTERFACE_.format('mgmt')}\n")
        # set IP Address data if set_mgmt_interface is True
        if self.set_mgmt_interface:
            self._send_command(f"{Commands.NO_SHUTDOWN}\n")
            self._send_command(f"{Commands.IP_STATIC_.format(self.switch_ip + IPs.CXO_NETMASK)}\n")
            self._send_command(f"{Commands.DEFAULT_GATEWAY_.format(IPs.CXO_GATEWAY)}\n")
            self._send_command(f"{Commands.NAMESERVER_.format(IPs.CXO_NAMESERVER_1 + " " + IPs.CXO_NAMESERVER_2)}\n")
        else:
            self._send_command(f"{Commands.SHUTDOWN}\n")
        # exit mgmt interface
        self._send_command(f"{Commands.EXIT}\n")

        # NOTE: The "hostname" command will bring the prompt back to: (config)#
        self._send_command(f"{Commands.HOSTNAME_.format(self.switch_hostname)}\n", wait=HOSTNAME_WAIT)

        # flush output
        self._get_output()

        self._send_command(f"{Commands.INTERFACE_.format('1/1/1-1/1/48')}\n")
        self._send_command(f"{Commands.NO_ROUTING}\n")
        self._send_command(f"{Commands.NO_SHUTDOWN}\n")
        self._send_command(f"{Commands.LOOP_PROTECT}\n")
        self._send_command(f"{Commands.VLAN_ACCESS_.format('1')}\n")
        self._send_command(f"{Commands.END}\n")

        # "write memory" needs a bit more time
        self._send_command(f"{Commands.WRITE_MEMORY}\n", wait=WRITE_MEMORY_WAIT)

        # flush output
        self._get_output()

        self.logger.info(f"[{self.switch_ip}] Switch Reset Complete")

        # logout and disconnect from switch
        if not self._logout_and_disconnect_from_switch():
            return False

        return True

    def switch_setup(self) -> bool:
        """
        Setup the switch for the CXO Cluster.

            primary_switch (bool): True if the switch is the primary switch, False otherwise.
            - Used for VSX:
            a) primary = 192.168.0.0/31
               secondary = 192.168.0.1/31
            b) role primary
               role secondary
            c) primary = keepalive peer 192.168.0.1 source 192.168.0.0
               secondary = keepalive peer 192.168.0.0 source 192.168.0.1

           Returns:
               bool: True if the switch was setup successfully, False otherwise.
        """
        if not self._connect_and_login_to_switch():
            return False

        ##############################################################
        # 4. Configure Keep Alive for the VSX
        self._send_command(f"{Commands.CONFIGURE_TERMINAL}\n")

        self._send_command(f"{Commands.INTERFACE_.format(Ports.PORT_48)}\n")
        self._send_command(f"{Commands.DESCRIPTION_.format('Reserved for VSX Keepalive')}\n")
        self._send_command(f"{Commands.ROUTING}\n")
        self._send_command(f"{Commands.NO_SHUTDOWN}\n")

        if self.primary_switch:
            self.logger.info(f"[{self.switch_ip}] Setting Keep Alive for Primary Switch")
            self._send_command(f"{Commands.IP_ADDRESS_.format(IPs.VSX_PRIMARY_IP_ADDRESS + IPs.VSX_MASK)}\n")
        else:
            self.logger.info(f"[{self.switch_ip}] Setting Keep Alive for Secondary Switch")
            self._send_command(f"{Commands.IP_ADDRESS_.format(IPs.VSX_SECONDARY_IP_ADDRESS + IPs.VSX_MASK)}\n")

        self._send_command(f"{Commands.EXIT}\n")

        # flush output
        self._get_output()

        self.logger.info(f"[{self.switch_ip}] Configure Keep Alive for the VSX: Complete")

        ##############################################################
        # 5. Create Link Aggregation (LAG) interfaces for the uplink and ISL
        self._send_command(f"{Commands.INTERFACE_.format('lag 256')}\n")
        self._send_command(f"{Commands.DESCRIPTION_.format('ISL link')}\n")
        self._send_command(f"{Commands.NO_SHUTDOWN}\n")
        self._send_command(f"{Commands.NO_ROUTING}\n")
        self._send_command(f"{Commands.VLAN_TRUNK_NATIVE_.format('1')}\n")
        self._send_command(f"{Commands.VLAN_TRUNK_ALLOWED_.format('all')}\n")
        self._send_command(f"{Commands.LACP_MODE_.format('active')}\n")
        self._send_command(f"{Commands.EXIT}\n")

        self._send_command(f"{Commands.INTERFACE_.format('lag 1 multi-chassis')}\n")
        self._send_command(f"{Commands.NO_SHUTDOWN}\n")
        self._send_command(f"{Commands.NO_ROUTING}\n")
        self._send_command(f"{Commands.VLAN_TRUNK_NATIVE_.format('1')}\n")
        self._send_command(f"{Commands.VLAN_TRUNK_ALLOWED_.format('all')}\n")
        self._send_command(f"{Commands.LACP_MODE_.format('active')}\n")
        self._send_command(f"{Commands.EXIT}\n")

        # flush output
        self._get_output()

        self.logger.info(
            f"[{self.switch_ip}] Create Link Aggregation (LAG) interfaces for the uplink and ISL: Complete"
        )

        ##############################################################
        # 6. Associate the ISL and Uplink ports to the respective lag interfaces
        self._send_command(f"{Commands.INTERFACE_.format(Ports.PORT_49 + '-' + Ports.PORT_50)}\n")
        self._send_command(f"{Commands.NO_SHUTDOWN}\n")
        self._send_command(f"{Commands.LAG_.format('256')}\n")
        self._send_command(f"{Commands.EXIT}\n")

        self._send_command(f"{Commands.INTERFACE_.format(Ports.PORT_51 + '-' + Ports.PORT_52)}\n")
        self._send_command(f"{Commands.NO_SHUTDOWN}\n")
        self._send_command(f"{Commands.LAG_.format('1')}\n")
        self._send_command(f"{Commands.EXIT}\n")

        # flush output
        self._get_output()

        self.logger.info(
            f"[{self.switch_ip}] Associate the ISL and Uplink ports to the respective lag interfaces: Complete"
        )

        ##############################################################
        # 7. Create a management vLAN and tag all the management interfaces
        self._send_command(f"{Commands.CREATE_VLAN_.format(self.mgmt_vlan)}\n")
        self._send_command(f"{Commands.EXIT}\n")

        self._send_command(f"{Commands.INTERFACE_.format(Ports.PORT_1 + '-' + Ports.PORT_47)}\n")
        self._send_command(f"{Commands.VLAN_ACCESS_.format(self.mgmt_vlan)}\n")
        self._send_command(f"{Commands.EXIT}\n")

        # flush output
        self._get_output()

        self.logger.info(f"[{self.switch_ip}] Create a management vLAN and tag all the management interfaces: Complete")

        ##############################################################
        # 8. Configure the VSX
        self._send_command(f"{Commands.VSX}\n")
        self._send_command(f"{Commands.INTER_SWITCH_LINK_.format('lag 256')}\n")

        if self.primary_switch:
            self.logger.info(f"[{self.switch_ip}] Role Primary")
            self._send_command(f"{Commands.ROLE_.format('primary')}\n")
            self._send_command(
                f"{Commands.KEEPALIVE_PEER_.format(IPs.VSX_SECONDARY_IP_ADDRESS, IPs.VSX_PRIMARY_IP_ADDRESS)}\n"
            )
        else:
            self.logger.info(f"[{self.switch_ip}] Role Secondary")
            self._send_command(f"{Commands.ROLE_.format('secondary')}\n")
            self._send_command(
                f"{Commands.KEEPALIVE_PEER_.format(IPs.VSX_PRIMARY_IP_ADDRESS, IPs.VSX_SECONDARY_IP_ADDRESS)}\n"
            )

        self._send_command(f"{Commands.VSX_SYNC}\n")
        self._send_command(f"{Commands.END}\n")

        self._send_command(f"{Commands.WRITE_MEMORY}\n", wait=WRITE_MEMORY_WAIT)

        # flush output
        self._get_output()

        self.logger.info(f"[{self.switch_ip}] Configure the VSX: Complete")

        ####
        if not self._logout_and_disconnect_from_switch():
            return False

        return True
