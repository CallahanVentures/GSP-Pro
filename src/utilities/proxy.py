from utilities.errors import get_error_location, handle_failure_point_and_exit
import os
import random
import requests
from utilities.config import ProxyType

from typing import List, Optional


def load_proxies() -> List[str]:
    try:
        filename = os.path.join(os.getcwd(), "proxies.txt")
        with open(filename, "r") as file:
            return file.read().split("\n")
    except FileNotFoundError as e:
        location = get_error_location()
        task = "loading proxies"
        handle_failure_point_and_exit(location, task, e)
    except PermissionError as e:
        location = get_error_location()
        task = "loading proxies"
        handle_failure_point_and_exit(location, task, e)
    except IsADirectoryError as e:
        location = get_error_location()
        task = "loading proxies"
        handle_failure_point_and_exit(location, task, e)
    except IOError as e:
        location = get_error_location()
        task = "loading proxies"
        handle_failure_point_and_exit(location, task, e)
    except Exception as e:
        location = get_error_location()
        task = "loading proxies"
        handle_failure_point_and_exit(location, task, e)


def random_proxy() -> Optional[str]:
    try:
        return random.choice(load_proxies())
    except IndexError as e:
        location = get_error_location()
        task = "selecting a random proxy"
        handle_failure_point_and_exit(location, task, e)
        return None
    except Exception as e:
        location = get_error_location()
        task = "selecting a random proxy"
        handle_failure_point_and_exit(location, task, e)
        return None


def needs_auth(e: Exception) -> bool:
    return "Proxy Authentication Required" in str(e)


def timed_out(e: Exception) -> bool:
    return "Cannot connect to proxy" or "Read timed out" in str(e)


def valid_proxy(proxy: str, proxy_type: ProxyType, proxy_auth: bool) -> bool:
    try:
        proxy_type_str = proxy_type.name.lower()
        if proxy in ["", None]:
            location = get_error_location()
            task = "verifying proxy, proxy selected is an empty or null value"
            handle_failure_point_and_exit(location, task)
            return False
        
        if proxy_auth:
            parts = proxy.split(":")
            if len(parts) != 3:
                task = "invalid proxy format, expected ip:port:user:pass"
                print(task)
                return False

            user, password, ip, port = parts[0], parts[1].split("@")[0], parts[1].split("@")[1], parts[2]
            proxy_url = f"{user}:{password}@{ip}:{port}"
            proxies = {
                "http": f"{proxy_type_str}://{proxy_url}",
                "https": f"{proxy_type_str}://{proxy_url}"
            }
        else:
            proxies = {
                "http": f"{proxy_type_str}://{proxy}",
                "https": f"{proxy_type_str}://{proxy}"
            }
            ip = proxy.split(":")[0]

        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        response.raise_for_status()

        origin_ip = response.json().get("origin")
        return origin_ip and ip in origin_ip

    except requests.exceptions.ProxyError as e:
        location = get_error_location()
        if needs_auth(e):
            task = f"accessing proxy due to an authentication error using: {proxy}\n"
        elif timed_out(e):
            task = f"making connection using: {proxy}"
        else:
            task = "verifying proxy due to proxy error"
        handle_failure_point_and_exit(location, task, e)
        return False
    except requests.exceptions.Timeout as e:
        print(e)
        location = get_error_location()
        task = "verifying proxy due to a timeout error"
        handle_failure_point_and_exit(location, task, e)
        return False
    except requests.exceptions.RequestException as e:
        location = get_error_location()
        task = "verifying proxy due to a request error"
        handle_failure_point_and_exit(location, task, e)
        return False
    except Exception as e:
        location = get_error_location()
        task = "verifying proxy due to a general exception"
        handle_failure_point_and_exit(location, task, e)
        return False