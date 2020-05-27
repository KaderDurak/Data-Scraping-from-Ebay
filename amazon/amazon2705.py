# -*- coding: utf-8 -*-
"""
Created on Wed May 27 18:11:25 2020

@author: kader
"""

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument(r"user-data-dir=C:\Users\kader\AppData\Local\Google\Chrome\User Data")
#options.headless = True
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\kader\Desktop\amazon\chromedriver.exe')

def req_engine(url):
    driver.get(url)
    print(url)
    return driver.page_source

#DATA ACQUISITION FUNCTION for More-Sellers products
def data_acquisition(url_for_func):
    print('Collecting data from table page')
    price_list = []
    condition_list = []
    seller_list = []
    
    #for page no:1
    url = url_for_func[:51] + 'ref=olp_page_1?ie=UTF8&f_all=true&startIndex=00'
    print('Page number: 1')
    response=req_engine(url)
    soup=BS(response, features="lxml") 
    child_list = [3,5,7,9,12,14,16,18,20,22]
    for i in child_list:
        try:
            price_list.append(soup.select('.olpOffer:nth-child({}) .olpOfferPrice'.format(str(i)))[0].get_text().strip())
        except:
            price_list.append(np.nan)  
        try:
            condition_list.append(soup.select('.olpOffer:nth-child({}) .olpCondition'.format(str(i)))[0].get_text().strip())
        except:
            condition_list.append(np.nan)
        try:
            seller_list.append(soup.select('.olpOffer:nth-child({}) .a-text-bold a'.format(str(i)))[0].get_text().strip())
        except:
            seller_list.append(np.nan)
            
    #for page no>1  
    for i in range(2,100):      
        
        url = url_for_func[:51] + 'ref=olp_page_{}?ie=UTF8&f_all=true&startIndex={}0'.format(str(i), str(i-1))
        response=req_engine(url)
        soup=BS(response, features="lxml") 
        table_content = soup.select('.a-padding-small')[0].get_text().strip()    
        url_previous = url_for_func[:51] + 'ref=olp_page_{}?ie=UTF8&f_all=true&startIndex={}0'.format(str(i-1), str(i-2))
        response_previous=req_engine(url_previous)
        soup_previous=BS(response_previous, features="lxml") 
        table_content_previous = soup_previous.select('.a-padding-small')[0].get_text().strip()
        
        print('Page number: ', i)
        if table_content != table_content_previous:
            print('the page table contents are not same')
            
            child_list = [3,5,7,9,12,14,16,18,20,22]
            for i in child_list:
                try:
                    price_list.append(soup.select('.olpOffer:nth-child({}) .olpOfferPrice'.format(str(i)))[0].get_text().strip())
                except:
                    price_list.append(np.nan)  
                try:
                    condition_list.append(soup.select('.olpOffer:nth-child({}) .olpCondition'.format(str(i)))[0].get_text().strip())
                except:
                    condition_list.append(np.nan)
                try:
                    seller_list.append(soup.select('.olpOffer:nth-child({}) .a-text-bold a'.format(str(i)))[0].get_text().strip())
                except:
                    seller_list.append(np.nan)
        else:
            print('The page table contents are same. Go to next product..')
            break
            
    df = pd.DataFrame(list(zip(price_list, condition_list, seller_list)), columns= ['Price', 'Condition', 'Seller']) 
    
    try:
        product_name=soup.select("#olpProductDetails .a-spacing-none")[0].get_text().strip()
    except:
        product_name = np.nan
    df['ProductName'] = product_name  
    
    try:
        brand = soup.select('#olpProductByline')[0].get_text().strip()
    except:
        brand = np.nan
    df['Brand'] = brand
    
    try:
        Feature1Name = soup.select('.a-spacing-micro:nth-child(1) .a-size-base:nth-child(1)')[0].get_text().strip()
        Feature1 = soup.select('.a-spacing-micro:nth-child(1) .a-text-bold')[0].get_text().strip()
    except:
        Feature1Name = np.nan
        Feature1 = np.nan
    df['Feature1Name'] = Feature1Name
    df['Feature1'] = Feature1
    
    try:
        Feature2Name = soup.select('.a-spacing-small+ .a-spacing-micro .a-size-base:nth-child(1)')[0].get_text().strip()
        Feature2 = soup.select('.a-spacing-small+ .a-spacing-micro .a-text-bold')[0].get_text().strip()
    except:
        Feature2Name = np.nan
        Feature2 = np.nan
    df['Feature2Name'] = Feature2Name
    df['Feature2'] = Feature2  
    
    return df

