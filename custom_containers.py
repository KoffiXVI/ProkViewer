import tkinter as tk
from tkinter import ttk

def add_title_card(container:object, variable_name:str, title):

    """
    self.title_card = ttk.Label(self, text=self.title, anchor=tk.W)
    self.title_card.pack(side=tk.TOP, expand=False, fill=tk.X)
    """
    setattr(container, variable_name, ttk.Label(container, text=title, anchor=tk.W))
    getattr(container, variable_name).pack(side=tk.TOP, expand=False, fill=tk.X)
    ttk.Separator(container, orient=tk.HORIZONTAL).pack(side=tk.TOP, expand=False, fill=tk.X)

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
    
    def cleanup(self):
        self.data = None
        self.delete(*self.get_children())


class Entry_element(tk.Frame):
    def __init__(self, master, entry_title, parameter_type, default_value, base_state, **kwargs):
        super().__init__(master=master, **kwargs)

        self.master = master
        self.entry_title = entry_title
        self.default_value = default_value

        self._page_buildup(base_state, parameter_type)
    
    def _page_buildup(self, base_state, parameter_type:tk.StringVar|tk.DoubleVar|tk.IntVar):
        self.entry_label = ttk.Label(self, text=self.entry_title)
        self.entry_label.pack(side=tk.LEFT)

        self.parameter_var = parameter_type(self, value=self.default_value) 
        
        self.entry_element = tk.Entry(self,textvariable=self.parameter_var, state=base_state)
        self.entry_element.pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    def edit_entry_status(self):
        self.entry_element.config(state=tk.DISABLED)

    @property
    def stored_value(self):
        return self.entry_element.get()
    
class Combobox_element(tk.Frame):
    def __init__(self, master, entry_title, value_list, default_value, base_state, **kwargs):
        super().__init__(master=master, **kwargs)

        self.master = master
        self.entry_title = entry_title
        self.value_list = value_list
        self.default_value = default_value
        self._page_buildup(base_state)
    
    def _page_buildup(self, base_state):
        self.entry_label = ttk.Label(self, text=self.entry_title)
        self.entry_label.pack(side=tk.LEFT)

        self.entry_element = ttk.Combobox(self, values=self.value_list, state=base_state)
        self.entry_element.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.entry_element.current(self.default_value)
    
    @property
    def stored_value(self):
        return self.entry_element.get()