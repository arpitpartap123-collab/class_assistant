import customtkinter as ctk
import tkinter.messagebox
from connection import connect

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Add_Course:
    def __init__(self, parent=None):
        if parent:
            self.root = ctk.CTkToplevel(parent)
        else:
            self.root = ctk.CTk()

        # Window configuration
        self.root.geometry("620x720")
        self.root.title("Add Course")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.conn = connect()
        self.cur = self.conn.cursor()

        # Page Heading
        self.mainlabel = ctk.CTkLabel(
            self.root,
            text="Add New Course",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold")
        )
        self.mainlabel.pack(pady=(20, 10))

        # Card Frame Container
        self.card_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.card_frame.pack(padx=25, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13, weight="bold")

        # --- 1. Course Name Row ---
        self.lbl_name = ctk.CTkLabel(self.card_frame, text="Course Name :-", font=font_label)
        self.lbl_name.grid(row=0, column=0, sticky="nw", padx=(25, 10), pady=(25, 10))

        self.txt_name = ctk.CTkEntry(
            self.card_frame,
            width=320,
            height=38,
            corner_radius=8,
            placeholder_text="e.g. B.Tech Computer Science"
        )
        self.txt_name.grid(row=0, column=1, padx=(0, 25), pady=(25, 10), sticky="w")

        # --- 2. Department Name Dropdown (Foreign Key) ---
        self.lbl_dept = ctk.CTkLabel(self.card_frame, text="Department :-", font=font_label)
        self.lbl_dept.grid(row=1, column=0, sticky="nw", padx=(25, 10), pady=10)

        # Fetch department names from the department table
        dept_list = self.fetch_departments()

        self.cmb_dept = ctk.CTkComboBox(
            self.card_frame,
            width=320,
            height=38,
            corner_radius=8,
            values=dept_list,
            state="readonly"
        )
        if dept_list:
            self.cmb_dept.set(dept_list[0])
        else:
            self.cmb_dept.set("No Departments Found")

        self.cmb_dept.grid(row=1, column=1, padx=(0, 25), pady=10, sticky="w")

        # --- 3. Semester Row ---
        self.lbl_sem = ctk.CTkLabel(self.card_frame, text="Semester/Terms :-", font=font_label)
        self.lbl_sem.grid(row=2, column=0, sticky="nw", padx=(25, 10), pady=10)

        self.txt_sem = ctk.CTkEntry(
            self.card_frame,
            width=320,
            height=38,
            corner_radius=8,
            placeholder_text="e.g. 8 Semesters"
        )
        self.txt_sem.grid(row=2, column=1, padx=(0, 25), pady=10, sticky="w")

        # --- 4. Duration Row ---
        self.lbl_duration = ctk.CTkLabel(self.card_frame, text="Duration :-", font=font_label)
        self.lbl_duration.grid(row=3, column=0, sticky="nw", padx=(25, 10), pady=10)

        self.txt_duration = ctk.CTkEntry(
            self.card_frame,
            width=320,
            height=38,
            corner_radius=8,
            placeholder_text="e.g. 4 Years"
        )
        self.txt_duration.grid(row=3, column=1, padx=(0, 25), pady=10, sticky="w")

        # --- 5. Description Row ---
        self.lbl_desc = ctk.CTkLabel(self.card_frame, text="Description :-", font=font_label)
        self.lbl_desc.grid(row=4, column=0, sticky="nw", padx=(25, 10), pady=10)

        self.txt_desc = ctk.CTkTextbox(
            self.card_frame,
            width=320,
            height=180,
            corner_radius=8,
            wrap="word",
            font=ctk.CTkFont(family="Arial", size=12)
        )
        self.txt_desc.grid(row=4, column=1, padx=(0, 25), pady=10, sticky="w")

        # Submit Button
        self.btn_submit = ctk.CTkButton(
            self.root,
            text="Add Course",
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            width=200,
            height=42,
            corner_radius=10,
            command=self.add_record
        )
        self.btn_submit.pack(pady=(10, 20))

    def fetch_departments(self):
        """Fetches all department names from department table to populate combobox."""
        try:
            q = "SELECT name FROM department"
            self.cur.execute(q)
            results = self.cur.fetchall()
            return [row[0] for row in results] if results else []
        except Exception as e:
            tkinter.messagebox.showerror("Database Error", f"Failed to fetch departments: {e}")
            return []

    def add_record(self):
        course_name = self.txt_name.get().strip()
        dept_name = self.cmb_dept.get().strip()
        semester = self.txt_sem.get().strip()
        duration = self.txt_duration.get().strip()
        description = self.txt_desc.get("1.0", "end-1c").strip()

        if not course_name or not dept_name or dept_name == "No Departments Found" or not semester or not duration or not description:
            tkinter.messagebox.showerror("Validation Error", "Please fill in all required fields.")
            return

        try:
            q = """
            INSERT INTO courses (name, description, department_name, semester, duration) 
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cur.execute(q, (course_name, description, dept_name, semester, duration))
            self.conn.commit()

            tkinter.messagebox.showinfo("Success", "Course Added Successfully!")
            self.root.destroy()
        except Exception as e:
            tkinter.messagebox.showerror("Database Error", f"Failed to insert course: {e}")


if __name__ == "__main__":
    app = Add_Course()
    app.root.mainloop()