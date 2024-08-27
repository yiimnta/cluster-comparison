import re
import io_utils as iou
import utils as ul
import xml.etree.ElementTree as ET

class Program:
    def __init__(self, log_filepath, csv_filepath, all_match = False, debug = False):
        
        self.log_filepath = log_filepath
        self.csv_filepath = csv_filepath
        self.all_match = all_match
        self.debug = debug

    def read_data(self):
        log_articles = {}
        article_pattern = r"#ATABEGIN-([^\n]+)\n(.*?)#ATAEND-\1"
        section_pattern = r"#ATSBEGIN-([^\n]+)\n(.*?)#ATSEND-\1"
        data_pattern = r'#ATD-([^\n]+)(.*?)\n'

        input_text = iou.read_log(self.log_filepath)
        # using re.findall to find all clusters
        articles_clusters = re.findall(article_pattern, input_text, re.DOTALL)

        if not articles_clusters:
            print("Article cluster not found")
            return {}

        for article_id, article_content in articles_clusters:
            section_clusters = re.findall(section_pattern, article_content, re.DOTALL)

            if len(section_clusters) == 0:
                continue
            
            if article_id not in log_articles:
                log_articles[article_id] = {}

            # reading section clusters
            for section_id, section_content in section_clusters:
                data_clusters = re.findall(data_pattern, section_content, re.DOTALL)

                if len(data_clusters) == 0:
                    continue
                
                if section_id not in log_articles[article_id]:
                    log_articles[article_id][section_id] = {}

                # reading data cluster
                for cluster, _ in data_clusters:
                    
                    id_data = cluster.strip().split('=')
                    if len(id_data) != 2:
                        continue

                    log_articles[article_id][section_id][id_data[0]] = ul.parse_value(id_data[1].strip())

        return log_articles

    def run(self):
        log_articles = self.read_data()
        test_articles = iou.read_csv(self.csv_filepath)

        return ul.compare_objects(log_articles, test_articles, self.all_match, self.debug)

log_filepath = '.\data\data.log'
csv_filepath = '.\data\\testdata.csv'
all_match = True
debug = True

program = Program( log_filepath, csv_filepath, all_match, debug)
if program.run() == True:
    print("Test successfully!")
