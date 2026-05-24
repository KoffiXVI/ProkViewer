import os
import gzip
import shutil
import io
import requests as req
from global_defaults import GENOME_FOLDER

class Template_Genome():
    def __init__(self):
        
        self.name = "-- Unselected --"
        self.taxid = "-- Unselected --"
        self.assembly = "-- Unselected --"

class Genome():
    def __init__(self, name, taxid, duplicates, assembly, link, storage:str=GENOME_FOLDER):
        self.name = name
        self.process_name = name.replace(" ","_") + f"_{taxid}"
        self.display_name = self.process_name + f"_{assembly}"
        self.taxid = taxid
        self.duplicates = duplicates
        self.assembly = assembly
        self.link = link

        self.storage = storage
        self.genome_folder = os.path.join(self.storage, self.process_name)
        self.accession_folder = os.path.join(self.genome_folder, self.assembly)
        
    def get_faa(self):
        faa_extension = "_protein.faa"
        faa_path = os.path.join(self.genome_folder, self.assembly, self.assembly + faa_extension)

        return faa_path

    def log_info(self):
        return (self.name, self.taxid, self.assembly)
    
    def download_genome(self):
        end_section = "/"+self.link.split("/")[-1]
        faa_extension = "_protein.faa.gz"
        feature_table_extension = "_feature_table.txt.gz"

        faa_file = os.path.join(self.accession_folder, self.assembly + faa_extension.removesuffix(".gz"))
        features_file = os.path.join(self.accession_folder, self.assembly + feature_table_extension.removesuffix(".gz"))

        if os.path.exists(self.accession_folder):
            if all([os.path.exists(path) for path in [faa_file, features_file]]):
                print("data alredy existing") # to be removed later
                return (True, "data alredy existing")
            else:
                shutil.rmtree(self.accession_folder)

        os.makedirs(self.accession_folder)

        target_genome_protein_faa = self.link + end_section + faa_extension
        target_genome_feature_table = self.link + end_section + feature_table_extension

        process = [(target_genome_protein_faa, faa_file), (target_genome_feature_table, features_file)]

        for data_link, data_file in process:
            with req.get(data_link) as data_download:
                if not data_download.status_code == 200:
                    print(f"error while donwloading {data_link}:{data_download.status_code}")
                    return (False, data_download.status_code)
                
                download_content = io.BytesIO(data_download.content)

                with open(data_file, 'x') as df:
                    with gzip.open(download_content, 'r') as content_info:
                        content_info_text = io.TextIOWrapper(content_info)
                        shutil.copyfileobj(content_info_text, df)
                        content_info_text.close()
                
                download_content.close()

        return (True, "data downloaded successfully")