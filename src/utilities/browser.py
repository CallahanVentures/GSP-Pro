from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utilities.colored import print_green, print_red, print_blue
from utilities.errors import get_error_location, handle_generic_error, handle_failure_point_and_exit
from utilities.proxy import random_proxy, valid_proxy
from utilities.recaptcha import RecaptchaSolver
from webdriver_manager.chrome import ChromeDriverManager
import random
import time

from utilities.config import ProxyType as ConfigProxyType
from typing import Optional, Union


# Creates a new seleniumwire instance
def initialize_browser(
    use_proxy: bool = False, proxy_type: Optional[ConfigProxyType] = None, user_agent=None
) -> Optional[webdriver.Chrome]:
    # Error handling variables and options declaration
    task = "initializing webdriver"
    options = webdriver.ChromeOptions()

    # Global options
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Removes devtools print statement

    if user_agent:
        options.add_argument(f"user-agent={user_agent}")

    PROXY = None
    if use_proxy:
        max_retries = 5

        for _ in range(max_retries):
            PROXY = random_proxy()
            if valid_proxy(PROXY, proxy_type):
                break

        if valid_proxy(PROXY, proxy_type):
            print_blue(f"Initializing browser using proxy: {PROXY}")
            options.add_argument(f"--proxy-server={PROXY}")
        else:
            print_blue("Proxy verification failed. Initializing browser without proxy.")
    else:
        print_blue("Initializing browser without proxy.")

    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_window_position(0, 1920)  # Sets position off screen since we can't minimize window

        if PROXY:
            driver.proxy = PROXY

            # Validate the proxy
            if proxy_works_in_browser(driver):
                print_green("Driver initialized with a working proxy.")
                print()
            else:
                print_red("Driver initialized, but the proxy is not working, continuing without proxy.")
                print()
        return driver

    except Exception as e:
        location = get_error_location()
        handle_generic_error(location, task, e)
        try:
            driver.quit()
        except Exception as e:
            print_red("Unable to close failed browser instance")


def random_firefox_ua() -> str:
    windows_versions = ["Windows NT 10.0; Win64; x64", "Windows NT 6.1; Win64; x64", "Windows NT 6.1; WOW64", "Windows NT 10.0"]

    firefox_versions = ["91.0", "92.0", "93.0", "94.0", "95.0", "96.0", "97.0", "98.0", "99.0", "100.0", "101.0", "102.0"]

    # Randomly select a Windows version and a Firefox version
    windows_version = random.choice(windows_versions)
    firefox_version = random.choice(firefox_versions)

    # Create the user agent string
    user_agent = f"Mozilla/5.0 ({windows_version}; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}"

    return user_agent


def proxy_works_in_browser(driver: webdriver.Chrome):
    """
    Ensures the set proxy works on the provided ChromeDriver instance by trying to access google.com.

    Args:
        driver (webdriver.Chrome): The ChromeDriver instance with the proxy configured.

    Returns:
        bool: True if the proxy works, False otherwise.
    """
    test_url = "https://www.google.com"
    location = get_error_location()
    task = "verifying proxy works in browser"
    try:
        driver.get(test_url)
        if "Google" not in driver.title:
            print_red("\nProxy loaded, but might be IP blocked.\nChoosing a new proxy.")
            return False
        print_green("\nProxy is working correctly.")
        return True
    except WebDriverException as e:
        handle_generic_error(location, task, e)
        return False
    except Exception as e:
        handle_generic_error(location, task, e)
        return False


def render_html(driver: webdriver.Chrome) -> str:
    try:
        # JavaScript function to get the rendered HTML
        location = get_error_location()
        task = "rendering response from browser"
        return driver.execute_script("return document.documentElement.innerHTML;")
    except Exception as e:
        handle_generic_error(location, task, e)
        return ""


def page_table_present(driver: webdriver.Chrome):
    try:
        return '<table class="AaVjTc" style="border-collapse:collapse;text-align:left" role="presentation">' in render_html(
            driver
        )
    except Exception:
        return False


def all_results_present(driver: webdriver.Chrome) -> Union[str, bool]:
    try:
        return "In order to show you the most relevant results, we have omitted some entries" in render_html(driver)
    except Exception:
        return False


def captcha_present(e) -> bool:
    return "Message: element not interactable: element has zero size" in str(e)


def captcha_onload(driver) -> Union[str, bool]:
    try:
        captcha_in_url: bool = "https://www.google.com/sorry/index?continue=" in driver.current_url
        captcha_in_resp: bool = "This page appears when Google automatically detects requests coming" in render_html(driver)
        return captcha_in_url or captcha_in_resp
    except Exception:
        return False


