import re
import os
import json
import copy
import csv
import xml.etree.ElementTree as ET
from dict2xml import dict2xml
from datetime import datetime

def parse_value(str : str) -> (str | float):
    str = str.strip()
    if (str.startswith('"') and str.endswith('"')) or (str.startswith('\'') and str.endswith('\'')):
        return str[1:-1]
    elif str.replace(',', '').isdigit() or str.replace('.', '').isdigit():
        return float(str.replace(',', '.'))
    else:
        return str


def parse_str2(str1):
    arr = re.findall(r'\[(.*?)\]', str1)
    return ' / '.join([f'"{x}"' for x in arr])


def compare_objects(input_objs: dict, test_objs: dict, all=False, debug=False) -> bool:
    one_match = False
    notfound_comp = []
    matched_comp = []
    mismatched_comp = []
    log_messages = []
    statistic_data = copy.deepcopy(test_objs)

    def compare_recursive(one_match, input_data, test_data, notfound_comp, matched_comp, mismatched_comp, path=""):
        all_match = True

        if isinstance(test_data, dict) and isinstance(input_data, dict):
            for key in test_data:
                new_path = f"{path}[{key}]"
                if key in input_data:
                    match = compare_recursive(one_match, input_data[key], test_data[key], notfound_comp, matched_comp, mismatched_comp, new_path)
                    all_match = all_match and match
                else:
                    print(f"{new_path}: not found in LOG.")
                    log_messages.append(f"{new_path}: not found in LOG.")
                    notfound_comp.append(new_path)
                    all_match = False
        else:
            if input_data != test_data:
                print(f"\033[31mFAIL::{path}: LOG = '{input_data}', EXPECTED = '{test_data}'\033[0m")
                log_messages.append(f"FAIL::{path}: LOG = '{input_data}', EXPECTED = '{test_data}'")
                mismatched_comp.append(f"{path}___(Log:{input_data})")
                all_match = False
            else:
                one_match = True
                matched_comp.append(path)
                log_messages.append(f"OK::::{path} = {test_data}")
                print(f"OK::::{path} = {test_data}")

        return all_match

    all_match = compare_recursive(one_match, input_objs, statistic_data, notfound_comp, matched_comp, mismatched_comp)

    if not all_match:
        print("\033[93mThere are mismatches between LOG and EXPECTED.\033[0m")
        log_messages.append("There are mismatches between LOG and EXPECTED.")

    return not all or all_match, log_messages, notfound_comp, matched_comp, mismatched_comp


def dict_to_xml(data: dict, wrap = "root", indent ="   ") -> ET.Element:
    return dict2xml(data, wrap, indent)


def validate_json_structure(data: dict, reference: dict, path="") -> bool:
    all_match = True

    for key in reference:
        current_path = f"{path}.{key}" if path else key
        if key not in data:
            print(f"Missing key: '{current_path}'")
            all_match = False
        else:
            if isinstance(reference[key], dict):
                if not isinstance(data[key], dict):
                    print(f"Type mismatch at '{current_path}': Expected dict, got {type(data[key]).__name__}")
                    all_match = False
                else:
                    all_match = all_match and validate_json_structure(data[key], reference[key], current_path)
            elif isinstance(reference[key], list):
                if not isinstance(data[key], list):
                    print(f"Type mismatch at '{current_path}': Expected list, got {type(data[key]).__name__}")
                    all_match = False
            else:
                if not isinstance(data[key], type(reference[key])):
                    print(f"Type mismatch at '{current_path}': Expected {type(reference[key]).__name__}, got {type(data[key]).__name__}")
                    all_match = False

    return all_match

def get_filename(folder_path, filename):
    if not folder_path.endswith('/'):
        folder_path += '/'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    if filename.strip() == "":
        current_time = datetime.now()
        filename = current_time.strftime("%Y%m%d_%H%M%S")
    
    return filename

def write_xml(xml_data, folder_path="./", suffix="", filename=""):
    doc = ET.fromstring(xml_data)
    tree = ET.ElementTree(doc)
    filename = get_filename(folder_path, filename)
    file_path = os.path.join(folder_path, f"{suffix}{filename}.xml")
    
    tree.write(file_path, encoding='utf-8', xml_declaration=True)


def write_json(json_data, folder_path="./", suffix="", filename=""):
    
    filename = get_filename(folder_path, filename)
    file_path = os.path.join(folder_path, f"{suffix}{filename}.json")
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)


def write_expected_file(data, folder_path='./', suffix="", filename=""):
    csv_data = []
    get_paths(data, result=csv_data)
    
    filename = get_filename(folder_path, filename)
    file_path = os.path.join(folder_path, f"{suffix}{filename}.csv")
    
    with open(file_path, 'w',  encoding='utf-8') as file:
        file.write("\n".join(csv_data))
 
def get_paths(data, result=[], current_path=''):
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path},{key}" if current_path else key
            get_paths(value, result, new_path)
    else:
        result.append(f"{current_path},{data}")
