import imagehash              # for generating perceptual hashes from images
import requests               # for sending HTTP requests to download logos
from PIL import Image         # for opening and manipulating images
from io import BytesIO        # for converting bytes response to PIL Image
from bs4 import BeautifulSoup # for parsing HTML to extract <link rel="icon">

# Get logo from Clearbit
def get_logo_clearbit(domain):
    url = f"https://logo.clearbit.com/{domain}"
    return download_logo_from_url(url)

# Get icon from DuckDuckGo
def get_logo_duckduckgo(domain):
    url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
    return download_logo_from_url(url)

# Get favicon directly from the website
def get_logo_favicon(domain):
    url = f"https://{domain}/favicon.ico"
    return download_logo_from_url(url)

# Try to extract logo from <link rel="icon"> in the HTML
def get_logo_from_html(domain):
    try:
        url = f"https://{domain}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=5, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        icon_link = soup.find("link", rel=lambda val: val and "icon" in val.lower())
        if icon_link and icon_link.get("href"):
            href = icon_link["href"]
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = f"https://{domain}" + href
            elif not href.startswith("http"):
                href = f"https://{domain}/" + href
            return download_logo_from_url(href)
    except Exception:
        pass
    return None

# Check if image is meaningful (large enough and not plain)
def is_meaningful_image(img):
    if img.width < 32 or img.height < 32:
        return False
    gray = img.convert("L")
    histogram = gray.histogram()
    unique_shades = sum(1 for v in histogram if v > 0)
    return unique_shades > 10

# Try all sources and return the first meaningful image
# If none found, return the first fallback image (even if weak)
def get_logo(domain):
    fallback_logo = None
    for fetcher in [get_logo_clearbit, get_logo_from_html, get_logo_duckduckgo, get_logo_favicon]:
        logo = fetcher(domain)
        if logo:
            if is_meaningful_image(logo):
                return logo
            elif not fallback_logo:
                fallback_logo = logo
    return fallback_logo

# Download image from URL and convert to RGB/RGBA
def download_logo_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode == "P" and "transparency" in img.info:
                return img.convert("RGBA")
            else:
                return img.convert("RGB")
    except Exception:
        pass
    return None

# Generate perceptual hash from an image
def hash_logo(image):
    return imagehash.phash(image)

# Compute Hamming distance between two hashes
def hamming_distance(hash1, hash2):
    return hash1 - hash2
