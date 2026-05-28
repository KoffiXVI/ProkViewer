from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog as fd
from custom_containers import Table, Combobox_search_Filter
from database_maintenance_functions import Database_Ops_Handler
from global_defaults import MAX_VIEW
from tkinter import filedialog
from analysis_classes import Blast_Results_Table, Blast_Display_Manager


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from page_notebook import PageViews

class History_page(ttk.Notebook):
    def __init__(self,  master: PageViews, title="History", **kwargs):
        super().__init__(master= master, **kwargs)

        self.master = master 
        self.title = title
        self.blastp_section = None
        self.rps_blast_section = None

        self._page_buildup()

    def _page_buildup(self):
        self.blastp_section = Blastp_Results_Frame(self)
        self.rps_blast_section = RPS_Blast_Results_Frame(self)
        self.bind("<FocusIn>", self.populate_history)
        self.master.add(self, text=self.title)

    def populate_history(self, event):
        self.blastp_section.populate_history()
        self.rps_blast_section.populate_history()


class Skeleton_Results_Frame(tk.Frame):
    def __init__(self, master:History_page, title, results_table,action_window, ops_func, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master 
        self.title = title
        self.view_window = 0
        self.ops_func = ops_func

        self._page_buildup(results_table, action_window)

    def _page_buildup(self, results_table:object, action_window:object):
        self.results_table = results_table(self)

        self.actions = action_window(self, self.results_table) #Blastp_actions

        self.page_reference = ttk.Label(self, text="page 0", anchor='center')
        self.page_reference.pack(side=tk.BOTTOM, expand=False, fill=tk.X)

        self.master.add(self, text=self.title)

    def update_page_value(self, update:str):
        self.page_reference.config(text=update)
        
    def populate_history(self):
        self.results_table.cleanup()
        res, page_data = self.ops_func(view_window=self.view_window, max_view=MAX_VIEW)
        page_text, data_max = page_data

        if res is not None:
            self.results_table.insert_rows(res)
            if self.actions.movement == None:
                self.actions.movement = tk.LEFT

        else:
            self.actions.movement = None

        self.update_page_value(page_text)

        if data_max or not self.view_window:
            self.actions.deactivate_movement_buttons()

class Blastp_Results_Frame(Skeleton_Results_Frame):
    def __init__(self, master:History_page, **kwargs):
        title = "Blastp Results"
        results_table = Blastp_Table
        action_window = Blastp_actions
        ops_func = Database_Ops_Handler().navigate_blast_logs
        super().__init__(master, title, results_table, action_window, ops_func, **kwargs)


class RPS_Blast_Results_Frame(Skeleton_Results_Frame):
    def __init__(self, master:History_page, **kwargs):
        title = "RPS Blast Results"
        results_table = RPS_Blast_Table
        action_window = RPS_Blast_actions
        ops_func = Database_Ops_Handler().navigate_rpsblast_logs
        super().__init__(master, title, results_table, action_window, ops_func, **kwargs)


class Blastp_Table_filter_options(Combobox_search_Filter):
    def __init__(self, master:Blastp_Results_Frame, reference: Blastp_Table, **kwargs):
        
        self.reference = reference
        value_list = list(self.reference.filter_index.keys())
        default_combo_value = 0
        base_combo_state = tk.DISABLED
        default_filter_value = ""
        default_filter_state = tk.DISABLED
        combo_title = "Blastp filter options"
        button_text = "Filter"
        button_base_state = tk.DISABLED
        button_func = self.filter_table

        super().__init__(master, value_list, combo_title, default_combo_value, default_filter_value,
                         base_combo_state, default_filter_state, button_text, button_base_state,
                         button_func, **kwargs)
        
        self.pack(side=tk.TOP, expand=False, fill=tk.X)
    
    def filter_table(self):
        self.reference.filter_results(self.current_filter, self.current_filter_var)

class RPS_Blast_Table_filter_options(Combobox_search_Filter):
    def __init__(self, master:RPS_Blast_Results_Frame, reference: RPS_Blast_Table, **kwargs):

        self.reference = reference
        value_list = list(self.reference.filter_index.keys())
        default_combo_value = 0
        base_combo_state = tk.DISABLED
        default_filter_value = ""
        default_filter_state = tk.DISABLED
        combo_title = "RPS Blast filter options"
        button_text = "Filter"
        button_base_state = tk.DISABLED
        button_func = self.filter_table

        super().__init__(master, value_list, combo_title, default_combo_value, default_filter_value,
                         base_combo_state, default_filter_state, button_text, button_base_state,
                         button_func, **kwargs)
        
        self.pack(side=tk.TOP, expand=False, fill=tk.X)
    
    def filter_table(self):
        self.reference.filter_results(self.current_filter, self.current_filter_var)

class Skeleton_Actions(tk.PanedWindow):
    def __init__(self, master:Skeleton_Results_Frame, reference:object, 
                 ops_func_delete:function, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.reference = reference
        self.movement = tk.LEFT
        self.ops_func_delete = ops_func_delete

        self._page_buildup()
    
    def _page_buildup(self):
        return
    
    def activate_treeview_options(self, event):
        selected = self.reference.focus()
        if not selected:
            self.deactivate_treeview_options(event)
            return
        
        self.delete_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)
    
    def deactivate_treeview_options(self, event):
        self.delete_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)
        
    def deactivate_movement_buttons(self):
        if not self.movement:
            self.master.results_table.filter_options.disable()
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
        elif self.movement == tk.LEFT:
            self.master.results_table.filter_options.activate()
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.NORMAL)
        elif self.movement == tk.RIGHT:
            self.master.results_table.filter_options.activate()
            self.next_button.config(state=tk.DISABLED)
            self.prev_button.config(state=tk.NORMAL)

    def previous_record_page(self):
        self.movement = tk.LEFT
        self.master.view_window -= 1
        self.master.populate_history()
    
    def delete_record(self):
        selected = self.reference.focus()
        if not selected:
            return
        
        confirm = messagebox.askyesno(message="Do you confirm deleting this record ?", icon="question")
        if confirm:
            
            self.master.view_window = 0
            self.movement = None

            row_data = self.reference.item(selected, "values")
            log_id = row_data[-1]

            self.ops_func_delete(log_id)

            self.master.populate_history()
    
    def download_results(self):
        return
    
    def next_record_page(self):
        self.movement = tk.RIGHT
        self.master.view_window += 1
        self.master.populate_history()

