class WordlistHandler:
    def __init__(self, wordlist_path):
        self.wordlist_path = wordlist_path

    def get_passwords(self):
        with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                password = line.strip()
                if password and not password.startswith('#'):
                    yield password 