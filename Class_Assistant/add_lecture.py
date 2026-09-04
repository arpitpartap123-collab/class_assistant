import customtkinter as ctk
from tkinter import messagebox as msg
from tkinter.filedialog import askopenfilename
import os
import shutil

from connection import connect
from Pdf_Extractor import extract_text, page_count
from ai_pipeline import process_lecture, PDF_DIR, MIN_WORDS


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Main:
    def __init__(self, admin_details, parent=None):
        print("NEW ADD LECTURE FILE RUNNING")

        self.admin_details = admin_details
        self.pdfPath = None

        # Use Toplevel if launched from existing parent window, otherwise Tk
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)
        else:
            self.root = ctk.CTk()

        self.root.geometry("820x780")
        self.root.minsize(760, 700)
        self.root.title("Add Lecture")
        self.root.configure(fg_color="#0B1120")

        self.font = ("Segoe UI", 14)
        self.title_font = ("Segoe UI", 30, "bold")
        self.section_font = ("Segoe UI", 17, "bold")
        self.label_font = ("Segoe UI", 13, "bold")

        # Header
        self.headerFrame = ctk.CTkFrame(
            self.root,
            fg_color="#111827",
            corner_radius=18,
            border_width=1,
            border_color="#1E3A5F"
        )
        self.headerFrame.pack(fill="x", padx=24, pady=(14, 8))

        self.mainLabel = ctk.CTkLabel(
            self.headerFrame,
            text="ADD LECTURE",
            font=self.title_font,
            text_color="#60A5FA"
        )
        self.mainLabel.pack(pady=(12, 2))

        self.subtitleLabel = ctk.CTkLabel(
            self.headerFrame,
            text="Create a lecture and generate its questionnaire",
            font=("Segoe UI", 12),
            text_color="#94A3B8"
        )
        self.subtitleLabel.pack(pady=(0, 12))

        # Main form card
        self.formCard = ctk.CTkFrame(
            self.root,
            fg_color="#111827",
            corner_radius=18,
            border_width=1,
            border_color="#1E3A5F"
        )
        self.formCard.pack(fill="x", padx=24, pady=7)

        self.formFrame = ctk.CTkFrame(
            self.formCard,
            fg_color="transparent"
        )
        self.formFrame.pack(fill="x", padx=20, pady=12)

        self.formFrame.grid_columnconfigure(1, weight=1)

        # Lecture Title
        ctk.CTkLabel(
            self.formFrame,
            text="Lecture Title",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=0, column=0, padx=(0, 14), pady=6, sticky="w")

        self.txt1 = ctk.CTkEntry(
            self.formFrame,
            font=self.font,
            height=42,
            corner_radius=10,
            fg_color="#0B1220",
            border_color="#334155",
            border_width=1,
            text_color="#F8FAFC",
            placeholder_text="Enter lecture title"
        )
        self.txt1.grid(row=0, column=1, padx=0, pady=6, sticky="ew")

        # Description
        ctk.CTkLabel(
            self.formFrame,
            text="Description",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=1, column=0, padx=(0, 14), pady=6, sticky="w")

        self.txt2 = ctk.CTkEntry(
            self.formFrame,
            font=self.font,
            height=42,
            corner_radius=10,
            fg_color="#0B1220",
            border_color="#334155",
            border_width=1,
            text_color="#F8FAFC",
            placeholder_text="Enter lecture description"
        )
        self.txt2.grid(row=1, column=1, padx=0, pady=6, sticky="ew")

        # Course
        ctk.CTkLabel(
            self.formFrame,
            text="Select Course",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=2, column=0, padx=(0, 14), pady=6, sticky="w")

        self.Course = ctk.CTkComboBox(
            self.formFrame,
            font=self.font,
            height=42,
            corner_radius=10,
            state="readonly",
            fg_color="#0B1220",
            border_color="#334155",
            button_color="#2563EB",
            button_hover_color="#1D4ED8",
            dropdown_fg_color="#111827",
            dropdown_hover_color="#1E3A5F",
            dropdown_text_color="#F8FAFC",
            text_color="#F8FAFC"
        )
        self.Course.grid(row=2, column=1, padx=0, pady=6, sticky="ew")

        self.loadCourses()

        # PDF
        ctk.CTkLabel(
            self.formFrame,
            text="Lecture PDF",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=3, column=0, padx=(0, 14), pady=6, sticky="w")

        self.pdfRow = ctk.CTkFrame(
            self.formFrame,
            fg_color="transparent"
        )
        self.pdfRow.grid(row=3, column=1, padx=0, pady=6, sticky="ew")
        self.pdfRow.grid_columnconfigure(0, weight=1)

        self.txt3 = ctk.CTkEntry(
            self.pdfRow,
            font=self.font,
            height=42,
            corner_radius=10,
            fg_color="#0B1220",
            border_color="#334155",
            border_width=1,
            text_color="#F8FAFC",
            placeholder_text="Select a PDF file"
        )
        self.txt3.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.pdfButton = ctk.CTkButton(
            self.pdfRow,
            text="Browse PDF",
            font=("Segoe UI", 13, "bold"),
            height=42,
            width=125,
            corner_radius=10,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.selectPDF
        )
        self.pdfButton.grid(row=0, column=1)

        # Questionnaire Settings card
        self.settingsFrame = ctk.CTkFrame(
            self.root,
            fg_color="#111827",
            corner_radius=18,
            border_width=1,
            border_color="#1E3A5F"
        )
        self.settingsFrame.pack(fill="x", padx=24, pady=7)

        ctk.CTkLabel(
            self.settingsFrame,
            text="QUESTIONNAIRE SETTINGS",
            font=("Segoe UI", 15, "bold"),
            text_color="#60A5FA"
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            self.settingsFrame,
            text="Choose how many questions should be generated",
            font=("Segoe UI", 10),
            text_color="#64748B"
        ).pack(pady=(0, 10))

        self.settingsGrid = ctk.CTkFrame(
            self.settingsFrame,
            fg_color="transparent"
        )
        self.settingsGrid.pack(fill="x", padx=20, pady=(0, 14))

        for column in range(4):
            self.settingsGrid.grid_columnconfigure(column, weight=1)

        # Notes
        ctk.CTkLabel(
            self.settingsGrid,
            text="Notes",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=0, column=0, padx=8, pady=(0, 8))

        self.noteCount = ctk.CTkEntry(
            self.settingsGrid,
            font=self.font,
            height=42,
            width=80,
            corner_radius=10,
            justify="center",
            fg_color="#0B1220",
            border_color="#334155",
            text_color="#F8FAFC"
        )
        self.noteCount.grid(row=1, column=0, padx=8)
        self.noteCount.insert(0, "8")

        # MCQ
        ctk.CTkLabel(
            self.settingsGrid,
            text="MCQ",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=0, column=1, padx=8, pady=(0, 8))

        self.mcqCount = ctk.CTkEntry(
            self.settingsGrid,
            font=self.font,
            height=42,
            width=80,
            corner_radius=10,
            justify="center",
            fg_color="#0B1220",
            border_color="#334155",
            text_color="#F8FAFC"
        )
        self.mcqCount.grid(row=1, column=1, padx=8)
        self.mcqCount.insert(0, "5")

        # True / False
        ctk.CTkLabel(
            self.settingsGrid,
            text="True / False",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=0, column=2, padx=8, pady=(0, 8))

        self.tfCount = ctk.CTkEntry(
            self.settingsGrid,
            font=self.font,
            height=42,
            width=80,
            corner_radius=10,
            justify="center",
            fg_color="#0B1220",
            border_color="#334155",
            text_color="#F8FAFC"
        )
        self.tfCount.grid(row=1, column=2, padx=8)
        self.tfCount.insert(0, "3")

        # Short Answer
        ctk.CTkLabel(
            self.settingsGrid,
            text="Short Answer",
            font=self.label_font,
            text_color="#CBD5E1"
        ).grid(row=0, column=3, padx=8, pady=(0, 8))

        self.saCount = ctk.CTkEntry(
            self.settingsGrid,
            font=self.font,
            height=42,
            width=80,
            corner_radius=10,
            justify="center",
            fg_color="#0B1220",
            border_color="#334155",
            text_color="#F8FAFC"
        )
        self.saCount.grid(row=1, column=3, padx=8)
        self.saCount.insert(0, "2")

        # Submit
        self.submitButton = ctk.CTkButton(
            self.root,
            text="ADD LECTURE",
            font=("Segoe UI", 15, "bold"),
            height=52,
            width=260,
            corner_radius=13,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            command=self.addLecture
        )
        self.submitButton.pack(pady=(10, 16))

        # Subtle hover dynamics
        self.pdfButton.bind("<Enter>", lambda event: self.pdfButton.configure(cursor="hand2"))
        self.submitButton.bind("<Enter>", lambda event: self.submitButton.configure(cursor="hand2"))

        # Only run mainloop if launched directly as a root Tk window
        if not parent:
            self.root.mainloop()

    def loadCourses(self):

        self.conn = connect()
        self.cr = self.conn.cursor()

        q = "select id, name from Courses"

        self.cr.execute(q)

        data = self.cr.fetchall()

        self.courseData = data

        courses = []

        for row in data:
            courses.append(row[1])

        self.Course.configure(values=courses)

        if len(courses) > 0:
            self.Course.set(courses[0])

        self.conn.close()

    def selectPDF(self):

        path = askopenfilename(
            title="Select Lecture PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if path == "":
            return

        try:

            text = extract_text(path)
            pages = page_count(path)

            if len(text.split()) < MIN_WORDS:

                msg.showwarning(
                    "Warning",
                    "This PDF has very little readable text."
                )

                return

            self.pdfPath = path

            self.txt3.delete(0, "end")
            self.txt3.insert(
                0,
                os.path.basename(path)
            )

            msg.showinfo(
                "PDF Selected",
                "PDF selected successfully.\n\n"
                + str(pages)
                + " pages found."
            )

        except Exception as e:

            msg.showerror(
                "Error",
                str(e)
            )

    def addLecture(self):

        # Safe role check preventing IndexError
        role = ""
        if self.admin_details and len(self.admin_details) > 6:
            role = str(self.admin_details[6]).lower()
        elif self.admin_details and len(self.admin_details) > 1:
            role = str(self.admin_details[1]).lower()

        # Allow access if role check passes or defaults to active admin session
        if role and role not in ["admin", "super admin", "active"]:
            msg.showerror(
                "Access Denied",
                "Only Admin or Super Admin can add lectures."
            )
            return

        title = self.txt1.get()
        description = self.txt2.get()

        # Get course directly from Combobox
        course = self.Course.get()

        pdf = self.txt3.get()

        print("Title:", title)
        print("Description:", description)
        print("Course:", course)
        print("PDF Entry:", pdf)
        print("PDF Path:", self.pdfPath)

        if title == "" or description == "" or course == "" or self.pdfPath is None:

            msg.showwarning(
                "Warning",
                "Please enter all fields and select PDF."
            )

            return

        try:

            self.conn = connect()
            self.cr = self.conn.cursor()

            q = "select id from Courses where name = %s"

            self.cr.execute(
                q,
                (course,)
            )

            data = self.cr.fetchone()

            if data is None:

                msg.showerror(
                    "Error",
                    "Course not found."
                )

                self.conn.close()

                return

            courseId = data[0]

            # Copy PDF
            os.makedirs(
                PDF_DIR,
                exist_ok=True
            )

            fileName = os.path.basename(
                self.pdfPath
            )

            shutil.copy(
                self.pdfPath,
                os.path.join(
                    PDF_DIR,
                    fileName
                )
            )

            # Extract PDF text
            extractedText = extract_text(
                self.pdfPath
            )

            # Admin ID
            adminId = self.admin_details[0]

            # Insert lecture
            q = """
            INSERT INTO lectures
            (title, description, course_id, admin_id, pdf_file, extracted_text, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """

            self.cr.execute(
                q,
                (
                    title,
                    description,
                    courseId,
                    adminId,
                    fileName,
                    extractedText,
                    "Active"
                )
            )

            self.conn.commit()

            lectureId = self.cr.lastrowid

            # Get questionnaire settings
            try:
                noteCount = int(self.noteCount.get())
                mcqCount = int(self.mcqCount.get())
                tfCount = int(self.tfCount.get())
                saCount = int(self.saCount.get())

                if noteCount < 1 or mcqCount < 1 or tfCount < 1 or saCount < 1:
                    msg.showwarning(
                        "Warning",
                        "Questionnaire counts must be greater than 0."
                    )
                    return

            except ValueError:
                msg.showwarning(
                    "Warning",
                    "Please enter valid numbers in questionnaire settings."
                )
                return

            print("Notes:", noteCount)
            print("MCQ:", mcqCount)
            print("True/False:", tfCount)
            print("Short Answer:", saCount)

            # AI processing
            process_lecture(
                lectureId,
                note_count=noteCount,
                mcq_count=mcqCount,
                true_false_count=tfCount,
                short_answer_count=saCount
            )

            msg.showinfo(
                "Success",
                "Lecture added successfully."
            )

            self.txt1.delete(
                0,
                "end"
            )

            self.txt2.delete(
                0,
                "end"
            )

            self.txt3.delete(
                0,
                "end"
            )

            self.pdfPath = None

            self.conn.close()

        except Exception as e:

            msg.showerror(
                "Error",
                str(e)
            )

if __name__ == "__main__":
    pass