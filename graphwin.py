import sys
import json
import os
import sys
import re
import jpype
import jpype.imports
import copy
import utils as ul
from PyQt5.QtWidgets import ( 
    QTabBar, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QTextEdit, QSplitter, QListWidgetItem,
    QMainWindow, QGraphicsScene, QGraphicsView, QToolButton,
    QSpacerItem, QSizePolicy, QFileDialog, QPushButton, QVBoxLayout, 
    QFrame, QWidget, QScrollArea, QLineEdit, QHBoxLayout, QSpacerItem,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon, QPen
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtCore import QSize
from datetime import datetime
from enum import Enum
from functools import partial

class ComparisonType(Enum):
    NOTFOUND = 0
    MATCHED = 1
    MISS = 2

class ItemType(Enum):
    VALUE = 0
    MAIN = 1

class SidebarMenu(QWidget):
    def __init__(self, data):
        super().__init__()

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        
        self.item_frames = []

        self.analyse_data(data)

        self.layout.addStretch()
        content_widget.setLayout(self.layout)

        scroll_area.setWidget(content_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.create_search_buttons_layout())
        main_layout.addWidget(scroll_area)

    def create_search_buttons_layout(self):
        search_and_buttons_layout = QVBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")
 #       self.search_bar.textChanged.connect(self.filter_items)
        
        button_layout = QHBoxLayout()
        self.collapse_all_button = QPushButton("Collapse All")
        self.expand_all_button = QPushButton("Expand All")
        self.reset_search_button = QPushButton("Reset Search")
        
        for button in [self.collapse_all_button, self.expand_all_button, self.reset_search_button]:
            button.setFixedSize(100, 30)

        button_layout.addWidget(self.collapse_all_button)
        button_layout.addWidget(self.expand_all_button)
        button_layout.addWidget(self.reset_search_button)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        
        search_and_buttons_layout.addWidget(self.search_bar)
        search_and_buttons_layout.addLayout(button_layout)
        return search_and_buttons_layout
        
    def analyse_data(self, data, parent_layout=None):
        
        if parent_layout == None:
            layout = self.layout
        else:
            layout = parent_layout
        
        for key, value in data.items():
            if key == "type":
                continue

            if isinstance(value, dict):
                if "value" in value:
                    value_item = self.create_item_button(f"{key} = {value['value']}", ItemType.VALUE, [ComparisonType.NOTFOUND.value] if "type" not in value else value["type"])
                    layout.addWidget(value_item)
                else:
                    item_frame = QFrame()
                    item_frame.setStyleSheet("""
                        padding: 0 0 0 0 ;
                        margin: 0 0 0 0 ;
                    """)
                    main_item_type = value.get("type", [ComparisonType.NOTFOUND.value])
                    main_item = self.create_item_button(key, ItemType.MAIN, main_item_type)

                    layout.addWidget(main_item)
                    layout.addWidget(item_frame)
                    main_item.clicked.connect(partial(self.toggle_visibility, item_frame))
                    
                    sub_layout = QVBoxLayout(item_frame)
                    sub_layout.setContentsMargins(20, 0, 0, 0)
                    self.analyse_data(value, sub_layout)
                    self.item_frames.append(item_frame)
            else:
                value_item = self.create_item_button(f"{key} = {value}", ItemType.VALUE, [ComparisonType.NOTFOUND.value])
                layout.addWidget(value_item)

    def toggle_visibility(self, item_frame):
        if item_frame:
            item_frame.setVisible(not item_frame.isVisible())

    def create_item_button(self, text, type: ItemType, messages_types=[]):
        icon = QIcon(self.create_multiple_circle_icon(messages_types))
        button = QPushButton(text)
        button.setIcon(icon)
        button.setIconSize(QSize(40, 10))

        if type == ItemType.MAIN:
            button.setCheckable(True)
            
            button.setStyleSheet("""
                text-align: left;
                padding: 8px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F5F5F5, stop:1 #E0E0E0);
                color: #333333;
                font-weight: bold;
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                margin:0px;
            """)
        elif type == ItemType.VALUE:
            button.setStyleSheet("""
                text-align: left; 
                padding: 5px; 
                margin-left: 10px; 
                background-color: #F5F5F5;  
                color: #555555;
                border: none;
                border-radius: 5px;
            """)

        return button

    def create_multiple_circle_icon(self, messages_types):
        pixmap = QPixmap(40, 10)
        pixmap.fill(QColor('transparent'))
        painter = QPainter(pixmap)

        for  index, type in enumerate(messages_types):
            if type == ComparisonType.MATCHED.value:
                painter.setBrush(QColor("green"))
            elif type == ComparisonType.NOTFOUND.value:
                painter.setBrush(QColor("yellow"))
            elif type == ComparisonType.MISS.value:
                painter.setBrush(QColor("red"))
            painter.setPen(QPen(QColor('gray'), 1)) 
            painter.drawEllipse(index * 13, 0, 10, 10)

        painter.end()

        return pixmap

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
    def __init__(self, title, dict_data, expected_data, head_split_into_tab= False, write_diagram_flag= False, log_messages = [], notfound_comp=[], matched_com=[], mismatched_comp=[], folder_path="./", suffix="", filename=""):
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
        statistic_tree = self.create_statistic_tree(expected_data, notfound_comp, matched_com, mismatched_comp)
        
        icon_path = "./icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 1200, 800)

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

        self.views = []
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
        
        self.add_tab_statistic(statistic_tree, names=missmatched_tab, messages=log_messages)

        uml_data = f"@startjson\n{style}\n{highlight_header}\n{json.dumps(dict_data)}\n@endjson"
        img_data = self.convert_uml_to_img(uml_data, write_diagram_flag, folder_path, "All", suffix)
        self.add_tab("All", img_data)
        self.offset = 2
        if len(missmatched_tab) > 0:
            self.set_error_tab(- 1)
        
        if head_split_into_tab and len(dict_data) > 1:
            for index, tab in enumerate(dict_data):
                uml_data = f"@startjson\n{style}\n{highlight_header}\n{json.dumps({tab:dict_data[tab]})}\n@endjson"
                img_data = self.convert_uml_to_img(uml_data, write_diagram_flag, folder_path, tab, suffix)
                self.add_tab(tab, img_data)
                if tab in missmatched_tab:
                    self.set_error_tab(index)

    def set_error_tab(self, index):
        self.custom_tab_bar.set_tab_color(index + self.offset, QColor('#e62c70'), QColor('#ffffff'))

    def add_tab_statistic(self, statistic_tree, names=[], messages=[]):
        tab = QWidget()
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        list_widget = QListWidget()
        for name in names:
            QListWidgetItem(name, list_widget)
        
        console = QTextEdit()
        console.setReadOnly(True)
        console.setText("\n".join(messages))
        splitter.addWidget(list_widget)
        splitter.addWidget(console)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 10)

        sidebar = SidebarMenu(statistic_tree)
        layout.addWidget(splitter)
        layout.addWidget(sidebar)
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Statistic")
        list_widget.itemClicked.connect(lambda item: self.on_item_clicked(item))

    def on_item_clicked(self, item):
        self.search_tab_by_text(item.text().lower())

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
        
        zoom_in_button = QToolButton(self)
        zoom_in_button.setText("Zoom in")
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_refresh_button = QToolButton(self)
        zoom_refresh_button.setText("refresh")
        zoom_refresh_button.clicked.connect(self.zoom_refresh)
        zoom_out_button = QToolButton(self)
        zoom_out_button.setText("Zoom out")
        zoom_out_button.clicked.connect(self.zoom_out)
        save_button = QToolButton(self)
        save_button.setText("Save image")
        save_button.clicked.connect(self.save_view)
        
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)

        button_layout.addWidget(zoom_in_button)
        button_layout.addWidget(zoom_refresh_button)
        button_layout.addWidget(zoom_out_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        layout.addWidget(graphics_view)
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, name)
        self.views.append(graphics_view)

    def zoom_in(self):
        current_index = self.tab_widget.currentIndex() - 1
        if current_index >= 0:
            current_view = self.views[current_index]
            current_view.scale(1.1, 1.1)

    def zoom_out(self):
        current_index = self.tab_widget.currentIndex() - 1
        if current_index >= 0:
            current_view = self.views[current_index]
            current_view.scale(0.9, 0.9) 
    
    def zoom_refresh(self):
        current_index = self.tab_widget.currentIndex() - 1
        if current_index >= 0:
            current_view = self.views[current_index]
            current_view.resetTransform()
    
    def save_view(self):
        current_index = self.tab_widget.currentIndex() - 1
        if current_index >= 0:
            current_view = self.views[current_index]

            file_path, _ = QFileDialog.getSaveFileName(self, "Save image", "", "PNG Files (*.png)")
            if file_path:
                rect = current_view.viewport().rect()
                pixmap = QPixmap(rect.size())
                painter = QPainter(pixmap)
                current_view.render(painter)
                painter.end()
                pixmap.save(file_path)

    def search_tab(self):
        search_text = self.search_bar.text().lower()
        self.search_tab_by_text(search_text)

    def search_tab_by_text(self, search_text):
        for i in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(i).lower()
            if search_text in tab_name:
                self.tab_widget.setCurrentIndex(i)
                break

    def generate_highlight_header(self, arr, style=""):
        converted_lines = []
        head = {}
        for item in arr:
            if style == "<<mismatched>>":
                item = item.split("___")[0]
            elements = re.findall(r'\[(.*?)\]', item)
            head[elements[0]]=""
            formatted_string = ' / '.join([f'"{element}"' for element in elements])
            converted_line = f"#highlight {formatted_string} {style}\n"
            converted_lines.append(converted_line)

        return ''.join(converted_lines), head
    
    def create_statistic_tree(self, expected_data, notfound_comp=[], matched_com=[], mismatched_comp=[]):
        statistic_data = copy.deepcopy(expected_data)

        for path in matched_com:
            self.set_value_by_path(statistic_data, path, ComparisonType.MATCHED)

        for path in notfound_comp:
            self.set_value_by_path(statistic_data, path, ComparisonType.NOTFOUND)
        
        for path in mismatched_comp:
            self.set_value_by_path(statistic_data, path, ComparisonType.MISS)

        return self.convert_type_to_list(statistic_data)
    
    def set_value_by_path(self, data, path, comType: ComparisonType):
        if comType == ComparisonType.MISS:
            values = path.split("___")
            path = values[0]
            log_value = values[1]
        elements = re.findall(r'\[(.*?)\]|\[(\d+)\]', path)
        
        keys = [key if key else int(index) for key, index in elements]
        
        d = data
        vd = data
        for key in keys[:-1]:
            if key in d:
                d = d[key]
                if isinstance(d, dict):
                    vd = vd[key]
            else:
                return
        
        final_key = keys[-1]
        if isinstance(d, dict):
            if final_key in d:
                if isinstance(d[final_key], dict):
                    d[final_key]["type"] = comType.value
                else:
                    if comType == ComparisonType.MISS:
                        d[final_key] = {"value": f"{d[final_key]}  {log_value}", "type": comType.value}
                    else:
                        d[final_key] = {"value": d[final_key], "type": comType.value}
    
    def convert_type_to_list(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'type' and isinstance(value, int):
                    data[key] = [value]
                elif isinstance(value, dict):
                    self.convert_type_to_list(value)

            if 'type' not in data:
                types = set()
                for key, value in data.items():
                    if isinstance(value, dict) and 'type' in value and isinstance(value['type'], list):
                        types.update(value['type'])
                if types:
                    data['type'] = list(types)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                self.convert_type_to_list(item)
        return data
                
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