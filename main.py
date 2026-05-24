from custom_containers import *
from global_defaults import * 
from page_notebook import *

class Main_Window(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.title(APP_TITLE)
        self.geometry(WINDOW_SHAPE)
        self.minsize(*WINDOW_MIN_DIMS)
        self.view_manager = None
        
        self._style_setup()
        self._pages_buildup()
        
    def _style_setup(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

    def _pages_buildup(self):
        self.view_manager = PageViews(self)

if __name__ == '__main__':
    app = Main_Window()
    app.mainloop()