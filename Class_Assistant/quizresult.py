"""Result of one quiz attempt, question by question."""

import customtkinter as ctk

from connection import connect

# Configure CustomTkinter default theme settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Local Theme Color Palette
BG_DARK = "#0f0e17"
CARD_BG = "#16151f"
CARD_INNER = "#1e1c2a"
BORDER_COLOR = "#2a273a"
ACCENT_PURPLE = "#7b5bf2"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#94a3b8"
SUCCESS_GREEN = "#10b981"
WARNING_AMBER = "#f59e0b"
DANGER_RED = "#ef4444"


class quizResult:
    def __init__(self, attemptId, parent=None):
        self.attemptId = attemptId

        # Handle window creation
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)  # Locks on top of parent window
        else:
            self.root = ctk.CTk()

        self.root.title("Quiz Result")
        self.root.configure(fg_color=BG_DARK)

        # Enable maximize/resizable controls
        self.root.resizable(True, True)
        self.center_window(1150, 850)

        # Force foreground focus
        self.root.lift()
        self.root.focus_force()

        # Database connection
        self.conn = connect()
        self.cr = self.conn.cursor()

        # Responsive grid configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # Title
        self.root.grid_rowconfigure(1, weight=0)  # Subtitle
        self.root.grid_rowconfigure(2, weight=0)  # Compact Scoreboard
        self.root.grid_rowconfigure(3, weight=1)  # Expanded Answer Area (Takes remaining height)
        self.root.grid_rowconfigure(4, weight=0)  # Close Button

        # Fetch attempt metadata
        q = """SELECT s.name, l.title, a.total_questions, a.correct_answers,
                      a.score, a.attempted_on
               FROM quiz_attempts a
               JOIN students s ON s.id = a.student_id
               JOIN lectures l ON l.id = a.lecture_id
               WHERE a.id = %s"""
        self.cr.execute(q, (attemptId,))
        row = self.cr.fetchone()

        if row is None:
            ctk.CTkLabel(
                self.root,
                text="Quiz Result",
                font=("Segoe UI", 26, "bold"),
                text_color=TEXT_WHITE
            ).grid(row=0, column=0, pady=(20, 2))

            ctk.CTkLabel(
                self.root,
                text="This attempt could not be found.",
                font=("Segoe UI", 15),
                text_color=TEXT_MUTED
            ).grid(row=1, column=0, pady=60)

            if not parent:
                self.root.mainloop()
            return

        name, lecture, total, correct, score, attemptedOn = row

        # Header Title and Subtitle
        ctk.CTkLabel(
            self.root,
            text="Quiz Result",
            font=("Segoe UI", 28, "bold"),
            text_color=TEXT_WHITE
        ).grid(row=0, column=0, pady=(15, 2))

        ctk.CTkLabel(
            self.root,
            text=f"{name}   |   {lecture}",
            font=("Segoe UI", 14),
            text_color=TEXT_MUTED
        ).grid(row=1, column=0, pady=(0, 10))

        # UI Layout Construction
        self.buildScoreCard(total, correct, score, attemptedOn)
        self.buildAnswers()

        ctk.CTkButton(
            self.root,
            text="Close Window",
            width=260,
            height=40,
            fg_color=DANGER_RED,
            hover_color="#dc2626",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.root.destroy
        ).grid(row=4, column=0, pady=(8, 15))

        # Run mainloop ONLY if script is executed standalone
        if not parent:
            self.root.mainloop()

    def center_window(self, width, height):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def gradeColour(self, score):
        if score >= 70:
            return SUCCESS_GREEN
        if score >= 40:
            return WARNING_AMBER
        return DANGER_RED

    def buildScoreCard(self, total, correct, score, attemptedOn):
        """Displays score card metrics in a compact header banner."""
        card = ctk.CTkFrame(
            self.root,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew")

        # Horizontal alignment for score summary banner
        score_container = ctk.CTkFrame(card, fg_color="transparent")
        score_container.pack(pady=12, padx=20)

        ctk.CTkLabel(
            score_container,
            text=f"{score}%",
            font=("Segoe UI", 42, "bold"),
            text_color=self.gradeColour(score)
        ).pack(side="left", padx=(0, 20))

        metrics_row = ctk.CTkFrame(score_container, fg_color="transparent")
        metrics_row.pack(side="left")

        for title, value in [("Total Questions", total), ("Correct", correct),
                             ("Wrong", total - correct)]:
            box = ctk.CTkFrame(
                metrics_row,
                fg_color=CARD_INNER,
                corner_radius=10,
                width=160,
                height=65
            )
            box.pack(side="left", padx=8)
            box.pack_propagate(0)

            ctk.CTkLabel(
                box,
                text=str(value),
                font=("Segoe UI", 20, "bold"),
                text_color=ACCENT_PURPLE
            ).pack(pady=(8, 0))

            ctk.CTkLabel(
                box,
                text=title,
                font=("Segoe UI", 10),
                text_color=TEXT_MUTED
            ).pack()

        ctk.CTkLabel(
            card,
            text=f"Attempted on {attemptedOn}",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 8))

    def buildAnswers(self):
        """Builds an expanded scrollable answers area taking maximum screen height."""
        answers_container = ctk.CTkFrame(self.root, fg_color="transparent")
        answers_container.grid(row=3, column=0, padx=30, pady=(0, 5), sticky="nsew")
        answers_container.grid_columnconfigure(0, weight=1)
        answers_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            answers_container,
            text="Detailed Question Breakdown",
            font=("Segoe UI", 16, "bold"),
            text_color=TEXT_WHITE,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        area = ctk.CTkScrollableFrame(
            answers_container,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER_COLOR
        )
        area.grid(row=1, column=0, sticky="nsew")

        q = """SELECT q.question_type, q.question_text, ans.student_answer,
                      q.correct_answer, ans.is_correct, ans.similarity_score,
                      q.option_a, q.option_b, q.option_c, q.option_d
               FROM quiz_answers ans JOIN questions q ON q.id = ans.question_id
               WHERE ans.attempt_id = %s ORDER BY ans.id"""
        self.cr.execute(q, (self.attemptId,))

        for number, record in enumerate(self.cr.fetchall(), start=1):
            self.buildAnswerCard(area, number, record)

    def buildAnswerCard(self, area, number, record):
        """Renders larger, highly legible question cards with adaptive text wrapping."""
        (qtype, question, given, correct, isCorrect, similarity,
         a, b, c, d) = record

        colour = SUCCESS_GREEN if isCorrect else DANGER_RED

        card = ctk.CTkFrame(
            area,
            fg_color=CARD_INNER,
            corner_radius=12,
            border_width=2,
            border_color=colour
        )
        card.pack(fill="x", padx=16, pady=10)

        head = ctk.CTkFrame(card, fg_color=CARD_INNER)
        head.pack(fill="x", padx=20, pady=(14, 0))

        ctk.CTkLabel(
            head,
            text=f"Q{number}.  [{qtype}]",
            font=("Segoe UI", 16, "bold"),
            text_color=ACCENT_PURPLE
        ).pack(side="left")

        ctk.CTkLabel(
            head,
            text="Correct" if isCorrect else "Wrong",
            font=("Segoe UI", 14, "bold"),
            text_color=colour
        ).pack(side="right")

        # Question text with large font and wraplength
        ctk.CTkLabel(
            card,
            text=question,
            font=("Segoe UI", 14, "bold"),
            text_color=TEXT_WHITE,
            wraplength=1050,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(10, 8))

        options = {"A": a, "B": b, "C": c, "D": d}
        givenText = given or "(not answered)"
        correctText = correct

        if qtype == "MCQ":
            if given in options and options[given]:
                givenText = f"{given}.  {options[given]}"
            if correct in options and options[correct]:
                correctText = f"{correct}.  {options[correct]}"

        # Larger student answer display
        ctk.CTkLabel(
            card,
            text=f"Your answer:  {givenText}",
            font=("Segoe UI", 13),
            text_color=colour,
            wraplength=1050,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(2, 2))

        # Larger reference answer display
        label = "Reference answer" if qtype == "ShortAnswer" else "Correct answer"
        ctk.CTkLabel(
            card,
            text=f"{label}:  {correctText}",
            font=("Segoe UI", 13),
            text_color=TEXT_MUTED,
            wraplength=1050,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(2, 4))

        if similarity is not None:
            ctk.CTkLabel(
                card,
                text=f"Cosine similarity with the reference answer: "
                     f"{similarity:.3f}",
                font=("Segoe UI", 12),
                text_color=ACCENT_PURPLE
            ).pack(anchor="w", padx=20, pady=(2, 4))

        ctk.CTkLabel(card, text="", font=("Segoe UI", 11)).pack(pady=(0, 4))


if __name__ == "__main__":
    quizResult(1)