import json
import requests
from bs4 import BeautifulSoup
from google_apis.sheet import insert_hyperlink


def extract_page_license_metadata(page_url, debug=False):
    """
    Fetches the HTML for the page at `page_url`, and returns any relevant
    copyright or license meta tags found (including Open Graph, CC, and Schema.org).
    If a 403 error is encountered, will retry using Selenium.
    """
    if page_url is None:
        return None, "no license found"

    # Adding a real user agent header helps websites accept the page download query
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    # --- Try with requests first ---
    try:
        response = requests.get(page_url, headers=headers, timeout=10)
        if response.status_code == 403:
            raise requests.HTTPError("403 Forbidden", response=response)
        response.raise_for_status()
        html = response.text
        return parse_html_for_metadata(html)
    except requests.HTTPError as http_err:
        if http_err.response is not None and http_err.response.status_code == 403:
            # Fallback to Selenium
            print("403 Forbidden → fallback to Selenium")
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options

                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument(
                    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                )
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(page_url)
                html = driver.page_source
                driver.quit()
                return parse_html_for_metadata(html, debug=debug, page_url=page_url)
            except Exception as selenium_exc:
                return None, f"Selenium failed: {selenium_exc}"
        else:
            return None, f"Could not fetch page: {http_err}"
    except Exception as e:
        return None, f"Could not fetch page: {e}"


def parse_html_for_metadata(html, debug=False, page_url=None):
    soup = BeautifulSoup(html, 'html.parser')
    meta_info = {}

    # --- Existing meta parsing ---
    meta_tags = soup.find_all("meta")
    for tag in meta_tags:
        attrs = tag.attrs
        for key in ("name", "property", "itemprop", "rel"):
            v = attrs.get(key, "").lower()
            if any(term in v for term in ["license", "copyright", "rights", "og:copyright", "og:license", "dc.rights", "dc.license", "cc:license"]):
                content = attrs.get("content", attrs.get("value", ""))
                if content:
                    meta_info[v] = content
        # Also search content for keywords
        for keyword in ["license", "creativecommons", "cc-", "public domain", "usage rights"]:
            content = attrs.get("content", "").lower()
            if keyword in content:
                meta_info[f"meta:contains:{keyword}"] = content

    # <link rel="license" href=...>
    link_tags = soup.find_all("link", rel=True, href=True)
    for link_tag in link_tags:
        rel = link_tag.get("rel")
        if isinstance(rel, list):
            rel = " ".join(rel)
        if "license" in rel.lower():
            meta_info["link:license"] = link_tag["href"]

    # <a rel="license" href=...>
    a_tags = soup.find_all("a", rel=True, href=True)
    for a_tag in a_tags:
        rel = a_tag.get("rel")
        if isinstance(rel, list):
            rel = " ".join(rel)
        if "license" in rel.lower():
            meta_info["a:license"] = a_tag["href"]

    # Structured data (JSON-LD)
    json_ld_tags = soup.find_all("script", type="application/ld+json")
    for script in json_ld_tags:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "license" in data:
                meta_info["schema:license"] = data["license"]
        except json.JSONDecodeError as error:
            print("JSONDecodeError:", error, "decoding json_ld_tags for", page_url)
            continue

    # Visible text scan
    text = soup.get_text(separator=' ').lower()
    for keyword in ["license", "creativecommons", "cc-", "public domain", "usage rights"]:
        if keyword in text:
            # Find sentence/paragraph containing keyword
            import re
            sentences = re.findall(r"([^.]*?{}[^.]*\.)".format(keyword), text)
            for s in sentences:
                meta_info[f"text:{keyword}"] = s.strip()

    # Figure/image alt/title/caption
    other_tags = soup.find_all(["img", "figure", "figcaption", "span", "div"])
    for tag in other_tags:
        alt = tag.get("alt", "") or tag.get("title", "")
        if alt and any(k in alt.lower() for k in ["license", "cc", "copyright"]):
            meta_info[f"{tag.name}:alt_or_title"] = alt

    if debug and not meta_info:
        from pprint import pprint
        print(f"\nurl: {page_url}")
        pprint(meta_tags)
        pprint(link_tags)
        pprint(a_tags)
        pprint(json_ld_tags)
        pprint(text)
        pprint(other_tags)

    return enrich_with_link(meta_info)


def enrich_with_link(info_dict):
    if not info_dict:
        return None, "no license found"
    info_str = str(info_dict).replace("\\n", "").replace("\\t", "")
    for key, value in info_dict.items():
        if value.startswith("http"):
            return insert_hyperlink(value, info_str)
    return info_str, None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract license/copyright info from a web page's metadata.")
    parser.add_argument("page_url", help="The URL of the web page to analyze.")
    parser.add_argument("--debug", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    result = extract_page_license_metadata(args.page_url, debug=args.debug)
    print(json.dumps(result, indent=2, ensure_ascii=False))