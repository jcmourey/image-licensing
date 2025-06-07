from bs4 import BeautifulSoup
import json
import re


def extract_metadata(html, debug) -> (dict[str, str], list[str]):
    """
        Returns a dict of license texts and a list of license urls
    """
    soup = BeautifulSoup(html, 'html.parser')
    meta_info = {}
    urls = []

    def add_info(key, value):
        if value:
            if value.startswith("http"):
                urls.append(value)
            else:
                meta_info[key] = sanitize(value)

    # --- Existing meta parsing ---
    meta_tags = soup.find_all("meta")
    for tag in meta_tags:
        attrs = tag.attrs
        for key in ("name", "property", "itemprop", "rel"):
            v = attrs.get(key, "").lower()
            if any(term in v for term in ["license", "copyright", "rights", "og:copyright", "og:license", "dc.rights", "dc.license", "cc:license"]):
                content = attrs.get("content", attrs.get("value", ""))
                add_info(v, content)
        # Also search content for keywords
        for keyword in ["license", "creativecommons", "cc-", "public domain", "usage rights"]:
            content = attrs.get("content", "").lower()
            if keyword in content:
                add_info(f"meta:contains:{keyword}", content)

    # <link rel="license" href=...>
    link_tags = soup.find_all("link", rel=True, href=True)
    for link_tag in link_tags:
        rel = link_tag.get("rel")
        if isinstance(rel, list):
            rel = " ".join(rel)
        if "license" in rel.lower():
            urls.append(link_tag["href"])

    # <a rel="license" href=...>
    a_tags = soup.find_all("a", rel=True, href=True)
    for a_tag in a_tags:
        rel = a_tag.get("rel")
        if isinstance(rel, list):
            rel = " ".join(rel)
        if "license" in rel.lower():
            urls.append(a_tag["href"])

    # Structured data (JSON-LD)
    json_ld_tags = soup.find_all("script", type="application/ld+json")
    for script in json_ld_tags:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "license" in data:
                add_info("schema:license", data["license"])
        except json.JSONDecodeError as error:
            print("JSONDecodeError:", error, "decoding json_ld_tags:", script.string)
            continue

    # Visible text scan
    text = soup.get_text(separator=' ').lower()
    for keyword in ["license", "creativecommons", "cc-", "public domain", "usage rights"]:
        if keyword in text:
            # Find sentence/paragraph containing keyword
            sentences = re.findall(r"([^.]*?{}[^.]*\.)".format(keyword), text)
            for s in sentences:
                add_info(f"text:{keyword}", s)

    # Figure/image alt/title/caption
    other_tags = soup.find_all(["img", "figure", "figcaption", "span", "div"])
    for tag in other_tags:
        alt = tag.get("alt", "") or tag.get("title", "")
        if alt and any(k in alt.lower() for k in ["license", "cc", "copyright"]):
            add_info(f"{tag.name}:alt_or_title", alt)

    if debug and (meta_info or urls):
        from pprint import pprint
        pprint(meta_tags)
        pprint(link_tags)
        pprint(a_tags)
        pprint(json_ld_tags)
        pprint(text)
        pprint(other_tags)
        
    return meta_info, urls
        
        
def sanitize(content):
    return re.sub(r'\s+', ' ', content).strip()