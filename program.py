import re
import io_utils as iou
import utils as ul
import xml.etree.ElementTree as ET

class Program:
    def __init__(self, row_pattern, data_pattern, log_filepath, csv_filepath, all_match = False):
        self.row_pattern = row_pattern
        self.data_pattern = data_pattern
        self.log_filepath = log_filepath
        self.csv_filepath = csv_filepath
        self.all_match = all_match

    def run(self):
        input_text = iou.read_log(self.log_filepath)

        # using re.findall to find all clusters
        matches = re.findall(self.row_pattern, input_text, re.DOTALL)

        if not matches:
            print("Not found any cluster")
            return
        
        input_objects = {}

        for section_id, section_content in matches:
            data_clusters = data_pattern.findall(section_content)

            if len(data_clusters) == 0:
                continue
            
            if section_id not in input_objects:
                input_objects[section_id] = {}

            # reading data cluster
            for cluster, _ in data_clusters:
                
                id_data = cluster.strip().split('=')
                if len(id_data) != 2:
                    break

                input_objects[section_id][id_data[0]] = ul.parse_value(id_data[1].strip())

        test_objects = iou.read_csv(self.csv_filepath)
        
        return ul.compare_objects(input_objects, test_objects, all_match)

row_pattern = r"#ATSBEGIN-([^\n]+)\n(.*?)#ATSEND-\1"
data_pattern = re.compile(r'#ATD-([^\n]+)(.*?)\n')
log_filepath = '.\data\data.log'
csv_filepath = '.\data\\testdata.csv'
all_match = True

program = Program(row_pattern, data_pattern, log_filepath, csv_filepath, all_match)
if program.run() == True:
    print("Test successfully!")
