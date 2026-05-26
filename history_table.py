from __future__ import annotations
import tkinter as tk
from datetime import datetime
from tkinter import ttk, Frame, Label, Button, messagebox, filedialog as fd
from custom_containers import File_Searcher, Entry_element, add_title_card, Table, Combobox_element
from database_constants import PROK_LINK, TAXDMP_LINK, COG_DATABASE_LINK, COG_FUNCTIONNAL_LINK, COG_FAMILY_LINK, GENOME_FOLDER
from database_creation_functions import Database_Manager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from page_notebook import PageViews

class History_page(ttk.Notebook):
    def __init__(self,  master: PageViews, title="History", **kwargs):
        super().__init__(master= master, **kwargs)

        self.master = master 
        self.title = title
        self.blasp_section = None
        self.rps_blast_section = None

        self._page_buildup()

    def _page_buildup(self):
        self.blasp_section = Blastp_Results_Frame(self)
        self.rps_blast_section = RPS_Blast_Results_Frame(self)
        self.master.add(self, text=self.title)

class Blastp_Results_Frame(tk.Frame):
    def __init__(self, master:History_page, title="Blastp Results", **kwargs):
        super().__init__(master, **kwargs)

        self.master = master 
        self.title = title

        self._page_buildup()

    def _page_buildup(self):
        self.results_table = Blastp_Table(self)

        self.actions = Blastp_actions(self, self.results_table)

        self.page_reference = ttk.Label(self, text="page 0", anchor='center')
        self.page_reference.pack(side=tk.BOTTOM, expand=False, fill=tk.X)

        self.master.add(self, text=self.title)

class Blastp_Table_filter_options(tk.PanedWindow):
    def __init__(self, master:Blastp_Results_Frame, reference:Blastp_Table, title:str="Blastp filter options",**kwargs):
        super().__init__(master, **kwargs)

        self.master = master 
        self.title = title
        self.title_card = None
        self.reference = reference

        self._page_buildup()

    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)
        
        self.pack(side=tk.TOP, expand=False, fill=tk.X)

class Blastp_actions(tk.PanedWindow):
    def __init__(self, master:Blastp_Results_Frame, reference:Blastp_Table, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.reference = reference
        self._page_buildup()
    
    def _page_buildup(self):

        self.blastp_button = ttk.Button(self, text="Previous page", state=tk.NORMAL, command=self.previous_record_page)
        self.blastp_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.blastp_button = ttk.Button(self, text="Rerun blast", state=tk.NORMAL, command=self.rerun_blast)
        self.blastp_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rpblast_button = ttk.Button(self, text="Delete record", state=tk.NORMAL, command=self.delete_record)
        self.rpblast_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rpblast_button = ttk.Button(self, text="Download results", state=tk.NORMAL, command=self.download_results)
        self.rpblast_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.blastp_button = ttk.Button(self, text="Next page", state=tk.NORMAL, command=self.next_record_page)
        self.blastp_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.pack(side=tk.BOTTOM, expand=False, fill=tk.BOTH)

    def previous_record_page(self):
        return
    
    def rerun_blast(self):
        return
    
    def delete_record(self):
        return
    
    def download_results(self):
        return
    
    def next_record_page(self):
        return
    
    """
    def confirm_setup(self):
        confirm = messagebox.askyesno(message="Create database with these settings ?", icon="question")
        if confirm:
            self.master.setup_database(Database_Manager().create_working_database)

    def confirm_update(self):
        if not self.check_genome_folder():
            messagebox.showinfo(message="There is no genome folder.\nPlease Set up the database", icon='warning')
            return
        
        confirm = messagebox.askyesno(message="Update database with these settings ?", icon="question")
        if confirm:
            self.master.update_database(Database_Manager().update_database)
        
    def browse_genomes(self):
        if self.check_genome_folder():
            fd.askopenfile(initialdir=GENOME_FOLDER)
        else:
            messagebox.showinfo(message="There is no genome folder.\nPlease Set up the database", icon='warning')
    
    @staticmethod
    def check_genome_folder():
        return os.path.exists(GENOME_FOLDER)
    """

class Blastp_Table(Table):
    def __init__(self, master:Blastp_Results_Frame, data=None, **kwargs):
        """
        command = f"INSERT INTO {target_table} ({Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, {S_NAME}, {S_ID}, {S_ASSEMBLY},\
            {EVALUE}, {WORD_SIZE}, {G_OPEN}, {G_EXTEND}, {MATRIX}, {LOOKUP_TABLE}) \
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?) RETURNING {LOG_ID} ;"
        """
        columns = ('q_name', 'q_id', 'q_assembly', 's_name', 's_id', 's_assembly',
                   'e_value', 'word_size', 'gap_open', 'gap_extend', 'matrix')
        headings = ('Q_name', 'Q_id', 'Q_assembly', 'S_name', 'S_id', 'S_assembly',
                   'Evalue', 'Word_size', 'Gap_open', 'Gap_extend', 'Matrix')
        

        super().__init__(master, columns, headings, data, show="headings")

        self._table_buildup()

    def _table_buildup(self):
        self.filter_options = Blastp_Table_filter_options(self.master, self)
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)


