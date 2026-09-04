"""All past quiz attempts of one student."""

import tkinter.messagebox as msg
from tkinter import ttk

import customtkinter as ctk

from connection import connect
from quizresult import quizResult

# --- COLOR PALETTE & STYLES ---
COLOR_BG = "#0D0E15"
COLOR_CARD = "#161822"
COLOR_CARD_BORDER = "#26293B"
COLOR_ACCENT = "#6366F1"  # Indigo accent
COLOR_ACCENT_HOVER = "#4F46E5"
COLOR_TEXT_PRIMARY = "#F3F4F6"
COLOR_TEXT_SECONDARY = "#9CA3AF"
COLOR_SUCCESS = "#10B981"
COLOR_DANGER = "#EF4444"
COLOR_ROW_ALT = "#1C1E2D"


class quizHistory:
    def __init__(self, studentId, parent=None):
        self.studentId = studentId

        # Apply Global Dark Appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Handle top-level modal parent relationship
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)
        else:
            self.root = ctk.CTk()

        self.root.title("Quiz History | AI College Agent")
        self.root.geometry("1180x750")
        self.root.configure(fg_color=COLOR_BG)
        self.root.after(0, lambda: self.root.state("zoomed"))

        # Force window focus
        self.root.lift()
        self.root.focus_force()

        # Database Connection
        self.conn = connect()
        self.cr = self.conn.cursor()

        # Grid Configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # Header
        self.root.grid_rowconfigure(1, weight=0)  # Stats cards
        self.root.grid_rowconfigure(2, weight=0)  # Action bar
        self.root.grid_rowconfigure(3, weight=10) # Table area

        self.apply_table_style()
        self.build_header()
        self.build_summary_cards()
        self.build_action_bar()
        self.build_history_table()

        self.getHistory()

        # Execute event loop only when run direct
        if not parent:
            self.root.mainloop()

    def build_header(self):
        """Builds top header title and subtitle banner."""
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 5))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="My Quiz History",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="Double click any row or select an attempt to view detailed analytical results.",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

    def build_summary_cards(self):
        """Displays key metrics in styled KPI cards using database aggregations."""
        q = """SELECT COUNT(*), ROUND(AVG(score), 1), MAX(score)
               FROM quiz_attempts WHERE student_id = %s"""
        self.cr.execute(q, (self.studentId,))
        attempts, average, best = self.cr.fetchone()

        cards_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=5)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        metrics = [
            ("Total Attempts", str(attempts or 0), COLOR_ACCENT),
            ("Average Score", f"{average}%" if average is not None else "0%", "#3B82F6"),
            ("Best Score", f"{best}%" if best is not None else "0%", COLOR_SUCCESS)
        ]

        for index, (label, val, indicator_color) in enumerate(metrics):
            card = ctk.CTkFrame(
                cards_frame,
                fg_color=COLOR_CARD,
                corner_radius=12,
                border_width=1,
                border_color=COLOR_CARD_BORDER
            )
            card.grid(row=0, column=index, padx=8, pady=5, sticky="ew")

            strip = ctk.CTkFrame(card, width=4, fg_color=indicator_color, corner_radius=2)
            strip.pack(side="left", fill="y", padx=(10, 0), pady=10)

            info_container = ctk.CTkFrame(card, fg_color="transparent")
            info_container.pack(side="left", fill="both", expand=True, padx=15, pady=10)

            val_lbl = ctk.CTkLabel(
                info_container,
                text=val,
                font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w"
            )
            val_lbl.pack(anchor="w")

            lbl = ctk.CTkLabel(
                info_container,
                text=label,
                font=ctk.CTkFont(family="Arial", size=12),
                text_color=COLOR_TEXT_SECONDARY,
                anchor="w"
            )
            lbl.pack(anchor="w")

    def build_action_bar(self):
        """Action toolbar containing controls for interacting with table rows."""
        bar = ctk.CTkFrame(self.root, fg_color="transparent")
        bar.grid(row=2, column=0, sticky="ew", padx=30, pady=5)

        ctk.CTkButton(
            bar,
            text="🔄  Refresh",
            width=120,
            height=36,
            corner_radius=8,
            fg_color="#272A3C",
            hover_color="#32364D",
            text_color=COLOR_TEXT_PRIMARY,
            command=self.getHistory
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            bar,
            text="📊  View Result",
            width=140,
            height=36,
            corner_radius=8,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.openResult
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            bar,
            text="✕  Close",
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#2A1B24",
            text_color=COLOR_DANGER,
            border_width=1,
            border_color=COLOR_DANGER,
            command=self.root.destroy
        ).pack(side="right")

    def build_history_table(self):
        """Configures expandable, large-format table in container."""
        table_container = ctk.CTkFrame(
            self.root,
            fg_color=COLOR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        table_container.grid(row=3, column=0, sticky="nsew", padx=30, pady=(5, 20))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        columns = ("id", "lecture", "total", "correct", "score", "grade", "on")
        self.table = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")

        headers = [
            ("id", "Attempt ID", 110),
            ("lecture", "Lecture Module Title", 380),
            ("total", "Questions", 120),
            ("correct", "Correct", 120),
            ("score", "Score %", 130),
            ("grade", "Result", 120),
            ("on", "Attempted On", 200)
        ]

        for key, title, width in headers:
            self.table.heading(key, text=title, anchor="center")
            self.table.column(key, width=width, anchor="center", stretch=(key == "lecture"))

        scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)

        self.table.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        scroll.grid(row=0, column=1, sticky="ns", pady=12, padx=(0, 12))

        self.table.bind("<Double-1>", lambda event: self.openResult())

    def apply_table_style(self):
        """Generous row height and large typography for Treeview."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=COLOR_CARD,
            foreground=COLOR_TEXT_PRIMARY,
            fieldbackground=COLOR_CARD,
            rowheight=46,
            font=("Segoe UI", 11),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#1E202E",
            foreground="#A5B4FC",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padding=10
        )

        style.map(
            "Treeview",
            background=[("selected", COLOR_ACCENT)],
            foreground=[("selected", "#FFFFFF")]
        )

    def getHistory(self):
        """Fetches data from MySQL and renders dynamic rows with pass/fail logic."""
        q = """SELECT a.id, l.title, a.total_questions, a.correct_answers,
                      a.score, a.attempted_on
               FROM quiz_attempts a JOIN lectures l ON l.id = a.lecture_id
               WHERE a.student_id = %s ORDER BY a.attempted_on DESC"""
        self.cr.execute(q, (self.studentId,))

        for row in self.table.get_children():
            self.table.delete(row)

        attempts = self.cr.fetchall()

        self.table.tag_configure("even", background=COLOR_CARD)
        self.table.tag_configure("odd", background=COLOR_ROW_ALT)

        for index, (attemptId, lecture, total, correct, score, on) in enumerate(attempts):
            grade = "PASS" if score >= 40 else "FAIL"
            row_tag = "even" if index % 2 == 0 else "odd"

            formatted_score = f"{score}%"
            formatted_date = str(on) if on else "-"

            self.table.insert(
                "",
                "end",
                values=(attemptId, lecture, total, correct, formatted_score, grade, formatted_date),
                tags=(row_tag,)
            )

    def openResult(self):
        """Opens detailed results page safely in front of quizHistory."""
        selected = self.table.selection()
        if not selected:
            msg.showwarning("Selection Missing", "Please select a quiz attempt from the list.", parent=self.root)
            return

        data = self.table.item(selected[0])["values"]
        attempt_id = data[0]

        # Pass parent reference so quizResult modal stays attached on top
        quizResult(attempt_id, parent=self.root)


if __name__ == "__main__":
    quizHistory(1)