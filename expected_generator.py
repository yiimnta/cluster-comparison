import os
import io_utils as iou
import utils as ul
from enum import Enum
from program import Program
import json

def main():
    settings_file_path = "./settings.json"
    pattern_file_path = "./pattern.json"

    if not os.path.exists(settings_file_path):
        print(f"Settings-File not found: {settings_file_path}")
        return

    if not os.path.exists(pattern_file_path):
        print(f"Pattern-File not found: {pattern_file_path}")
        return

    with open(settings_file_path, 'r') as file:
        settings = json.load(file)

    reference_structure = {
        "log_file":"",
        "expected_file":"",
        "search_pattern": "",
    }

    if ul.validate_json_structure(settings, reference_structure):
        
        with open(pattern_file_path, 'r') as file:
            pattern = json.load(file)

        program = Program(settings, pattern)
        program.export_expected_data()
        print("Generate successfully!")
    else:
        print("Settings-JSON structure is invalid.")

if __name__ == "__main__":
    main()