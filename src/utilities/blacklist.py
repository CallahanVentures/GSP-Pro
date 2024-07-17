
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple
from utilities.colored import print_green, print_red
from utilities.config import ProxyType as ConfigProxyType
from utilities.logger import Logger
from utilities.proxy import needs_auth, timed_out
import requests

def check(proxy: str, proxyType: ConfigProxyType, logger: Logger) -> Tuple[str, str]:
    if proxy in [None, ""]:
        return proxy, "skipped"
    
    parts = proxy.split(":")

    if len(parts) not in [2, 3]:
        return proxy, "improper"

    if len(parts) == 3:
        period_count = parts[1].split("@")[1].count('.')
        if period_count not in [2, 3, 4]:
            return proxy, "invalid_ip"

    proxy_dict = {
        "http": f"{proxyType.name.lower()}://{proxy}",
        "https": f"{proxyType.name.lower()}://{proxy}",
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'authorization': 'Basic b3Blbl9rZXk=',
        'Origin': 'https://blacklistchecker.com',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://blacklistchecker.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }
    
    try:
        response = requests.get(f'https://api.blacklistchecker.com/check/{proxy}', headers=headers, proxies=proxy_dict)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "ok":
            detections: int = data.get("detections", -1)

    
            if detections == -1:
                print(data.get("detections", None))
                return proxy, "skipped"

            elif detections == 0:
                print_green(f"Proxy {proxy} is clean!")
                return proxy, "clean"
    
            elif detections >= 1:
                blacklists: List[Dict[str, Any]] = data.get("blacklists", [])
                for blacklist in blacklists:
                    print_red(f"Proxy {proxy} blacklisted from {blacklist}")
                return proxy, "blacklisted"
            
            else:
                print_red("An unexpected error occurred, we didn't anticipate any issues, if this behavior continues, please contact us.")
                print()
                print_red(e)
                return proxy, "unexpected_error"


        else:
            print_red(f"There was an error while checking proxy {proxy}")
            print_red(response.text)
            return proxy, "skipped"

    except requests.exceptions.ProxyError as e:
        if needs_auth(e):
            print_red(f"Proxy {proxy} needs authentication, please ensure your IP is whitelisted or credentials are valid.")
            return proxy, "auth_needed"
        elif timed_out(e):
            print_red(f"Proxy {proxy} timed out while attempting to make request.")
            return proxy, "timed_out"
        else:
            print_red("An unexpected error occurred, we didn't anticipate any issues, if this behavior continues, please contact us.")
            print()
            print_red(e)
            return proxy, "unexpected_error"
    except IndexError as e:
        print(e)
        return proxy, "index_error"

def runCheck(proxies: List[str], proxyType: ConfigProxyType, logger: Logger) -> Tuple[List[str], List[str], List[str]]:
    isBlacklisted: List[str] = []
    isClean: List[str] = []
    wasSkipped: List[str] = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(check, proxy, proxyType, logger): proxy for proxy in proxies}

        for future in as_completed(futures):
            proxy = futures[future]
            try:
                proxy, result = future.result()
                if result == "blacklisted":
                    isBlacklisted.append(proxy)
                elif result == "clean":
                    isClean.append(proxy)
                elif result == "skipped":
                    wasSkipped.append(proxy)
                elif result == "improper":
                    print_red(f"Improperly formatted proxy, expected: IP:PORT or USER:PASS@IP:PORT, got {proxy}")
                    wasSkipped.append(proxy)
                elif result == "invalid_ip":
                    period_count = proxy.split(":")[1].split("@")[1].count('.')
                    print_red(f"Invalid IP provided for proxy, expected 2-4 '.', got {period_count}")
                    wasSkipped.append(proxy)
                elif result == "unexpected_error" or result == "index_error" or result == "auth_needed" or result == "timed_out":
                    wasSkipped.append(proxy)
                else:
                    wasSkipped.append(proxy)

            except Exception as e:
                print_red(f"Proxy {proxy} closed connection without a response")
                wasSkipped.append(proxy)
            
    return isBlacklisted, isClean, wasSkipped
