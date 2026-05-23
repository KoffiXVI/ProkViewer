import tkinter as tk
from tkinter import ttk, Frame, Label, Button, messagebox

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

        #Expanded section
        self.ResExpansion = tk.PanedWindow(self, background='Yellow')

        #packing the full view
        self.PanH.pack(side=tk.TOP, expand=False, fill=tk.X)
        self.PanRes.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.ResExpansion.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.master.add(self, text=self.title)

    def clear_search_bar(self):
        self.text_zone.delete(0, tk.END)
        self.launch_search()

    def launch_search(self):
        var = self.text_zone.get()
        messagebox.showinfo("IMPORTANT INFORMATION", var)
