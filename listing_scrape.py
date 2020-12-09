# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 11:34:17 2020

@author: danie
"""

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import os
import re


def clean_listing(apt_dict):
    def get_nums(cell):
        match = re.search('[0-9.,]+', cell)
        if match:
            return match.group()
        else:
            return 'No Info'

    num_list = ['rooms', 'beds', 'bath', 'sqft', 'price/ft']
    for col in num_list:
        apt_dict[col] = get_nums(apt_dict[col])


def scrape_listing(file_path):
    """
    Input: file path

    Output: row for SQL database
    """
    soup = bs(open(file_path, 'rb').read(), 'lxml')
    apt = {}
    apt['file_name'] = file_path
    # get title of listing
    if soup.find_all('meta', attrs={'name': 'title'}):
        apt['title'] = soup.find_all('meta',
                                     attrs={'name': 'title'})[0]['content']

    # get address
    address_selector = 'article.right-two-fifths > section > h1 > a'
    if soup.select(address_selector):
        apt['address'] = soup.select(address_selector)[0].text

    # get description (for reference)
    apt['desc'] = [tag['content'] for tag in
                   soup.find_all('meta',
                                 attrs={'property': 'og:description'})]

    # get url
    apt['url'] = [tag['content'] for tag in
                  soup.find_all('meta',
                                attrs={'property': 'og:url'})]
    if apt['url']:
        apt['url'] = apt['url'][0]
    else:
        apt['url'] = apt['url']

    # get geographic data
    apt['coord'] = [tag['content'] for tag in
                    soup.find_all('meta',
                                  attrs={'name': 'ICBM'})]

    state_temp = [tag['content'] for tag in
                  soup.find_all('meta',
                                attrs={'name': 'geo.region'})]
    if state_temp:
        apt['state'] = state_temp[0]
    else:
        apt['state'] = state_temp

    # get main listing details
    price_selector = 'div.details > div.details_info_price > div.price'
    if soup.select(price_selector):
        apt['price'] = re.search('[0-9.,]+',
                                 soup.select(price_selector)[0].text).group()
    avail_selector = 'article.left-three-fifths > section > div > div > div'
    for tag in soup.select(avail_selector):
        if 'avail' in tag.text: apt['availibility'] = tag.text
        if 'contract' in tag.text: apt['availibility'] = tag.text
        if 'days' in tag.text: apt['days on market'] = tag.text
        if 'today' in tag.text: apt['days on market'] = tag.text

    details = {}

    for tag in soup.select('div.details_info > span'):
        if 'room' in tag.text: details['rooms'] = tag.text
        if 'bed' in tag.text: details['beds'] = tag.text
        if 'bath' in tag.text: details['bath'] = tag.text
        if 'ft' in tag.text and 'per' not in tag.text:
            details['sqft'] = tag.text
        elif 'per' in tag.text:
            details['price/ft'] = tag.text

    nghbr_selector = 'div.details_info > span.nobreak > a'
    if soup.select(nghbr_selector):
        details['Neighborhood'] = soup.select(nghbr_selector)[0].text

    for detail in ['rooms', 'beds', 'bath',
                   'sqft', 'price/ft', 'Neighborhood']:
        if detail not in details.keys():
            details[detail] = 'No Info'
        apt[detail] = details[detail]
    apt['details'] = details

    amenities_selector = ('section.DetailsPage-contentBlock '
                          '> div.AmenitiesBlock > ul > li > div > div.Text')
    apt['amenities'] = [tag.text.strip() for tag in
                        soup.select(amenities_selector)]
    amenities_selector = ('section.DetailsPage-contentBlock > '
                          'div.AmenitiesBlock > ul > li.AmenitiesBlock-item')
    apt['amenities'].extend([tag.text.strip() for tag in
                             soup.select(amenities_selector)
                             if tag.text.strip()])
    subway_selector = ('div.full > section > div.Nearby > div.Nearby-half > '
                       'div.Nearby-transportation > ul > '
                       'li.Nearby-transportationItem')
    subway_tags = soup.select(subway_selector)
    subway_list = []
    for tag in subway_tags:
        lines_dict = {}
        lines_dict['lines'] = [letter for letter in
                               tag.text.strip().split('\n')
                               if len(letter) == 1]
        if tag.select('span > b'):
            lines_dict['distance'] = tag.select('span > b')[0].text
        if tag.select('span.Text'):
            lines_dict['station'] = tag.select('span.Text')[0].text
            lines_dict['station'] = lines_dict['station'].strip().split('\n')
        subway_list.append(lines_dict)
    apt['subway'] = subway_list
    for tag in soup.select('div.BuildingInfo > div.BuildingInfo-item > span.BuildingInfo-detail'):
        att_list = ['Units', 'Stories', 'Built']
        for att_name in att_list:
            if att_name in tag.text:
                apt['Building-' + att_name] = tag.text
    for amenity in apt['amenities']:
        apt[amenity] = 1
    return apt


if __name__ == '__main__':
    html_list = [f for f in os.listdir(r'C:\Users\Daniel\PycharmProjects\WebScraping\htmls')
                 if os.path.isfile(os.path.join(r'C:\Users\Daniel\PycharmProjects\WebScraping\htmls', f))]

    dictionary_rows = []
    counter = 0