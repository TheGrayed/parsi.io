"""
This minimal code detects quantities which follow "keyword + amount" pattern.
Units are limited to "متر","ضلع"
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
    
    keywords = ["طول","ضلع"]
    keywords_joined = "|".join(keywords)
    
    all_matches = re.findall(f'({keywords_joined})+\s*({phrases_joined})+',input_str)
    
    i = 0
    output = [{} for sub in range(len(all_matches))]
    for match in re.finditer(f'({keywords_joined})+\s*({phrases_joined})+',input_str):
        output[i]['unit'] = ""#all_matches[i][1]
        output[i]['amount'] = phrase_amount_dict[all_matches[i][1]]
        output[i]['marker'] = match.group()
        output[i]['span'] = match.span()
        i += 1
        
    return output

input_str = "خانه اتاقی به ضلع 4 و حیاطی با طول 12 دارد"
print(match_amount_unit_pattern(input_str))