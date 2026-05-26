from __future__ import annotations
import tkinter as tk
from tkinter import ttk, Frame, Label, Button, messagebox
from custom_containers import Table, Combobox_element, Entry_element, add_title_card
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
        self.Blast_Parameters = Blast_Parameter_Window(self, background='red') #tk.PanedWindow(self, background='red')

        #RPS Blast Parameters
        self.RPS_Blast_Parameters = RPS_Blast_Parameter_Window(self, background='yellow')#tk.PanedWindow(self, background='yellow')

        #Action Buttons
        self.OpsAction = Analysis_actions(self, background='Blue') #tk.PanedWindow(self, background='Blue')

        #Packing
        self.RPS_Blast_Parameters.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.OpsAction.pack(side=tk.BOTTOM, expand=False)

        self.master.add(self, text=self.title)

    def set_query_genome(self, genome:Genome):
        self.Genome_window.query_card.update_card(genome)
        self.check_ops_button_activity()

    def set_subject_genome(self, genome:Genome):
        self.Genome_window.subject_card.update_card(genome)
        self.check_ops_button_activity()

    def check_ops_button_activity(self):
        activate = self.cards_filled()
        self.OpsAction.check_action_button_activity(activate)

    def cards_filled(self):
        query_card_genome = self.Genome_window.query_card.genome
        subject_card_genome = self.Genome_window.subject_card.genome
        return all(isinstance(card, Genome) for card in [query_card_genome, subject_card_genome])
    
    def validate_blastp_settings(self):
        proceed, data = self.Blast_Parameters.validate_inputs()
        if not proceed:
            return
        print("launching blastp")
        #later adding the blast function
        
    def validate_rpsblast_settings(self):
        proceed, data = self.RPS_Blast_Parameters.validate_inputs()
        if not proceed:
            return
        print("launching rpsblast")

class Analysis_actions(tk.PanedWindow):
    def __init__(self, master:Analysis_Page, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self._page_buildup()
    
    def _page_buildup(self):

        self.blastp_button = ttk.Button(self, text="Run Blastp", state=tk.DISABLED, command=self.launch_blastp)
        self.blastp_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rpblast_button = ttk.Button(self, text="Run RPS Blast", state=tk.DISABLED, command=self.launch_rpsblast_data)
        self.rpblast_button.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        self.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

    def launch_blastp(self):
        self.master.validate_blastp_settings()

    def launch_rpsblast_data(self):
        self.master.validate_rpsblast_settings()
        
    def check_action_button_activity(self, activate):
        if not activate:
            self.blastp_button.config(state=tk.DISABLED)
            self.rpblast_button.config(state=tk.DISABLED)
        
        else:
            self.blastp_button.config(state=tk.NORMAL)
            self.rpblast_button.config(state=tk.NORMAL)


class RPS_Blast_Parameter_Window(tk.PanedWindow):
    def __init__(self,  master: Analysis_Page, title= "RPS Blast Settings", **kwargs):
        super().__init__(master=master,  **kwargs)

        self.title = title
        self.master = master
        self.title_card = None
        self._page_buildup()
    
    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)
        self.pane = tk.Frame(self, bg="white", padx=20)
        self.evalue_entry = Blast_Evalue_Entry(self.pane)
        self.pane.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def validate_inputs(self):
        try:
            value = self.evalue_entry.send_value()
        except Exception:
            return (False, None)
        
        return (True, value)