class Blastp_actions(Skeleton_Actions):
    def __init__(self, master:Blastp_Results_Frame, reference:Blastp_Table, **kwargs):

        ops_func_delete = Database_Ops_Handler().delete_blast_log_record

        super().__init__(master, reference, ops_func_delete, **kwargs)
    
    def _page_buildup(self):

        self.prev_button = ttk.Button(self, text="Previous page", state=tk.DISABLED, command=self.previous_record_page)
        self.prev_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rerun_button = ttk.Button(self, text="Rerun blast", state=tk.DISABLED, command=self.rerun_blast)
        self.rerun_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.delete_button = ttk.Button(self, text="Delete record", state=tk.DISABLED, command=self.delete_record)
        self.delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.download_button = ttk.Button(self, text="Download results", state=tk.DISABLED, command=self.download_results)
        self.download_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.next_button = ttk.Button(self, text="Next page", state=tk.NORMAL, command=self.next_record_page)
        self.next_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.reference.bind("<<TreeviewSelect>>", self.activate_treeview_options)

        self.pack(side=tk.BOTTOM, expand=False, fill=tk.BOTH)

    def rerun_blast(self):
        selected = self.reference.focus()
        if not selected:
            return

        row_data = self.reference.item(selected, "values")
        query_name = f"{row_data[2]}_{row_data[3]}_{row_data[4]}"
        subject_name = f"{row_data[5]}_{row_data[6]}_{row_data[7]}"
        log_id = row_data[-1]

        evalue = float(row_data[8])

        res = Database_Ops_Handler().load_previous_blast(log_id)
        blast_table = Blast_Results_Table(res, evalue)
        blast_displayer = Blast_Display_Manager(query_name, subject_name, blast_table)

        self.master.master.master.add_plot(blast_displayer)
    
    def download_results(self):
        selected = self.reference.focus()
        if not selected:
            return
        
        row_data = self.reference.item(selected, "values")
        log_id = row_data[-1]
        query_info = "".join(row_data[2:5])
        subject_info = "".join(row_data[5:8])
        default_name = f"Blastp_{query_info}_{subject_info}"
        
        try:
            with filedialog.asksaveasfile(initialfile=default_name,title="Save as", defaultextension='.txt') as file_saver:
                Database_Ops_Handler().download_blast_res(filename=file_saver, Log_id=log_id) 
        except TypeError:
            #Happens in case of canceling the save
            return
    
    def deactivate_treeview_options(self, event):
        super().deactivate_treeview_options(event)
        self.rerun_button.config(state=tk.DISABLED)

    def activate_treeview_options(self, event):
        selected = self.reference.focus()
        if not selected:
            self.deactivate_treeview_options(event)
            return
        
        super().activate_treeview_options(event)
        self.rerun_button.config(state=tk.NORMAL)
        

