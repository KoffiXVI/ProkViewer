import os
import gzip
import shutil
import io
import requests as req
from database_constants import GENOME_FOLDER
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

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
                return (True, "Data alredy existing")
            else:
                shutil.rmtree(self.accession_folder)

        os.makedirs(self.accession_folder)

        target_genome_protein_faa = self.link + end_section + faa_extension
        target_genome_feature_table = self.link + end_section + feature_table_extension

        process = [(target_genome_protein_faa, faa_file), (target_genome_feature_table, features_file)]

        for data_link, data_file in process:
            try:
                with req.get(data_link) as data_download:
                    
                    download_content = io.BytesIO(data_download.content)

                    with open(data_file, 'x') as df:
                        with gzip.open(download_content, 'r') as content_info:
                            content_info_text = io.TextIOWrapper(content_info)
                            shutil.copyfileobj(content_info_text, df)
                            content_info_text.close()
                    
                    download_content.close()

            except Exception as e:
                return (False, e)

        return (True, "Data downloaded successfully")
    

class RPSBlast_Results_Table(np.ndarray):

    def __new__(cls, input_array, evalue):
        arr = np.asarray(input_array).view(cls)
        arr.rpsblast_evalue = evalue
        
        return arr
    
    @property
    def query_sid(self):
        return self[:,0]
    
    @property
    def cog_fam(self):
        return self[:,[0, 1]]
    
    @property
    def al_eval(self):
        return self[:,[1, 2]]
    
    @property
    def family(self):
        return self[:,[0, 3]]
    
    def filter_by_family(self, id:list[str]|None=None, evalue=1e-10):
        
        if not isinstance(id, list) and id is not None:
            if id is not None and isinstance(id, str):
                id = [id]
            elif id is not None and not isinstance(id, list):
                raise AttributeError(f"Expected list[str] or str for id, got {type(list).__name__} instead")
            
        filtered_table = self[np.where(self.al_eval[:, -1].astype(float) < evalue)]
        
        res = filtered_table
        
        if id is not None:
            if len(id):
                pos = np.nonzero([any(char_id in word for char_id in id) for word in res[:, -1]])
                
                res = res[pos]

        return res
    

class Blast_Results_Table(np.ndarray):
    
    def __new__(cls, input_array, evalue):
        arr = np.asarray(input_array).view(cls)
        arr.blast_evalue = evalue
       
        return arr
    
    @property
    def query_sid(self):
        return self[:,0]
    
    @property
    def subject_sid(self):
        return self[:,1]
    
    @property
    def id_percent(self):
        return self[:,[0, 1, 2]]
    
    @property
    def lenght(self):
        return self[:,[0, 1, 3]]

    @property
    def mismatchs(self):
        return self[:,[0, 1, 4]]
    
    @property
    def gaps(self):
        return self[:,[0, 1, 5]]
    
    @property
    def q_al_start(self):
        return self[:,[0, 1, 6]]
    
    @property
    def q_al_end(self):
        return self[:,[0, 1, 7]]
    
    @property
    def s_al_start(self):
        return self[:,[0, 1, 8]]
    
    @property
    def s_al_end(self):
        return self[:,[0, 1, 9]]
    
    @property
    def al_eval(self):
        return self[:,[0, 1, 10]]
    
    @property
    def al_bitscore(self):
        return self[:,[0, 1, 11]]
    
    def get_indexes(self, evalue, query_fam_filter=None, subject_fam_filter=None):
        goog_pos = np.where(self.al_eval[:,-1].astype(float) < evalue)
        query_ids, query_idx = np.unique(self.query_sid, return_inverse=True)
        subject_ids, subject_idx = np.unique(self.subject_sid, return_inverse=True)
        
        query_idx = query_idx[goog_pos]
        subject_idx = subject_idx[goog_pos]

        if query_fam_filter is not None:
            query_fam_mask = np.nonzero(np.isin(query_ids, query_fam_filter))
            query_idx = query_idx[np.isin(query_idx, query_fam_mask)]

        if subject_fam_filter is not None:
            sub_fam_mask = np.nonzero(np.isin(subject_ids, subject_fam_filter))
            subject_idx = subject_idx[np.isin(subject_idx, sub_fam_mask)]

        min_rep = min(len(query_idx), len(subject_idx))
        
        query_idx = query_idx[:min_rep]
        subject_idx = subject_idx[:min_rep]

        return (query_ids, query_idx), (subject_ids, subject_idx)


