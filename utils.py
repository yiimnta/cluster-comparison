import xml.etree.ElementTree as ET
from dict2xml import dict2xml
from datetime import datetime
import os

def parse_value(str : str) -> (str | float):
    str = str.strip()
    if (str.startswith('"') and str.endswith('"')) or (str.startswith('\'') and str.endswith('\'')):
        return str[1:-1]
    elif str.replace(',', '').isdigit() or str.replace('.', '').isdigit():
        return float(str.replace(',', '.'))
    else:
        return str

def compare_objects(input_objs: dict, test_objs: dict, all=False, debug=False) -> bool:
    def compare_recursive(input_data, test_data, path=""):
        all_match = True
        mismatches = []

        if isinstance(test_data, dict) and isinstance(input_data, dict):
            for key in test_data:
                new_path = f"{path}[{key}]"
                if key in input_data:
                    match, mismatches_sub = compare_recursive(input_data[key], test_data[key], new_path)
                    all_match = all_match and match
                    mismatches.extend(mismatches_sub)
                else:
                    print(f"{new_path}: not found in INPUT.")
                    mismatches.append(new_path)
                    all_match = False
        else:
            if input_data != test_data:
                print(f"\033[31mFAIL::{path}: INPUT = '{input_data}', EXPECT = '{test_data}'\033[0m")
                mismatches.append(path)
                all_match = False
            elif debug:
                print(f"OK::::{path} = {test_data}")

        return all_match, mismatches

    all_match, mismatches = compare_recursive(input_objs, test_objs)

    if not all_match:
        print("TEST OK. BUT there are mismatches between INPUT and TEST.")

    return not all or all_match

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

def write_xml(xml_data, folder_path, suffix="", filename=""):
    doc = ET.fromstring(xml_data)
    tree = ET.ElementTree(doc)
    
    if not folder_path.endswith('/'):
        folder_path += '/'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    if filename.strip() == "":
        current_time = datetime.now()
        file_name = current_time.strftime("%Y%m%d_%H%M%S")

    file_path = os.path.join(folder_path, f"{suffix}{file_name}.xml")
    
    tree.write(file_path, encoding='utf-8', xml_declaration=True)
