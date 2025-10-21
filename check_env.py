def read_env_file():
    with open('.env', 'rb') as f:  # Open in binary mode to see exact bytes
        lines = f.readlines()
        for line in lines:
            # Decode and print each line with its raw representation
            decoded = line.decode('utf-8').strip()
            if 'PASSWORD' in decoded:
                print(f"Raw line: {line}")
                print(f"Decoded line: {decoded}")
                parts = decoded.split('=')
                if len(parts) == 2:
                    print(f"Password value: '{parts[1]}'")
                    print(f"Length: {len(parts[1])} characters")
                    print(f"ASCII values: {[ord(c) for c in parts[1]]}")

if __name__ == "__main__":
    print("Reading .env file directly:")
    read_env_file()