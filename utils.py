import re
import os
import sys
import json
import jpype
import jpype.imports
import xml.etree.ElementTree as ET
from dict2xml import dict2xml
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtGui import QPixmap
from pygments import highlight


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
                    notfound_comp.append(new_path)
                    all_match = False
        else:
            if input_data != test_data:
                print(f"\033[31mFAIL::{path}: LOG = '{input_data}', EXPECTED = '{test_data}'\033[0m")
                mismatched_comp.append(path)
                all_match = False
            elif debug:
                one_match = True
                matched_comp.append(path)
                print(f"OK::::{path} = {test_data}")

        return all_match

    all_match = compare_recursive(one_match, input_objs, test_objs, notfound_comp, matched_comp, mismatched_comp)

    if not all_match:
        print("\033[93mTEST OK. BUT there are mismatches between LOG and EXPECTED.\033[0m")

    return not all or all_match, notfound_comp, matched_comp, mismatched_comp


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


def write_json(json_data, folder_path, suffix="", filename=""):
    
    if not folder_path.endswith('/'):
        folder_path += '/'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    if filename.strip() == "":
        current_time = datetime.now()
        file_name = current_time.strftime("%Y%m%d_%H%M%S")

    file_path = os.path.join(folder_path, f"{suffix}{file_name}.json")
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

def generate_highlight_header(arr, style=""):
    converted_lines = []
    for item in arr:
        elements = re.findall(r'\[(.*?)\]', item)
        formatted_string = ' / '.join([f'"{element}"' for element in elements])
        converted_line = f"#highlight {formatted_string} {style}\n"
        converted_lines.append(converted_line)

    return ''.join(converted_lines)


def write_diagram(title, dict_data, write_diagram_flag= False, notfound_comp=[], matched_com=[], mismatched_comp=[], folder_path="./", suffix="", filename=""):

    style = """
    <style>
        .notfound {
            BackGroundColor yellow
            FontColor black
        }
        .mismatched {
            BackGroundColor red
            FontColor white
        }
    </style>
    """

    notfound_highlight_header = generate_highlight_header(notfound_comp, "<<notfound>>")
    matched_highlight_header = generate_highlight_header(matched_com)
    missmatched_highlight_header = generate_highlight_header(mismatched_comp, "<<mismatched>>")
    highlight_header= f"{notfound_highlight_header}\n{matched_highlight_header}\n{missmatched_highlight_header}"
    
    uml_data = f"@startjson\n{style}\n{highlight_header}\n{json.dumps(dict_data)}\n@endjson"
    
    SourceStringReader = jpype.JClass('net.sourceforge.plantuml.SourceStringReader')
    reader = SourceStringReader(uml_data)
    ByteArrayOutputStream = jpype.JClass('java.io.ByteArrayOutputStream')
    output = ByteArrayOutputStream()
    reader.generateImage(output)
    image_data = output.toByteArray()
    image_bytes = bytes(image_data)
    byte_array = QByteArray(image_bytes)
    
    if write_diagram_flag:
        if not folder_path.endswith('/'):
            folder_path += '/'

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        if filename.strip() == "":
            current_time = datetime.now()
            file_name = current_time.strftime("%Y%m%d_%H%M%S")

        file_path = os.path.join(folder_path, f"{suffix}{file_name}.png")
        
        with open(file_path, "wb") as f:
            f.write(image_bytes)

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle(title)
    window.setGeometry(100, 100, 1200, 800)

    pixmap = QPixmap()
    pixmap.loadFromData(byte_array)

    scene = QGraphicsScene()
    scene.addPixmap(pixmap)

    graphics_view = QGraphicsView(scene)
    graphics_view.setRenderHint(QPainter.Antialiasing)
    graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
    graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
    graphics_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
    graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    window.setCentralWidget(graphics_view)

    window.show()
    app.exec_()
