from __future__ import annotations
import tkinter as tk
from tkinter import ttk, Frame, Label, Button, messagebox
from global_defaults import EXAMPLE_SEARCH_OUTPUT, EXAMPLE_ADVANCED_SEARCH
from custom_containers import Table

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
        self.PanH = tk.PanedWindow(self, background='blue')

        self.search_label = Label(self.PanH, text="Search")
        self.search_label.pack(side=tk.LEFT)

        self.search_query = tk.StringVar(value="Enter text here")
        self.text_zone = tk.Entry(self.PanH,textvariable=self.search_query) #, background="white", foreground='black'
        self.text_zone.pack(side=tk.LEFT, expand=True, fill=tk.X)

        #Setting the search_radiobuttons
        self.search_option = tk.StringVar(value="name")

        radio_button_options = {
            "Search by Name":"name",
            "Search by TaxId":"taxid"
        }

        for text, value in radio_button_options.items():
            ttk.Radiobutton(self.PanH, text=text, value=value, variable=self.search_option).pack(side=tk.LEFT)

        #Adding search buttons
        search_button_options = {
            "Search": self.launch_search, #launch_search
            "Clear": self.clear_search_bar
        }
        
        for text, func in search_button_options.items():
            ttk.Button(self.PanH, text=text, command=func).pack(side=tk.LEFT)

        #Results Section
        self.PanRes = tk.PanedWindow(self, background='Red')
        ttk.Label(self.PanRes, text="Results", anchor=tk.W).pack(side=tk.TOP, expand=False, fill=tk.X)
        ttk.Separator(self.PanRes, orient=tk.HORIZONTAL).pack(side=tk.TOP, expand=False, fill=tk.X)

        self.res_treeview = Prok_Search_Table(self.PanRes)
        
        #Expanded section
        self.ResExpansion = tk.PanedWindow(self, background='Yellow')
        ttk.Label(self.ResExpansion, text="Advanced Results", anchor=tk.W).pack(side=tk.TOP, expand=False, fill=tk.X)
        ttk.Separator(self.ResExpansion, orient=tk.HORIZONTAL).pack(side=tk.TOP, expand=False, fill=tk.X)
        
        self.adv_res_treeview = Prok_Search_Table_Advanced(self.ResExpansion)

        #Action Buttons section
        self.PanAction = tk.PanedWindow(self, background='Blue')
        self.query_button = ttk.Button(self.PanAction, text="Set as Query", state=tk.DISABLED, command=self.set_query)
        self.subject_button = ttk.Button(self.PanAction, text="Set as Subject", state=tk.DISABLED, command=self.set_subject)

        self.query_button.pack(side=tk.LEFT)
        self.subject_button.pack(side=tk.LEFT)

        #Bindings
        self.res_treeview.bind("<<TreeviewSelect>>", self.launch_advanced_search)
        self.adv_res_treeview.bind("<<TreeviewSelect>>", self.update_candidate_genome_advanced)

        #packing the full view
        self.PanH.pack(side=tk.TOP, expand=False, fill=tk.X)
        self.PanRes.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.ResExpansion.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.PanAction.pack(side=tk.BOTTOM, expand=False)

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
        """
        Will link to the analysis page
        """
        return
    
    def set_subject(self):
        """
        Will link to the analysis page
        """

        return

    def clear_search_bar(self):
        self.text_zone.delete(0, tk.END)
        self.res_treeview.cleanup()
        self.adv_res_treeview.cleanup()

        self.candidate_genome = None
        self.check_action_button_activity()

    def launch_search(self):
        var = self.text_zone.get()
        self.res_treeview.cleanup()
        self.adv_res_treeview.cleanup()

        self.res_treeview.insert_rows(EXAMPLE_SEARCH_OUTPUT)

        self.candidate_genome = None
        self.check_action_button_activity()
        #messagebox.showinfo("IMPORTANT INFORMATION", var)

    def launch_advanced_search(self, event):
        selected = self.res_treeview.focus()
        if not selected:
            return
        
        self.adv_res_treeview.cleanup()
        res = EXAMPLE_ADVANCED_SEARCH #later replaced by the written function for it
        self.adv_res_treeview.insert_rows(res)

        row_data = self.res_treeview.item(selected, "values")
        self.candidate_genome = row_data
        self.check_action_button_activity()
        

class Prok_Search_Table(Table):
    """
        command = f"SELECT DISTINCT Name, taxid, COUNT(taxid) \
                       AS counter, assembly, link FROM {target_table} WHERE Name LIKE ? GROUP BY taxid;"
    """
    def __init__(self, master, data=None, **kwargs):
        columns = ('name', 'taxid', 'copies', 'assembly', 'link')
        headings = ('Name', 'Taxid', 'Copies', 'Assembly','Link')
        user_seen = ('name', 'taxid', 'copies', 'assembly')

        super().__init__(master, columns, headings, data, show="headings", displaycolumns=user_seen)

        self._table_buildup()

    def _table_buildup(self):
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

class Prok_Search_Table_Advanced(Table):
    """
        command = f"SELECT Name,reference,release_data, \
                    modify_data, size, genes, ROUND(genes/size,2) as gene_ratio, protein, \
                    ROUND(protein/size,2) as protein_ratio, assembly, link FROM {target_table} \
                    WHERE Name LIKE ? AND taxid = ?;"
    """
    def __init__(self, master, data=None, **kwargs):
        columns = ('name', 'reference', 'release_date', "modification_date", "size", "gene#",
                                     "gene_ratio", "protein#", "protein_ratio", "assembly", "link")
        
        headings = ('Name', 'Reference', 'Release date', "Modification date", "Size", "Gene#",
                                     "Gene Ratio", "Protein#", "Protein Ratio", "Assembly", "Link")
        
        user_seen = ('name', 'reference', 'release_date', "modification_date", "size", "gene#",
                                     "gene_ratio", "protein#", "protein_ratio", "assembly")
        
        super().__init__(master, columns, headings, data, show="headings", displaycolumns=user_seen)

        self._table_buildup()

    def _table_buildup(self):
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

