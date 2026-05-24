from __future__ import annotations
import tkinter as tk
from tkinter import ttk, Frame, Label, Button, messagebox
from global_defaults import EXAMPLE_SEARCH_OUTPUT, EXAMPLE_ADVANCED_SEARCH
from custom_containers import Table
from analysis_classes import Genome, Template_Genome

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from page_notebook import PageViews

class Analysis_Page(tk.Frame):
    def __init__(self,  master: PageViews, title="Analysis"):
        super().__init__(master=master)

        self.master = master 
        self.title = title
        
        self._page_buildup()
    
    def _page_buildup(self):
        #Genome information
        self.Genome_window = Genomic_Window(self, background='blue')

        #Blast Parameters
        self.Blast_Parameters = tk.PanedWindow(self, background='red')

        #RPS Blast Parameters
        self.RPS_Blast_Parameters = tk.PanedWindow(self, background='yellow')

        #Action Buttons
        self.OpsAction = tk.PanedWindow(self, background='Blue')

        #Packing
        #packing the full view
        #self.Genome_window.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.Blast_Parameters.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.RPS_Blast_Parameters.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.OpsAction.pack(side=tk.BOTTOM, expand=False)

        self.master.add(self, text=self.title)

    def set_query_genome(self, genome:Genome):
        self.Genome_window.query_card.update_card(genome)

    def set_subject_genome(self, genome:Genome):
        self.Genome_window.subject_card.update_card(genome)

class Genomic_Window(tk.PanedWindow):
    def __init__(self,  master: Analysis_Page, **kwargs):
        super().__init__(master=master,  **kwargs)

        self.master = master
        self.query_card:Genome_Card = None
        self.subject_card:Genome_Card = None

        self._page_buildup()
    
    def _page_buildup(self):

        self.query_card = Genome_Card(self, 'Query', Template_Genome(), bg="lightblue")
        self.subject_card = Genome_Card(self, 'Subject', Template_Genome(), bg="purple")

        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        

class Genome_Card(tk.Frame):
    def __init__(self, master:Genomic_Window, title:str, genome:Genome|Template_Genome, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.genome = genome
        self.title = title

        self._update_labels()

        self._page_buildup()
    
    def _page_buildup(self):
        self.title_card = ttk.Label(self, text=self.title, anchor=tk.W)
        self.title_card.pack(side=tk.TOP, expand=False, fill=tk.X)
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(side=tk.TOP, expand=False, fill=tk.X)

        self.name_label = ttk.Label(self, text=self.name_label_text, anchor=tk.W)
        self.name_label.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.taxid_label = ttk.Label(self, text=self.taxid_label_text, anchor=tk.W)
        self.taxid_label.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.CGA_label = ttk.Label(self, text=self.CGA_label_text, anchor=tk.W)
        self.CGA_label.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.clearing_button = ttk.Button(self, text="Clear", state=tk.DISABLED, command=self.clear_name_card)
        self.clearing_button.pack(side=tk.TOP, expand=False, fill=tk.X)
        
        self.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def update_card(self, genome:Genome|Template_Genome):
        self.genome = genome
        self._update_labels()

        self.name_label.configure(text=self.name_label_text)
        self.taxid_label.configure(text=self.taxid_label_text)
        self.CGA_label.configure(text=self.CGA_label_text)

        if isinstance(genome, Template_Genome):
            self.clearing_button.configure(state=tk.DISABLED)
        else:
            self.clearing_button.configure(state=tk.NORMAL)

    def clear_name_card(self):
        self.update_card(Template_Genome())

    def _update_labels(self):
        self.name_label_text = f"Name: {self.genome.name}"
        self.taxid_label_text = f"Taxid: {self.genome.taxid}"
        self.CGA_label_text = f"CGA: {self.genome.assembly}"