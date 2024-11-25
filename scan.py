import requests
import subprocess
import argparse
from urllib.parse import urlparse
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def check_status_with_requests(target_url):
    try:
        response = requests.get(target_url, timeout=10, allow_redirects=False)  # Allow_redirects=False for manual check
        if 200 <= response.status_code < 300:
            return True, "requests", response.status_code, target_url
        elif 300 <= response.status_code < 400:
            # Extract redirected URL from the 'Location' header
            redirected_url = response.headers.get("Location", None)
            if redirected_url:
                # Make sure the URL is absolute, not relative
                redirected_url = urlparse(redirected_url)._replace(
                    scheme=urlparse(target_url).scheme, 
                    netloc=urlparse(target_url).netloc if not urlparse(redirected_url).netloc else urlparse(redirected_url).netloc
                ).geturl()
            return True, "requests-redirect", response.status_code, redirected_url
        return False, "requests", response.status_code, None
    except requests.exceptions.RequestException:
        return False, "requests", None, None

def check_status_with_curl(target_url):
    try:
        result = subprocess.run(
            ["curl", "-I", "-L", "-m", "10", target_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            status_code = None
            final_url = target_url
            for line in result.stdout.splitlines():
                if line.startswith("HTTP/"):
                    status_code = int(line.split()[1])
                if line.lower().startswith("location:"):
                    # Extract redirected URL from Location header
                    redirected_url = line.split(":", 1)[1].strip()
                    final_url = urlparse(redirected_url)._replace(
                        scheme=urlparse(target_url).scheme, 
                        netloc=urlparse(target_url).netloc if not urlparse(redirected_url).netloc else urlparse(redirected_url).netloc
                    ).geturl()
            if 200 <= status_code < 300:
                return True, "curl", status_code, final_url
            elif 300 <= status_code < 400:
                return True, "curl", status_code, final_url
        return False, "curl", None, None
    except Exception:
        return False, "curl", None, None

def test_protocols(base_url):
    for protocol in ["http://", "https://"]:
        url = protocol + base_url

        # Try requests
        reachable, method, *details = check_status_with_requests(url)
        if reachable:
            if method == "requests":
                print(f"{Fore.GREEN}[+] {url} is reachable with status code {details[0]} using {method}{Style.RESET_ALL}")
            elif method == "requests-redirect":
                print(f"{Fore.YELLOW}[YELLOW] {url} redirected to {details[1]} with status code {details[0]} using {method}{Style.RESET_ALL}")
            return

        # Try curl
        reachable, method, *details = check_status_with_curl(url)
        if reachable:
            if 300 <= details[0] < 400:
                print(f"{Fore.YELLOW}[YELLOW] {url} redirected to {details[1]} with status code {details[0]} using {method}{Style.RESET_ALL}")
            elif 200 <= details[0] < 300:
                print(f"{Fore.GREEN}[+] {details[1]} is reachable with status code {details[0]} using {method}{Style.RESET_ALL}")
            return

    print(f"{Fore.RED}[-] {base_url} is unreachable{Style.RESET_ALL}")

def process_url(url):
    parsed = urlparse(url)
    if parsed.scheme:
        test_protocols(parsed.netloc)
    else:
        test_protocols(url)

def main():
    parser = argparse.ArgumentParser(description="Check URL reachability and handle redirects")
    parser.add_argument("file", help="Path to the .txt file containing URLs")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as file:
            urls = [line.strip() for line in file.readlines()]
        for url in urls:
            process_url(url)
    except FileNotFoundError:
        print(f"{Fore.RED}File not found: {args.file}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