def captcha_missing(driver) -> bool:
    try:
        time.sleep(3)
        if "https://www.google.com/sorry/index?continue=https://www.google.com/search" not in driver.current_url:
            return False

        elif "<iframe" in render_html(driver):
            return False

        elif "<iframe" not in render_html(driver):
            return True
        return False
    except NoSuchElementException:
        return True
    except WebDriverException as wd_error:
        print(f"WebDriverException occurred: {str(wd_error)}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False



def swap_proxy(driver: webdriver.Chrome, PROXY_TYPE: ConfigProxyType = ConfigProxyType.HTTP, retries: int = 10, current_url: str = None) -> Union[bool, webdriver.Chrome]:
    """
    Generates a valid proxy of the defined PROXY_TYPE with the specified retry count.

    Parameters:
        driver (WebDriver): The Selenium WebDriver instance.
        retries (int): The number of retries to find a valid proxy.

    Returns:
        [bool(True), new_driver] or [bool(False)] depending on status of proxy swap
    """

    attempts: int = 0
    proxy_manual = ProxyType.MANUAL
    working_proxy: bool = False
    if not current_url:
        return False


    try:
        while not working_proxy and attempts < retries:
            attempts += 1
            proxy = random_proxy()
            working_proxy = valid_proxy(proxy, PROXY_TYPE)

        if working_proxy:
            # Parse proxy string
            proxy_dict = {
                "proxyType": proxy_manual,
                "httpProxy": f"{PROXY_TYPE}://{proxy}",
                "ftpProxy": f"{PROXY_TYPE}://{proxy}",
                "sslProxy": f"{PROXY_TYPE}://{proxy}",
            }

            # Create a Proxy object
            proxy_obj = Proxy(proxy_dict)
            driver.close()

            print_red(f"Starting a new browser instance with proxy: {proxy}")
            new_driver = initialize_browser(use_proxy=True, proxy_type=PROXY_TYPE, user_agent=random_firefox_ua())

            # Although new_driver's proxy should be set, this ensure it is.
            new_driver.proxy = proxy_obj
            new_driver.get(current_url)

            print_green(f"Proxy on new browser instance set to: {proxy}")
            return [True, new_driver]
        return [False]
    except Exception as e:
        # location = get_error_location()
        # task = "swapping proxy"
        # handle_generic_error(location, task, e)
        print(e)
        print("In Swap_Proxy()")
        return [False]


def get_captcha_url(driver: webdriver.Chrome) -> Optional[str]:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    iframe = soup.find("iframe")
    if iframe:
        src = iframe.get("src")
        if src:
            return src
    return None


def get_audio_link(driver: webdriver.Chrome) -> Optional[str]:
    try:
        # Wait until the audio challenge link is available and clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.rc-audiochallenge-tdownload-link")))

        # Get the HTML content of the page
        html_content = driver.execute_script("return document.documentElement.innerHTML;")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the <a> tag with the class 'rc-audiochallenge-tdownload-link'
        audio_link_tag = soup.find("a", class_="rc-audiochallenge-tdownload-link")

        if audio_link_tag:
            # Extract the 'href' attribute
            audio_link = audio_link_tag["href"]
            print(f"Audio link found: {audio_link}")
            return audio_link
        else:
            print("Audio link not found.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_search_response(driver: webdriver.Chrome, search_link: str, thread_id: str) -> Optional[str]:
    location = get_error_location()

    try:
        driver.get(search_link)

        if "https://www.google.com/sorry/index?continue=" in driver.current_url:
            if captcha_missing(driver) is False:
                print_red(f"[{thread_id}]: Captcha present! Please wait while we solve it, this takes about 60 seconds.")
                solver = RecaptchaSolver(driver, thread_id)
                captcha_solved = solver.solveCaptcha()

                if captcha_solved is False:
                    handle_failure_point_and_exit(location, "solving captcha")

            else:
                print_red(f"[{thread_id}]: Unable to solve captcha due to IP Block, please wait while we swap proxies.")
                return "swap proxy"

        scroll_count = 0
        while scroll_count < 20:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                click_result = click_more_results(driver, thread_id)  # Pass thread_id to click_more_results

                if isinstance(click_result, str):
                    if "https://www.google.com/sorry/index?continue=" in click_result:
                        driver.get(click_result)
                        solver = RecaptchaSolver(driver, thread_id)
                        captcha_solved = solver.solveCaptcha()

                        if captcha_solved is True:
                            continue

                        else:
                            handle_failure_point_and_exit(location, "solving captcha")

                    elif "break" in click_result:
                        break
                    else:
                        continue

                elif isinstance(click_result, bool):
                    if click_result is False:
                        continue
                    elif click_result is True:
                        scroll_count += 1
                        print_green(f"[{thread_id}]: Scraped page {scroll_count}!")
                    else:
                        continue

                else:
                    continue

            except Exception as e:
                task = "scrolling through search results"
                handle_generic_error(location, task, e)

        print_green(f"\n[{thread_id}]: Scrolling finished, returning response for parsing.")
        return render_html(driver)

    except Exception as e:
        task = "getting search response"
        handle_generic_error(location, task, e)
    return None


def click_more_results(driver: webdriver.Chrome, thread_id: str) -> Union[bool, str]:
    try:
        more_results_element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[aria-label="More results"][role="button"][aria-hidden="false"]'))
        )
        more_results_element.click()
        return True

    except Exception as e:
        if captcha_onload(driver):
            return driver.current_url
        elif all_results_present(driver) or page_table_present(driver):
            return "break"
        elif captcha_present(e):
            print_red(f"[{thread_id}]: Captcha found!")
            captcha_url = get_captcha_url(driver)
            if captcha_url:
                return str(captcha_url)
        elif captcha_missing(driver):
            print_red(f"[{thread_id}]: Captcha expected but not found, likely due to an IP block.")
            return "ip block"

        return False


def close_browser(driver: webdriver.Chrome):
    try:
        driver.quit()
    except Exception as e:
        location = get_error_location()
        task = "closing browser"
        handle_generic_error(location, task, e)