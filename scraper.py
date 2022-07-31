from queue import PriorityQueue
import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from random import choice
import re
import pandas as pd


def search_amazon(product, total_products_count):
    try:

        dealslist = []
        word_list = product.replace(' ', '+')
        url = 'https://www.amazon.com/s?k=' + word_list

        def getdata(url):

            # Define headers for request
            headers = { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
                'Accept-Language' : 'en-US,en;q=0.5',
                'Accept-Encoding' : 'gzip', 
                'DNT' : '1', # Do Not Track Request Header 
                'Connection' : 'close'
            }
            response = requests.get(url, headers=headers).text

            soup = BeautifulSoup(response, 'lxml')
            return soup

        def getdeals(soup):
            item_div = soup.find_all('div', {'data-component-type': 's-search-result'})
            item_div = item_div + soup.find_all('div', {'cel_widget_id': 'MAIN-SEARCH_RESULTS-2'})
                        
            for item in item_div:
                #Getting item name
                item_name = item.find('a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}).text.strip()
                
                #Getting item rating
                try:
                    item_rating = item.find('span', {'class': 'a-icon-alt'}).text.strip()
                except:
                    item_rating = 'Not Available'
                                
                #Getting item price
                try:
                    item_price = float(item.find('span', {'class': 'a-price'}).find('span',{'class':'a-offscreen'}).text.replace('$','').replace(',','').strip())
                    old_price = float(item.find('span', {'class': 'a-price a-text-price'}).find('span',{'class':'a-offscreen'}).text.replace('$','').replace(',','').strip())
                except:
                    old_price = float(item.find('span',{'class':'a-offscreen'}).text.replace('$','').replace(',','').strip())

                percentoff = round((100 - ((item_price / old_price) * 100)),2)

                #Getting item link
                item_link = item.find('a', {'class': 'a-link-normal'})
                item_link = "".join(['https://www.amazon.com', item_link['href']])

                saleitem = {
                    'item_name': item_name,
                    'item_rating': item_rating,
                    'item_price': item_price,
                    'old_price': old_price,
                    'percentoff': percentoff,
                    'item_link': item_link         
                }

                dealslist.append(saleitem)

            return
        
        reached_last_page = False

        def getnextpage(soup): 
            pages = soup.find('ul', {'class': 'a-pagination'})   
            if not pages.find('li', {'class': 'a-disabled a-last'}):
                url = 'https://www.amazon.com' + str(pages.find('li', {'class': 'a-last'}).find('a')['href'])
                return url
            else:
                reached_last_page = True
                return 

        try:
            while reached_last_page == False:
                soup = getdata(url)
                getdeals(soup)
                url = getnextpage(soup)
      
        except:
            print('Blocked')
        
        df = pd.DataFrame(dealslist)
        df = df.sort_values(by='percentoff',ascending=False, ignore_index=True)
        
        amazon_products_data = defaultdict(dict)
        
        for x in range(total_products_count):
            amazon_products_data[x]['item_name'] = df.at[x,'item_name']
            amazon_products_data[x]['item_rating'] = df.at[x,'item_rating']
            amazon_products_data[x]['item_price'] = str(df.at[x,'item_price'])
            amazon_products_data[x]['old_price'] = str(df.at[x,'old_price'])
            amazon_products_data[x]['percentoff'] = str(df.at[x,'percentoff'])
            amazon_products_data[x]['item_link'] = df.at[x,'item_link']

        return(amazon_products_data)

    except Exception as e:
        # Could not fetch data from Amazon
        return {}

def search_ebay(product, total_products_count):
    try:

        dealslist = []
        word_list = product.replace(' ', '+')
        url = 'https://www.ebay.com/sch/i.html?_nkw=' + word_list

        def getdata(url):

            # Define headers for request
            headers = { 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
                'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
                'Accept-Language' : 'en-US,en;q=0.5',
                'Accept-Encoding' : 'gzip', 
                'DNT' : '1', # Do Not Track Request Header 
                'Connection' : 'close'
            }
            response = requests.get(url, headers=headers)

            soup = BeautifulSoup(response.content, 'lxml')
            return soup

        def getdeals(soup):
            item_div = soup.find_all('li', {'class': 's-item s-item__pl-on-bottom s-item--watch-at-corner'})

            for item in item_div:
                #Getting item name
                item_name = item.find('a', {'class': 's-item__link'}).find('h3',{'class':'s-item__title'}).text.strip()

                #Getting item price
                item_price = item.find('span',{'class':'s-item__price'}).text.strip()
                try:
                    item_price_lower_range = float(item_price.split('t')[0].replace('$','').replace(',','').strip())
                except:
                    item_price_lower_range = float(item_price.replace('$','').replace(',',''))
                                
                #Getting item link
                item_link = item.find('a', {'class': 's-item__link'})['href']
                
                saleitem = {
                    'item_name': item_name,
                    'item_price': item_price,
                    'item_price_lower_range': item_price_lower_range,
                    'item_link': item_link      
                }

                dealslist.append(saleitem)

            return

        reached_last_page = False

        def getnextpage(soup,curr_url): 
            pages = soup.find('nav', {'class': 'pagination'})
            next_page_url = pages.find('a', {'class': 'pagination__next'})['href']
            if next_page_url != curr_url:
                return next_page_url
            else:
                reached_last_page = True
                return

        try:
            while reached_last_page == False or x in range(2):
                soup = getdata(url)
                getdeals(soup)
                curr_url = url
                url = getnextpage(soup,curr_url)
                x += 1
      
        except:
            print('Blocked')

        df = pd.DataFrame(dealslist)
        df = df.sort_values(by='item_price_lower_range',ascending=True, ignore_index=True)
        
        ebay_products_data = defaultdict(dict)
        
        for x in range(total_products_count):
            ebay_products_data[x]['item_name'] = df.at[x,'item_name']
            ebay_products_data[x]['item_price'] = df.at[x,'item_price']
            ebay_products_data[x]['item_link'] = df.at[x,'item_link']

        return(ebay_products_data)
        

    except Exception as e:
        # Could not fetch data from Ebay
        return {}
