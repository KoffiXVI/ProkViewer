from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from database_maintenance_functions import Database_Ops_Handler
from database_constants import NAME, TAXID
from analysis_classes import Genome
from custom_containers import Table, add_title_card

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from page_notebook import PageViews

_DUMMY_PREFIX = "_dummy_"
_ROOT_TAXID = 1


class Taxonomy_Breadcrumb(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._widgets: list[tk.Widget] = []

    def update_path(self, taxid: int | str):
        self.clear()
        try:
            history = Database_Ops_Handler().find_taxon_history(taxid)
        except Exception as e:
            print(e)
            return

        for i, (tid, name, _) in enumerate(reversed(history)):
            if i:
                sep = ttk.Label(self, text=" › ")
                sep.pack(side=tk.LEFT)
                self._widgets.append(sep)

            lbl = ttk.Label(self, text=name, foreground="blue", cursor="hand2")
            lbl.pack(side=tk.LEFT)
            lbl.bind("<Button-1>", lambda e, t=tid: self._jump(t))
            self._widgets.append(lbl)

    def _jump(self, taxid):
        page: Phylogeny_Page = self.master.master
        page.tree_panel.navigate_to(taxid)

    def clear(self):
        for w in self._widgets:
            w.destroy()
        self._widgets.clear()


class Phylogeny_Top_Bar(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master: Phylogeny_Page = master
        self._page_buildup()

    def _page_buildup(self):
        search_row = tk.Frame(self)
        search_row.pack(side=tk.TOP, fill=tk.X, padx=4, pady=2)

        ttk.Label(search_row, text="Jump to taxon:").pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        tk.Entry(search_row, textvariable=self.search_var).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        self.search_option = tk.StringVar(value=NAME)
        ttk.Radiobutton(search_row, text="By Name",  value=NAME,  variable=self.search_option).pack(side=tk.LEFT)
        ttk.Radiobutton(search_row, text="By TaxID", value=TAXID, variable=self.search_option).pack(side=tk.LEFT)
        ttk.Button(search_row, text="Go",    command=self._jump_to_taxon).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_row, text="Reset", command=self._reset).pack(side=tk.LEFT)

        crumb_row = tk.Frame(self)
        crumb_row.pack(side=tk.TOP, fill=tk.X, padx=4)
        ttk.Label(crumb_row, text="Path: ").pack(side=tk.LEFT)
        self.breadcrumb = Taxonomy_Breadcrumb(crumb_row)
        self.breadcrumb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X, pady=2)

    def _jump_to_taxon(self):
        query = self.search_var.get().strip()
        if not query:
            return

        if self.search_option.get() == TAXID:
            try:
                taxid = int(query)
            except ValueError:
                messagebox.showwarning(message="Please enter a valid TaxID number.", icon="warning")
                return
            self.master.tree_panel.navigate_to(taxid)
        else:
            res = Database_Ops_Handler().process_query(query, NAME)
            if not res:
                messagebox.showinfo(message=f"No taxon found for '{query}'.", icon="info")
                return
            self.master.tree_panel.navigate_to(res[0][1])

    def _reset(self):
        self.master.tree_panel.reset_to_root()
        self.breadcrumb.clear()
        self.master.genome_panel.clear()


class Taxonomy_Tree_Panel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        add_title_card(self, "_title", "Taxonomy Browser")
        self._page_buildup()
        self._load_root()

    def _page_buildup(self):
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill=tk.BOTH)

        self.tree = ttk.Treeview(frame, columns=("taxid",), show="tree headings", selectmode="browse")
        self.tree.heading("#0",    text="Name")
        self.tree.heading("taxid", text="TaxID")
        self.tree.column("#0",    width=200, stretch=True)
        self.tree.column("taxid", width=80, stretch=False, anchor="e", minwidth=60)

        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL,   command=self.tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewOpen>>", self._on_expand)

    def _load_root(self):
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", tk.END, iid="1", text="root", values=(_ROOT_TAXID,))
        self.tree.insert("1", tk.END, iid=f"{_DUMMY_PREFIX}1", text="")

    def reset_to_root(self):
        self._load_root()

    def _populate_children(self, parent_iid: str, taxid: int | str) -> int:
        try:
            children = Database_Ops_Handler().target_child_nodes(taxid)
        except Exception as e:
            messagebox.showerror(message=f"Failed to load children: {e}", icon="error")
            return 0

        for child_taxid, child_name in children:
            iid = str(child_taxid)
            if self.tree.exists(iid):
                continue
            self.tree.insert(parent_iid, tk.END, iid=iid, text=child_name, values=(child_taxid,))
            self.tree.insert(iid, tk.END, iid=f"{_DUMMY_PREFIX}{child_taxid}", text="")

        return len(children)

    def _on_expand(self, event):
        node = self.tree.focus()
        children = self.tree.get_children(node)

        if len(children) == 1 and children[0].startswith(_DUMMY_PREFIX):
            self.tree.delete(children[0])
            taxid = self.tree.set(node, "taxid")
            count = self._populate_children(node, taxid)
            if count == 0:
                self.tree.item(node, open=False)

    def navigate_to(self, taxid: int | str):
        try:
            history = Database_Ops_Handler().find_taxon_history(taxid)
        except Exception as e:
            print(e)
            return

        path = list(reversed(history))

        if not self.tree.exists("1"):
            self._load_root()

        parent_iid = "1"

        for tid, _, _ in path[1:]:
            iid = str(tid)
            if not self.tree.exists(iid):
                dummy = f"{_DUMMY_PREFIX}{self.tree.set(parent_iid, 'taxid') or parent_iid}"
                if self.tree.exists(dummy):
                    self.tree.delete(dummy)
                parent_taxid = self.tree.set(parent_iid, "taxid") or parent_iid
                self._populate_children(parent_iid, parent_taxid)

            if self.tree.exists(iid):
                self.tree.item(iid, open=True)
                parent_iid = iid

        final_iid = str(taxid)
        if self.tree.exists(final_iid):
            self.tree.selection_set(final_iid)
            self.tree.focus(final_iid)
            self.tree.see(final_iid)


