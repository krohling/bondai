# from requests_html import HTMLSession
# import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# REQUEST_HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
# }

# def get_website_html(url):
#         response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
#         return response.text

# def get_website_html(url):
#         session = HTMLSession()
#         response = session.get(url, headers=REQUEST_HEADERS, timeout=10)
#         try:
#                 response.html.render()
#                 text = response.html.raw_html
#         except Exception:
#                 response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
#                 text = response.text
        
#         return text


def get_website_html(url, include_iframes=False):
        with sync_playwright() as p:
                browser = p.chromium.launch()  # you can also use "firefox" or "webkit"
                page = browser.new_page()
                page.goto(url)
                page.wait_for_load_state('load', timeout=60000)  # waits for the network to be idle

                if include_iframes:
                        result = [page.content()]
                        for i, frame in enumerate(page.frames):
                                frame.wait_for_load_state('load', timeout=60000)
                                result.append(frame.content())
                else:
                        result = page.content()  # get HTML content of the page

                browser.close()
                return result

def get_html_text(html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()

def get_website_iframes(url):
        with sync_playwright() as p:
                browser = p.chromium.launch()  # you can also use "firefox" or "webkit"
                page = browser.new_page()
                page.goto(url)
                page.wait_for_load_state('load', timeout=60000)  # waits for the network to be idle

                results = []
                for i, frame in enumerate(page.frames):
                        frame.wait_for_load_state('load', timeout=60000)
                        results.append(frame.url)

                browser.close()
                return results


def get_website_text(url):
        html = get_website_html(url)
        return get_html_text(html)

def query_website_html(url, xpath):
        html = get_website_html(url)
        soup = BeautifulSoup(html, "html.parser")
        root = soup.html
        return root.xpath(xpath)

def get_website_links(url):
        html = get_website_html(url)
        soup = BeautifulSoup(html, "html.parser")
        return soup.find_all("a")
