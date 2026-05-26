from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from analysis_classes import Blast_Display_Manager, RPSBlast_Results_Table
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from page_notebook import PageViews

_VALID_COG_CODES = set("JAKLDYVTMNZWUOXCGEFHIPQRS")


class Dotplot_Page(ttk.Notebook):
    def __init__(self, master: PageViews, title="Plots", **kwargs):
        super().__init__(master=master, **kwargs)

        self.master = master
        self.title = title
        self.plot_index = 0
        self.plot_prefix = "Plot"

        self._page_buildup()

    def _page_buildup(self):
        self.master.add(self, text=self.title)

    def add_plot(self, display_manager, title: str = None):
        if title is None:
            title = f"{self.plot_prefix} {self.plot_index}"

        plot_view = Dotplot_View(self, display_manager, title)
        self.plot_index += 1

        self.select(plot_view)


class Dotplot_View(tk.Frame):
    def __init__(self, master: Dotplot_Page, display_manager: Blast_Display_Manager, title: str, **kwargs):
        super().__init__(master=master, **kwargs)

        self.master = master
        self.title = title
        self.display_manager = display_manager

        self.query_cog = None
        self.subject_cog = None
        self.current_image: Image.Image | None = None

        self.setup = False

        self._page_buildup()

    def _page_buildup(self):
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(self.control_frame, text="Blast E-value").pack(side=tk.LEFT)

        self.evalue_slider = ttk.Scale(self.control_frame, from_=-100, to=0,
                                       orient="horizontal", command=self.update_plot_event)
        self.evalue_slider.set(-10)
        self.evalue_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.evalue_label = ttk.Label(self.control_frame, text="1e-10")
        self.evalue_label.pack(side=tk.LEFT)

        if self.display_manager.q_rpblast is not None:
            ttk.Label(self.control_frame, text="Query COG").pack(side=tk.LEFT)
            self.query_cog = ttk.Combobox(
                self.control_frame,
                values=self._extract_cogs(self.display_manager.q_rpblast),
                state="readonly", width=6)
            self.query_cog.pack(side=tk.LEFT)
            self.query_cog.bind("<<ComboboxSelected>>", self.update_plot_event)

        if self.display_manager.s_rpblast is not None:
            ttk.Label(self.control_frame, text="Subject COG").pack(side=tk.LEFT)
            self.subject_cog = ttk.Combobox(
                self.control_frame,
                values=self._extract_cogs(self.display_manager.s_rpblast),
                state="readonly", width=6)
            self.subject_cog.pack(side=tk.LEFT)
            self.subject_cog.bind("<<ComboboxSelected>>", self.update_plot_event)

        ttk.Button(self.control_frame, text="Save",    command=self.save_plot).pack(side=tk.RIGHT)
        ttk.Button(self.control_frame, text="Refresh", command=self.update_plot).pack(side=tk.RIGHT)
        ttk.Button(self.control_frame, text="Close",   command=self.kill_yourself).pack(side=tk.RIGHT)

        self.image_label = ttk.Label(self)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.master.add(self, text=self.title)

        self.setup = True

    @staticmethod
    def _extract_cogs(rps_table: RPSBlast_Results_Table):
        if rps_table.shape[1] < 4:
            return []
        codes = rps_table[:, 3]
        return sorted(c for c in set(codes) if c in _VALID_COG_CODES)

    def kill_yourself(self):
        current = self.master.index(self)
        self.master.forget(current)
        self.destroy()

    def render_figure_to_photo(self, fig):
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        buffer.seek(0)
        self.current_image = Image.open(buffer)
        return ImageTk.PhotoImage(self.current_image)

    def save_plot(self):
        if self.current_image is None:
            return
        try:
            path = filedialog.asksaveasfilename(
                initialfile=self.title,
                title="Save plot as",
                defaultextension=".png",
                filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("All files", "*.*")])
            if path:
                self.current_image.save(path)
        except Exception:
            return

    def update_plot_event(self, event):
        if self.setup:
            self.update_plot()

    def update_plot(self):
        exp = int(self.evalue_slider.get())
        evalue = 10 ** exp
        self.evalue_label.configure(text=f"1e{exp}")

        q_filter = None
        if self.query_cog is not None:
            selected = self.query_cog.get()
            if selected:
                q_filter = ([selected], 1e-10)

        s_filter = None
        if self.subject_cog is not None:
            selected = self.subject_cog.get()
            if selected:
                s_filter = ([selected], 1e-10)

        self.display_manager.get_display_data(evalue=evalue, q_filter_params=q_filter, s_filter_params=s_filter)

        fig = self.display_manager.display_dotplot()

        photo = self.render_figure_to_photo(fig)

        self.image_label.configure(image=photo)
        self.image_label.image = photo

        plt.close(fig)