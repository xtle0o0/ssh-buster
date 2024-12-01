# SSH Buster

SSH Buster is a Python-based SSH brute force tool designed for ethical hacking and security testing purposes. It supports using Tor for anonymizing connections.

## Features

- Brute force SSH login attempts using a wordlist.
- Option to route connections through the Tor network.
- Progress bar and ETA for the brute force process.
- Password verification to ensure accuracy.

## Requirements

- Python 3.6 or higher
- [Tor](https://www.torproject.org/) (if using the `--use-tor` option)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/xtle0o0/ssh-buster.git
   cd ssh-buster
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python ssh_bruteforce.py --target <target_ip> --username <username> --wordlist <path_to_wordlist> [--use-tor]
```

### Options
- `--target`: Target IP address or hostname.
- `--port`: SSH port (default: 22).
- `--wordlist`: Path to the wordlist file.
- `--username`: Username to test.
- `--use-tor`: Use Tor for connections.
- `--timeout`: Connection timeout in seconds (default: 5).
- `--max-retries`: Maximum connection retries (default: 3).

## Disclaimer

This tool is intended for educational purposes only. Use it responsibly and only on systems you have permission to test. The author is not responsible for any misuse or damage caused by this tool.

## Author

Developed by Leo. GitHub: [xtle0o0](https://github.com/xtle0o0)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.