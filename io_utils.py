from pathlib import Path
import utils as ul
import csv
from collections import defaultdict
import xml.etree.ElementTree as ET
from xml.dom import minidom

def read_log(file_path) -> str:
    text = Path(file_path).read_text(encoding="utf8")

    if text.strip() == "":
        print("content not found")
        return ""
    
    return text

def read_csv(file_path: str) -> dict:
    data_objects = {}

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or len(row) < 2:
                continue

            keys = row[:-1]
            value = ul.parse_value(row[-1].strip())
            keys_len = len(keys)

            current_level = data_objects
            for key in keys:
                key = key.strip()
                keys_len = keys_len - 1
                if key not in current_level:
                    if keys_len == 0:
                        current_level[key] = value
                    else:
                        current_level[key] = {}
                current_level = current_level[key]
    
    return data_objects
