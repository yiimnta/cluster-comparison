from pathlib import Path
import utils as ul
import csv

def read_log(file_path):
    text = Path(file_path).read_text(encoding="utf8")

    if text.strip() == "":
        print("content not found")
        return ""
    
    return text

def read_csv(file_path):
    data = []
    
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            data.append(row)
    
    data_objects = {}

    for obj in data:
        if obj['RowID'] not in data_objects:
            data_objects[obj['RowID']] = {}
        data_objects[obj['RowID']][obj['DataID']] = ul.parse_value(obj['Value'])

    return data_objects
