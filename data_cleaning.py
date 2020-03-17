# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 16:35:51 2020

@author: danie
"""

import pandas as pd
import re

data = pd.read_csv('listings_df.csv')
data.drop(data.columns.values[0], axis = 1, inplace = True)

def get_nums(cell):
    match = re.search('[0-9.,]+', cell)
    if match:
        return match.group()
    else:
        return 'No Info'

num_list = ['rooms', 'beds', 'bath', 'sqft', 'price/ft']
for col in num_list:
    data[col] = data[col].apply(get_nums)

remove_list = ['[', ']', "'"]
unique_amenities = set()
max_len = 0
for pack in data['amenities'].values.tolist():
    new_pack = pack
    for char in remove_list:
        new_pack = new_pack.replace(char, '')
    unpack = new_pack.split(',')
    unpack = [item.strip() for item in unpack if 'google' not in item]
    max_len = max(max_len, len(unpack))
    for item in unpack:
        unique_amenities.add(item)