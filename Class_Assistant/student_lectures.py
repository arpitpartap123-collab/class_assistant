"""Lectures of the student's own course, with open and download of the PDF."""

import os
import shutil
import tkinter.ttk as ttk
from tkinter.filedialog import asksaveasfilename

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from connection import connect
from ai_pipeline import PDF_DIR

# Configure CustomTkinter default theme settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Theme Color Palette based on dashboard UI
BG_DARK = "#0f0e17"
CARD_BG = "#16151f"
CARD_INNER = "#1e1c2a"
BORDER_COLOR = "#2a273a"
ACCENT_PURPLE = "#7b5bf2"
ACCENT_BLUE = "#3b82f6"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#94a3b8"
SUCCESS_GREEN = "#10b981"
WARNING_AMBER = "#f59e0b"


class studentLectures:
    def __init__(self, studentId):
        self.studentId = studentId

        self.root = ctk.CTk()
        self.root.title("My Lectures")
        self.root.configure(fg_color=BG_DARK)
        self.root.state("zoomed")

        # Force window to top
        self.root.lift()
        self.root.focus_force()

        self.conn = connect()
        self.cr = self.conn.cursor()

        # Header Title and Subtitle
        ctk.CTkLabel(
            self.root,
            text="My Lectures",
            font=("Segoe UI", 26, "bold"),
            text_color=TEXT_WHITE
        ).pack(pady=(20, 2))

        ctk.CTkLabel(
            self.root,
            text="Open or download the lecture PDF",
            font=("Segoe UI", 13),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 15))

        self.style_treeview()

        # Top Controls Bar Frame
        bar = ctk.CTkFrame(self.root, fg_color="transparent")
        bar.pack(pady=10)

        self.searchField = ctk.CTkEntry(
            bar,
            width=320,
            height=38,
            placeholder_text="Search lecture title",
            fg_color=CARD_BG,
            border_color=BORDER_COLOR,
            text_color=TEXT_WHITE,
            placeholder_text_color=TEXT_MUTED,
            corner_radius=8
        )
        self.searchField.grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            bar,
            text="Search",
            width=120,
            height=38,
            fg_color=ACCENT_PURPLE,
            hover_color="#6d42e2",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.searchLectures
        ).grid(row=0, column=1, padx=8)

        ctk.CTkButton(
            bar,
            text="Refresh",
            width=120,
            height=38,
            fg_color=ACCENT_BLUE,
            hover_color="#2563eb",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.refreshData
        ).grid(row=0, column=2, padx=8)

        ctk.CTkButton(
            bar,
            text="Open PDF",
            width=130,
            height=38,
            fg_color=SUCCESS_GREEN,
            hover_color="#059669",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.openPdf
        ).grid(row=0, column=3, padx=8)

        ctk.CTkButton(
            bar,
            text="Download PDF",
            width=150,
            height=38,
            fg_color=WARNING_AMBER,
            hover_color="#d97706",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.downloadPdf
        ).grid(row=0, column=4, padx=8)

        # Table Outer Wrapper
        wrapper = ctk.CTkFrame(
            self.root,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER_COLOR
        )
        wrapper.pack(fill="both", expand=True, padx=40, pady=(15, 30))

        columns = ("id", "title", "description", "pdf", "notes", "questions", "created")
        self.table = ttk.Treeview(wrapper, columns=columns, show="headings")
        for key, title, width, anchor in [("id", "ID", 60, "center"),
                                          ("title", "Lecture", 220, "w"),
                                          ("description", "Description", 300, "w"),
                                          ("pdf", "PDF File", 220, "w"),
                                          ("notes", "Notes", 80, "center"),
                                          ("questions", "Questions", 90, "center"),
                                          ("created", "Uploaded", 160, "center")]:
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor=anchor)

        # Custom CTkScrollbar for dark theme alignment
        scroll = ctk.CTkScrollbar(wrapper, orientation="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", pady=14, padx=(0, 10))
        self.table.pack(fill="both", expand=True, padx=14, pady=14)

        # Define alternating row styles (Zebra striping)
        self.table.tag_configure("evenrow", background=CARD_BG, foreground=TEXT_WHITE)
        self.table.tag_configure("oddrow", background=CARD_INNER, foreground=TEXT_WHITE)

        self.getLectures()
        self.root.mainloop()

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Table Body Configuration
        style.configure(
            "Treeview",
            background=CARD_BG,
            foreground=TEXT_WHITE,
            fieldbackground=CARD_BG,
            rowheight=38,
            font=("Segoe UI", 11),
            borderwidth=0
        )

        # Header Configuration
        style.configure(
            "Treeview.Heading",
            background=CARD_INNER,
            foreground=ACCENT_PURPLE,
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            relief="flat"
        )

        # Selection & Hover States
        style.map("Treeview", background=[("selected", ACCENT_PURPLE)], foreground=[("selected", TEXT_WHITE)])
        style.map("Treeview.Heading", background=[("active", BORDER_COLOR)])

    def getLectures(self, keyword=None):
        base = """SELECT l.id, l.title, l.description, l.pdf_file,
                         (SELECT COUNT(*) FROM notes n WHERE n.id = l.id),
                         (SELECT COUNT(*) FROM questions q WHERE q.id = l.id),
                         l.created_at
                  FROM lectures l
                  JOIN students s ON s.course_id = l.course_id
                  WHERE s.id = %s"""

        if keyword:
            self.cr.execute(base + " AND l.title LIKE %s ORDER BY l.id",
                            (self.studentId, f"%{keyword}%"))
        else:
            self.cr.execute(base + " ORDER BY l.id", (self.studentId,))

        for row in self.table.get_children():
            self.table.delete(row)

        for i, record in enumerate(self.cr.fetchall()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.table.insert("", "end", values=record, tags=(tag,))

    def searchLectures(self):
        self.getLectures(self.searchField.get().strip())

    def refreshData(self):
        self.searchField.delete(0, "end")
        self.getLectures()

    def selectedRow(self):
        selected = self.table.selection()
        if not selected:
            CTkMessagebox(title="Warning", message="Please select a lecture first", icon="warning")
            return None
        return self.table.item(selected[0])["values"]

    def sourcePath(self, data):
        path = os.path.join(PDF_DIR, str(data[3]))
        if not os.path.exists(path):
            CTkMessagebox(title="Error", message="The lecture PDF is missing on the server", icon="cancel")
            return None
        return path

    def openPdf(self):
        data = self.selectedRow()
        if data is None:
            return

        path = self.sourcePath(data)
        if path:
            os.startfile(os.path.abspath(path))

    def downloadPdf(self):
        data = self.selectedRow()
        if data is None:
            return

        path = self.sourcePath(data)
        if path is None:
            return

        target = asksaveasfilename(parent=self.root, defaultextension=".pdf",
                                   filetypes=[("PDF files", "*.pdf")],
                                   initialfile=str(data[3]))
        if not target:
            return

        try:
            shutil.copy(path, target)
            CTkMessagebox(title="Downloaded", message=f"Saved to\n{target}", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Could not save the file.\n\n{e}", icon="cancel")


if __name__ == "__main__":
    studentLectures(1)