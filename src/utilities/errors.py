from utilities.colored import print_red
import inspect

from typing import Optional


def get_error_location():
    try:
        frame = inspect.currentframe()
        parent_frame = frame.f_back  # Grabs parent frame by moving up one level in call stack
        module = inspect.getmodule(parent_frame)  # Grabs parent module name
        function_name = parent_frame.f_code.co_name  # Grabs parent function name
        line_number = parent_frame.f_lineno  # Grabs the line number
        location = f"{module.__name__}.{function_name}() at line {line_number}"
        return location
    except Exception as e:
        return f"Unknown exception occurred while grabbing error location:\n{e}"


def handle_generic_error(location: str, task: str, e: Exception):
    print_red(f"An exception occurred in:\n{location}\nwhile {task}, please see below.\n{e}")


def handle_generic_error_without_location(e: Exception):
    print_red("An exception occurred in while extracting hrefs from response content, please see below.\n")
    print_red(e)


def handle_failure_point(
    location: Optional[str] = None, task: Optional[str] = None, e: Optional[Exception] = None, error_string: Optional[str] = None
):
    if location and task and e:
        print_red(f"An exception occurred in: {location}\nwhile {task}, please see below.\n{e}")
    elif location and task and error_string:
        print_red(f"An exception occurred in: {location}\nwhile {task}, please see below.\n{error_string}")
    elif location and task:
        print_red(f"An error occurred in: {location}\nwhile {task}\n")
    elif error_string:
        print_red(f"{error_string}\n")
    elif e:
        print_red("An unknown error occurred.\n")


def handle_failure_point_and_exit(
    location: Optional[str] = None, task: Optional[str] = None, e: Optional[Exception] = None, error_string: Optional[str] = None
):
    if error_string:
        print_red(error_string)
    elif location and task:
        print_red(f"An error occurred in:\n{location}\nwhile {task}")
    elif location and task and e:
        print_red(f"An exception occurred in:\n{location}\nwhile {task}, please see below.\n{e}")
    elif location and task and error_string:
        print_red(f"An exception occurred in:\n{location}\nwhile {task}, please see below.\n{error_string}")
    elif e:
        print_red("An unknown error occurred.")
    exit()