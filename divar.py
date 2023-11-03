from bs4 import BeautifulSoup
import time
from pymongo import MongoClient
from selenium import webdriver

mongodb_client = MongoClient('mongodb://localhost:27017/')
db = mongodb_client['mydatabase']
collection = db['houses']


def get_ads():
    driver = webdriver.Chrome()
    driver.get('https://divar.ir/s/tehran/buy-apartment?size=40-40')

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    time.sleep(2)

    ads = []
    ads.extend(soup.findAll('div', class_='post-card-item-af972 kt-col-6-bee95 kt-col-xxl-4-e9d46'))

    # scroll down website
    for i in range(10):
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        ads.extend(soup.findAll('div', class_='post-card-item-af972 kt-col-6-bee95 kt-col-xxl-4-e9d46'))
        i += 1

    # get title, price and url of ads and save in mongodb
    for ad in ads:
        ad_title = ad.find('h2', class_='kt-post-card__title').text
        price = ad.find('div', class_='kt-post-card__description').text
        agancy = ad.find('span', class_='kt-post-card__bottom-description kt-text-truncate').text
        try:
            link = ad.find('a', href=True)['href']
            house_data = {
                'title': ad_title,
                'price': price,
                'link': 'https://divar.ir' + link,
                'real estate agency': agancy
            }
            collection.insert_one(house_data)
        except TypeError:
            house_data = {
                'title': ad_title,
                'price': price,
                'link': "",
                'real estate agency': agancy
            }
            collection.insert_one(house_data)


if __name__ == '__main__':
    get_ads()
