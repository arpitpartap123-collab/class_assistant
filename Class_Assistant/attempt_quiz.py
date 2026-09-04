"""The quiz screen.

Every question is graded by quiz_evaluator.py. MCQ and True/False are compared
directly, a short answer is graded with cosine similarity against the reference
sentence that the AI stored when the question was created.

One row goes into quiz_attempts and one row per question into quiz_answers.
"""

import tkinter.messagebox as msg

import customtkinter as ctk

from connection import connect
from quiz_evaluator import evaluate_answer, SHORT_ANSWER_THRESHOLD
from quizresult import quizResult

# Configure CustomTkinter default theme settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Local Theme Color Palette
BG_DARK = "#0f0e17"
CARD_BG = "#16151f"
CARD_INNER = "#1e1c2a"
BORDER_COLOR = "#2a273a"
ACCENT_PURPLE = "#7b5bf2"
ACCENT_BLUE = "#3b82f6"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#94a3b8"
SUCCESS_GREEN = "#10b981"
DANGER_RED = "#ef4444"


class attemptQuiz:
    def __init__(self, studentId):
        self.studentId = studentId
        self.questions = []
        self.answerWidgets = {}

        self.root = ctk.CTkToplevel()
        self.root.title("Attempt Quiz")
        self.root.configure(fg_color=BG_DARK)
        self.root.state("zoomed")

        self.conn = connect()
        self.cr = self.conn.cursor()

        # Header Title and Subtitle
        ctk.CTkLabel(
            self.root,
            text="Attempt Quiz",
            font=("Segoe UI", 26, "bold"),
            text_color=TEXT_WHITE
        ).pack(pady=(20, 2))

        ctk.CTkLabel(
            self.root,
            text="Short answers are checked by meaning, not word by word",
            font=("Segoe UI", 13),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 15))

        bar = ctk.CTkFrame(self.root, fg_color=BG_DARK)
        bar.pack(pady=14)

        ctk.CTkLabel(
            bar,
            text="Lecture",
            font=("Segoe UI", 13, "bold"),
            text_color=TEXT_WHITE
        ).grid(row=0, column=0, padx=8)

        self.lectureBox = ctk.CTkComboBox(
            bar,
            width=440,
            height=38,
            values=self.lectureValues(),
            command=self.loadQuiz,
            fg_color=CARD_BG,
            border_color=BORDER_COLOR,
            button_color=ACCENT_PURPLE,
            button_hover_color="#6d42e2",
            dropdown_fg_color=CARD_BG,
            dropdown_hover_color=CARD_INNER,
            dropdown_text_color=TEXT_WHITE,
            text_color=TEXT_WHITE,
            corner_radius=8
        )
        self.lectureBox.grid(row=0, column=1, padx=8)

        ctk.CTkButton(
            bar,
            text="Load Quiz",
            width=130,
            height=38,
            fg_color=ACCENT_PURPLE,
            hover_color="#6d42e2",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.loadQuiz
        ).grid(row=0, column=2, padx=8)

        self.quizArea = ctk.CTkScrollableFrame(
            self.root,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.quizArea.pack(fill="both", expand=True, padx=40, pady=(4, 10))

        footer = ctk.CTkFrame(self.root, fg_color=BG_DARK)
        footer.pack(pady=(0, 18))

        self.submitBtn = ctk.CTkButton(
            footer,
            text="Submit Quiz",
            width=220,
            height=38,
            fg_color=SUCCESS_GREEN,
            hover_color="#059669",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self.submitQuiz
        )
        self.submitBtn.grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            footer,
            text="Close",
            width=180,
            height=38,
            fg_color=DANGER_RED,
            hover_color="#dc2626",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=lambda: self.root.destroy()
        ).grid(row=0, column=1, padx=10)

        lectures = self.lectureValues()
        if lectures:
            self.lectureBox.set(lectures[0])
            self.loadQuiz()
        else:
            self.showMessage("There are no quizzes available for your course yet.")

        self.root.mainloop()

    # ------------------------------------------------------------- data ----
    def lectureValues(self):
        """Only lectures that actually have questions can be attempted."""
        q = """SELECT l.id, l.title FROM lectures l
               JOIN students s ON s.course_id = l.course_id
               WHERE s.id = %s
                 AND (SELECT COUNT(*) FROM questions q WHERE q.lecture_id = l.id) > 0
               ORDER BY l.id"""
        self.cr.execute(q, (self.studentId,))
        return [f"{row[0]} - {row[1]}" for row in self.cr.fetchall()]

    def currentLectureId(self):
        value = self.lectureBox.get().strip()
        if not value:
            return None
        return int(value.split(" - ")[0])

    def clearArea(self):
        for widget in self.quizArea.winfo_children():
            widget.destroy()
        self.answerWidgets = {}

    def showMessage(self, text):
        self.clearArea()
        ctk.CTkLabel(
            self.quizArea,
            text=text,
            font=("Segoe UI", 15),
            text_color=TEXT_MUTED
        ).pack(pady=60)

    # ------------------------------------------------------------- build ----
    def loadQuiz(self, _value=None):
        lectureId = self.currentLectureId()
        if lectureId is None:
            return

        q = """SELECT id, question_type, question_text, option_a, option_b,
                      option_c, option_d, marks
               FROM questions WHERE lecture_id = %s ORDER BY question_type, id"""
        self.cr.execute(q, (lectureId,))
        self.questions = self.cr.fetchall()

        if not self.questions:
            self.showMessage("This lecture has no questions yet.")
            return

        self.clearArea()

        total = sum(row[7] for row in self.questions)
        ctk.CTkLabel(
            self.quizArea,
            text=f"{len(self.questions)} questions   |   {total} marks",
            font=("Segoe UI", 15, "bold"),
            text_color=ACCENT_PURPLE
        ).pack(pady=(14, 4))

        for number, row in enumerate(self.questions, start=1):
            self.buildQuestion(number, row)

    def buildQuestion(self, number, row):
        questionId, qtype, text, a, b, c, d, marks = row

        card = ctk.CTkFrame(self.quizArea, fg_color=CARD_INNER, corner_radius=12)
        card.pack(fill="x", padx=16, pady=9)

        head = ctk.CTkFrame(card, fg_color=CARD_INNER)
        head.pack(fill="x", padx=16, pady=(12, 0))

        ctk.CTkLabel(
            head,
            text=f"Q{number}.  [{qtype}]",
            font=("Segoe UI", 14, "bold"),
            text_color=ACCENT_PURPLE
        ).pack(side="left")

        ctk.CTkLabel(
            head,
            text=f"{marks} mark/s",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=text,
            font=("Segoe UI", 13, "bold"),
            text_color=TEXT_WHITE,
            wraplength=880,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(6, 8))

        if qtype == "MCQ":
            choice = ctk.StringVar(value="")
            for letter, option in zip("ABCD", (a, b, c, d)):
                if option is None:
                    continue
                ctk.CTkRadioButton(
                    card,
                    text=f"{letter}.  {option}",
                    variable=choice,
                    value=letter,
                    font=("Segoe UI", 12),
                    text_color=TEXT_WHITE,
                    fg_color=ACCENT_PURPLE,
                    hover_color="#6d42e2"
                ).pack(anchor="w", padx=34, pady=3)
            self.answerWidgets[questionId] = ("MCQ", choice)
            ctk.CTkLabel(card, text="", font=("Segoe UI", 11)).pack(pady=(0, 8))

        elif qtype == "TrueFalse":
            choice = ctk.StringVar(value="")
            for option in ("True", "False"):
                ctk.CTkRadioButton(
                    card,
                    text=option,
                    variable=choice,
                    value=option,
                    font=("Segoe UI", 12),
                    text_color=TEXT_WHITE,
                    fg_color=ACCENT_PURPLE,
                    hover_color="#6d42e2"
                ).pack(anchor="w", padx=34, pady=3)
            self.answerWidgets[questionId] = ("TrueFalse", choice)
            ctk.CTkLabel(card, text="", font=("Segoe UI", 11)).pack(pady=(0, 8))

        else:
            box = ctk.CTkTextbox(
                card,
                width=860,
                height=90,
                font=("Segoe UI", 12),
                fg_color=CARD_BG,
                text_color=TEXT_WHITE,
                border_width=1,
                border_color=BORDER_COLOR,
                corner_radius=8
            )
            box.pack(anchor="w", padx=34, pady=(2, 4))
            ctk.CTkLabel(
                card,
                text=f"Answer in your own words. Accepted at a similarity of "
                     f"{SHORT_ANSWER_THRESHOLD:.2f} or more.",
                font=("Segoe UI", 11),
                text_color=TEXT_MUTED
            ).pack(anchor="w", padx=34, pady=(0, 12))
            self.answerWidgets[questionId] = ("ShortAnswer", box)

    def readAnswer(self, questionId):
        kind, widget = self.answerWidgets[questionId]
        if kind == "ShortAnswer":
            return widget.get("1.0", "end-1c").strip()
        return widget.get().strip()

    # ------------------------------------------------------------ submit ----
    def submitQuiz(self):
        lectureId = self.currentLectureId()
        if lectureId is None or not self.questions:
            msg.showwarning("Warning", "Please load a quiz first", parent=self.root)
            return

        answered = sum(1 for row in self.questions if self.readAnswer(row[0]) != "")
        if answered == 0:
            msg.showwarning("Warning", "Please answer at least one question",
                            parent=self.root)
            return

        if answered < len(self.questions):
            confirm = msg.askyesno("Confirm",
                                   f"You have answered {answered} of {len(self.questions)} "
                                   f"questions.\n\nSubmit anyway?", parent=self.root)
            if not confirm:
                return

        # Grade every question first, then save everything in one go.
        self.cr.execute("SELECT id, question_type, correct_answer FROM questions "
                        "WHERE lecture_id = %s", (lectureId,))
        correctAnswers = {row[0]: (row[1], row[2]) for row in self.cr.fetchall()}

        graded = []
        correctCount = 0

        for row in self.questions:
            questionId = row[0]
            qtype, reference = correctAnswers[questionId]
            given = self.readAnswer(questionId)

            isCorrect, similarity = evaluate_answer(qtype, reference, given)
            if isCorrect:
                correctCount += 1

            graded.append((questionId, given, 1 if isCorrect else 0, similarity))

        total = len(self.questions)
        score = round(correctCount / total * 100, 2) if total else 0.0

        try:
            attempt = """INSERT INTO quiz_attempts
                         (student_id, lecture_id, total_questions, correct_answers, score)
                         VALUES (%s, %s, %s, %s, %s)"""
            self.cr.execute(attempt, (self.studentId, lectureId, total, correctCount, score))
            attemptId = self.cr.lastrowid

            answer = """INSERT INTO quiz_answers
                        (attempt_id, question_id, student_answer, is_correct, similarity_score)
                        VALUES (%s, %s, %s, %s, %s)"""
            for questionId, given, isCorrect, similarity in graded:
                self.cr.execute(answer, (attemptId, questionId, given, isCorrect, similarity))

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            msg.showerror("Error", f"The quiz could not be saved.\n\n{e}", parent=self.root)
            return

        msg.showinfo("Submitted",
                     f"Quiz submitted.\n\nCorrect: {correctCount} of {total}\n"
                     f"Score: {score}%", parent=self.root)

        self.root.destroy()
        quizResult(attemptId)


if __name__ == "__main__":
    attemptQuiz(1)