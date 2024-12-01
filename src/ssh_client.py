import paramiko
import socket
import logging
from time import sleep
import socks
from colorama import Fore, Style

class SSHClient:
    def __init__(self, target, port, username, timeout=5, max_retries=3, tor_controller=None):
        self.target = target
        self.port = port
        self.username = username
        self.timeout = timeout
        self.max_retries = max_retries
        self.tor_controller = tor_controller
        self.logger = logging.getLogger(__name__)

    def _create_proxy_socket(self):
        """Create a SOCKS proxy socket for Tor connection."""
        if self.tor_controller:
            proxy_socket = socks.socksocket()
            proxy_socket.set_proxy(
                proxy_type=socks.PROXY_TYPE_SOCKS5,
                addr="127.0.0.1",
                port=self.tor_controller.socks_port,
                username=None,
                password=None
            )
            proxy_socket.settimeout(self.timeout)
            return proxy_socket
        return None

    def try_login(self, password):
        for attempt in range(self.max_retries):
            ssh = None
            sock = None
            
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Create socket
                if self.tor_controller:
                    sock = self._create_proxy_socket()
                    try:
                        sock.connect((self.target, self.port))
                    except Exception as e:
                        if sock:
                            sock.close()
                        sleep(2 ** attempt)
                        continue

                # Increase timeout for banner reading
                transport_timeout = self.timeout * 2
                
                # Connect with custom timeout for banner reading
                ssh.connect(
                    self.target,
                    port=self.port,
                    username=self.username,
                    password=password,
                    timeout=transport_timeout,  # Longer timeout for initial connection
                    sock=sock,
                    banner_timeout=transport_timeout,  # Explicit banner timeout
                    auth_timeout=self.timeout,  # Normal timeout for auth
                    disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}  # Disable problematic algorithms
                )
                
                # Test the connection with a simple command
                _, stdout, _ = ssh.exec_command('echo test', timeout=self.timeout)
                stdout.channel.recv_exit_status()
                
                return True

            except paramiko.AuthenticationException:
                # Password is wrong, no need to retry
                return False
                
            except (socket.timeout, paramiko.SSHException, EOFError) as e:
                # Connection issues - retry with backoff
                if attempt < self.max_retries - 1:
                    sleep(2 ** attempt)
                continue
                
            except Exception as e:
                # Unknown errors - retry with backoff
                if attempt < self.max_retries - 1:
                    sleep(2 ** attempt)
                continue
                
            finally:
                # Clean up connections
                if ssh:
                    try:
                        ssh.close()
                    except:
                        pass
                if sock:
                    try:
                        sock.close()
                    except:
                        pass

        return False 