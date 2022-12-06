import bs4 as bs
import requests
from selenium import webdriver
from time import sleep
# - - - - -

def add_item_to_list(item): # Search for item on Prisma, Selver, Rimi
    link_prisma = "https://www.prismamarket.ee/products/search/" + item
    link_rimi = "https://www.rimi.ee/epood/ee/otsing?query=" + item
    link_selver = "https://www.selver.ee/search?q=" + item
    
    for link in [link_prisma, link_rimi, link_selver]:
        # Create soup object from link using requests and bs4

        # RIMI: Find links to all matching items
        if link == link_rimi:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            soup = bs.BeautifulSoup(requests.get(link, headers=headers).text, features='html.parser')
            rimi_shop_links = []
            for d in soup.find_all('div', class_="js-product-container card -horizontal-for-mobile"):
                if item in d['data-gtms-click-name']:
                    for a in d.find_all('a', class_="card__url js-gtm-eec-product-click"):
                        rimi_shop_links.append('https://www.rimi.ee' + a['href'])

        elif link == link_prisma:
            prisma_shop_links = []
            browser = webdriver.Chrome(executable_path='chromedriver.exe')
            browser.get(link)
            soup = bs.BeautifulSoup(browser.page_source, features='html.parser')

            for a in soup.find_all('a', class_="js-link-item"):
                for div in a.find_all('div'):
                    for img in div.find_all('img'):
                        if item in img['alt']:
                            prisma_shop_links.append('https://www.prismamarket.ee' + a['href'])

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
