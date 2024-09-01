import re
import json
import os
import io_utils as iou
import utils as ul
from enum import Enum

class Tag(Enum):
    LOG_FILE = "log_file"
    EXPECT_FILE = "expect_file"
    FULL_SCAN = "full_scan"
    VALUE = "value"
    TITLE = "title"
    TYPE = "type"
    CHILDREN = "children"
    DEBUG = "debug"
    XML_OUTPUT = "xml_output"
    LOG = "log"
    TEST = "test"
    PATH = "path"
    ALL_MATCH = "all_match"

class Program:
    def __init__(self, settings: json, pattern: json):
        self.settings = settings
        self.pattern = pattern

    def analyse_data(self):
        if not os.path.exists(self.settings[Tag.LOG_FILE.value]):
            print(f"Log-File not found: {self.settings[Tag.LOG_FILE.value]}")
            return False

        if not os.path.exists(self.settings[Tag.EXPECT_FILE.value]):
            print(f"Expect-File not found: {self.settings[Tag.EXPECT_FILE.value]}")
            return False

        log_objects = {}
        log_text = iou.read_log(self.settings[Tag.LOG_FILE.value])
        
        obj_clusters = re.findall(self.pattern[Tag.VALUE.value], log_text, re.DOTALL)

        if not obj_clusters:
            print(f"{self.pattern[Tag.TITLE.value]} cluster not found")
            return {}
        
        self.read_pattern(self.pattern, obj_clusters, log_objects)
        
        return log_objects

        
    def read_pattern(self, pattern, data_objects: dict, output_objects: dict):
        if pattern[Tag.TYPE.value] == "data":
            for cluster, _ in data_objects:
                id_data = cluster.strip().split('=')
                if len(id_data) != 2:
                    continue
                output_objects[id_data[0].strip()] = ul.parse_value(id_data[1].strip())
        else:
            if len(pattern[Tag.CHILDREN.value]) == 0:
                return
            for obj_id, obj_content in data_objects:
                if obj_id not in output_objects:
                    output_objects[obj_id] = {}
                for child in pattern[Tag.CHILDREN.value]:
                    child_clusters = re.findall(child[Tag.VALUE.value], obj_content, re.DOTALL)
                    if not child_clusters:
                        if not self.settings[Tag.FULL_SCAN.value]:
                            del output_objects[obj_id]
                        continue
                    self.read_pattern(child, child_clusters, output_objects[obj_id])

    def run(self):
        log_data = self.analyse_data()
        if self.settings[Tag.DEBUG.value] or self.settings[Tag.XML_OUTPUT.value][Tag.LOG.value]:
            xml_data = ul.dict_to_xml(log_data)
            if self.settings[Tag.DEBUG.value]:
                print(xml_data)
            if self.settings[Tag.XML_OUTPUT.value][Tag.LOG.value]:
                ul.write_xml(xml_data,self.settings[Tag.XML_OUTPUT.value][Tag.PATH.value], suffix="log_")
        
        expected_data = iou.read_csv(self.settings[Tag.EXPECT_FILE.value])
        if self.settings[Tag.DEBUG.value] or self.settings[Tag.XML_OUTPUT.value][Tag.LOG.value]:
            xml_data = ul.dict_to_xml(expected_data)
            if self.settings[Tag.DEBUG.value]:
                print(xml_data)
            if self.settings[Tag.XML_OUTPUT.value][Tag.LOG.value]:
                ul.write_xml(xml_data,self.settings[Tag.XML_OUTPUT.value][Tag.PATH.value], suffix="expected_")

        return ul.compare_objects(log_data, expected_data, self.settings[Tag.ALL_MATCH.value], self.settings[Tag.DEBUG.value])


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
        "log_file": "",
        "expect_file": "",
        "pattern": "",
        "header": True,
        "full_scan": True,
        "xml_output": {
            "log": True,
            "test": True,
            "path": ""
        },
        "all_match": True,
        "debug": True
    }

    if ul.validate_json_structure(settings, reference_structure):
        
        with open(pattern_file_path, 'r') as file:
            pattern = json.load(file)

        program = Program(settings, pattern)
        if program.run() == True:
            print("Test successfully!")
    else:
        print("Settings-JSON structure is invalid.")

if __name__ == "__main__":
    main()