class Blast_Parameter_Window(tk.PanedWindow):
    def __init__(self,  master: Analysis_Page, title= "Blast Settings", **kwargs):
        super().__init__(master=master,  **kwargs)

        self.title = title
        self.master = master
        self.title_card = None
        self._page_buildup()
    
    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)

        self.left_pane = tk.Frame(self, bg="white", padx=20)
        self.evalue_entry = Blast_Evalue_Entry(self.left_pane)
        self.word_size_entry = Word_Size_Entry(self.left_pane)
        self.gap_open_cost_entry = Gap_Open_Cost_Entry(self.left_pane)
        self.left_pane.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.right_pane = tk.Frame(self, bg="white", padx=20)
        self.gap_extend_cost_entry = Gap_Extend_Cost_Entry(self.right_pane) 
        self.threshold_entry = Threshold_Entry(self.right_pane)
        self.matrix_entry = Matrix_Entry(self.right_pane)
        self.right_pane.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def validate_inputs(self):
        entry_points = (self.evalue_entry, self.word_size_entry, 
                        self.gap_open_cost_entry, self.gap_extend_cost_entry,
                        self.threshold_entry, self.matrix_entry)
        
        try:
            values = [entry.send_value() for entry in entry_points]
        except Exception:
            return (False, None)
        
        return (True, values)

class Matrix_Entry(Combobox_element):
    def __init__(self, master, **kwargs):
        value_list = ["PAM30", "PAM70", "PAM250", "BLOSUM90", "BLOSUM80","BLOSUM62","BLOSUM50","BLOSUM45"]
        entry_title = "Matrix: "
        default_value = 5
        base_state = "readonly"
        super().__init__(master, entry_title, value_list, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)

    def send_value(self):
        if self.stored_value not in self.value_list:
            message = f"Invalid parameter for Blastp\nPlease select a valid Matrix"
            messagebox.showerror(message=message, icon="error")
            raise ValueError(message)
        return self.stored_value


class Blast_Evalue_Entry(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "E-value: "
        default_value = 1e-10
        parameter_type = tk.DoubleVar
        base_state = tk.NORMAL
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)
    
    def send_value(self):
        evalue = self.stored_value
        try:
            evalue = abs(float(evalue.strip().replace(",",".")))
        except Exception as e:
            message = f"Invalid parameter for Blast\nPlease enter a valid E-value"
            messagebox.showerror(message=message, icon="error")
            raise e
        
        return evalue

class Word_Size_Entry(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "Word size: "
        default_value = 3
        parameter_type = tk.IntVar
        base_state = tk.NORMAL
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)
    
    def send_value(self):
        value = self.stored_value
        try:
            value = abs(int(value.strip()))
        except Exception as e:
            message = f"Invalid parameter for Blastp\nPlease enter a valid Word Size"
            messagebox.showerror(message=message, icon="error")
            raise e
        
        return value

class Gap_Open_Cost_Entry(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "Gap Open: "
        default_value = 11
        parameter_type = tk.IntVar
        base_state = tk.NORMAL
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)
    
    def send_value(self):
        value = self.stored_value
        try:
            value = abs(int(value.strip()))
        except Exception as e:
            message = f"Invalid parameter for Blastp\nPlease enter a valid Gap Opening cost"
            messagebox.showerror(message=message, icon="error")
            raise e
        
        return value

class Gap_Extend_Cost_Entry(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "Gap Extend: "
        default_value = 1
        parameter_type = tk.IntVar
        base_state = tk.NORMAL
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)

    def send_value(self):
        value = self.stored_value
        try:
            value = abs(int(value.strip()))
        except Exception as e:
            message = f"Invalid parameter for Blastp\nPlease enter a valid Gap Extension cost"
            messagebox.showerror(message=message, icon="error")
            raise e
        
        return value

class Threshold_Entry(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "Threshold: "
        default_value = 11
        parameter_type = tk.IntVar
        base_state = tk.NORMAL
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)

    def send_value(self):
        value = self.stored_value
        try:
            value = abs(int(value.strip()))
        except Exception as e:
            message = f"Invalid parameter for Blastp\nPlease enter a valid Threshold Value"
            messagebox.showerror(message=message, icon="error")
            raise e
        
        return value

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
        self.title_card = None

        self._update_labels()

        self._page_buildup()
    
    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)

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
        self.master.master.check_ops_button_activity()

    def _update_labels(self):
        self.name_label_text = f"Name: {self.genome.name}"
        self.taxid_label_text = f"Taxid: {self.genome.taxid}"
        self.CGA_label_text = f"CGA: {self.genome.assembly}"