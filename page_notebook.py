from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from search_table import Search_Page
from analysis_table import Analysis_Page
from database_table import Database_Page
from history_table import History_page
from plot_table import Dotplot_Page
from phylogeny_page import Phylogeny_Page 

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from analysis_classes import Blast_Display_Manager

class PageViews(ttk.Notebook):
    def __init__(self, master:tk.Tk):
        super().__init__(master=master)
        self.master = master 
        self.search_page = None
        self.analysis_page = None
        self.results_page = None
        self.history_page = None
        self.db_setup_page = None
        self.phylogeny = None

        self._page_buildup()

    def _page_buildup(self):
        self.search_page = Search_Page(self)
        self.phylogeny = Phylogeny_Page(self)
        self.analysis_page = Analysis_Page(self)
        self.results_page = Dotplot_Page(self)
        self.history_page = History_page(self)
        self.db_setup_page = Database_Page(self)
        self.pack(expand=True, fill=tk.BOTH)

    def add_plot(self, display_manager:Blast_Display_Manager, title=None):
        if self.results_page is not None:
            self.results_page.add_plot(display_manager, title)
        