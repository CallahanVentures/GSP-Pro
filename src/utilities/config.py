import configparser
import os
from pathlib import Path
from utilities.colored import print_red, print_green
from utilities.errors import handle_failure_point_and_exit
from utilities.threads import calc_safe_threads

from typing import List, Optional
from enum import Enum


class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class Config:
    excluded_domains: List[str] = []
    thread_count: int = 1
    proxy_type: ProxyType = ProxyType.HTTP
    run_vuln_scan: bool = True


def get_config_path():
    parent_directory = get_parent_path()
    if parent_directory:
        return os.path.join(parent_directory, "config.ini")
    return None


def get_parent_path() -> Optional[str]:
    try:
        # Grabs the location of the current file (functions.py)
        functions_file_path: Path = Path(__file__).resolve()

        # Get the directory where the current script exists
        utilities_directory = functions_file_path.parent

        # Grabs the parent directory of the child directory `utilities`
        parent_directory = utilities_directory.parent

        # Converts the parent directory path object to a string then returns it
        return str(parent_directory)
    except FileNotFoundError:
        print("Error: The current script file cannot be found.")
    except PermissionError:
        print("Error: Permission denied while accessing file or directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


def load_config() -> Optional[Config]:
    config = Config()

    config_path = get_config_path()
    if not os.path.exists(config_path):
        print_red("Configuration file not found. Generating...")
        config_status = write_default_config()  # Returns True or False depending on success status.
        if not config_status:  # Initializes constants with default settings in the event of a failed file generation
            print_red("An error occurred while attempting to generate a new configuration file")
            print_green("Continuing without config.ini, this will not affect the performance of the application.")
            config.excluded_domains.extend(["google.com", "/search?client=", "/search?q="])
            return config

    try:
        # Reads configuration settings
        config_parser = configparser.ConfigParser()
        config_parser.read(config_path)

        # Assigns configuration settings to constants
        config.excluded_domains.extend(item.strip() for item in config_parser.get("SETTINGS", "excluded_domains").split(","))
        config.thread_count = config_parser.getint("SETTINGS", "thread_count", fallback=1)
        if config.thread_count <= 0:
            print_red("thread_count must be >= 1")
            config.thread_count = 1
        config.thread_count = min(config.thread_count, calc_safe_threads())
        try:
            config.proxy_type = ProxyType(config_parser.get("SETTINGS", "proxy_type", fallback="http"))
        except Exception as e:
            handle_failure_point_and_exit(
                "utilities.load_config",
                "parsing confgfile",
                f"Invalid proxy_type value. The valid values are: {','.join(ProxyType)}",
                e,
            )
        config.run_vuln_scan = config_parser.getboolean("SETTINGS", "run_vuln_scan", fallback=False)

        print_green("Successfully loaded configuration file!")
        return config

    except Exception as e:
        print_red(f"Error reading configuration file: {e}.\n\nGenerating new configuration file using the default settings.")
        config_status = write_default_config()  # returns True or False depending on success status.
        if not config_status:
            print_red("An error occurred while attempting to generate a new configuration file")
            print_green("Continuing without config.ini, this will not affect the performance of the application.")
            config.excluded_domains.extend(["google.com", "/search?client=", "/search?q="])
            return config

        return load_config()  # calls the function recursively in the event the generation is successful


def write_default_config():
    try:
        # Defines the configuration file path and contents
        config_path = get_config_path()
        config_file_contents = """[SETTINGS]
# List of excluded domains separated by commas
excluded_domains = google.com, /search?client=, /search?q=, .gov

# Number of threads to use for parsing | Recommended Maximum: 3
thread_count = 1

# Type of proxy to use for parsing | Options: http, https, socks4, socks5
proxy_type = http

# Whether to run vulnerability scan on parsed links | Options: True, False
run_vuln_scan = True"""

        # Write the contents to the configuration file path
        with open(config_path, "w") as config_file:
            config_file.write(config_file_contents)
        print_green("Configuration file generated successfully!")
        return True

    except Exception as e:
        print_red(f"Error generating configuration file\n{e}\nUsing default configuration settings.")
        return False