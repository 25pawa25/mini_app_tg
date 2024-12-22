import os
from bs4 import BeautifulSoup
import json
import aiohttp
import asyncio

from dotenv import load_dotenv


async def fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Ошибка доступа к {url}: {response.status}")
        return await response.text()


async def get_end_date_discount(session, game_url):
    try:
        page_content = await fetch(session, game_url)
        soup = BeautifulSoup(page_content, 'html.parser')
        end_date = soup.find('span', class_="psw-t-overline psw-t-bold psw-l-line-left psw-fill-x").find('span', class_="psw-c-t-2").get_text(strip=True)
        return end_date.strip("Teklif sonu: ")
    except AttributeError:
        return "Не найдено"
    except Exception as e:
        print(f"Ошибка получения деталей игры с {game_url}: {e}")
        return "Ошибка"


async def parse_psn_store(base_url, list_url):
    async with aiohttp.ClientSession() as session:
        page_content = await fetch(session, f"{base_url}{list_url}")
        soup = BeautifulSoup(page_content, 'html.parser')

        games = []
        tasks = []

        blocks = soup.find_all('div', class_="psw-product-tile psw-interactive-root")
        links = soup.find("ul", class_="psw-strand-scroller psw-l-line-left-top psw-list-style-none psw-l-space-x-5 psw-p-y-4 psw-p-x-4 psw-m-sub-x-4 psw-hide-scrollbar").find_all('a', class_="psw-link psw-content-link")

        for block, link in zip(blocks, links):
            try:
                title = block.find('span', class_="psw-t-body psw-c-t-1 psw-t-truncate-2 psw-m-b-2").get_text(strip=True)
                current_price = block.find('span', class_="psw-m-r-3").get_text(strip=True)
                old_price = block.find('s', class_="psw-c-t-2").get_text(strip=True)
                discount = block.find('span', class_="psw-body-2 psw-badge__text psw-badge--none psw-text-bold psw-p-y-0 psw-p-2 psw-r-1 psw-l-anchor").get_text(strip=True)

                game_link = link['href']
                game_url = f"{base_url}{game_link}"

                tasks.append(
                    asyncio.create_task(get_end_date_discount(session, game_url))
                )

                games.append({
                    "title": title,
                    "current_price": current_price,
                    "old_price": old_price,
                    "discount": discount.replace("-", ""),
                    "link": game_url
                })
            except AttributeError:
                continue

        additional_infos = await asyncio.gather(*tasks)
        for game, additional_info in zip(games, additional_infos):
            game["end_date"] = additional_info

        return games


def save_to_json(data, filename="psn_discounts.json"):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    PSN_BASE_URL = os.getenv("PSN_BASE_URL", "")
    PSN_LIST_POSTFIX = os.getenv("PSN_LIST_POSTFIX", "")
    games = asyncio.run(parse_psn_store(PSN_BASE_URL, PSN_LIST_POSTFIX))
    save_to_json(games)
    print("Данные успешно сохранены в psn_discounts.json")
