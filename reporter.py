import datetime
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from telethon import TelegramClient, events
from webdriver_manager.chrome import ChromeDriverManager

from env import API_ID, BOT_TOKEN, API_HASH

bot = TelegramClient(
    "news_scraper", api_id=int(API_ID),
    api_hash=API_HASH).start(
    bot_token=BOT_TOKEN
)
bot_settings = {}


def scraping():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    news = []
    for i in range(bot_settings["scraping_duration"] * 86400):

        if datetime.datetime.now().strftime("%H:%M") == bot_settings["scraping_time"]:
            if "youtube" in bot_settings.get("url"):
                news = youtube_news(driver,
                    bot_settings.get("keywords"),
                    bot_settings.get("news_count")
                )

            elif "instagram" in bot_settings.get("url"):
                news = instagram_news(
                    driver,
                    bot_settings.get("news_count"),
                )
            elif "bbc" in bot_settings.get("url"):
                news = bbc_news(
                    driver,
                    bot_settings.get("news_count"),
                )
            elif "cnn" in bot_settings.get("url"):
                news = instagram_news(
                    driver,
                    bot_settings.get("news_count"),
                )
            return news


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "Вітаю! Це Telegram-бот для скрапінгу та публікації новин. "
        "Ви можете налаштувати параметри для кожного сайту "
        "та каналу через панель користувача. Введіть  команду,"
        " щоб розпочати налаштування в наступному форматі:\n"
        " - /set_site youtube\n"
        " - /set_site instagram\n"
        " - /set_site cnn\n"
        " - /set_site bbc\n"
    )


@bot.on(events.NewMessage(pattern="/set_site"))
async def set_site(event):
    await event.respond(
        "Адресу ортимано.\n"
        "Тепер введіть ключові слова в такому форматі:\n"
        "/set_keywords ключові слова\n"
        "Або пробіл в разі їх відсутності."
    )
    url = event.text.split()[1]
    bot_settings["url"] = url


@bot.on(events.NewMessage(pattern="/set_keywords"))
async def set_keywords(event):
    await event.respond(
        "Ключові слова ортимано.\n"
        "Тепер введіть кількість новин цифрою в такому форматі:\n"
        "/set_news_count 0"
    )
    keywords = " ".join(event.text.split()[1:])
    if len(keywords) > 1:
        bot_settings["keywords"] = keywords


@bot.on(events.NewMessage(pattern="/set_news_count"))
async def set_news_count(event):
    await event.respond(
        "Кількість новин встановлено.\n"
        "Тепер введіть введіть час в який буде скрапитись даний сайт в форматі 24 години:\n"
        "/set_scraping_time години:хвилини"
    )
    scraping_time = event.text.split()[1]
    if len(scraping_time) > 1:
        bot_settings["scraping_time"] = scraping_time


@bot.on(events.NewMessage(pattern="/set_scraping_time"))
async def set_scraping_time(event):
    await event.respond(
        "Час скрапінгу встановлено.\n"
        "Тепер введіть введіть час протягом якого буде проводитись скрапінг:\n"
        "/set_scraping_duration 0 днів"
    )
    scraping_duration = event.text.split()[1]
    if len(scraping_duration) > 1:
        bot_settings["scraping_duration"] = int(scraping_duration)


@bot.on(events.NewMessage(pattern="/scraping"))
async def start_scraping(event):
    news_list = scraping()
    [await event.respond(news) for news in news_list]


def youtube_news(driver, keywords, count_of_news):
    driver.get(f"{bot_settings.get('url')}search?query={keywords}")
    news_list = [news.get_attribute("href") for news in
                 driver.find_elements(By.ID, "video-title")
                 if news.get_attribute("href")]
    return news_list[:count_of_news]


def instagram_news(driver, count_of_news):
    driver.get(bot_settings.get('url'))
    news_list = [
        news.get_attribute("href")
        for news in driver.find_elements(By.XPATH,
                                         "//a[@role='link']")
    ]
    return news_list[1:count_of_news + 1]


def bbc_news(webdriver, count_of_news, keywords=None):
    webdriver.get(
        f"https://www.bbc.co.uk/search?q={keywords.replace(' ', '+')}&d=SEARCH_PS")

    news_list = webdriver.find_elements(
        By.XPATH,
        "//div[@data-testid='default-promo']"
    )
    news_links = [
        link.find_element(By.TAG_NAME, "a").get_attribute("href")
        for link in news_list
    ]

    return news_links[:count_of_news]


def cnn_news(driver, count_of_news, keywords=None):
    driver.get(f"https://edition.cnn.com/search?q={keywords.replace(' ', '+')}&from=0&size=10&page=1&sort=newest&types=all&section=")
    time.sleep(4)
    links = [link.get_attribute("href") for link in driver.find_elements(By.CLASS_NAME, "container__link")]
    return links[:count_of_news]


def main():
    bot.run_until_disconnected()


if __name__ == "__main__":
    main()
    scraping()
