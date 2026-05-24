import tkinter as tk
from tkinter import ttk

class Table(ttk.Treeview):
    def __init__(self, master, columns, headings, data:list|None= None, **kwargs):
        self.frame = ttk.Frame(master)

        super().__init__(self.frame, columns=columns, **kwargs)
        
        self.master = master
        self.columns = columns
        self.headings = headings
        self.data = data
        
        self._page_buildup()

    def _page_buildup(self):

        v_scroller = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscrollcommand=v_scroller.set)

        self.grid(row=0, column=0, sticky="nsew")
        v_scroller.grid(row=0, column=1, sticky="ns")

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        for col, head in zip(self.columns, self.headings):
            self.heading(col, text=head)
            self.column(col, width=max(80, len(head)*11), stretch=True, minwidth=50, anchor="w")

        if self.data is not None:
            self.insert_rows(None)

    def insert_rows(self, data:list|tuple|None):
        if data is not None:
            self.data = data
        
        for line in self.data:
            self.insert('', tk.END, values=line)

        #print(self.get_children())
    
    def cleanup(self):
        self.data = None
        self.delete(*self.get_children())