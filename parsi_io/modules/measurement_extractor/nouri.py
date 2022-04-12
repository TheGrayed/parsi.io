from __future__ import unicode_literals

import pandas as pd
import numpy as np
import re
from parsi_io.modules.number_extractor import NumberExtractor
from hazm import *

#loading units data and replacing "NaN" values with 0
units_dataframe = pd.read_csv("Units.csv",header=None)
units_dataframe = units_dataframe.replace(np.nan, 0)


# loading pre-unit words which are used in "pre-unit word + [decimal frachtion] + unit" pattern.
preunits_dataframe = pd.read_csv("PreUnitWords.csv",header=None)
preunits_dataframe = preunits_dataframe.transpose()


# loading pre-unit words which are used in "pre-unit word + [decimal frachtion] + unit" pattern.
decimal_fractions_dataframe = pd.read_csv("DecimalFractions.csv",header=None)
decimal_fractions_dataframe = decimal_fractions_dataframe.transpose()


#creating a dictionary of units which key corresponds quantity name and value corresponds list of units related to that quantity
units_dict = {}
for index, row in units_dataframe.iterrows():
    qunantity_name = row[0]
    quantity_units = row[1:].tolist()
    #removing 0 values
    quantity_units = list(filter(lambda a: a != 0, quantity_units))
    units_dict [qunantity_name] = quantity_units


#joining all units sorted by length in descending order
all_units = []
for key, value in units_dict.items():
    all_units += value
sorted_units = sorted(all_units, key=len, reverse = True)
sorted_units_joined = "|".join(sorted_units)


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


def extract_noun_phrases(input_str):
    tagger = POSTagger(model='resources/postagger.model')
    chunker = Chunker(model='resources/chunker.model')
    tagged = tagger.tag(word_tokenize(input_str))
    phrases = tree2brackets(chunker.parse(tagged))
    chunks = re.split('] ', phrases)
    noun_phrases = []
    pharases_span = []
    for i in range(len(chunks)):
        t = ()
        m = re.search('.*NP',chunks[i][1:])
        if m != None:
            match = m.group()
            np = match[:-3]
            t += (input_str.find(np), input_str.find(np)+len(np))
            pharases_span.append(t)
            noun_phrases.append(np)
    return noun_phrases, pharases_span



# a function that gets the unit and returns corresponding quantity type in persian
def get_quantity_type(unit):
    for key, value in units_dict.items():
        if unit in value:
            return quantity_name_translator[key]
    return 0


# We don't need this function anymore.
# a function that joins all units with or ("|") 
def join_all_units_with_or():
    units_joined = ""
    for key, value in units_dict.items():
        units_joined += "|".join(value)
        units_joined += "|"
    return units_joined[:-1]



"""
A function that detects quantities which follow "amount + unit" pattern.
"""

extractor = NumberExtractor()
def match_amount_unit_pattern (input_str):
    nphrases,np_s = extract_noun_phrases(input_str)

    values = extractor.run(input_str)
    phrase_amount_dict = {}
    for value in values:
        phrase_amount_dict[value['phrase']] = value['value'] 
    phrases_joined = "|".join(phrase_amount_dict.keys())
        
    all_matches = re.findall(f'({phrases_joined})+\s*({sorted_units_joined})+',input_str)
    i = 0
    output = [{} for sub in range(len(all_matches))]
    for match in re.finditer(f'({phrases_joined})+\s*({sorted_units_joined})+',input_str):
        #comment to be added :)) 
        marker = match.group()
        j=0
        span = match.span()
        for s in np_s: 
            if s[0]<=match.span()[0] and s[1]>=match.span()[1]:
                start = match.span()[0]
                end = s[1]
                marker = input_str[start:end]
                span = (start, end)
            j+=1

        output[i]['type'] = get_quantity_type(all_matches[i][1])
        output[i]['amount'] = phrase_amount_dict[all_matches[i][0]]
        output[i]['unit'] = all_matches[i][1]
        output[i]['item'] = marker.replace(match.group(),'')
        output[i]['marker'] = marker
        output[i]['span'] = span
        
        i += 1
        
    return output


"""
A function that detects quantities which follow "pre-unit words such as "چند" + 
                                                [decimal fractions (ده-صد-هزار و ...)] + 
                                                unit" pattern.
"""
def match_preunit_decimal_unit_pattern(input_str):
    units_joined = join_all_units_with_or()
    preunits_list = preunits_dataframe.values.tolist()
    preunits_joined = "|".join(preunits_list[0])
    
    decimal_fractions_list = decimal_fractions_dataframe.values.tolist()
    decimal_fractions_joined = "|".join(decimal_fractions_list[0])
    all_matches = re.findall(f'({preunits_joined})+\s*({decimal_fractions_joined})?\s*({units_joined})+',input_str)
    i = 0
    output = [{} for sub in range(len(all_matches))]
    for match in re.finditer(f'({preunits_joined})+\s*({decimal_fractions_joined})?\s*({units_joined})+',input_str):
        output[i]['type'] = get_quantity_type(all_matches[i][2])
        output[i]['amount'] = ''
        output[i]['unit'] = all_matches[i][2]
        output[i]['marker'] = match.group()
        output[i]['span'] = match.span()
        i += 1
        
    return output


# amount + unit examples:
input1 = "دو کیلوگرم آرد خرید . یک ساعت صبر کرد."
print(match_amount_unit_pattern(input1))

input2 = "۲ گیگا بایت اینترنت رایگان گرفت"
print(match_amount_unit_pattern(input2))

input4 = "باتری خود را هشتاد و پنج صدم وات شارژ کرد."
print(match_amount_unit_pattern(input4))

input5 = "علی سه کیلوگرم آرد را خرید"
print(match_amount_unit_pattern(input5))

input6 = "سه مثقال طلا خرید و فروخت."
print(match_amount_unit_pattern(input6))


# test cases:
t1 = "علی ۳.۵ کیلوگرم آرد خرید و باتری خود را هشتاد و پنج صدم وات شارژ کرد."
print(match_amount_unit_pattern(t1))

t2 = "شهاب سنگی به تندی ۱۵ km/s وارد جو زمین شد."
print(match_amount_unit_pattern(t2))

# t3 = "یک خودرو با سرعت زیاد از ما سبقت گرفت"


# buggy examples:
# in b1, it doesn't get نان as an item.
b1 = 'سه کیلوگرم نان را خورد و باتری خود را هشتاد و پنج صدم وات شارژ کرد.'
print(match_amount_unit_pattern(b1))

b2 = "علی سه کیلوگرم آرد خرید"
print(match_amount_unit_pattern(b2))


# pre-unit word + [decimal fraction] + unit examples:
#input3 = "چند صد هزار تن گوشت وارداتی"
#print(match_preunit_decimal_unit_pattern(input3))

