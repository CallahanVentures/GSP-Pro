#!/usr/bin/env python3
# main.py
from concurrent.futures import ThreadPoolExecutor, as_completed

from utilities.backup import backup_last_session
from utilities.branding import show_branding
from utilities.browser import (
    close_browser,
    get_search_response,
    initialize_browser,
    random_chrome_ua,
    swap_proxy,
)
from utilities.colored import print_red, print_blue, print_green
from utilities.config import Config, load_config
from utilities.errors import handle_failure_point, handle_failure_point_and_exit
from utilities.logger import Logger
from utilities.query import load_queries
from utilities.recaptcha import RecaptchaSolver
from utilities.scanner import check_links_for_keywords
from utilities.search import (
    clean_hrefs,
    export_links,
    extract_hrefs,
    generate_search_link,
)
from utilities.threads import get_thread_id
from typing import Optional, Tuple, List

# All functions from: errors.py
# random_proxy, valid_proxy, valid_type from proxy.py
# RecaptchaSolver() from recaptcha.py


def main() -> None:
    show_branding()
    backup_last_session()
    logger = Logger()
    config: Optional[Config] = load_config()
    if config is None:
        logger.logCritical("Error loading configuration file during runtime.")
        handle_failure_point_and_exit("main.py", "loading config file")

    # Loads queries from queries.txt
    queries: List[str] = load_queries()

    # Processes each query
    def process_query(query_string: str) -> Tuple[str, List[str]]:
        USER_AGENT: str = random_chrome_ua()
        try:
            browser = None
            retries: int = 5

            for _ in range(retries):
                browser = initialize_browser(use_proxy=True, proxy_type=config.proxy_type, user_agent=USER_AGENT)
                if browser is not None:
                    break
                print_red("Failed to initialize browser, retrying...")
                logger.logInfo("Failed to initialize browser, retrying...")

            if browser is None:
                return query_string, []

            thread_id: str = f"Thread {get_thread_id()}"
            print_blue(f"[{thread_id}]: Processing query: {query_string}")
            logger.logInfo(f"[{thread_id}]: Processing query: {query_string}")
            
            search_link = generate_search_link(query_string)
                
            # Make search request and process results
            response_text = get_search_response(browser, search_link, thread_id)

            if response_text == "swap proxy":
                print_blue(f"[{thread_id}]: Swapping proxy for query: {query_string}")
                logger.logInfo(f"[{thread_id}]: Swapping proxy for query: {query_string}")

                status_and_browser = swap_proxy(browser, PROXY_TYPE=config.proxy_type, current_url=browser.current_url)
                
                if not len(status_and_browser) == 2: # swap_proxy returns either [bool(True), new_driver] or [bool(False)]
                    handle_failure_point("Unable to swap proxy, closing current thread.")
                    logger.logCritical("Unable to swap proxy, closing current thread.")
                    return "break"
                
                else: # if length of status_and_browser is 2 it has a value of [True, new_driver]
                    browser = status_and_browser[1]

                solver = RecaptchaSolver(browser, thread_id)
                if not solver.solveCaptcha():
                    browser.quit()
                    print_red(f"[{thread_id}]: Failed to solve captcha.")
                    logger.logCritical(f"[{thread_id}]: Failed to solve captcha.")

            if response_text is None:
                return query_string, "break"

            extracted_hrefs = extract_hrefs(response_text)
            cleaned_links = clean_hrefs(extracted_hrefs, config.excluded_domains)
            print_green(f"[{thread_id}]: Finished processing query: {query_string} with {len(cleaned_links)} unique links")
            logger.logInfo(f"[{thread_id}]: Finished processing query: {query_string} with {len(cleaned_links)} unique links")
            return query_string, cleaned_links
            
        except Exception as e:
            if "GetHandleVerifier" in str(e):
                print_red(f"[{thread_id}]: Exception while processing query: {query_string}: browser instance was closed")
                logger.logCritical(f"[{thread_id}]: Exception while processing query: {query_string}: browser instance was closed")
            return query_string, []
        
        finally:
            if browser is not None:
                close_browser(browser)

    # Process each query and collect results using multithreading
    all_cleaned_links = []
    with ThreadPoolExecutor(max_workers=config.thread_count) as executor:
        future_to_query = {executor.submit(process_query, query): query for query in queries}
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                query, cleaned_links = future.result()
                if cleaned_links:
                    if cleaned_links == "break":
                        break
                    all_cleaned_links.extend(cleaned_links)
            except Exception as exc:
                print_red(f"Query '{query}' generated an exception: {exc}")
                logger.logError(f"Query '{query}' generated an exception: {exc}")

    # Ensure all_cleaned_links has unique links
    unique_cleaned_links = list(set(all_cleaned_links))

    # Export all collected links
    export_links(unique_cleaned_links)

    if config.run_vuln_scan:
        check_links_for_keywords(unique_cleaned_links)


if __name__ == "__main__":
    main()