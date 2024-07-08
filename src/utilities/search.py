from bs4 import BeautifulSoup
from typing import List
from utilities.colored import print_blue, print_green, print_red
from utilities.errors import get_error_location, handle_failure_point, handle_generic_error
from utilities.query import (
    encode_query1,
    encode_query2,
    clean_query2,
    quote_plus,
)


# Search utilities

# Preserved for storytelling reasons
def get_gs_lp(query1, query2, first_operator):
    """Cleans query 2 as its encoded counterpart requires the first operator removed,
    then encodes query1 and query2 in base64 before combining the b64 string"""
    try:
        query2_cleaned = clean_query2(first_operator, query2)
        query1_encoded = encode_query1(query1)
        query2_encoded = encode_query2(query2_cleaned)
        gs_lp_string = query1_encoded + query2_encoded
        if gs_lp_string:
            return gs_lp_string
        exit()
    except Exception as e:
        print(e)
        print("In get_gs_lp")
        exit()

def generate_search_link(query: str) -> str:
    if not query:
        print(f"Invalid Query Provided: `{query}`")
        exit()

    link = "https://www.google.com/search?q="
    queryStr = quote_plus(query)
    link += queryStr
    link += "&oq="
    link += queryStr
    link += "&sourceid=chrome&ie=UTF-8"
    return link

def extract_hrefs(responses: List[str]) -> List[str]:
    try:
        location = "utilities.search.extract_hrefs()"  # Used for error handling
        task = "extracting hrefs from response content"  # Used for error handling
        hrefs = []
        for content in responses:
            soup = BeautifulSoup(content, "html.parser")  # Parses the HTML content using BeautifulSoup
            hrefs.extend(a["href"] for a in soup.find_all("a", href=True))  # Extracts all hrefs found in response content
        if hrefs:
            return hrefs
        handle_failure_point(
            "No href tags found, ensure your query is properly formatted and contains at least two search operators."
        )

    except Exception as e:
        handle_generic_error(location, task, e)
    return []

def clean_hrefs(hrefs: List[str], excluded_domains: List[str]) -> List[str]:
    try:
        if hrefs is None:
            return []

        cleaned_hrefs = [
            href for href in hrefs if href.startswith("http") and not any(domain in href for domain in excluded_domains)
        ]
        return cleaned_hrefs
    except Exception as e:
        location = get_error_location()
        task = "extracting hrefs from response content"
        handle_generic_error(location, task, e)
        return []

def export_links(links: List[str]) -> bool:
    try:
        print_green(f"{len(links)} links parsed!\n")
        if len(links) > 0:
            print_blue("\nPlease wait while we export your links.")
            with open("links.txt", "a", encoding="utf-8") as file:
                for link in links:
                    file.write(link + "\n")
            return True
        else:
            print_red("0 links parsed, please ensure your queries are properly formatted and spelled correctly.")
            return False

    except Exception as e:
        location = get_error_location()
        task = "trying to export your links"
        handle_generic_error(location, task, e)
        return False
    
