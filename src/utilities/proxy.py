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


def valid_proxy(proxy: str, proxy_type: ProxyType) -> bool:
    try:
        proxy_type = proxy_type.name.lower()
        if proxy in ["", None]:
            location = get_error_location()
            task = "verifying proxy, proxy selected is an empty or null value"
            handle_failure_point_and_exit(location, task)

        proxies = {"http": f"{proxy_type}://{proxy}", "https": f"{proxy_type}://{proxy}"}

        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        response.raise_for_status()

        origin_ip = response.json().get("origin")
        return origin_ip and proxy.split(":")[0] in origin_ip

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
        task = "verifying proxy due to timeout error"
        handle_failure_point_and_exit(location, task, e)
        return False
    except requests.exceptions.RequestException as e:
        location = get_error_location()
        task = "verifying proxy due to requests error"
        handle_failure_point_and_exit(location, task, e)
        return False
    except Exception as e:
        location = get_error_location()
        task = "verifying proxy due to general exception"
        handle_failure_point_and_exit(location, task, e)
        # print(e)
        # print("In valid_proxy()")
        return False