import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as msg
from connection import connect

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Manage_Course:
    def __init__(self, parent=None):
        if parent:
            self.root = ctk.CTkToplevel(parent)
        else:
            self.root = ctk.CTk()

        self.root.geometry("1080x680")
        self.root.title("Manage Courses")
        self.root.resizable(True, True)
        self.root.attributes("-topmost", True)

        self.conn = connect()
        self.cur = self.conn.cursor()

        # Header Title
        self.lbl_title = ctk.CTkLabel(
            self.root,
            text="Manage Courses",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        self.lbl_title.pack(pady=(20, 10))

        # --- TOP CONTROLS FRAME (Search Bar + Action Buttons) ---
        self.ctrl_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.ctrl_frame.pack(fill="x", padx=25, pady=10)

        # Search Entry
        self.txt_search = ctk.CTkEntry(
            self.ctrl_frame,
            width=280,
            height=38,
            corner_radius=8,
            placeholder_text="Search by course name or dept..."
        )
        self.txt_search.pack(side="left", padx=(0, 10))

        # Search Button
        self.btn_search = ctk.CTkButton(
            self.ctrl_frame,
            text="🔍 Search",
            width=110,
            height=38,
            corner_radius=8,
            fg_color="#3F51B5",
            hover_color="#303F9F",
            command=self.search_courses
        )
        self.btn_search.pack(side="left", padx=5)

        # Refresh Button
        self.btn_refresh = ctk.CTkButton(
            self.ctrl_frame,
            text="🔄 Refresh",
            width=110,
            height=38,
            corner_radius=8,
            fg_color="#374151",
            hover_color="#1F2937",
            command=self.load_data
        )
        self.btn_refresh.pack(side="left", padx=5)

        # Delete Button
        self.btn_delete = ctk.CTkButton(
            self.ctrl_frame,
            text="🗑 Delete Selected",
            width=130,
            height=38,
            corner_radius=8,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.delete_course
        )
        self.btn_delete.pack(side="right", padx=(5, 0))

        # Update Button
        self.btn_update = ctk.CTkButton(
            self.ctrl_frame,
            text="✏ Edit Selected",
            width=130,
            height=38,
            corner_radius=8,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.open_update_dialog
        )
        self.btn_update.pack(side="right", padx=5)

        # --- TABLE CONTAINER (Custom CTk Card Container) ---
        self.table_frame = ctk.CTkFrame(self.root, fg_color="#181924", corner_radius=12)
        self.table_frame.pack(fill="both", expand=True, padx=25, pady=(10, 20))

        # Apply Modern Custom Theme for Treeview Table
        self.apply_table_style()

        # Treeview Setup
        columns = ("id", "name", "department_name", "semester", "duration", "description")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")

        # Column Headings
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Course Name")
        self.tree.heading("department_name", text="Department")
        self.tree.heading("semester", text="Semesters")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("description", text="Description")

        # Column Formatting
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("department_name", width=170, anchor="w")
        self.tree.column("semester", width=110, anchor="center")
        self.tree.column("duration", width=110, anchor="center")
        self.tree.column("description", width=280, anchor="w")

        # Scrollbar styled to match
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        self.scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)

        # Initial Data Load
        self.load_data()

    def apply_table_style(self):
        """Customizes the ttk Treeview style to match CustomTkinter dark card theme."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure Main Treeview Table Area
        style.configure(
            "Treeview",
            background="#1E1F2C",
            foreground="#E0E0E0",
            fieldbackground="#1E1F2C",
            rowheight=38,
            font=("Arial", 11),
            borderwidth=0
        )

        # Configure Header Styling
        style.configure(
            "Treeview.Heading",
            background="#12131C",
            foreground="#4361EE",
            font=("Arial", 11, "bold"),
            relief="flat",
            padding=8
        )

        # Hover and Selection Colors
        style.map(
            "Treeview",
            background=[("selected", "#3F51B5")],
            foreground=[("selected", "#FFFFFF")]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#1A1B28")]
        )

    def fetch_departments(self):
        """Fetches department list for combobox."""
        try:
            self.cur.execute("SELECT name FROM department")
            results = self.cur.fetchall()
            return [r[0] for r in results] if results else []
        except Exception as e:
            msg.showerror("Database Error", f"Error loading departments: {e}")
            return []

    def load_data(self):
        """Fetches and displays all courses from database."""
        self.txt_search.delete(0, "end")
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            query = "SELECT id, name, department_name, semester, duration, description FROM courses"
            self.cur.execute(query)
            rows = self.cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            msg.showerror("Database Error", f"Failed to load records: {e}")

    def search_courses(self):
        """Filters courses based on search text."""
        search_term = self.txt_search.get().strip()
        if not search_term:
            self.load_data()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            query = """
            SELECT id, name, department_name, semester, duration, description 
            FROM courses 
            WHERE name LIKE %s OR department_name LIKE %s
            """
            val = f"%{search_term}%"
            self.cur.execute(query, (val, val))
            rows = self.cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            msg.showerror("Database Error", f"Search failed: {e}")

    def delete_course(self):
        """Deletes selected course from database."""
        selected_item = self.tree.selection()
        if not selected_item:
            msg.showwarning("Selection Error", "Please select a course to delete.")
            return

        item_data = self.tree.item(selected_item[0])["values"]
        course_id = item_data[0]
        course_name = item_data[1]

        confirm = msg.askyesno("Confirm Deletion", f"Are you sure you want to delete '{course_name}'?")
        if confirm:
            try:
                self.cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
                self.conn.commit()
                msg.showinfo("Success", "Course deleted successfully!")
                self.load_data()
            except Exception as e:
                msg.showerror("Database Error", f"Failed to delete course: {e}")

    def open_update_dialog(self):
        """Opens a modal popup form pre-filled with selected course details."""
        selected_item = self.tree.selection()
        if not selected_item:
            msg.showwarning("Selection Error", "Please select a course to edit.")
            return

        item_data = self.tree.item(selected_item[0])["values"]
        course_id, c_name, c_dept, c_sem, c_dur, c_desc = item_data

        # Dialog Window
        dialog = ctk.CTkToplevel(self.root)
        dialog.geometry("550x620")
        dialog.title("Update Course")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        lbl = ctk.CTkLabel(dialog, text="Update Course Details", font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(pady=15)

        form_frame = ctk.CTkFrame(dialog, fg_color="#181924", corner_radius=12)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(size=12, weight="bold")

        # Course Name
        ctk.CTkLabel(form_frame, text="Course Name:", font=font_label).grid(row=0, column=0, padx=15, pady=12, sticky="w")
        txt_u_name = ctk.CTkEntry(form_frame, width=300)
        txt_u_name.insert(0, c_name)
        txt_u_name.grid(row=0, column=1, padx=15, pady=12)

        # Department Dropdown
        ctk.CTkLabel(form_frame, text="Department:", font=font_label).grid(row=1, column=0, padx=15, pady=12, sticky="w")
        dept_list = self.fetch_departments()
        cmb_u_dept = ctk.CTkComboBox(form_frame, width=300, values=dept_list, state="readonly")
        cmb_u_dept.set(c_dept if c_dept in dept_list else (dept_list[0] if dept_list else ""))
        cmb_u_dept.grid(row=1, column=1, padx=15, pady=12)

        # Semesters
        ctk.CTkLabel(form_frame, text="Semesters:", font=font_label).grid(row=2, column=0, padx=15, pady=12, sticky="w")
        txt_u_sem = ctk.CTkEntry(form_frame, width=300)
        txt_u_sem.insert(0, c_sem)
        txt_u_sem.grid(row=2, column=1, padx=15, pady=12)

        # Duration
        ctk.CTkLabel(form_frame, text="Duration:", font=font_label).grid(row=3, column=0, padx=15, pady=12, sticky="w")
        txt_u_dur = ctk.CTkEntry(form_frame, width=300)
        txt_u_dur.insert(0, c_dur)
        txt_u_dur.grid(row=3, column=1, padx=15, pady=12)

        # Description
        ctk.CTkLabel(form_frame, text="Description:", font=font_label).grid(row=4, column=0, padx=15, pady=12, sticky="nw")
        txt_u_desc = ctk.CTkTextbox(form_frame, width=300, height=120, wrap="word")
        txt_u_desc.insert("1.0", c_desc)
        txt_u_desc.grid(row=4, column=1, padx=15, pady=12)

        # Update Action
        def save_changes():
            u_name = txt_u_name.get().strip()
            u_dept = cmb_u_dept.get().strip()
            u_sem = txt_u_sem.get().strip()
            u_dur = txt_u_dur.get().strip()
            u_desc = txt_u_desc.get("1.0", "end-1c").strip()

            if not u_name or not u_dept or not u_sem or not u_dur or not u_desc:
                msg.showerror("Validation Error", "All fields are required.", parent=dialog)
                return

            try:
                q = """
                UPDATE courses 
                SET name=%s, department_name=%s, semester=%s, duration=%s, description=%s 
                WHERE id=%s
                """
                self.cur.execute(q, (u_name, u_dept, u_sem, u_dur, u_desc, course_id))
                self.conn.commit()
                msg.showinfo("Success", "Course details updated successfully!", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                msg.showerror("Database Error", f"Failed to update course: {e}")

        btn_save = ctk.CTkButton(
            dialog,
            text="Save Changes",
            width=180,
            height=38,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=save_changes
        )
        btn_save.pack(pady=15)


if __name__ == "__main__":
    app = Manage_Course()
    app.root.mainloop()