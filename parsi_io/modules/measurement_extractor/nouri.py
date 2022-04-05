import pandas as pd
import numpy as np

#loading units data and replacing "NaN" values with 0
units_dataframe = pd.read_csv("Units.csv",header=None)
units_dataframe = units_dataframe.replace(np.nan, 0)


#creating a dictionary of units which key corresponds quantity name and value corresponds list of units related to that quantity
units_dict = {}
for index, row in units_dataframe.iterrows():
    qunantity_name = row[0]
    quantity_units = row[1:].tolist()
    #removing 0 values
    quantity_units = list(filter(lambda a: a != 0, quantity_units))
    units_dict [qunantity_name] = quantity_units


#a dictionary to map qunatity's name from english to farsi
quantity_name_translator = {
    "length": "طول",
    "mass": "وزن",
    "pressure": "فشار",
    "volume": "حجم",
    "temperature": "دما",
    "area":"مساحت",
    "speed":"سرعت",
    "force":"نیرو",
    "energy":"انرژی",
    "power":"توان",
    "torque":"گشتاور",
    "time":"زمان",
    "density":"چگالی",
    "frequency":"فرکانس",
    "degree":"زاویه",
    "acceleration":"شتاب",
    "debi":"شارش جرمی",
    "debi-v":"شارش حجمی",
    "data-storage":"ذخیره دیجیتال",
    "data-transfer":"انتقال داده"    
}



#a function that gets the unit and returns corresponding quantity type in persian
def get_quantity_type(unit):
    for key, value in units_dict.items():
        if unit in value:
            return quantity_name_translator[key]
    return 0



#a function that joins all units with or ("|") 
def join_all_units_with_or():
    units_joined = ""
    for key, value in units_dict.items():
        units_joined += "|".join(value)
        units_joined += "|"
    return units_joined[:-1]



"""
This minimal code detects quantities which follow "amount + unit" pattern.
"""

import re
from parsi_io.modules.number_extractor import NumberExtractor

extractor = NumberExtractor()
def match_amount_unit_pattern (input_str):
    values = extractor.run(input_str)
    phrase_amount_dict = {}
    for value in values:
        phrase_amount_dict[value['phrase']] = value['value'] 
    phrases_joined = "|".join(phrase_amount_dict.keys())
    
    units_joined = join_all_units_with_or()
    
    all_matches = re.findall(f'({phrases_joined})+\s*({units_joined})+',input_str)
    i = 0
    output = [{} for sub in range(len(all_matches))]
    for match in re.finditer(f'({phrases_joined})+\s*({units_joined})+',input_str):
        output[i]['type'] = get_quantity_type(all_matches[i][1])
        output[i]['amount'] = phrase_amount_dict[all_matches[i][0]]
        output[i]['unit'] = all_matches[i][1]
        output[i]['marker'] = match.group()
        output[i]['span'] = match.span()
        i += 1
        
    return output

input1 = "علی سه متر پارچه و دو کیلوگرم آرد خرید و یک ساعت صبر کرد."
input2 = "2 Gb"

print(match_amount_unit_pattern(input1))
print(match_amount_unit_pattern(input2))

#bug: the first pattern gets mathced. not the longest.
print(match_amount_unit_pattern("دو فوت بر ثانیه"))

