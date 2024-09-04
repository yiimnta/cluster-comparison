import sys
import json
import os
import sys
import re
from PyQt5.QtWidgets import QTabBar, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QApplication, QLabel, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QByteArray
import jpype
import jpype.imports
from datetime import datetime

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_colors = {}

    def set_tab_color(self, index, bg_color, text_color):
        self.tab_colors[index] = bg_color
        self.text_color = text_color
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        for index, color in self.tab_colors.items():
            rect = self.tabRect(index)
            painter.setPen(Qt.black)
            painter.setBrush(color)
            painter.drawRect(rect)
            painter.setPen(self.text_color)
            painter.drawText(rect, Qt.AlignCenter, self.tabText(index))

class GraphWindow(QMainWindow):
    def __init__(self, title, dict_data, head_split_into_tab= False, write_diagram_flag= False, notfound_comp=[], matched_com=[], mismatched_comp=[], folder_path="./", suffix="", filename=""):
        super().__init__()
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
        notfound_highlight_header, _ = self.generate_highlight_header(notfound_comp, "<<notfound>>")
        matched_highlight_header, _ = self.generate_highlight_header(matched_com)
        missmatched_highlight_header, missmatched_tab  = self.generate_highlight_header(mismatched_comp, "<<mismatched>>")
        highlight_header= f"{notfound_highlight_header}\n{matched_highlight_header}\n{missmatched_highlight_header}"
   
   
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tabs...")
        self.search_bar.textChanged.connect(self.search_tab)

        self.tab_widget = QTabWidget()
        
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                padding: 10px 15px;
            }
        """)

        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(self.tab_widget)
        self.custom_tab_bar = CustomTabBar(self.tab_widget)
        self.tab_widget.setTabBar(self.custom_tab_bar)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        if write_diagram_flag:
            current_time = datetime.now()
            folder_name = current_time.strftime("%Y%m%d_%H%M%S")

            if not folder_path.endswith('/'):
                folder_path += '/'

            folder_path = f"{folder_path}{folder_name}/"

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                
        uml_data = f"@startjson\n{style}\n{highlight_header}\n{json.dumps(dict_data)}\n@endjson"
        img_data = self.convert_uml_to_img(uml_data, write_diagram_flag, folder_path, "All", suffix)
        self.add_tab("All", img_data)
        
        if head_split_into_tab and len(dict_data) > 1:
            for index, tab in enumerate(dict_data):
                uml_data = f"@startjson\n{style}\n{highlight_header}\n{json.dumps({tab:dict_data[tab]})}\n@endjson"
                img_data = self.convert_uml_to_img(uml_data, write_diagram_flag, folder_path, tab, suffix)
                self.add_tab(tab, img_data)
                if tab in missmatched_tab:
                    self.custom_tab_bar.set_tab_color(index + 1, QColor('#e62c70'), QColor('#ffffff'))

    def add_tab(self, name, img_data):
        tab = QWidget()
        layout = QVBoxLayout()
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)

        graphics_view = QGraphicsView(scene)
        graphics_view.setRenderHint(QPainter.Antialiasing)
        graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        graphics_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(graphics_view)
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, name)

    def search_tab(self):
        search_text = self.search_bar.text().lower()
        for i in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(i).lower()
            if search_text in tab_name:
                self.tab_widget.setCurrentIndex(i)
                break
    
    def generate_highlight_header(self, arr, style=""):
        converted_lines = []
        head = {}
        for item in arr:
            elements = re.findall(r'\[(.*?)\]', item)
            head[elements[0]]=""
            formatted_string = ' / '.join([f'"{element}"' for element in elements])
            converted_line = f"#highlight {formatted_string} {style}\n"
            converted_lines.append(converted_line)

        return ''.join(converted_lines), head
    
    def convert_uml_to_img(self, uml_data, write_diagram_flag= False, folder_path="./", filename="", suffix=""):
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
                filename = current_time.strftime("%Y%m%d_%H%M%S")

            file_path = os.path.join(folder_path, f"{suffix}{filename}.png")
            
            with open(file_path, "wb") as f:
                f.write(image_bytes)

        return byte_array
    