import pandas as pd 
from dotenv import load_dotenv
import os

load_dotenv("n.env")
URL = os.environ['URL']

def get_StudentData():
   data = (pd.read_csv(URL)).to_dict()
   rows = []
   for i in range(len(data['OSIS'])):
        row = {}
        for key in data:
            value = data[key].get(i)
            row[key] = value
       # Skip mostly empty rows
        if sum(v is not None and v != 'n' for v in row.values()) >= 3:
            rows.append(row)

   return rows

if __name__ == "__main__":
    print(get_StudentData())