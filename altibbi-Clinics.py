from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json
import pandas as pd
import csv
import pickle
import logging
import requests


print("")

def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--verbose")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920, 1200")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--enable-javascript")
    driver = webdriver.Chrome(options=options)
    return driver


def get_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
                     
    }
    return headers

url = "https://altibbi.com/%D8%A7%D9%84%D8%AF%D9%84%D9%8A%D9%84-%D8%A7%D9%84%D8%B7%D8%A8%D9%8A/%D8%AC%D9%85%D9%8A%D8%B9-%D8%A7%D9%84%D8%AF%D9%88%D9%84/%D8%AC%D9%85%D9%8A%D8%B9-%D8%A7%D9%84%D9%85%D8%AF%D9%86/%D8%B9%D9%8A%D8%A7%D8%AF%D8%A7%D8%AA/%D8%AC%D9%85%D9%8A%D8%B9-%D8%A7%D9%84%D8%AA%D8%AE%D8%B5%D8%B5%D8%A7%D8%AA?per-page=10&page={}"
links = []
def get_list(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    results = []
    try:
        for i in soup.find_all('div', class_='doctor-location-details'):
            #print(i)
            results.append(i.find('a')['href'])
        return results
    except Exception as e:
       print(e)
       return results
    
    

for i in range(1,7):
    links.extend(get_list(url.format(i)))
print(links[:3])
#print(len(links))

baseUrl = "https://altibbi.com"

# Get the main extion of any given page an return a soup
def get_html(url, xpaths):
    headers = get_headers()

    driver = web_driver()

    driver.get(url)  
    time.sleep(2)

    try:
        try:
            name = BeautifulSoup(driver.find_element(By.XPATH,xpaths[0] ).get_attribute('innerHTML'), 'html.parser')
        except:
            print("nameError")
            name = ""
        try:
            phone = BeautifulSoup(driver.find_element(By.XPATH,xpaths[1] ).get_attribute('innerHTML'), 'html.parser')

        except:
            print("phoneError")
            phone = ""
        try:
            data = BeautifulSoup(driver.find_element(By.XPATH,xpaths[2] ).get_attribute('innerHTML'), 'html.parser')
        except:
            print("dataError")
            data = ""
        try:
            title = BeautifulSoup(driver.find_element(By.XPATH,xpaths[3] ).get_attribute('innerHTML'), 'html.parser')
        except:
            print("titleError")
            title = ""       
            
    except Exception  as e:
        pass
    soups =[name, phone,data,title]
    driver.quit()
    return soups

      #  logging.warning(f"getHtml error for {url}: {e}")
        

clinic_dic_list = []
### scrape_item_data_selenium
# Define the XPath expressions for each data field
ITEM_NAME_XPATH = '//*[@id="right-side"]/section[1]/div[1]/div[1]/div/div/div/h1'
PHONE_XPATH = '//*[@id="right-side"]/section[1]/div[4]/div/div[2]/div[2]/a'
DATA_XPATH = '//*[@id="working-title"]'
TITLE_XPATH = '//*[@id="right-side"]/section[1]'


def scrape_item_data(url):
    """This function takes a URL of an item page and returns a dictionary of scraped data."""

    item_name_xpath = """//*[@id="right-side"]/section[1]/div[1]/div[1]/div/div/div/h1"""
    phone_xpath = """//*[@id="right-side"]/section[1]/div[4]/div/div[2]/div[2]/a"""
    data_xpath = """//*[@id="working-title"]"""
    title_xpath = """//*[@id="right-side"]/section[1]"""
    xpaths = [item_name_xpath, phone_xpath, data_xpath, title_xpath]
    soups = get_html(url,xpaths )
    # Initialize an empty dictionary to store the scraped data
    info_dict = {}

    # Try to get the title soup from the title xpath
    try:
        title_soup = soups[0]
    except Exception as e:
        logging.error(f"Failed to get title soup from {url}: {e}")
        return info_dict

    # Try to get the item name from the item name xpath
    try:
        info_dict["title"] = soups[0].text.strip()
        print(info_dict["title"])
    except Exception as e:
        logging.error(f"Failed to get item name from {url}: {e}")
        return info_dict

    # Try to get the specialty from the title soup
    try:
        specialty = soups[3].find('h2', {'class': 'specialities'}).text.strip()
        info_dict['specialty'] = specialty
    except AttributeError:
        logging.warning(f"No specialty found for {url}")
        info_dict['specialty'] = ""

    # Try to get the location from the title soup
    try:
        location = soups[3].find('p', {'class': 'city font-bold'}).text.strip()
        info_dict['location'] = location
    except AttributeError:
        logging.warning(f"No location found for {url}")
        info_dict['location'] = ""

    # Try to get the phone number from the phone xpath or the data xpath
    try:
        phone_number = soups[1]
        if phone_number:
            info_dict["phone_number"] = phone_number            
        else:
            phone_number = soups[2].find_all('span', {'itemprop': 'telephone'})[0].text.strip()
            info_dict["phone_number"] = phone_number
    except Exception as e:
        logging.warning(f"No phone number found for {url}: {e}")
        info_dict["phone_number"] = ""

    # Try to get the address information from the data xpath
    try:
        address1 = soups[2].find('div', {'id': 'about_address_1'}).find_all('div')[1].text.strip()
        address2 =soups[2].find_all('div', {'class': 'row mb-10'})[1].find_all('div')[1].text.strip()
        info_dict['address'] = f"{address1}, {address2}"
    except Exception as e:
        logging.warning(f"No address found for {url}: {e}")
        info_dict['address'] = ""

    # Try to get the email from the data xpath
    try:
        email = soups[2].find('div', {'itemprop': 'email'}).find("a").get("href").split(':')[1]
        info_dict['email'] = email
    except Exception as e:
        logging.warning(f"No email found for {url}: {e}")
        info_dict['email'] = ""

    return info_dict


for clinic in links:
    url = baseUrl+clinic
    print("<<<<<<< {} >>>>>>".format(url))
    clinic_dic_list.append(scrape_item_data(url))
    with open('clinic_dic_list.pickle', 'wb') as f:
        pickle.dump(clinic_dic_list, f)
    print(len(clinic_dic_list))
    
    
df = pd.DataFrame(clinic_dic_list)
df.to_csv("clinic_dic_list.csv")