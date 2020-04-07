# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 16:35:51 2020

@author: danie
"""

import pandas as pd
import re

data = pd.read_csv('listings_df.csv')

#drop residual index from csv
data.drop(data.columns.values[0], axis = 1, inplace = True)

#function to get numbers from string
def get_nums(cell):
    match = re.search('[0-9.,]+', cell)
    if match:
        return match.group()
    else:
        return 'No Info'

#create list of columns to convert to number
num_list = ['rooms', 'beds', 'bath', 'sqft', 'price/ft']
for col in num_list:
    data[col] = data[col].apply(get_nums)

#characters to remove from list of items
remove_list = ['[', ']', "'"]

amenities_list = []

unique_amenities = set()
max_len = 0

for pack in data['amenities'].values.tolist():
    new_pack = pack
    for char in remove_list:
        new_pack = new_pack.replace(char, '')
    unpack = new_pack.split(',')
    unpack = [item.strip() for item in unpack if item.strip() and'google' not in item]
    
    max_len = max(max_len, len(unpack))
    for item in unpack:
        unique_amenities.add(item)
for item in unique_amenities:
    if not 'NYC Storm' in item:
        amenities_list.append(item)


for item in amenities_list:
        data[item] = data.apply(lambda x: item in x['amenities'], axis = 1)

mapping_df = pd.read_csv('neighborhoods_grouped.csv')
map_dict = dict(zip(mapping_df['old'], mapping_df['new']))

data[amenities_list] = data[amenities_list].astype(int)

data['Neighborhood'] = data['Neighborhood'].replace(map_dict)

data.to_csv('data_cleaned.csv')