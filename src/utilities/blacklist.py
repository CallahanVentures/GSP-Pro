from typing import Dict, List
from utilities.colored import print_blue, print_red
from utilities.config import ProxyType as ConfigProxyType
from utilities.logger import Logger
from utilities.proxy import needs_auth, timed_out
import json
import requests
import uuid

def runCheck(PROXIES: List[str], PROXY_TYPE: ConfigProxyType, logger: Logger):
    isBlacklisted: List[str] = []
    isClean: List[str] = []
    wasSkipped: List[str] = []

    for proxy in PROXIES:
        print(count)
        try:
            if proxy in [None, ""]:
                print("Empty line detected, skipping.")
                wasSkipped.append(proxy)
                continue
            
            parts = proxy.split(":")
            
            # Colon check for proxy: 2 for IP:PORT, 3 for USER:PASS@IP:PORT
            if len(parts) not in [2, 3]:
                print(f"Improperly formatted proxy, expected: IP:PORT or USER:PASS@IP:PORT, got {proxy}")
                continue

            if len(parts) == 3:

                # Dot check for IP: 2 for domains being used as proxies, 3 for subdomains being used as proxies, 4 for IPs being provided
                period_count = parts[1].split("@")[1].count('.')
                if period_count not in [2, 3, 4]:
                    print(f"Invalid IP provided for proxy, expected 2-4 '.', got {period_count}")
                    continue

            proxy_dict = {
                    "http": f"{PROXY_TYPE.name.lower()}://{proxy}",
                    "https": f"{PROXY_TYPE.name.lower()}://{proxy}",
            }

            # Generates a unique boundary string for payload
            boundary: str = '-----------------------------' + str(uuid.uuid4()).replace('-', '')
            headers: Dict[str, str] = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': f'multipart/form-data; boundary={boundary}',
                'origin': 'https://www.whatismyip.com',
                'referer': 'https://www.whatismyip.com/',
                'sec-ch-ua': '"Opera GX";v="109", "Not:A-Brand";v="8", "Chromium";v="123"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
            }
            body: str = (
                f'--{boundary}\r\n'
                'Content-Disposition: form-data; name="action"\r\n\r\n'
                'blacklist-check\r\n'
                f'--{boundary}\r\n'
                'Content-Disposition: form-data; name="host"\r\n\r\n'
                f'{proxy.split(":")[0]}\r\n'
                f'--{boundary}--\r\n'
            )
            response = requests.post('https://api.whatismyip.com/app.php', headers=headers, data=body, proxies=proxy_dict)

            response.raise_for_status()

            if "Your lookup limit has been reached." in response.text:
                print_red(f"Proxy: {proxy} is temporarily banned from checking blacklist reports, please try again tomorrow with this proxy.")
                wasSkipped.append(proxy)
                continue

            data: list[dict[str, any]] = json.loads(response.text)
            for entry in data:
                logger.logInfo(f"Proxy Tested: {proxy}")
                logger.logInfo(f"Response Time: {entry['response-time']} ms")
                logger.logInfo(f"Database: {entry['list-name']}")
                logger.logInfo(f"Hostname: {entry['list-host']}")
                logger.logInfo(f"Rating: {entry['list-rating']}/10")
                logger.logInfo(f"Blacklisted: {entry['is-listed']}")
                logger.logInfo(f"TXT Record: {entry['txt-record'] if entry['txt-record'] else 'N/A'}")
                logger.logInfo('-' * 40)

                if entry['is-listed'] is True:
                    if proxy not in isBlacklisted:
                        isBlacklisted.append(proxy)
            
                elif entry['is-listed'] is False:
                    if proxy not in isClean:
                        isClean.append(proxy)
            
                else:
                    if proxy not in wasSkipped:
                        wasSkipped.append(proxy)
        
        except requests.exceptions.ProxyError as e:
            if needs_auth(e):
                print_red(f"Proxy {proxy} needs authentication, please ensure your IP is whitelisted or credentials are valid.")
            
            elif timed_out(e):
                print_red(f"Proxy {proxy} timed out while attempting to make request.")
            
            else:
                print_red("An unexpected error occured, we didn't anticipate any issues, if this behavior continues, please contact us.")
                print()
                print_red(e)
        
        except IndexError as e:
            print(e)
            continue

    return isBlacklisted, isClean, wasSkipped



