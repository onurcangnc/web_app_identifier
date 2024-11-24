import requests
import argparse
from urllib.parse import urlparse
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Function to check availability and return status code with colorized output
def check_status(target_url):
    try:
        response = requests.get(target_url, timeout=10)
        if 200 <= response.status_code < 400:
            print(f"{Fore.GREEN}[+] {target_url} is reachable with status code {response.status_code}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[+] {target_url} is reachable with status code {response.status_code}{Style.RESET_ALL}")
    except requests.exceptions.RequestException:
        print(f"{Fore.RED}[-] {target_url} is not reachable{Style.RESET_ALL}")

# Function to test both HTTP and HTTPS if no protocol is specified
def test_protocols(base_url):
    for protocol in ["http://", "https://"]:
        url = protocol + base_url
        print(f"[*] Testing {url}...")
        check_status(url)

# Function to handle full URLs or domains without protocol
def process_url(url):
    parsed = urlparse(url)
    if parsed.scheme:  # If URL includes protocol, check it directly
        print(f"[*] Testing full URL: {url}")
        check_status(url)
    else:  # If no protocol, test both HTTP and HTTPS
        print(f"[*] No protocol specified for {url}. Testing both HTTP and HTTPS...")
        test_protocols(url)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Check HTTP status and reachability of URLs with color-coded output.")
    parser.add_argument("file", help="Path to the .txt file containing target URLs or domains")
    args = parser.parse_args()

    file_path = args.file

    try:
        with open(file_path, "r") as file:
            urls = [line.strip() for line in file.readlines()]
        
        print("[*] Checking URL reachability...")
        for url in urls:
            print(f"\n[*] Checking {url}...")
            process_url(url)
    except FileNotFoundError:
        print(f"{Fore.RED}[!] File not found: {file_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
