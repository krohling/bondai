import requests
from bs4 import BeautifulSoup
from typing import List

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def is_html(text: str) -> bool:
    soup = BeautifulSoup(text, "html.parser")
    return bool(soup.find())


def get_website_html(url: str) -> str:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
    return response.text


def get_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def get_website_text(url: str) -> str:
    html = get_website_html(url)
    return get_html_text(html)


def query_website_html(url: str, xpath: str) -> str:
    html = get_website_html(url)
    soup = BeautifulSoup(html, "html.parser")
    root = soup.html
    return root.xpath(xpath)


def get_website_links(url: str) -> List[str]:
    html = get_website_html(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("a")
