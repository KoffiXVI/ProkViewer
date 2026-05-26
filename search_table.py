from __future__ import annotations
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from database_maintenance_functions import Database_Ops_Handler
from custom_containers import Table, Entry_element, Radio_Buttons, Combobox_element, add_title_card
from analysis_classes import Genome
from database_constants import NAME, TAXID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from page_notebook import PageViews

class Search_Page(tk.Frame):
    def __init__(self,  master: PageViews, title="Search"):
        super().__init__(master=master)

        self.master = master 
        self.title = title
        self.candidate_genome = None

        self._page_buildup()

    def _page_buildup(self):
        self.searchbar_section = Search_Page_Searchbar(self)

        #Results Section
        self.PanRes = tk.PanedWindow(self)
        add_title_card(self.PanRes, "", "Results")
        
        self.res_treeview = Prok_Search_Table(self.PanRes)
        
        #Expanded section
        self.ResExpansion = tk.PanedWindow(self)
        add_title_card(self.ResExpansion, "", "Advanced Results")
        
        self.adv_res_treeview = Prok_Search_Table_Advanced(self.ResExpansion)

        #Action Buttons section
        self.PanAction = tk.PanedWindow(self)
        self.query_button = ttk.Button(self.PanAction, text="Set as Query", state=tk.DISABLED, command=self.set_query)
        self.subject_button = ttk.Button(self.PanAction, text="Set as Subject", state=tk.DISABLED, command=self.set_subject)

        self.query_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.subject_button.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        #Bindings
        self.res_treeview.bind("<<TreeviewSelect>>", self.launch_advanced_search)
        self.adv_res_treeview.bind("<<TreeviewSelect>>", self.update_candidate_genome_advanced)

        #packing the full view
        self.PanRes.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.ResExpansion.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.PanAction.pack(side=tk.BOTTOM, expand=False, fill=tk.BOTH)

        self.master.add(self, text=self.title)

    def check_action_button_activity(self):
        if self.candidate_genome is None:
            self.query_button.config(state=tk.DISABLED)
            self.subject_button.config(state=tk.DISABLED)
        
        else:
            self.query_button.config(state=tk.NORMAL)
            self.subject_button.config(state=tk.NORMAL)

    def update_candidate_genome_advanced(self, event):
        selected = self.adv_res_treeview.focus()
        if not selected:
            return

        self.res_treeview.selection_remove(self.res_treeview.selection())

        row_data = self.adv_res_treeview.item(selected, "values")
        self.candidate_genome = (*self.candidate_genome[:-2], *row_data[-2:])

    def set_query(self):
        base = Genome(*self.candidate_genome)
        self.master.analysis_page.set_query_genome(base)
    
    def set_subject(self):
        base = Genome(*self.candidate_genome)
        self.master.analysis_page.set_subject_genome(base)

    def clear_search_bar(self):
        self.res_treeview.cleanup()
        self.adv_res_treeview.cleanup()

        self.candidate_genome = None
        self.check_action_button_activity()

    def launch_search(self, query, method):
        self.res_treeview.cleanup()
        self.adv_res_treeview.cleanup()

        res = Database_Ops_Handler().process_query(query, method)

        self.res_treeview.insert_rows(res)

        self.candidate_genome = None
        self.check_action_button_activity()

    def launch_advanced_search(self, event):
        selected = self.res_treeview.focus()
        if not selected:
            return
        
        self.adv_res_treeview.cleanup()

        row_data = self.res_treeview.item(selected, "values")
        res = Database_Ops_Handler().advanced_process_query(*row_data[:2]) 
        self.adv_res_treeview.insert_rows(res)

        self.candidate_genome = row_data
        self.check_action_button_activity()

class Search_Page_Searchbar(tk.PanedWindow):
    def __init__(self, master:Search_Page, title = "Search", **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.title = title
        self.default_text = "Enter text here"
        self._page_buildup()

    def _page_buildup(self):
        
        self.search_bar = Entry_element(self, self.title, tk.StringVar, self.default_text, tk.NORMAL)
        self.search_bar.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.radio_buttons = Search_radio_options(self)

        #Adding search buttons
        search_button_options = {
            "Search": self.validate_search, 
            "Clear": self.clear_search_bar
        }
        
        for text, func in search_button_options.items():
            ttk.Button(self, text=text, command=func).pack(side=tk.LEFT)

        self.pack(side=tk.TOP, expand=False, fill=tk.X)
    
    def validate_search(self):
        search_type = self.radio_buttons.send_value()
        data = self.search_bar.send_value()
        if search_type == TAXID:
            try: 
                data = int(data.strip())
            except Exception:
                message = "Please enter a valid number for a TaxID search"
                messagebox.showwarning(message=message, icon="warning")
                return
        else:
            data = data.strip()
        
        self.master.launch_search(data, search_type)
    
    def clear_search_bar(self):
        self.search_bar.clear()
        self.master.clear_search_bar()

class Search_radio_options(Radio_Buttons):
    def __init__(self, master:Search_Page_Searchbar, **kwargs):
        radio_options = (
        ("Search by Name", NAME, tk.LEFT),
        ("Search by TaxId", TAXID, tk.LEFT)
        )
        parameter = tk.StringVar
        default = NAME
        super().__init__(master, radio_options, parameter, default, title=None, **kwargs)
        self.pack(side=tk.LEFT)
        
class Prok_Search_Table(Table):
    def __init__(self, master, data=None, **kwargs):
        columns = ('name', 'taxid', 'copies', 'assembly', 'link')
        headings = ('Name', 'Taxid', 'Copies', 'Assembly','Link')
        user_seen = ('name', 'taxid', 'copies', 'assembly')

        super().__init__(master, columns, headings, data, show="headings", displaycolumns=user_seen)

        self._table_buildup()

    def _table_buildup(self):
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

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
