import socket
import socks
import logging
import requests
import time
from colorama import Fore, Style

class TorController:
    def __init__(self, socks_ports=[9050, 9150]):
        self.socks_ports = socks_ports
        self.logger = logging.getLogger(__name__)
        self.socks_port = None
        self.current_ip = None

    def _get_ip_address(self):
        """Get current IP address through Tor network"""
        session = requests.session()
        session.proxies = {
            'http': f'socks5h://127.0.0.1:{self.socks_port}',
            'https': f'socks5h://127.0.0.1:{self.socks_port}'
        }

        apis = [
            'https://api.ipify.org?format=json',
            'https://ident.me',
            'https://api.myip.com'
        ]

        for api in apis:
            try:
                response = session.get(api, timeout=10)
                if 'json' in api:
                    return response.json()['ip']
                return response.text.strip()
            except:
                continue
        return None

    def check_tor_service(self):
        """Check if Tor SOCKS proxy is available and working"""
        print(f"{Fore.CYAN}[*] Checking Tor connection...{Style.RESET_ALL}", end='\r')
        
        # Check SOCKS ports
        for port in self.socks_ports:
            try:
                test_socket = socks.socksocket()
                test_socket.set_proxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", port)
                test_socket.settimeout(5)
                test_socket.connect(("check.torproject.org", 443))
                test_socket.close()
                self.socks_port = port
                break
            except:
                continue

        if not self.socks_port:
            print(f"{Fore.RED}[!] No accessible Tor SOCKS ports found{Style.RESET_ALL}")
            return False

        # Verify Tor connection
        try:
            session = requests.session()
            session.proxies = {
                'http': f'socks5h://127.0.0.1:{self.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.socks_port}'
            }
            
            response = session.get('https://check.torproject.org/api/ip', timeout=10)
            if not response.json().get('IsTor', False):
                print(f"{Fore.RED}[!] Not connected through Tor network{Style.RESET_ALL}")
                return False

            self.current_ip = self._get_ip_address()
            if not self.current_ip:
                print(f"{Fore.RED}[!] Failed to get current IP address{Style.RESET_ALL}")
                return False

            print(f"{Fore.GREEN}[+] Connected through Tor (IP: {self.current_ip}){Style.RESET_ALL}")
            return True

        except Exception as e:
            print(f"{Fore.RED}[!] Tor connection failed: {str(e)}{Style.RESET_ALL}")
            return False

    def cleanup(self):
        """Reset SOCKS proxy settings"""
        socks.setdefaultproxy()