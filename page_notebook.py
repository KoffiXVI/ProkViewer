import tkinter as tk
from tkinter import ttk
from search_table import Search_Page

class PageViews(ttk.Notebook):
    def __init__(self, master:tk.Tk):
        super().__init__(master=master)
        self.master = master 
        self.search_page = None
        self.analysis_page = None
        self.results_page = None
        self.history_page = None
        self.db_setup_page = None

        self._page_buildup()

    def _page_buildup(self):
        self.search_page = Search_Page(self)
        self.pack(expand=True, fill=tk.BOTH)