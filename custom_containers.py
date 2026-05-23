import tkinter as tk
from tkinter import ttk, Frame, Label, Button

class PageViews(ttk.Notebook):
    def __init__(self, master:tk.Tk):
        super().__init__()
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

class Search_Page(tk.Frame):
    def __init__(self,  master:PageViews, title="Search",):
        super().__init__()

        self.master = master 
        self.title = title

        self._page_buildup()

    def _page_buildup(self):
        PanH = tk.PanedWindow(self, background='blue')

        lbl = Label(PanH, text="Some nonsense")
        lbl.pack(side=tk.LEFT)

        btn = Button(PanH, text="Button")
        btn.pack(side=tk.LEFT)

        PanH.pack(side=tk.TOP, expand=False, fill=tk.X)
        self.master.add(self, text=self.title)