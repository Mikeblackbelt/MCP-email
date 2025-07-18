import pandas as pd 
from dotenv import load_dotenv
import os
import student_grouper

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

def filter_out(*
               , includeRACE: list[str] = None, includeGPA_RANGE: list[list[int]] = None, includeGENDER: list[str] = None, include_INCOME_RANGE: list[list[int]] = None,includeGrade: list[int] = None,
                  excludeRACE: list[str] = None, excludeGPA_RANGE: list[list[int]] = None, excludeGENDER: list[str] = None, exclude_INCOME_RANGE: list[list[int]] = None, excludeGrade: list[int] = None,
                  student_data: list[dict] = get_StudentData()):
        """RACISM FUNCTION"""
        #student_data = get_StudentData()
        valid_student_data = []
        for student in student_data:
            if not (
                (includeRACE is not None and student['Race'] not in includeRACE) or
                (includeGrade is not None and student['Grade'] not in includeGrade) or
                (includeGENDER is not None and student['Gender'] not in includeGENDER) or 
                (include_INCOME_RANGE is not None and not any([R[0] <= student['Income'] <= R[1] for R in include_INCOME_RANGE])) or
                (includeGPA_RANGE is not None and not any([R[0] <= student['GPA'] <= R[1] for R in includeGPA_RANGE])) or
                (excludeRACE is not None and student['Race'] in excludeRACE) or
                (excludeGPA_RANGE is not None and any([R[0] <= student['GPA'] <= R[1]] for R in excludeGPA_RANGE)) or
                (excludeGENDER is not None and student['Gender'] in excludeGENDER) or
                (exclude_INCOME_RANGE is not None and any([R[0] <= student['Income'] <= R[1] for R in exclude_INCOME_RANGE])) or
                (excludeGrade is not None and student['Grade'] in excludeGrade)
                ): valid_student_data.append(student)
        return valid_student_data
          
def get_Interest(interest: str, *, student_data: list[dict] = get_StudentData(), categories: int = 3):
     data = []
     for student in student_data:
            if interest in student_grouper.map_student_to_interest(
                 student['Major'],
                 student['Interests'],
                 student['Career Path'],
                 numCategories=categories): 
                
                data.append(student)
     return data
   

if __name__ == "__main__":
    print(get_StudentData())