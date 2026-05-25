from __future__ import annotations
import tkinter as tk
import os
from tkinter import ttk, Frame, Label, Button, messagebox, filedialog as fd
from custom_containers import File_Searcher, Entry_element, add_title_card
from database_constants import PROK_LINK, TAXDMP_LINK, COG_DATABASE_LINK, COG_FUNCTIONNAL_LINK, COG_FAMILY_LINK, GENOME_FOLDER
from database_creation_functions import Database_Manager#create_working_database, update_database

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from page_notebook import PageViews

class Database_Page(tk.Frame):
    def __init__(self,  master: PageViews, title="DB Setup"):
        super().__init__(master=master)

        self.master = master 
        self.title = title
        
        self._page_buildup()
    
    def _page_buildup(self):

        self.prokaryotes_options = Prokaryote_Window(self, bg="Blue")

        self.taxonomy_options = Taxonomy_Window(self, bg="Red")

        self.cog_options = COG_Window(self, bg="Red")

        self.database_ops = Database_actions(self, bg="Yellow")

        self.master.add(self, text=self.title)

    def setup_database(self, creation_func:function):
        info = self.gather_inputs()
        creation_func(*info)
    
    def update_database(self, update_func:function):
        info = self.gather_inputs()
        update_func(*info)
    
    def gather_inputs(self):

        windows = (self.prokaryotes_options, self.taxonomy_options, self.cog_options)
        data = list()
        for window in windows:
            [data.append(element) for element in window.send_inputs()]
        
        return data
    
class Database_actions(tk.PanedWindow):
    def __init__(self, master:Database_Page, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self._page_buildup()
    
    def _page_buildup(self):

        self.blastp_button = ttk.Button(self, text="Set up database", state=tk.NORMAL, command=self.confirm_setup)
        self.blastp_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rpblast_button = ttk.Button(self, text="Update database", state=tk.NORMAL, command=self.confirm_update)
        self.rpblast_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.rpblast_button = ttk.Button(self, text="Browse Genomes", state=tk.NORMAL, command=self.browse_genomes)
        self.rpblast_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.pack(side=tk.BOTTOM, expand=False, fill=tk.BOTH)

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

class Prokaryote_Window(tk.PanedWindow):
    def __init__(self,  master: Database_Page, title= "Prokaryotes options", **kwargs):
        super().__init__(master=master,  **kwargs)

        self.title = title
        self.master = master
        self.title_card = None
        self._page_buildup()
    
    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)
        self.prok_link = Prokaryote_Link(self)
        self.prok_fsearch = Prokaryote_FSearch(self)

        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def send_inputs(self):
        data = [element.send_value() for element in (self.prok_link, self.prok_fsearch)]

        return data

class Taxonomy_Window(tk.PanedWindow):
    def __init__(self,  master: Database_Page, title= "Taxonomy options", **kwargs):
        super().__init__(master=master,  **kwargs)

        self.title = title
        self.master = master
        self.title_card = None
        self._page_buildup()
    
    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)
        self.tax_link = Taxonomy_Link(self)
        self.tax_fsearch = Taxonomy_FSearch(self)

        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def send_inputs(self):
        data = [element.send_value() for element in (self.tax_link, self.tax_fsearch)]

        return data

class COG_Window(tk.PanedWindow):
    def __init__(self,  master: Database_Page, title= "COG options", **kwargs):
        super().__init__(master=master,  **kwargs)

        self.title = title
        self.master = master
        self.title_card = None
        self._page_buildup()
    
    def _page_buildup(self):
        add_title_card(self, "title_card", self.title)
        self.cog_database_link = COG_Database_Link(self)
        self.cog_database_fsearch = COG_Database_FSearch(self)

        self.cog_families_link = COG_Families_Link(self)
        self.cog_families_fsearch = COG_Families_FSearch(self)

        self.cog_functions_link = COG_Functions_Link(self)
        self.cog_functions_fsearch = COG_Functions_FSearch(self)

        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def send_inputs(self):
        data = [element.send_value() for element in (self.cog_database_link, 
                                                     self.cog_database_fsearch,
                                                     self.cog_families_link,
                                                     self.cog_families_fsearch,
                                                     self.cog_functions_link,
                                                     self.cog_functions_fsearch)]
        return data

class Prokaryote_FSearch(File_Searcher):
    def __init__(self, master, **kwargs):
        button_text = "Prokaryote local file"
        super().__init__(master, button_text, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

class Taxonomy_FSearch(File_Searcher):
    def __init__(self, master, **kwargs):
        button_text = "Taxonomy local file"
        super().__init__(master, button_text, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

class COG_Database_FSearch(File_Searcher):
    def __init__(self, master, **kwargs):
        button_text = "COG database local file"
        super().__init__(master, button_text, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

class COG_Functions_FSearch(File_Searcher):
    def __init__(self, master, **kwargs):
        button_text = "COG functions local file"
        super().__init__(master, button_text, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

class COG_Families_FSearch(File_Searcher):
    def __init__(self, master, **kwargs):
        button_text = "COG families local file"
        super().__init__(master, button_text, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
 
class Prokaryote_Link(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "Prokaryote download link: "
        default_value = PROK_LINK
        parameter_type = tk.StringVar
        base_state = tk.DISABLED
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)

class Taxonomy_Link(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "Taxonomy download link: "
        default_value = TAXDMP_LINK
        parameter_type = tk.StringVar
        base_state = tk.DISABLED
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)

class COG_Database_Link(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "COG database download link: "
        default_value = COG_DATABASE_LINK
        parameter_type = tk.StringVar
        base_state = tk.DISABLED
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)

class COG_Functions_Link(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "COG functions download link: "
        default_value = COG_FUNCTIONNAL_LINK
        parameter_type = tk.StringVar
        base_state = tk.DISABLED
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)

class COG_Families_Link(Entry_element):
    def __init__(self, master, **kwargs):
        entry_title = "COG families download link: "
        default_value = COG_FAMILY_LINK
        parameter_type = tk.StringVar
        base_state = tk.DISABLED
        super().__init__(master, entry_title, parameter_type, default_value, base_state, **kwargs)
        self.pack(side=tk.TOP, expand=True, fill=tk.X)