from utilities.colored import print_green, print_red
import re

def check_links_for_keywords(links):
    """
    Check each link for sensitive keywords and print links containing keywords,
    highlighting the keywords.

    Args:
    - links (list): A list of links to check.

    Returns:
    - None
    """
    sensitive_keywords = [
        "acct_pr", "ach", "acrobat", "aetna", "agendacenter", "annualreportarchive", "api", "app", "application",
        "ar", "asset", "assets", "attachment", "attachments", "audit", "bid", "bidid", "bids", "billing", "board",
        "board.nsf", "boarddocs", "brokers", "budget", "business", "ca", "calendar", "cd", "certifications",
        "claims", "clerk", "clients", "commission-orders", "company", "content", "contract", "contract_documents",
        "cp", "credentials", "csa", "cs_us_en", "dam", "default", "demo-google", "dist","docs", "documentcenter", 
        "documentdownload.aspx", "documents", "doc_financials", "download", "downloadcontractfile",
        "downloads", "en-us", "enrollment", "era", "events", "expenses", "file", "filemanager", "files", "finance",
        "forms", "fs", "gaoreports", "getattachment", "getmedia", "grants", "hosteddata", "images", "index=true",
        "intacct", "invoices", "la=en", "legal-pricing", "licenses", "log", "manuals", "mdonline", "media", "medicaid",
        "meeting", "meetingdocuments", "metaviewer.php", "nebraskabluedotcom", "notifications", "notificationscenter",
        "officeally", "orders", "payerpdf", "/pdf/", "/pdfs/", "plans", "pricing", "procurement", "products", "profiles",
        "provider", "psft", "public", "q4", "registrations", "renewals", "reports", "requests", "reservations",
        "resource-manager", "resources", "reviews", "sage-business-cloud", "server", "servers", "sites", "small-group",
        "solicitations", "statements", "states", "static-files", "subscriptions", "suppliers-files", "support", "tickets",
        "transactions", "ua", "ugd", "updates", "uploaded", "uploads", "us", "userfiles", "vendorspdf", "view",
        "viewfile", "wp-content"
    ]
    with open("vulnerables.txt", "a+") as file:
        count = 0
        for link in links:
            link_lower = link.lower()
            found_keywords = []
            for keyword in sensitive_keywords:
                pattern = r"\b" + re.escape(keyword) + r"\b"
                if re.search(pattern, link_lower):
                    found_keywords.append(keyword)
            if found_keywords:
                count += 1
                print_green(f"Link: {link}")
                print_green(f"Keywords found: {', '.join(found_keywords)}\n")
                file.write(f"{link}\n")
    if count == 0:
        print_red("No vulnerable links were found, exiting now.")
    
    else:
        print_green(f"Exported {count} vulnerable links to 'vulnerables.txt'")
    


