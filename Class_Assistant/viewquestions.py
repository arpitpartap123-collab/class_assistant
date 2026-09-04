"""Admin review of the AI generated questionnaire.

Double click a question to correct the wording or the answer before students
attempt it.
"""

import tkinter.ttk as ttk
import tkinter.messagebox as msg
import customtkinter as ctk
from connection import connect

# Modern Theme Palette Constants
COLOR_BG_DARK = "#0D0E15"
COLOR_SIDEBAR = "#13151F"
COLOR_CARD = "#1A1C29"
COLOR_CARD_HOVER = "#222536"
COLOR_ACCENT = "#4361EE"
COLOR_ACCENT_HOVER = "#3046B5"
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#8A8D9B"
COLOR_BORDER = "#2A2D3D"
COLOR_RED = "#E74C3C"
COLOR_RED_HOVER = "#C0392B"
COLOR_GREEN = "#2ECC71"
COLOR_GREEN_HOVER = "#27AE60"
COLOR_PURPLE = "#6C5CE7"
COLOR_PURPLE_HOVER = "#5B4BC4"


class viewQuestions:
    def __init__(self, parent_root=None):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        if parent_root:
            self.root = ctk.CTkToplevel(parent_root)
        else:
            self.root = ctk.CTk()

        self.root.title("AI Generated Questions - Admin Review")
        self.root.geometry("1180x720")
        self.root.configure(fg_color=COLOR_BG_DARK)
        self.root.after(0, lambda: self.root.state("zoomed"))

        self.conn = connect()
        self.cr = self.conn.cursor()

        self.apply_table_style()
        self.build_ui()

        lectures = self.lectureValues()
        if lectures:
            self.lectureBox.set(lectures[0])
            self.lectureChanged(lectures[0])

        if not parent_root:
            self.root.mainloop()

    def build_ui(self):
        # ---- HEADER CARD ----
        self.header_card = ctk.CTkFrame(
            self.root, fg_color=COLOR_CARD, corner_radius=14,
            border_width=1, border_color=COLOR_BORDER
        )
        self.header_card.pack(fill="x", padx=35, pady=(25, 15))

        lbl_title = ctk.CTkLabel(
            self.header_card, text="QUESTIONS",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        lbl_title.pack(pady=(18, 4))

        lbl_subtitle = ctk.CTkLabel(
            self.header_card, text="Manage and edit AI-generated questionnaire for students",
            font=ctk.CTkFont(family="Arial", size=12),
            text_color=COLOR_TEXT_SECONDARY
        )
        lbl_subtitle.pack(pady=(0, 4))

        lbl_hint = ctk.CTkLabel(
            self.header_card, text="Right click or double click a question for quick edits",
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            text_color=COLOR_ACCENT
        )
        lbl_hint.pack(pady=(0, 18))

        # ---- TOP ACTION / FILTER BAR ----
        self.action_bar = ctk.CTkFrame(
            self.root, fg_color=COLOR_CARD, corner_radius=12,
            border_width=1, border_color=COLOR_BORDER
        )
        self.action_bar.pack(fill="x", padx=35, pady=(0, 15), ipady=8)

        ctk.CTkLabel(
            self.action_bar, text="Lecture:",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(20, 10))

        self.lectureBox = ctk.CTkComboBox(
            self.action_bar, width=380, height=36,
            values=self.lectureValues(), command=self.lectureChanged,
            fg_color=COLOR_BG_DARK, text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_BORDER, dropdown_fg_color=COLOR_CARD,
            dropdown_text_color=COLOR_TEXT_PRIMARY, button_color=COLOR_ACCENT,
            button_hover_color=COLOR_ACCENT_HOVER, corner_radius=8
        )
        self.lectureBox.pack(side="left", padx=(0, 15))

        btn_refresh = ctk.CTkButton(
            self.action_bar, text="Refresh", width=110, height=36, corner_radius=8,
            fg_color=COLOR_PURPLE, hover_color=COLOR_PURPLE_HOVER,
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            command=self.refreshData
        )
        btn_refresh.pack(side="left", padx=6)

        btn_delete = ctk.CTkButton(
            self.action_bar, text="Delete Question", width=140, height=36, corner_radius=8,
            fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER,
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            command=self.deleteQuestion
        )
        btn_delete.pack(side="left", padx=6)

        # ---- TREEVIEW TABLE WRAPPER ----
        wrapper = ctk.CTkFrame(
            self.root, fg_color=COLOR_CARD, corner_radius=14,
            border_width=1, border_color=COLOR_BORDER
        )
        wrapper.pack(fill="both", expand=True, padx=35, pady=(0, 25))

        columns = ("id", "type", "question", "a", "b", "c", "d", "answer", "marks")
        self.table = ttk.Treeview(wrapper, columns=columns, show="headings")

        column_configs = [
            ("id", "ID", 55, "center"),
            ("type", "Type", 110, "center"),
            ("question", "Question Text", 450, "w"),
            ("a", "A", 100, "center"),
            ("b", "B", 100, "center"),
            ("c", "C", 100, "center"),
            ("d", "D", 100, "center"),
            ("answer", "Correct Answer", 160, "center"),
            ("marks", "Marks", 65, "center")
        ]

        for key, title, width, anchor in column_configs:
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor=anchor)

        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y", padx=(0, 8), pady=12)
        self.table.pack(fill="both", expand=True, padx=(12, 0), pady=12)

        self.table.bind("<Double-1>", self.openUpdateWindow)

    def apply_table_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=36,
            font=("Arial", 10),
            background=COLOR_CARD,
            foreground=COLOR_TEXT_PRIMARY,
            fieldbackground=COLOR_CARD,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold"),
            background=COLOR_SIDEBAR,
            foreground=COLOR_TEXT_PRIMARY,
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", COLOR_ACCENT)],
            foreground=[("selected", COLOR_TEXT_PRIMARY)]
        )

    def lectureValues(self):
        self.cr.execute("SELECT id, title FROM lectures ORDER BY id")
        return [f"{row[0]} - {row[1]}" for row in self.cr.fetchall()]

    def currentLectureId(self):
        value = self.lectureBox.get().strip()
        if not value:
            return None
        return int(value.split(" - ")[0])

    def lectureChanged(self, _value=None):
        lectureId = self.currentLectureId()

        for row in self.table.get_children():
            self.table.delete(row)

        if lectureId is None:
            return

        q = """SELECT id, question_type, question_text, option_a, option_b, option_c,
                      option_d, correct_answer, marks
               FROM questions WHERE lecture_id = %s ORDER BY question_type, id"""
        self.cr.execute(q, (lectureId,))

        for record in self.cr.fetchall():
            record = ["-" if value is None else value for value in record]
            self.table.insert("", "end", values=record)

    def refreshData(self):
        self.lectureBox.configure(values=self.lectureValues())
        self.lectureChanged()

    def deleteQuestion(self):
        selected = self.table.selection()
        if not selected:
            msg.showwarning("Warning", "Please select a question first", parent=self.root)
            return

        data = self.table.item(selected[0])["values"]

        confirm = msg.askyesno(
            "Confirm Delete",
            "Delete this question?\n\nAny student answers recorded for it will also be deleted.",
            parent=self.root
        )
        if not confirm:
            return

        self.cr.execute("DELETE FROM questions WHERE id = %s", (data[0],))
        self.conn.commit()
        self.lectureChanged()

    def openUpdateWindow(self, _event=None):
        selected = self.table.selection()
        if not selected:
            return

        data = self.table.item(selected[0])["values"]
        self.updateId = data[0]
        self.questionType = data[1]

        self.updateRoot = ctk.CTkToplevel(self.root)
        self.updateRoot.title("Edit Question")
        self.updateRoot.geometry("760x680")
        self.updateRoot.configure(fg_color=COLOR_BG_DARK)
        self.updateRoot.grab_set()

        # Header Frame
        hdr_frame = ctk.CTkFrame(self.updateRoot, fg_color=COLOR_SIDEBAR, corner_radius=0, height=70)
        hdr_frame.pack(fill="x", side="top")

        ctk.CTkLabel(
            hdr_frame, text="Edit Question",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", padx=25, pady=(12, 0))

        ctk.CTkLabel(
            hdr_frame, text=f"Question Type: {self.questionType}",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=COLOR_ACCENT
        ).pack(anchor="w", padx=25, pady=(0, 10))

        # Main Card Area
        card = ctk.CTkFrame(
            self.updateRoot, fg_color=COLOR_CARD, corner_radius=14,
            border_width=1, border_color=COLOR_BORDER
        )
        card.pack(pady=20, padx=30, fill="both", expand=True)

        ctk.CTkLabel(
            card, text="Question Text",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", padx=25, pady=(18, 4))

        self.uQuestion = ctk.CTkTextbox(
            card, width=640, height=80,
            font=ctk.CTkFont(family="Arial", size=12),
            fg_color=COLOR_BG_DARK, text_color=COLOR_TEXT_PRIMARY,
            border_width=1, border_color=COLOR_BORDER, corner_radius=8
        )
        self.uQuestion.pack(padx=25)
        self.uQuestion.insert("1.0", data[2])

        self.optionBoxes = []
        if self.questionType == "MCQ":
            grid = ctk.CTkFrame(card, fg_color="transparent")
            grid.pack(pady=10)

            for i, letter in enumerate("ABCD"):
                ctk.CTkLabel(
                    grid, text=f"Option {letter}:",
                    font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
                    text_color=COLOR_TEXT_SECONDARY
                ).grid(row=i, column=0, padx=10, pady=4, sticky="w")

                box = ctk.CTkEntry(
                    grid, width=500, height=34,
                    fg_color=COLOR_BG_DARK, text_color=COLOR_TEXT_PRIMARY,
                    border_color=COLOR_BORDER, corner_radius=6
                )
                box.grid(row=i, column=1, padx=10, pady=4)
                box.insert(0, "" if data[3 + i] == "-" else data[3 + i])
                self.optionBoxes.append(box)

        ctk.CTkLabel(
            card, text=self.answerHint(),
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w", padx=25, pady=(10, 4))

        if self.questionType == "ShortAnswer":
            self.uAnswer = ctk.CTkTextbox(
                card, width=640, height=70,
                font=ctk.CTkFont(family="Arial", size=12),
                fg_color=COLOR_BG_DARK, text_color=COLOR_TEXT_PRIMARY,
                border_width=1, border_color=COLOR_BORDER, corner_radius=8
            )
            self.uAnswer.pack(padx=25)
            self.uAnswer.insert("1.0", data[7])
        elif self.questionType == "TrueFalse":
            self.uAnswer = ctk.CTkComboBox(
                card, width=640, height=36, values=["True", "False"],
                fg_color=COLOR_BG_DARK, text_color=COLOR_TEXT_PRIMARY,
                border_color=COLOR_BORDER, dropdown_fg_color=COLOR_CARD,
                dropdown_text_color=COLOR_TEXT_PRIMARY, button_color=COLOR_ACCENT, corner_radius=8
            )
            self.uAnswer.pack(padx=25)
            self.uAnswer.set(data[7])
        else:
            self.uAnswer = ctk.CTkComboBox(
                card, width=640, height=36, values=["A", "B", "C", "D"],
                fg_color=COLOR_BG_DARK, text_color=COLOR_TEXT_PRIMARY,
                border_color=COLOR_BORDER, dropdown_fg_color=COLOR_CARD,
                dropdown_text_color=COLOR_TEXT_PRIMARY, button_color=COLOR_ACCENT, corner_radius=8
            )
            self.uAnswer.pack(padx=25)
            self.uAnswer.set(data[7])

        ctk.CTkButton(
            card, text="Save Changes", width=300, height=40, corner_radius=8,
            fg_color=COLOR_GREEN, hover_color=COLOR_GREEN_HOVER,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            command=self.updateQuestion
        ).pack(pady=(18, 18))

    def answerHint(self):
        if self.questionType == "MCQ":
            return "Correct Answer Option Letter (A, B, C, or D):"
        if self.questionType == "TrueFalse":
            return "Correct True/False Selection:"
        return "Reference Answer (Used for Cosine Similarity evaluation):"

    def readAnswer(self):
        if self.questionType == "ShortAnswer":
            return self.uAnswer.get("1.0", "end-1c").strip()
        return self.uAnswer.get().strip()

    def updateQuestion(self):
        question = self.uQuestion.get("1.0", "end-1c").strip()
        answer = self.readAnswer()

        if question == "" or answer == "":
            msg.showwarning("Warning", "Question and answer cannot be empty", parent=self.updateRoot)
            return

        if self.questionType == "MCQ":
            options = [box.get().strip() for box in self.optionBoxes]
            if any(option == "" for option in options):
                msg.showwarning("Warning", "All four options are required", parent=self.updateRoot)
                return

            q = """UPDATE questions SET question_text = %s, option_a = %s, option_b = %s,
                   option_c = %s, option_d = %s, correct_answer = %s WHERE id = %s"""
            self.cr.execute(q, (question, options[0], options[1], options[2], options[3], answer, self.updateId))
        else:
            q = "UPDATE questions SET question_text = %s, correct_answer = %s WHERE id = %s"
            self.cr.execute(q, (question, answer, self.updateId))

        self.conn.commit()
        msg.showinfo("Success", "Question has been updated successfully", parent=self.updateRoot)
        self.updateRoot.destroy()
        self.lectureChanged()


if __name__ == "__main__":
    viewQuestions()