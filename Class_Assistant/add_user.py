import customtkinter as ctk
import tkinter.messagebox
from connection import connect

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Demo:
    def __init__(self, parent=None):
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)
        else:
            self.root = ctk.CTk()

        self.root.geometry("520x650")
        self.root.title("Add Student")
        self.root.resizable(False, False)

        # Focus modal window cleanly without topmost z-index conflict
        self.root.grab_set()
        self.root.focus_force()

        self.conn = connect()
        self.cur = self.conn.cursor()

        self.mainlabel = ctk.CTkLabel(
            self.root,
            text="Add Student",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold")
        )
        self.mainlabel.pack(pady=(25, 15))

        self.card_frame = ctk.CTkScrollableFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.card_frame.pack(padx=25, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13)

        # Name
        self.lb1 = ctk.CTkLabel(self.card_frame, text="Enter Name :-", font=font_label)
        self.lb1.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.txt1 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt1.grid(row=0, column=1, padx=(0, 20), pady=10)

        # Gender
        self.lb2 = ctk.CTkLabel(self.card_frame, text="Enter Gender :-", font=font_label)
        self.lb2.grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.txt2 = ctk.CTkOptionMenu(
            self.card_frame, values=["Male", "Female", "Other"],
            width=220, height=35, corner_radius=8, fg_color="#3a3a3a", button_color="#4a4a4a"
        )
        self.txt2.grid(row=1, column=1, padx=(0, 20), pady=10)
        self.txt2.set("Male")

        # Mobile
        self.lb3 = ctk.CTkLabel(self.card_frame, text="Enter Mobile :-", font=font_label)
        self.lb3.grid(row=2, column=0, sticky="w", padx=20, pady=10)
        self.txt3 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt3.grid(row=2, column=1, padx=(0, 20), pady=10)

        # Email
        self.lb4 = ctk.CTkLabel(self.card_frame, text="Enter Email :-", font=font_label)
        self.lb4.grid(row=3, column=0, sticky="w", padx=20, pady=10)
        self.txt4 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt4.grid(row=3, column=1, padx=(0, 20), pady=10)

        # Department
        self.lb5 = ctk.CTkLabel(self.card_frame, text="Select Department :-", font=font_label)
        self.lb5.grid(row=4, column=0, sticky="w", padx=20, pady=10)
        self.txt5 = ctk.CTkOptionMenu(
            self.card_frame, values=self.departmentValues(), command=self.departmentChanged,
            width=220, height=35, corner_radius=8, fg_color="#3a3a3a", button_color="#4a4a4a"
        )
        self.txt5.grid(row=4, column=1, padx=(0, 20), pady=10)

        # Course
        self.lb6 = ctk.CTkLabel(self.card_frame, text="Select Course :-", font=font_label)
        self.lb6.grid(row=5, column=0, sticky="w", padx=20, pady=10)
        self.txt6 = ctk.CTkOptionMenu(
            self.card_frame, values=[],
            width=220, height=35, corner_radius=8, fg_color="#3a3a3a", button_color="#4a4a4a"
        )
        self.txt6.grid(row=5, column=1, padx=(0, 20), pady=10)

        # Password
        self.lb7 = ctk.CTkLabel(self.card_frame, text="Enter Password :-", font=font_label)
        self.lb7.grid(row=6, column=0, sticky="w", padx=20, pady=10)
        self.txt7 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8, show="*")
        self.txt7.grid(row=6, column=1, padx=(0, 20), pady=10)

        # Populate departments and trigger first load of courses
        departments = self.departmentValues()
        if departments:
            self.txt5.set(departments[0])
            self.departmentChanged(departments[0])

        # Submit Button
        self.bt1 = ctk.CTkButton(
            self.root,
            text="Submit",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            width=180,
            height=40,
            corner_radius=10,
            command=self.add_record
        )
        self.bt1.pack(pady=15)

    def departmentValues(self):
        """Fetches department names directly from the department table."""
        self.cur.execute("SELECT name FROM department ORDER BY name")
        return [row[0] for row in self.cur.fetchall()]

    def departmentChanged(self, department):
        """Filters courses based on department_name matching in the courses table."""
        q = "SELECT name FROM courses WHERE department_name = %s ORDER BY name"
        self.cur.execute(q, (department,))
        courses = [row[0] for row in self.cur.fetchall()]

        if courses:
            self.txt6.configure(values=courses)
            self.txt6.set(courses[0])
        else:
            self.txt6.configure(values=["No courses available"])
            self.txt6.set("No courses available")

    def add_record(self):
        name = self.txt1.get().strip()
        gender = self.txt2.get().strip()
        mobile = self.txt3.get().strip()
        email = self.txt4.get().strip()
        course = self.txt6.get().strip()
        password = self.txt7.get().strip()

        # Validation Checks
        if not name or not gender or not mobile or not email or not course or not password:
            tkinter.messagebox.showerror("Error", "Please fill all fields", parent=self.root)
            return

        if course == "No courses available":
            tkinter.messagebox.showerror("Error", "Selected department has no available courses", parent=self.root)
            return

        if not (mobile.isdigit() and len(mobile) == 10):
            tkinter.messagebox.showerror("Error", "Mobile number must contain exactly 10 digits", parent=self.root)
            return

        if "@" not in email or "." not in email:
            tkinter.messagebox.showerror("Error", "Please enter a valid email address", parent=self.root)
            return

        # Duplicate email check
        self.cur.execute("SELECT id FROM students WHERE email = %s", (email,))
        if self.cur.fetchone():
            tkinter.messagebox.showerror("Error", "This email is already registered", parent=self.root)
            return

        # Retrieve course primary key ID from courses table
        self.cur.execute("SELECT id FROM courses WHERE name = %s", (course,))
        row = self.cur.fetchone()
        if row is None:
            tkinter.messagebox.showerror("Error", "Please select a valid course", parent=self.root)
            return

        course_id = row[0]

        # Insert student record
        q = """INSERT INTO students (name, email, mobile, gender, password, status, course_id)
               VALUES (%s, %s, %s, %s, %s, 'active', %s)"""
        self.cur.execute(q, (name, email, mobile, gender, password, course_id))
        self.conn.commit()

        tkinter.messagebox.showinfo("Success", "Student Added Successfully", parent=self.root)
        self.root.destroy()


# Alias for compatibility with import strategies
Add_admin = Demo

if __name__ == "__main__":
    app = Demo()
    app.root.mainloop()