from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://omocoro.jp/"


def get_soup(url):
    """Get a BeautifulSoup object from a URL."""
    headers = {"User-Agent": "curl/8.5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


def scrape_tag(tag_name):
    """Scrape MP3s from the page of a specified tag."""
    page_url = urljoin(BASE_URL, f"tag/{tag_name}/")

    for _ in range(5):
        if not page_url:
            break

        soup = get_soup(page_url)
        if not soup:
            break

        article_links = soup.select("div.boxs div.title > a")
        if not article_links:
            break

        for link in article_links:
            article_url = urljoin(BASE_URL, link.get("href"))
            article_soup = get_soup(article_url)

            if article_soup:
                mp3_link = article_soup.select_one('a[href$=".mp3"]')
                if mp3_link and mp3_link.get("href"):
                    mp3_url = urljoin(BASE_URL, mp3_link.get("href"))
                    print(mp3_url)

        next_page_link = soup.select_one("div.page-navi span + a")
        if next_page_link and next_page_link.get("href"):
            page_url = urljoin(BASE_URL, next_page_link.get("href"))
        else:
            page_url = None


def main():
    """Main process."""
    tag_name = input("Please enter a tag: ")
    if not tag_name:
        print("No tag entered.")
        return

    scrape_tag(tag_name)


if __name__ == "__main__":
    main()
