import tldextract

def get_domain(url):
    if not url:
        return None
    ext = tldextract.extract(url)
    # ext.domain: 'creativecommons', ext.suffix: 'org'
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    return url  # fallback

def get_domain_without_suffix(url):
    if not url:
        return None
    ext = tldextract.extract(url)
    return ext.domain if ext.domain else url
