import json
import pandas as pd

templates = open('data.json')

print(templates)

text = ""
with open("data.json", "r") as file1:
    # итерация по строкам
    for line in file1:
        text += line

print(text[43:-2])

#d = templates['features']
ndf = json.loads(text[43:-2])

print(ndf)
#df = pd.DataFrame.from_dict(ndf)
#df
#print(df)
#for section, commands in templates.items():
#    print(section)
