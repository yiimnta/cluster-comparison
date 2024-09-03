import re
import json
import os
import io_utils as iou
import utils as ul
from enum import Enum
import jpype

class Tag(Enum):
    LOG_FILE = "log_file"
    EXPECTED_FILE = "expected_file"
    FULL_SCAN = "full_scan"
    VALUE = "value"
    TITLE = "title"
    TYPE = "type"
    CHILDREN = "children"
    DEBUG = "debug"
    XML = "xml"
    JSON = "json"
    DIAGRAM = "diagram"
    LOG = "log"
    EXPECTED = "expected"
    PATH = "path"
    ALL_MATCH = "all_match"
    COMPARISON = "comparison"
    WRITE_FILE = "write_file"

class Program:
    def __init__(self, settings: json, pattern: json):
        self.settings = settings
        self.pattern = pattern

    def analyse_data(self):
        if not os.path.exists(self.settings[Tag.LOG_FILE.value]):
            print(f"Log-File not found: {self.settings[Tag.LOG_FILE.value]}")
            return False

        if not os.path.exists(self.settings[Tag.EXPECTED_FILE.value]):
            print(f"Expect-File not found: {self.settings[Tag.EXPECTED_FILE.value]}")
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

    def print_data(self, data, con_tag, suffix): 
        if self.settings[Tag.XML.value][Tag.DEBUG.value] or self.settings[Tag.XML.value][con_tag]:
            xml_data = ul.dict_to_xml(data)
            if self.settings[Tag.XML.value][Tag.DEBUG.value]:
                print(xml_data)
            if self.settings[Tag.XML.value][con_tag]:
                ul.write_xml(xml_data,self.settings[Tag.XML.value][Tag.PATH.value], suffix)
        
        if self.settings[Tag.JSON.value][Tag.DEBUG.value] or self.settings[Tag.JSON.value][con_tag]:
            json_data = json.dumps(data)
            if self.settings[Tag.JSON.value][Tag.DEBUG.value]:
                print(json_data)
            if self.settings[Tag.JSON.value][con_tag]:
                ul.write_json(json_data,self.settings[Tag.JSON.value][Tag.PATH.value], suffix)
        
        if self.settings[Tag.DIAGRAM.value][con_tag]:
            if self.settings[Tag.DIAGRAM.value][con_tag]:
                ul.write_diagram(suffix, data, write_diagram_flag=self.settings[Tag.DIAGRAM.value][Tag.WRITE_FILE.value], folder_path=self.settings[Tag.DIAGRAM.value][Tag.PATH.value], suffix=suffix)

    def run(self):
        plantuml_jar_path = "./lib/plantuml-1.2024.6.jar"
        jpype.startJVM(classpath=[plantuml_jar_path])
        log_data = self.analyse_data()

        expected_data = iou.read_csv(self.settings[Tag.EXPECTED_FILE.value])
        result, notfound_comp, matched_comp, mismatched_comp = ul.compare_objects(log_data, expected_data, self.settings[Tag.ALL_MATCH.value], self.settings[Tag.DEBUG.value])
        self.print_data(log_data, Tag.LOG.value, "log_")
        self.print_data(expected_data, Tag.EXPECTED.value, "expected_")
        
        if self.settings[Tag.DIAGRAM.value][Tag.COMPARISON.value]:
            ul.write_diagram("result", log_data, self.settings[Tag.DIAGRAM.value][Tag.WRITE_FILE.value], notfound_comp, matched_comp, mismatched_comp, self.settings[Tag.DIAGRAM.value][Tag.PATH.value], "result_")
        jpype.shutdownJVM()
        return result


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
        "header": True,
        "full_scan": True,
        "all_match": True,
        "debug": True,
        "xml": {
            "debug": True,
            "log": True,
            "expected": True,
            "path": ""
        },
        "json": {
            "debug": True,
            "log": True,
            "expected": True,
            "path": ""
        },
        "diagram": {
            "log": True,
            "expected": True,
            "comparison": True,
            "write_file": True,
            "path": ""
        }
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