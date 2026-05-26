import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk

def add_title_card(container:object, variable_name:str, title:str):

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

    def send_value(self):
        return None if not len(self.stored_value.strip()) else self.stored_value
    
    def clear(self):
        self.entry_element.delete(0, tk.END)

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
    
    def send_value(self):
        return self.stored_value

    def disable(self):
        self.entry_element.configure(state=tk.DISABLED)

    def readonly(self):
        self.entry_element.configure(state="readonly")
    
    @property
    def current(self):
        return self.entry_element.current()
    
    @property
    def stored_value(self):
        return self.entry_element.get()
    
class File_Searcher(tk.Frame):
    def __init__(self, master, button_text, **kwargs):
       super().__init__(master, **kwargs)

       self._page_buildup(button_text)

    def _page_buildup(self, button_text):
        
        self.frame_button = ttk.Button(self, text=button_text, command=self.set_localfile)
        self.frame_button.pack(side=tk.LEFT)
        self.frame_var = tk.StringVar(self, value="")
        self.frame_entry = tk.Entry(self, textvariable=self.frame_var, state="readonly")
        self.frame_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def set_localfile(self):
        file_path = fd.askopenfilename()
        self.frame_var.set(file_path)

    def send_value(self):
        return None if not len(self.stored_value.strip()) else self.stored_value
    
    @property
    def stored_value(self):
        return self.frame_entry.get()
    
class Radio_Buttons(tk.Frame):
    def __init__(self, master:object, buttons, var_type:object, var_default:int|float|str, title:str|None = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.master = master
        self.title = title
        self.buttons = buttons
        self.variable = var_type(value = var_default)
        self._page_buildup()

    def _page_buildup(self):
        if self.title:
            add_title_card(self, "title", self.title)
        
        for text, value, position in self.buttons:
            ttk.Radiobutton(self, text=text, value=value, variable=self.variable).pack(side=position)

    def send_value(self):
        return self.stored_value
    
    @property
    def stored_value(self):
        return self.variable.get()