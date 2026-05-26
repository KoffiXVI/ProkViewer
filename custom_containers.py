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

        h_scroller = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.xview)
        self.configure(xscrollcommand=h_scroller.set)

        self.grid(row=0, column=0, sticky="nsew")
        v_scroller.grid(row=0, column=1, sticky="ns")
        h_scroller.grid(row=1, column=0, sticky="ew")

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
       super().__init__(master, bg="White",**kwargs)

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
    
class Combobox_search_Filter(tk.Frame):
    def __init__(self, master, value_list:list, combobox_title:str, defaut_combo_value:int,
                  default_filter_value, base_combo_state:str, default_filter_state, 
                  button_text, button_base_state, button_func, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master 
        self.value_list = value_list
        self.defaut_combo_value = defaut_combo_value
        self.base_combo_state = base_combo_state

        self.default_filter_value = default_filter_value
        self.default_filter_state = default_filter_state

        self.button_text = button_text
        self.button_base_state = button_base_state
        self.button_func = button_func
        self.combobox_title = combobox_title
        self._page_buildup()

    def _page_buildup(self):

        self.combo_entry = Combobox_element(self, self.combobox_title, self.value_list, self.defaut_combo_value, self.base_combo_state)
        self.combo_entry.pack(side=tk.LEFT)

        self.filter_var = tk.StringVar(value=self.default_filter_value)
        self.text_filter = tk.Entry(self, textvariable=self.filter_var, state=self.default_filter_state)
        self.text_filter.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.activation_button = ttk.Button(self, text=self.button_text, state=self.button_base_state, command=self.button_func)
        self.activation_button.pack(side=tk.RIGHT, expand=False)

    def reset_field(self):
        self.text_filter.delete(0, tk.END)

    def disable(self):
        self.reset_field()
        self.combo_entry.disable()
        self.text_filter.config(state=tk.DISABLED)
        self.activation_button.config(state=tk.DISABLED)

    def activate(self): 
        self.combo_entry.readonly()
        self.text_filter.config(state=tk.NORMAL)
        self.activation_button.config(state=tk.NORMAL)
        
    @property
    def current_filter(self):
        return self.combo_entry.send_value()
    
    @property
    def current_filter_var(self):
        return self.text_filter.get().strip()