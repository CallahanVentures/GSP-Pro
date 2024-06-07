from urllib.parse import quote_plus
from utilities.colored import print_red
import base64

from typing import List, Optional


# loads queries from queries.txt or asks for a single query as input if an exception is thrown
def load_queries() -> List[str]:
    try:
        with open("queries.txt", "r+", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        print_red(f"There was an issue reading queries.txt: {e}")
        return [input("Enter A Query To Search By, For Example 'Realtors in 30303':\n")]


def query_to_operatives_dict(query_string):  # currently unused, future plans are to implement features utilizing this function
    # Initialize JSON object
    data = {
        "inurl": [],
        "intext": [],
        "ext": [],
        "intitle": [],
        "site": [],
        "negatives": [],
        "numrange": [],
        "after": [],
        "before": [],
    }

    # Parse the query string
    parts = query_string.split()
    for part in parts:
        if part.startswith("inurl:"):
            data["inurl"].append(part.replace("inurl:", ""))
        elif part.startswith("intext:"):
            data["intext"].append(part.replace("intext:", ""))
        elif part.startswith("ext:"):
            data["ext"].append(part.replace("ext:", ""))
        elif part.startswith("intitle:"):
            data["intitle"].append(part.replace("intitle:", ""))
        elif part.startswith("site:"):
            data["site"].append(part.replace("site:", ""))
        elif part.startswith("-"):
            data["negatives"].append(part[1:])  # Remove the '-' sign
        elif part.startswith("numrange:"):
            data["numrange"].append(part.replace("numrange:", ""))
        elif part.startswith("after:"):
            data["after"].append(part.replace("after:", ""))
        elif part.startswith("before:"):
            data["before"].append(part.replace("before:", ""))
    # import json
    # print(json.dumps(data, indent=4))

    return data


def get_first_operator(query: str) -> Optional[str]:
    try:
        parts = query.split()

        for part in parts:
            if any(
                operator in part
                for operator in ["inurl:", "intext:", "ext:", "intitle:", "site:", "numrange:", "after:", "before:"]
            ):
                return part
        print_red("No search operators found, skipping query.")
        return None

    except Exception as e:
        print_red("An exception occurred while getting the first search operator to build the search URL, please see below.")
        print_red(str(e))
        print()
        print_red("Skipping query.")
        return None


def encode_query(query_string: str) -> str:
    # URL encode the query string
    encoded_query = quote_plus(query_string)

    # Replace "%20" with "+"
    encoded_query = encoded_query.replace("%20", "+")

    # Replace "%22" with '"'
    encoded_query = encoded_query.replace("%22", '"')

    return encoded_query


def encode_query1(query1) -> str:
    try:
        encoded_bytes = query1.encode("utf-8")

        # Encode the bytes using base64
        encoded_string = base64.b64encode(encoded_bytes).decode("utf-8").replace("=", "g")
        if encoded_string:
            return encoded_string
        exit()
    except Exception as e:
        print(e)
        print("In get_gs_lp_part_1")
        exit()


def encode_query2(query2) -> str:
    try:
        encoded_query = base64.b64encode(query2.encode()).decode()
        if encoded_query:
            return encoded_query
        exit()
    except Exception as e:
        print(e)
        print("In get_gs_lp_part_2")
        exit()


def clean_query2(
    first_operator: str, query2: str
) -> str:  # Removes the first_operator from the query as per Google's encoding protocol
    return query2.replace(f"{first_operator} ", "")


def inurl_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("inurl:")]
    if queries:
        return " ".join(queries)
    return ""


def intext_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("intext:")]
    if queries:
        return " ".join(queries)
    return ""


def ext_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("ext:")]
    if queries:
        return " ".join(queries)
    return ""


def intitle_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("intitle:")]
    if queries:
        return " ".join(queries)
    return ""


def site_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("site:")]
    if queries:
        return " ".join(queries)
    return ""


def numrange_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("numrange:")]
    if queries:
        return " ".join(queries)
    return ""


def after_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("after:")]
    if queries:
        return " ".join(queries)
    return ""


def before_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("before:")]
    if queries:
        return " ".join(queries)
    return ""


def negative_queries(query_string: str) -> str:
    queries = [part for part in query_string.split() if part.startswith("-")]
    if queries:
        return " ".join(queries)
    return ""