from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = (
    "https://www.imdb.com/search/title/?title_type=tv_episode&sort=user_rating,desc&num_votes=1000,"
)

data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless = False, slow_mo = 50)
    page = browser.new_page()
    page.goto(BASE_URL, wait_until="domcontentloaded")

    page.wait_for_selector("#__next", timeout=15000)
    
    try:
        page.wait_for_selector("a.ipc-title-link-wrapper", timeout=15000)
    except:
        print("Primary selector failed, dumping page...")
        print(page.content()[:2000])
        page.screenshot(path="debug.png")
        raise

    for i in range(19):
        btn =  page.locator("button:has-text('50 more')")
        btn.first.click()
        page.wait_for_timeout(3000)

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all("div", class_="dli-parent")

    for el in elements:
        raw_episode_name = el.find("h4", class_="ipc-title__text").text
        episode_number = el.find("span", class_="epCwUB").text

        items = el.find_all("li", class_="ipc-inline-list__item")[2:]
        series_name = el.find_all("h4", class_="ipc-title__text")[1].text

        episode_rating = el.find("span", class_="ipc-rating-star--rating").text
        voting_count = el.find("span", class_="ipc-rating-star--voteCount").text[1:]

        series_airdate, episode_length, tv_rating = None, None, None

        for item in items:
            text = item.text

            if "–" in text:
                series_airdate = text

            if "m" in text:
                episode_length = text

            if "-" in text:
                tv_rating = text
        
        position, episode_name = map(str.strip, raw_episode_name.split(".", maxsplit=1))

        data.append({
        "position": position,
        "episode_name": episode_name,
        "series_name": series_name,
        "episode_number": episode_number, 
        "airdate": series_airdate,
        "duration": episode_length,
        "tv_rating": tv_rating,
        "episode_rating": episode_rating,
        "votes": voting_count
        })

    browser.close()

df = pd.DataFrame(data)
df.to_csv("imdb_top_tv_episodes.csv", index=False)