links = {'https://www.amazon.de/s?k=robotic+vacuum+cleaner&page=':20}
df_main = pd.DataFrame(columns = ['Price', 'Condition', 'Seller', 'ProductName', 'Brand',
                                 'Feature1Name', 'Feature1', 'Feature2Name', 'Feature2'])
for link in links.keys():
    for pn in range(1, links[link]+1):
        url_main = link + str(pn)
        print(url_main)
        response_main=req_engine(url_main)
        soup_main=BS(response_main, features="lxml")
        a = soup_main.select('a.a-link-normal.a-text-normal')
        url_link_list = []
        for i in a:
            url_link = 'https://www.amazon.de' + i['href']
            url_link_list.append(url_link)
        url_link_list = list(dict.fromkeys(url_link_list))
        for url_link in url_link_list:
            print(url_link, 'url_link')
            try:
                response_link=req_engine(url_link)
                soup_link=BS(response_link, features="lxml")
                source_codes = ['a#buybox-see-all-buying-choices-announce.a-button-text', 
                                '#olpDiv a', 
                                'a.a-touch-link.a-box.olp-touch-link', 
                                '#availability a', 
                                '#olpLinkWidget_feature_div .a-box-inner',
                               '#olpLinkWidget_feature_div .a-color-price',
                               '#olp-upd-new-used .a-link-normal',
                               '#alternativeOfferEligibilityMessaging_feature_div a']
                url_link_in_link_list = []
                print('Searching source codes...')
                for s in source_codes:
                    try:
                        b = soup_link.select(s)
                        if b != []:

                            for i in b:
                                url_link_in_link = 'https://www.amazon.de' + i['href']
                                url_link_in_link_list.append(url_link_in_link) 
                            print('full link')
                        else:
                            print('empty link')
                    except:
                        pass
                print(url_link_in_link_list, 'url_link_in_link_list')
                if len(url_link_in_link_list) != 0:
                    url_link_in_link = url_link_in_link_list[0]
                    print(url_link_in_link, 'url_link_in_link')
                    try:
                        response_link_in_link=req_engine(url_link_in_link)

                        soup_link_in_link=BS(response_link_in_link, features="lxml")
                        response_link_in_link_in_link=req_engine(url_link_in_link)
 
                        soup=BS(response_link_in_link_in_link, features="lxml")
                        print('there are links in url_link_in_link')
                        #for product specifications:
                        q = soup.select('ul.a-unordered-list.a-nostyle.a-button-list.a-declarative.a-button-toggle-group.a-horizontal.a-spacing-small')
                        #first feature 
                        list_f1 = []
                        for i in q[0]:
                            for j in i:
                                for k in j:
                                    for l in k:
                                        for p in l:
                                                list_f1.append(p)
                        url_feature_1 = []
                        for i in list_f1:
                            try:
                                url_feature_1.append(i['href'])
                            except:
                                pass
                        for i in url_feature_1:
                            url_detail = 'https://www.amazon.de' + i
                            try:
                                response_detail=req_engine(url_detail)

                                soup_detay=BS(response_detail, features="lxml")
                                q = soup_detay.select('ul.a-unordered-list.a-nostyle.a-button-list.a-declarative.a-button-toggle-group.a-horizontal.a-spacing-small')
                                #second feature
                                list_f2 = []
                                for n in q[1]:
                                    for j in n:
                                        for k in j:
                                            for l in k:
                                                for p in l:
                                                        list_f2.append(p)
                                                        url_feature_2 = []
                                                        for i in list_f2:
                                                            try:
                                                                url_feature_2.append(i['href'])
                                                            except:
                                                                pass
                                for i in url_feature_2:
                                    url_in_detail = 'https://www.amazon.de' + i
                                    url_for_func = url_in_detail

                                    df_main = df_main.append(data_acquisition(url_for_func))
                                    print(url_in_detail[:51], 'url_double_feature')
                            except:
                                url_for_func = url_detail
                                df_main = df_main.append(data_acquisition(url_for_func))
                                print(url_detail[:51], 'url_single_feature')
                    except:
                        url_for_func = url_link_in_link
                        df_main = df_main.append(data_acquisition(url_for_func))
                        print(url_link_in_link[:51], 'url_no_feature')
                else:
                    #url_for_func = url_link
                    #df_main = df_main.append(data_acq_for_one_seller(url_for_func))
                    print('one seller')
            except:
                print('no product link')