class Taxonomy_Node_Genome_Table(Table):
    def __init__(self, master, data=None, **kwargs):
        columns  = ("name", "taxid", "count", "assembly", "link")
        headings = ("Name", "TaxID", "Genomes", "Assembly", "Link")
        user_seen = ("name", "taxid", "count", "assembly")
        super().__init__(master, columns, headings, data, show="headings", displaycolumns=user_seen, **kwargs)
        self.frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)


class Taxonomy_Genome_Actions(tk.Frame):
    def __init__(self, master, reference: Taxonomy_Node_Genome_Table, phylogeny_page, **kwargs):
        super().__init__(master, **kwargs)
        self.reference = reference
        self.page: Phylogeny_Page = phylogeny_page

        self.query_btn   = ttk.Button(self, text="Set as Query",   state=tk.DISABLED, command=self.set_query)
        self.subject_btn = ttk.Button(self, text="Set as Subject", state=tk.DISABLED, command=self.set_subject)
        self.query_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=2)
        self.subject_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=2)

        self.reference.bind("<<TreeviewSelect>>", self._on_select)

    def _on_select(self, event):
        selected = self.reference.focus()
        state = tk.NORMAL if selected else tk.DISABLED
        self.query_btn.config(state=state)
        self.subject_btn.config(state=state)

    def _selected_genome(self) -> Genome | None:
        selected = self.reference.focus()
        if not selected:
            return None
        name, taxid, count, assembly, link = self.reference.item(selected, "values")
        return Genome(name, taxid, count, assembly, link)

    def set_query(self):
        genome = self._selected_genome()
        if genome:
            notebook: PageViews = self.page.master
            notebook.analysis_page.set_query_genome(genome)
            notebook.select(notebook.analysis_page)

    def set_subject(self):
        genome = self._selected_genome()
        if genome:
            notebook: PageViews = self.page.master
            notebook.analysis_page.set_subject_genome(genome)
            notebook.select(notebook.analysis_page)


class Taxonomy_Genome_Panel(tk.Frame):
    def __init__(self, master, phylogeny_page, **kwargs):
        super().__init__(master, **kwargs)
        add_title_card(self, "_title", "Genomes under selected node")

        self.table = Taxonomy_Node_Genome_Table(self)
        self.actions = Taxonomy_Genome_Actions(self, self.table, phylogeny_page)
        self.actions.pack(side=tk.BOTTOM, fill=tk.X)

    def load_genomes(self, taxid: int | str, node_name: str):
        self.table.cleanup()
        try:
            res = Database_Ops_Handler().query_by_node(taxid)
        except Exception as e:
            messagebox.showerror(message=f"Error querying node genomes: {e}", icon="error")
            return
        if res:
            self.table.insert_rows(res)

    def clear(self):
        self.table.cleanup()


class Phylogeny_Page(tk.Frame):
    def __init__(self, master: PageViews, title="Phylogeny"):
        super().__init__(master=master)
        self.master = master
        self.title = title
        self._page_buildup()

    def _page_buildup(self):
        self.top_bar = Phylogeny_Top_Bar(self)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        self.content = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        self.content.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.tree_panel   = Taxonomy_Tree_Panel(self.content)
        self.genome_panel = Taxonomy_Genome_Panel(self.content, phylogeny_page=self)

        self.content.add(self.tree_panel,   minsize=220, width=280)
        self.content.add(self.genome_panel, minsize=400)

        self.tree_panel.tree.bind("<<TreeviewSelect>>", self._on_node_select)

        self.master.add(self, text=self.title)

    def _on_node_select(self, event):
        selected = self.tree_panel.tree.focus()
        if not selected:
            return

        taxid = self.tree_panel.tree.set(selected, "taxid")
        name  = self.tree_panel.tree.item(selected, "text")

        self.top_bar.breadcrumb.update_path(taxid)
        self.genome_panel.load_genomes(taxid, name)