class Blast_Display_Manager():
    def __init__(self, query_name, subject_name, blast_table:Blast_Results_Table, 
                 q_rpblast:RPSBlast_Results_Table|None=None, 
                 s_rpblast:RPSBlast_Results_Table|None=None):
        
        self.query_name = query_name
        self.subject_name = subject_name
        self.q_rpblast = q_rpblast
        self.s_rpblast = s_rpblast
        self.blast_table = blast_table

        self.q_filter_defaults = (None, q_rpblast.rpsblast_evalue) if self.q_rpblast is not None else None
        self.s_filter_defaults = (None, s_rpblast.rpsblast_evalue) if self.s_rpblast is not None else None
        self.max_blast_evalue = blast_table.blast_evalue

        self.display_query_data = None
        self.display_subject_data = None
        self.saved_diag_pos = None
        
    def get_display_data(self, evalue=0, q_filter_params:tuple|None = None, s_filter_params:tuple|None = None):
        q_filter = None
        s_filter = None
        if self.q_rpblast is not None:
            if q_filter_params is not None:
                q_filter = self.q_rpblast.filter_by_family(*q_filter_params)
            else:
                q_filter = self.q_rpblast.filter_by_family(*self.q_filter_defaults)
        
        if self.s_rpblast is not None:
            if s_filter_params is not None:
                s_filter = self.s_rpblast.filter_by_family(*s_filter_params)
            else:
                s_filter = self.s_rpblast.filter_by_family(*self.s_filter_defaults) 

        used_evalue = min(self.max_blast_evalue, evalue)

        query_data, subject_data = self.blast_table.get_indexes(used_evalue, q_filter, s_filter)

        self.display_query_data, self.display_subject_data = query_data, subject_data

        return query_data, subject_data
    
    def diagonal_tester(self, query_info:tuple|None=None, subject_info:tuple|None = None, ax_thres:int=300, ali_thres:int=300, distance = 1):
        if query_info is None:
            if self.display_query_data is None:
                self.get_display_data(self.max_blast_evalue)
            q_idx = self.display_query_data[1]
        else:
            q_idx = query_info

        if subject_info is None:
            if self.display_subject_data is None:
                self.get_display_data(self.max_blast_evalue)
            s_idx = self.display_subject_data[1]
        else:
            s_idx = subject_info

        diag_pos = set()
        #diag_locations = list()

        for diag_type in ["classic", "reversed"]:
            diagonals = defaultdict(list)
            #print(diag_type)

            for q_id, s_id in zip(q_idx, s_idx):
                if diag_type == "classic":
                    diagonals[q_id - s_id].append((int(q_id), int(s_id)))
                elif diag_type == "reversed":
                    diagonals[q_id + s_id].append((int(q_id), int(s_id)))

            for i, (_, hits) in enumerate(diagonals.items()):
                hits.sort()
                index = 0
                if len(hits) > ax_thres:
                    while index < len(hits):
                        ali = 1
                        for j in range(index+1, len(hits)):
                            if hits[j][0] - hits[index][0] <= ali + distance:
                                ali += 1
                            else:
                                break

                        if ali > ali_thres:
                            for h in hits[index:index+ali]:
                                diag_pos.add(h)
                        
                        index += ali

        res = np.array(list(diag_pos))
        self.saved_diag_pos = res
        return res

    def display_dotplot(self, query_data:tuple|None=None, subject_data:tuple|None=None, 
                        coloring:list|None=None, tick_number:int=4, width:int|float=8, 
                        height:int|float=8, size:int=1, query_name:str|None=None, db_query:str|None=None):
        
        if query_name is None:
            query_name = self.query_name 

        if db_query is None:
            db_query = self.subject_name 

        if coloring is None:
            if self.saved_diag_pos is None:
                coloring = self.diagonal_tester()
            else:
                coloring = self.saved_diag_pos
            
            query_data, subject_data = self.display_query_data, self.display_subject_data

        query_idx, query_pos = query_data
        subject_idx, subject_pos = subject_data
        
        fig, ax = plt.subplots()
        fig.set_figwidth(width)
        fig.set_figheight(height)
        
        """
        x_step_len = len(query_idx)
        x_step_number = max(1, round(x_step_len / tick_number))

        y_step_len = len(subject_idx)
        y_step_number = max(1, round(y_step_len / tick_number))

        query_ticks_pos = np.arange(x_step_len,step=x_step_number)
        query_labels = query_idx[np.arange(x_step_len, step=x_step_number)]

        subject_ticks_pos = np.arange(y_step_len,step=y_step_number)
        subject_labels = subject_idx[np.arange(y_step_len, step = y_step_number)]
        """

        ax.scatter(query_pos,subject_pos, s=size, marker="o", color="black")
        if len(coloring) > 0:
            color_x, color_y = coloring[:,0],coloring[:,1]
            ax.scatter(color_x,color_y, s=size, marker="o", color="red")
        
        """
        ax.set_xticks(query_ticks_pos, query_labels, rotation=45)
        ax.set_yticks(subject_ticks_pos, subject_labels)
        """
        
        ax.set_yticks([])
        ax.set_xticks([])
        #Will be important to remove ticklabels when implementing interactive graph
        
        ax.set_xlabel(f"{query_name}", fontsize=10)
        ax.set_ylabel(f"{db_query}", fontsize=10)

        ax.invert_yaxis()
        ax.xaxis.set(ticks_position="top",label_position="top")

        ax.set_title(f"Blastp {query_name} vs {db_query}", fontsize=10, y=-0.05, verticalalignment = 'bottom')
        
        self.saved_diag_pos = None
        return fig