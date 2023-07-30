import os
import concurrent.futures
import requests

url = "https://www.bing.com/"
proxies_file = os.path.join(os.path.dirname(__file__), "proxies.txt")
working_file = os.path.join(os.path.dirname(__file__), "working.txt")

session = requests.Session()
session.headers.update({"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})

def check(proxy):
    try:
        response = session.get(url, proxies={"http": "http://" + str(proxy), "https": "http://" + str(proxy)}, timeout=2)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working!")
            with open(working_file, "a") as f:
                f.write(proxy + "\n")

    except (requests.exceptions.ProxyError, requests.exceptions.Timeout, requests.exceptions.ConnectTimeout):
        pass

def main():
    with open(proxies_file, 'r') as file:
        proxylist = [line.strip() for line in file if line.strip()]
    
    print(f"Total number of proxies found: {len(proxylist)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(check, proxylist)

    print("Done!")  

if __name__ == "__main__":
    main()
