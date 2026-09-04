"""Admin review of the AI generated important notes.

rank_score is the cosine similarity of that sentence with the centroid of the
whole lecture, which is exactly why the summarizer picked it.
"""

import tkinter.ttk as ttk
import tkinter.messagebox as msg
import customtkinter as ctk

from connection import connect

# Configure global CustomTkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class viewNotes:
    def __init__(self, parent=None):
        # Support Toplevel window if embedded, otherwise standalone main root
        if parent:
            self.root = ctk.CTkToplevel(parent)
        else:
            self.root = ctk.CTk()

        self.root.title("AI Generated Important Notes")
        self.root.geometry("1100x650")
        self.root.configure(fg_color="#0A0B10")
        self.root.state("zoomed")

        # Database Connection
        self.conn = connect()
        self.cr = self.conn.cursor()

        # Build UI Components
        self.create_header()
        self.create_control_bar()
        self.create_table_card()
        self.apply_treeview_styles()

        # Initial Data Load
        lectures = self.lectureValues()
        if lectures:
            self.lectureBox.set(lectures[0])
            self.lectureChanged(lectures[0])

        if not parent:
            self.root.mainloop()

    def create_header(self):
        """Header section with sleek title and subheader."""
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(20, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="AI Generated Important Notes",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="Extractive summarization using TF-IDF and cosine similarity",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color="#8A8D9B"
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

    def create_control_bar(self):
        """Control frame containing combobox filter and animated buttons."""
        bar = ctk.CTkFrame(
            self.root,
            fg_color="#12131C",
            corner_radius=12,
            border_width=1,
            border_color="#1F222E"
        )
        bar.pack(fill="x", padx=40, pady=15, ipady=5)

        # Centered Inner Container
        control_inner = ctk.CTkFrame(bar, fg_color="transparent")
        control_inner.pack(anchor="center", pady=10)

        # Label
        lbl = ctk.CTkLabel(
            control_inner,
            text="Select Lecture:",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color="#E0E0E0"
        )
        lbl.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Custom Combo Box
        self.lectureBox = ctk.CTkComboBox(
            control_inner,
            width=380,
            height=38,
            corner_radius=8,
            fg_color="#1A1C23",
            button_color="#3F51B5",
            button_hover_color="#303F9F",
            dropdown_fg_color="#1A1C23",
            dropdown_hover_color="#282B36",
            dropdown_text_color="#FFFFFF",
            border_width=1,
            border_color="#2E3240",
            font=ctk.CTkFont(family="Arial", size=12),
            values=self.lectureValues(),
            command=self.lectureChanged
        )
        self.lectureBox.grid(row=0, column=1, padx=10)

        # Animated Refresh Button
        self.btn_refresh = ctk.CTkButton(
            control_inner,
            text="🔄  Refresh",
            width=130,
            height=38,
            corner_radius=8,
            fg_color="#3F51B5",
            hover_color="#303F9F",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            command=self.animate_refresh
        )
        self.btn_refresh.grid(row=0, column=2, padx=10)

        # Animated Danger Delete Button
        self.btn_delete = ctk.CTkButton(
            control_inner,
            text="🗑  Delete Note",
            width=140,
            height=38,
            corner_radius=8,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            command=self.animate_delete
        )
        self.btn_delete.grid(row=0, column=3, padx=10)

    def create_table_card(self):
        """Card wrapper holding the modern Treeview table."""
        wrapper = ctk.CTkFrame(
            self.root,
            fg_color="#12131C",
            corner_radius=14,
            border_width=1,
            border_color="#1F222E"
        )
        wrapper.pack(fill="both", expand=True, padx=40, pady=(0, 25))

        self.table = ttk.Treeview(
            wrapper,
            columns=("id", "no", "note", "score"),
            show="headings"
        )

        columns_config = [
            ("id", "ID", 70, "center"),
            ("no", "#", 50, "center"),
            ("note", "Important Note", 880, "w"),
            ("score", "Score", 110, "center")
        ]

        for key, title, width, anchor in columns_config:
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor=anchor, stretch=(key == "note"))

        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y", pady=14, padx=(0, 14))
        self.table.pack(fill="both", expand=True, padx=(14, 0), pady=14)

    def apply_treeview_styles(self):
        """Custom dark styling for standard ttk.Treeview."""
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            rowheight=36,
            font=("Arial", 11),
            background="#1A1C23",
            foreground="#E0E0E0",
            fieldbackground="#1A1C23",
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold"),
            background="#252836",
            foreground="#8A8D9B",
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#3F51B5")],
            foreground=[("selected", "#FFFFFF")]
        )

    # --- Animated Button Handlers ---
    def animate_refresh(self):
        """Micro-animation effect on Refresh button click."""
        self.btn_refresh.configure(fg_color="#283593")
        self.root.after(150, lambda: self.btn_refresh.configure(fg_color="#3F51B5"))
        self.refreshData()

    def animate_delete(self):
        """Micro-animation effect on Delete button click."""
        self.btn_delete.configure(fg_color="#A93226")
        self.root.after(150, lambda: self.btn_delete.configure(fg_color="#E74C3C"))
        self.deleteNote()

    # --- Data Methods ---
    def lectureValues(self):
        try:
            self.cr.execute("SELECT id, title FROM lectures ORDER BY id")
            return [f"{row[0]} - {row[1]}" for row in self.cr.fetchall()]
        except Exception as e:
            msg.showerror("Database Error", f"Failed to fetch lectures: {e}", parent=self.root)
            return []

    def currentLectureId(self):
        value = self.lectureBox.get().strip()
        if not value:
            return None
        try:
            return int(value.split(" - ")[0])
        except ValueError:
            return None

    def lectureChanged(self, _value=None):
        lectureId = self.currentLectureId()

        # Clear existing rows
        for row in self.table.get_children():
            self.table.delete(row)

        if lectureId is None:
            return

        q = """SELECT id, note_text, rank_score FROM notes 
               WHERE lecture_id = %s ORDER BY sentence_index"""
        try:
            self.cr.execute(q, (lectureId,))
            for number, (noteId, text, score) in enumerate(self.cr.fetchall(), start=1):
                formatted_score = f"{score:.3f}" if score is not None else "N/A"
                self.table.insert("", "end", values=(noteId, number, text, formatted_score))
        except Exception as e:
            msg.showerror("Database Error", f"Failed to load notes: {e}", parent=self.root)

    def refreshData(self):
        lectures = self.lectureValues()
        self.lectureBox.configure(values=lectures)
        if lectures and not self.lectureBox.get():
            self.lectureBox.set(lectures[0])
        self.lectureChanged()

    def deleteNote(self):
        selected = self.table.selection()
        if not selected:
            msg.showwarning("Warning", "Please select a note first", parent=self.root)
            return

        data = self.table.item(selected[0])["values"]

        if not msg.askyesno("Confirm", "Delete this note?", parent=self.root):
            return

        try:
            self.cr.execute("DELETE FROM notes WHERE id = %s", (data[0],))
            self.conn.commit()
            self.lectureChanged()
            msg.showinfo("Success", "Note deleted successfully", parent=self.root)
        except Exception as e:
            self.conn.rollback()
            msg.showerror("Database Error", f"Failed to delete note: {e}", parent=self.root)


if __name__ == "__main__":
    viewNotes()