class RPS_Blast_Results_Frame(tk.Frame):
    def __init__(self, master:History_page, title="RPSBlast Results", **kwargs):
        super().__init__(master, **kwargs)

        self.master = master 
        self.title = title

        self._page_buildup()

    def _page_buildup(self):

        self.results_table = RPS_Blast_Table(self)

        self.actions = RPS_Blast_actions(self, self.results_table)

        self.page_reference = ttk.Label(self, text="page 0", anchor='center')
        self.page_reference.pack(side=tk.BOTTOM, expand=False, fill=tk.X)
        
        self.master.add(self, text=self.title)


"""
RPS_Blast_Table_filter_options
command = f"INSERT INTO {target_table} ({Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, {EVALUE}) VALUES (?,?,?,?) RETURNING {LOG_ID} ;"
"""

class RPS_Blast_Table_filter_options(tk.PanedWindow):
    def __init__(self, master:RPS_Blast_Results_Frame, reference:RPS_Blast_Table, title:str="RPS Blast filter options",**kwargs):
        super().__init__(master, **kwargs)

        self.master = master 
        self.title = title
        self.title_card = None
        self.reference = reference

        self._page_buildup()

    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)
        
        self.pack(side=tk.TOP, expand=False, fill=tk.X)

class RPS_Blast_actions(tk.PanedWindow):
    def __init__(self, master:RPS_Blast_Results_Frame, reference:RPS_Blast_Table, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.reference = reference
        self._page_buildup()
    
    def _page_buildup(self):

        self.blastp_button = ttk.Button(self, text="Previous page", state=tk.NORMAL, command=self.previous_record_page)
        self.blastp_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rpblast_button = ttk.Button(self, text="Delete record", state=tk.NORMAL, command=self.delete_record)
        self.rpblast_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rpblast_button = ttk.Button(self, text="Download results", state=tk.NORMAL, command=self.download_results)
        self.rpblast_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.blastp_button = ttk.Button(self, text="Next page", state=tk.NORMAL, command=self.next_record_page)
        self.blastp_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.pack(side=tk.BOTTOM, expand=False, fill=tk.BOTH)

    def previous_record_page(self):
        return
    
    def delete_record(self):
        return
    
    def download_results(self):
        return
    
    def next_record_page(self):
        return
    

class RPS_Blast_Table(Table):
    def __init__(self, master:RPS_Blast_Results_Frame, data=None, **kwargs):
        """
        command = f"INSERT INTO {target_table} ({Q_NAME}, {Q_ID}, {Q_ASSEMBLY}, {EVALUE}) VALUES (?,?,?,?) RETURNING {LOG_ID} ;"
        """
        columns = ('q_name', 'q_id', 'q_assembly', 'e_value')
        headings = ('Q_name', 'Q_id', 'Q_assembly', 'Evalue')

        super().__init__(master, columns, headings, data, show="headings")

        self._table_buildup()

    def _table_buildup(self):
        self.filter_options = Blastp_Table_filter_options(self.master, self)
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)


#table template

class Prok_Search_Table_Advanced(Table):
    def __init__(self, master, data=None, **kwargs):
        columns = ('name', 'reference', 'release_date', "modification_date", "size", "gene#",
                                     "gene_ratio", "protein#", "protein_ratio", "assembly", "link")
        
        headings = ('Name', 'Reference', 'Release date', "Modification date", "Size", "Gene#",
                                     "Gene Ratio", "Protein#", "Protein Ratio", "Assembly", "Link")
        
        user_seen = ('name', 'reference', 'release_date', "modification_date", "size", "gene#",
                                     "gene_ratio", "protein#", "protein_ratio", "assembly")
        
        super().__init__(master, columns, headings, data, show="headings", displaycolumns=user_seen)
        self.original_data = None
        self._table_buildup()

    def filter_results(self, option):
        super().cleanup()
        if option == "None":
            self.insert_rows(self.original_data)
        
        elif option == "REPR/REFR":
            data = [element for element in self.original_data if element[1] in ["REFR", "REPR"]]

        elif "Date" in option:
            data = sorted(self.original_data, key=lambda k: datetime.strptime(k[self.filter_options.current], '%Y-%m-%d'), reverse=True)
        
        else:
            data = sorted(self.original_data, key=lambda x:x[self.filter_options.current], reverse=True)

        super().insert_rows(data)

    def cleanup(self):
        super().cleanup()
        self.data = None
        self.filter_options.disable()
         
    def insert_rows(self, data):
        if self.data is None and self.filter_options.stored_value == "None":
            self.original_data = data
        super().insert_rows(data)
        self.filter_options.readonly()

    def _table_buildup(self):
        self.filter_options = Advanced_search_table_Filters(self.master, self)
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)


class Advanced_search_table_Filters(Combobox_element):
    def __init__(self, master, reference:Prok_Search_Table_Advanced, **kwargs):
        value_list = ["None","REPR/REFR", "Release Date", "Modification Date", 
                      "Size", "Gene#","Gene ratio","Protein number","Protein ratio"]
        entry_title = "Filter by: "
        default_value = 0
        base_state = tk.DISABLED#"readonly"
        self.reference = reference
        super().__init__(master, entry_title, value_list, default_value, base_state, **kwargs)
        self.entry_element.bind('<<ComboboxSelected>>', self.trigger_table_filter)
        self.pack(side=tk.TOP, expand=False, fill=tk.X)

    def trigger_table_filter(self, event):

        self.reference.filter_results(self.stored_value)

    def disable(self):
        self.entry_element.set(self.value_list[0])
        super().disable() 
    
    def readonly(self):
        self.entry_element.set(self.value_list[0])
        super().readonly() 

    def send_value(self):
        return self.stored_value