class RPS_Blast_actions(Skeleton_Actions):
    def __init__(self, master:RPS_Blast_Results_Frame, reference:RPS_Blast_Table, **kwargs):

        ops_func_delete = Database_Ops_Handler.delete_rpsblast_log_record

        super().__init__(master, reference, ops_func_delete, **kwargs)
    
    def _page_buildup(self):

        self.prev_button = ttk.Button(self, text="Previous page", state=tk.DISABLED, command=self.previous_record_page)
        self.prev_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.delete_button = ttk.Button(self, text="Delete record", state=tk.DISABLED, command=self.delete_record)
        self.delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.download_button = ttk.Button(self, text="Download results", state=tk.DISABLED, command=self.download_results)
        self.download_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.next_button = ttk.Button(self, text="Next page", state=tk.NORMAL, command=self.next_record_page)
        self.next_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.reference.bind("<<TreeviewSelect>>", self.activate_treeview_options)

        self.pack(side=tk.BOTTOM, expand=False, fill=tk.BOTH)

    def download_results(self):
        selected = self.reference.focus()
        if not selected:
            return
        
        row_data = self.reference.item(selected, "values")
        log_id = row_data[-1]
        query_info = "".join(row_data[2:5])
        
        default_name = f"RPS_Blast_{query_info}"
        
        try:
            with filedialog.asksaveasfile(initialfile=default_name,title="Save as", defaultextension='.txt') as file_saver:
                Database_Ops_Handler().download_rps_blast_res(filename=file_saver, Log_id=log_id) 
        except TypeError:
            #Happens in case of canceling the save
            return

class Skeleton_Res_Table(Table):
    def __init__(self, master:Skeleton_Results_Frame, 
                filter_options:Blastp_Table_filter_options|RPS_Blast_Table_filter_options,
                columns, headings, user_seen, filter_index, data=None, **kwargs):
       
        
        self.filter_index = filter_index
        self.filter_options = filter_options

        super().__init__(master, columns, headings, data, show="headings", displaycolumns=user_seen)
        self.original_data = None
        self._table_buildup()

    def _table_buildup(self):
        self.filter_options = self.filter_options(self.master, self)
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def insert_rows(self, data):
        if self.data is None and self.filter_index[self.filter_options.current_filter] is None:
            self.original_data = data
        super().insert_rows(data)

    def filter_results(self, key:str, filter_value:str):
        super().cleanup()
        if self.filter_index[key] is None:
            self.insert_rows(self.original_data)
            return
        
        data = list()
        for element in self.original_data:
            if filter_value in str(element[self.filter_index[key]]):
                data.append(element)

        super().insert_rows(data)

class Blastp_Table(Skeleton_Res_Table):
    def __init__(self, master:Blastp_Results_Frame, data=None, **kwargs):
        
        columns = ("#",'date','q_name', 'q_id', 'q_assembly', 's_name', 's_id', 's_assembly',
                   'e_value', 'word_size', 'gap_open', 'gap_extend', 'matrix', 'lookup_threshold','log_id')
        
        headings = ("#",'Date','Q_name', 'Q_id', 'Q_assembly', 'S_name', 'S_id', 'S_assembly',
                   'Evalue', 'Word_size', 'Gap_open', 'Gap_extend', 'Matrix', 'Lookup Threshold', 'Log_id')
        
        user_seen = ("#",'date','q_name', 'q_id', 'q_assembly', 's_name', 's_id', 's_assembly',
                   'e_value', 'word_size', 'gap_open', 'gap_extend', 'matrix', 'lookup_threshold')
        
        filter_index = {
            "None":None,
            "Date": 1,
            "Q_name": 2,
            "Q_id": 3,
            "Q_assembly": 4,
            "S_name":5,
            "S_id": 6,
            "S_assembly": 7,
            "Evalue": 8, 
            "Word Size": 9,
            "Gap Open": 10,
            "Gap Extend": 11,
            "Matrix":12,
            "Lookup Threshold": 13
        }

        filter_options = Blastp_Table_filter_options
        
        super().__init__(master, filter_options, columns, headings, user_seen, filter_index, data, **kwargs)

class RPS_Blast_Table(Skeleton_Res_Table):
    def __init__(self, master:RPS_Blast_Results_Frame, data=None, **kwargs):
        
        columns = ("#", "date", "q_name", "q_id", "q_assembly", "evalue", "log_id")
        headings = ("#", "Date",'Q_name', 'Q_id', 'Q_assembly', 'Evalue', "Log_id")
        user_seen = ("#", "date", "q_name", "q_id", "q_assembly", "evalue")
        
        filter_index = {
            "None":None,
            "Date": 1,
            "Q_name": 2,
            "Q_id": 3,
            "Q_assembly": 4,
            "Evalue":5
        }

        filter_options = RPS_Blast_Table_filter_options
        
        super().__init__(master, filter_options, columns, headings, user_seen, filter_index, data, **kwargs)
