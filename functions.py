import re
from time import sleep

import bs4 as bs
import requests
from selenium import webdriver
from unidecode import unidecode

# - - - - -

def add_item_to_list(item): # Search for item on Prisma, Selver, Rimi and add to items_to_check.txt
    link_prisma = "https://www.prismamarket.ee/products/search/" + item
    link_rimi = "https://www.rimi.ee/epood/ee/otsing?query=" + item
    link_selver = "https://www.selver.ee/search?q=" + item
    
    for link in [link_rimi, link_prisma, link_selver]:
        # Create soup object from link using requests and bs4

        # RIMI: Find links to all matching items
        if link == link_rimi:
            rimi_shop_links = []
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            soup = bs.BeautifulSoup(requests.get(link, headers=headers).text, features='html.parser')
            for d in soup.find_all('div', class_="js-product-container card -horizontal-for-mobile"):
                if item.lower() in unidecode(d['data-gtms-click-name'].lower()):
                    for a in d.find_all('a', class_="card__url js-gtm-eec-product-click"):
                        rimi_shop_links.append('https://www.rimi.ee' + a['href'])

        # PRISMA: Find links to all matching items
        elif link == link_prisma:
            prisma_shop_links = []
            browser = webdriver.Chrome(executable_path='chromedriver.exe')
            browser.get(link)
            soup = bs.BeautifulSoup(browser.page_source, features='html.parser')

            for a in soup.find_all('a', class_="js-link-item"):
                for div in a.find_all('div'):
                    for img in div.find_all('img'):
                        if item.lower() in unidecode(img['alt'].lower()):
                            prisma_shop_links.append('https://www.prismamarket.ee' + a['href'])

        # SELVER: Find links to all matching items
        elif link == link_selver:
            selver_shop_links = []
            browser = webdriver.Chrome(executable_path='chromedriver.exe')
            browser.get(link)
            sleep(5)
            soup = bs.BeautifulSoup(browser.page_source, features='html.parser')

            for a in soup.find_all('a', class_="ProductCard__link"):
                selver_shop_links.append('https://www.selver.ee' + a['href'])

    add_to_checklist = {item: {'Prisma': prisma_shop_links, 'Rimi': rimi_shop_links, 'Selver': selver_shop_links}}
    
    with open('items_to_check.txt', 'a') as f:
        f.write(str(add_to_checklist) + '\n')

    print('INFO: Added %s items from Prisma, %s items from Rimi and %s items from Selver to the list.' % (len(prisma_shop_links), len(rimi_shop_links), len(selver_shop_links)))


def get_all_items(): # Output all items from items_to_check.txt as a list
    output = []

    with open('items_to_check.txt', 'r') as f:
        for i in f.readlines():
            i = i.strip()
            if i != '':
                output.append(eval(i))
    return output

def get_product_info(link): # Read product name, price/l and alc. volume from Prisma, Rimi or Selver
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    name = ''
    price = ''
    volume = ''

    if 'rimi' in link:
        soup = bs.BeautifulSoup(requests.get(link, headers=headers).text, features='html.parser')
        
        for i in soup.find_all('h3', class_='name'):
            name = i.text.strip()
        
        for i in soup.find_all('p', class_='price-per'):
            i = i.text.strip().replace(' ', '').split('\n')
            price = float(i[0].replace('€/l', '').replace(',', '.').replace('€', ''))

        name_info = name.split(' ')
        for i in name_info:
            if '%' in i:
                volume = float(i.replace('%', '').replace('vol', '').replace(',', '.'))

    if 'prisma' in link:
        soup = bs.BeautifulSoup(requests.get(link, headers=headers).text, features='html.parser')
        
        for i in soup.find_all('h1', id='product-name'):
            name = i.text.strip()
        
        for i in soup.find_all('div', class_='details text-right'):
            i = i.text.strip().replace(' ', '').split('\n')
            price = float(i[2].replace('€/l', '').replace(',', '.'))

        for i in soup.find_all('div', class_='aisle'):
            i = i.text.strip().replace(' ', '').replace('\n', '').split(':')
            volume = float(i[len(i)-1].replace('%', ''))

    if 'selver' in link:
        browser = webdriver.Chrome(executable_path='chromedriver.exe')
        browser.get(link)
        soup = bs.BeautifulSoup(browser.page_source, features='html.parser')

        for i in soup.find_all('h1', class_='ProductName'):
            name = i.text.strip()

        for i in soup.find('span', class_='ProductPrice__unit-price'):
            price = float(i.strip().replace('€/l', '').replace(',', '.').replace(' ', ''))

        for i in soup.find('td', class_='ProductAttributes__value p0 pr30'):
            i = i.strip().split(' ')
            if '%' in i[1]:
                volume = float(i[1].replace('%', ''))

    return{'name': name, 'price': price, 'volume': volume}

def calculate_parmukoefitsient(item): # Calculates parmukoefitsient. Expects {'name': name, 'price': price, 'volume': volume} as parameter.
    return item['volume'] / item['price']

def get_best_offer(item): # Returns the best offer for the item, based on price per litre. #TODO: Test
    l = get_all_items()
    min_price = 10000

    for i in l:
        if item.lower() in list(i.keys()):
            for shop in i.values():
                for links in shop.values():
                    for link in links:
                        if get_product_info(link)['price'] < min_price:
                            min_price = get_product_info(link)['price']
                            best_offer = get_product_info(link)
    
    return best_offer

def get_cheapest_drink(): # Gets cheapest drink based on parmukoefitsient #TODO: Test
    l = get_all_items
    best_pk = 0
    
    for i in l:
        for shop in i.values():
            for links in shop.values():
                for link in links:
                    if get_product_info(link)['price'] > best_pk:
                        best_pk = get_product_info(link)['price']
                        best_offer = get_product_info(link)       

    return best_pk