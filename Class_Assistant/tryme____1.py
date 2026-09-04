import customtkinter as ctk
import tkinter.messagebox as msg
from tkinter import Menu, ttk

# Import the modal classes
from edit_user import Edit_Profile
from user_pass import Change_Pass
from student_courses import studentCourses
from student_lectures import studentLectures
from attempt_quiz import attemptQuiz

# Set appearance and default color palette
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class StudentDashboard:
    def __init__(self, student_detail=None):
        # Expected tuple/list structure: (student_id, status, name, email) or custom dashboard tuple
        self.student_detail = student_detail or (101, "active", "Alex Morgan", "alex.m@college.edu")

        self.root = ctk.CTk()
        self.root.title("EduPulse AI - Student Dashboard")
        self.root.geometry("1150x700")
        self.root.after(0, lambda: self.root.state("zoomed"))

        # Global Table/Treeview Theme
        self.apply_global_table_style()

        # Navigation State Trackers
        self.profile_modal_visible = False

        # --- TOP MENU BAR ---
        self.mainMenu = Menu(self.root)
        self.root.config(menu=self.mainMenu)

        # Academics Menu
        self.academicsMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Academics", menu=self.academicsMenu)
        self.academicsMenu.add_command(label="My Courses", command=self.open_courses)
        self.academicsMenu.add_command(label="My Lectures", command=self.open_lectures)
        self.academicsMenu.add_command(label="Take Quiz 📝", command=self.take_quiz)
        self.academicsMenu.add_command(label="Schedule & Attendance", command=self.open_schedule)

        # Grades Menu
        self.gradesMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Grades", menu=self.gradesMenu)
        self.gradesMenu.add_command(label="View Performance", command=self.open_grades)

        # Profile Menu
        self.profileMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Profile", menu=self.profileMenu)
        self.profileMenu.add_command(label="View Profile Overlay", command=self.toggle_profile_overlay)
        self.profileMenu.add_command(label="Edit Profile", command=self.edit_profile)
        self.profileMenu.add_command(label="Change Password", command=self.change_password)
        self.profileMenu.add_separator()
        self.profileMenu.add_command(label="Logout", command=self.logout)

        # Main Layout Configuration
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR NAVIGATION ---
        self.sidebar_frame = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color="#12131C")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)  # Spacer pushes logout to bottom

        # App Brand Title
        self.lbl_logo = ctk.CTkLabel(
            self.sidebar_frame, text="EduPulse AI",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="#8B5CF6"
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 2))

        self.lbl_sublogo = ctk.CTkLabel(
            self.sidebar_frame, text="Student Portal",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color="#8A8D9B"
        )
        self.lbl_sublogo.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Dashboard Button
        self.btn_dash = ctk.CTkButton(
            self.sidebar_frame, text="🏠  Dashboard", anchor="w",
            fg_color="#8B5CF6", hover_color="#7C3AED", height=38, corner_radius=8
        )
        self.btn_dash.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        # Academic / Learning Sidebar Buttons
        self.btn_courses = ctk.CTkButton(
            self.sidebar_frame, text="📚  Enrolled Courses", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.open_courses
        )
        self.btn_courses.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_lectures = ctk.CTkButton(
            self.sidebar_frame, text="📖  Lectures", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.open_lectures
        )
        self.btn_lectures.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        self.btn_quiz = ctk.CTkButton(
            self.sidebar_frame, text="📝  Take Quiz", anchor="w",
            fg_color="#10B981", hover_color="#059669", text_color="#FFFFFF", height=38,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"), corner_radius=8,
            command=self.take_quiz
        )
        self.btn_quiz.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        self.btn_schedule = ctk.CTkButton(
            self.sidebar_frame, text="📅  Schedule & Timetable", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.open_schedule
        )
        self.btn_schedule.grid(row=6, column=0, padx=15, pady=5, sticky="ew")

        self.btn_grades = ctk.CTkButton(
            self.sidebar_frame, text="📊  Grades & Analytics", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.open_grades
        )
        self.btn_grades.grid(row=7, column=0, padx=15, pady=5, sticky="ew")

        # Profile Actions (Sidebar)
        self.btn_profile = ctk.CTkButton(
            self.sidebar_frame, text="👤  Profile Settings", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.toggle_profile_overlay
        )
        self.btn_profile.grid(row=8, column=0, padx=15, pady=5, sticky="ew")

        self.btn_change_pass = ctk.CTkButton(
            self.sidebar_frame, text="🔒  Change Password", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.change_password
        )
        self.btn_change_pass.grid(row=9, column=0, padx=15, pady=5, sticky="ew")

        # Logout Button
        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame, text="🚪  Logout", anchor="w",
            fg_color="transparent", text_color="#E74C3C", hover_color="#202330", height=38,
            command=self.logout
        )
        self.btn_logout.grid(row=11, column=0, padx=15, pady=20, sticky="ew")

        # --- MAIN RIGHT CONTENT CONTAINER ---
        self.main_content = ctk.CTkFrame(self.root, fg_color="#0A0B10", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # Header Bar Component
        self.create_header_bar()

        # Scrollable Body Panel for Dynamic Cards
        self.scroll_body = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent", corner_radius=0)
        self.scroll_body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Build Main Body Content
        self.build_stats_grid()
        self.build_middle_analytics_section()
        self.build_course_progress_list()

        # --- SLIDE-OVER PROFILE MODAL SIDE PANEL ---
        self.profile_overlay_frame = ctk.CTkFrame(self.root, width=300, fg_color="#181924", corner_radius=0, border_width=1, border_color="#2B2B38")

        self.root.mainloop()

    def get_student_name(self):
        """Helper to safely retrieve student name regardless of tuple format"""
        if self.student_detail and len(self.student_detail) > 2:
            return str(self.student_detail[2])
        return "Student User"

    def get_student_email(self):
        """Helper to safely retrieve student email regardless of tuple format"""
        if self.student_detail and len(self.student_detail) > 3:
            return str(self.student_detail[3])
        return "N/A"

    def get_student_id(self):
        """Helper to safely retrieve student ID"""
        if self.student_detail and len(self.student_detail) > 0:
            return self.student_detail[0]
        return None

    def create_header_bar(self):
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        student_name = self.get_student_name()

        # Welcome Text
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", anchor="w")

        lbl_dash_title = ctk.CTkLabel(
            title_frame, text="Student Dashboard",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color="#8A8D9B"
        )
        lbl_dash_title.pack(anchor="w")

        lbl_welcome = ctk.CTkLabel(
            title_frame, text=f"Welcome back, {student_name} 👋",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold")
        )
        lbl_welcome.pack(anchor="w")

        # Header Profile Action Trigger
        profile_chip = ctk.CTkFrame(header, fg_color="#181924", corner_radius=20, border_width=1, border_color="#2B2B38")
        profile_chip.pack(side="right", padx=10)

        btn_prof_trigger = ctk.CTkButton(
            profile_chip, text=f"👤  {student_name}", fg_color="transparent",
            text_color="#FFFFFF", hover_color="#202330", corner_radius=20,
            command=self.toggle_profile_overlay
        )
        btn_prof_trigger.pack(padx=5, pady=2)

    def build_stats_grid(self):
        cards_frame = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(10, 20))

        self.create_stat_card(cards_frame, col=0, count="3.88", label="Cumulative GPA", trend="+0.12 this term", circle_color="#8B5CF6")
        self.create_stat_card(cards_frame, col=1, count="94 / 120", label="Completed Credits", trend="78% Completed", circle_color="#3B82F6")
        self.create_stat_card(cards_frame, col=2, count="28.5 hrs", label="Weekly Study Time", trend="+4.2 hrs vs last week", circle_color="#10B981")

    def create_stat_card(self, parent, col, count, label, trend, circle_color):
        card = ctk.CTkFrame(parent, fg_color="#181924", corner_radius=14, border_width=1, border_color="#242634")
        card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        circle = ctk.CTkLabel(
            card, text=count, font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            fg_color=circle_color, text_color="white", corner_radius=10, height=36, width=110
        )
        circle.pack(anchor="w", padx=15, pady=(15, 5))

        lbl = ctk.CTkLabel(card, text=label, font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#FFFFFF")
        lbl.pack(anchor="w", padx=15, pady=(2, 0))

        lbl_trend = ctk.CTkLabel(card, text=f"📈 {trend}", font=ctk.CTkFont(family="Arial", size=11), text_color="#8A8D9B")
        lbl_trend.pack(anchor="w", padx=15, pady=(0, 15))

    def build_middle_analytics_section(self):
        middle_frame = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        middle_frame.pack(fill="x", pady=10)
        middle_frame.grid_columnconfigure(0, weight=2)
        middle_frame.grid_columnconfigure(1, weight=1)

        # Performance Box (Left)
        perf_box = ctk.CTkFrame(middle_frame, fg_color="#181924", corner_radius=14, border_width=1, border_color="#242634")
        perf_box.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        lbl_perf_title = ctk.CTkLabel(
            perf_box, text="Academic Performance Overview",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold")
        )
        lbl_perf_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Visual Score Indicators
        scores_frame = ctk.CTkFrame(perf_box, fg_color="transparent")
        scores_frame.pack(fill="x", padx=20, pady=10)

        self.create_mini_progress(scores_frame, "Data Structures & Algorithms", 0.88, "#8B5CF6")
        self.create_mini_progress(scores_frame, "Database Systems & SQL", 0.76, "#3B82F6")
        self.create_mini_progress(scores_frame, "Computer Networks", 0.92, "#10B981")

        # Deadlines Panel (Right)
        deadline_box = ctk.CTkFrame(middle_frame, fg_color="#181924", corner_radius=14, border_width=1, border_color="#242634")
        deadline_box.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        lbl_dead_title = ctk.CTkLabel(
            deadline_box, text="Upcoming Tasks",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold")
        )
        lbl_dead_title.pack(anchor="w", padx=20, pady=(15, 10))

        self.create_task_item(deadline_box, "Algorithms Quiz", "Available Now", "#10B981", action_cmd=self.take_quiz)
        self.create_task_item(deadline_box, "Database Midterm", "May 14, 10:00 AM", "#3B82F6")
        self.create_task_item(deadline_box, "UI/UX Case Study", "May 18, 05:00 PM", "#8B5CF6")

    def create_mini_progress(self, parent, course_title, value, color):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x", pady=6)

        lbl = ctk.CTkLabel(box, text=course_title, font=ctk.CTkFont(family="Arial", size=11), text_color="#A0A5B5")
        lbl.pack(anchor="w")

        pbar = ctk.CTkProgressBar(box, height=8, progress_color=color, fg_color="#2B2B38")
        pbar.pack(fill="x", pady=(2, 0))
        pbar.set(value)

    def create_task_item(self, parent, title, date_str, tag_color, action_cmd=None):
        box = ctk.CTkFrame(parent, fg_color="#12131C", corner_radius=8)
        box.pack(fill="x", padx=15, pady=6)

        tag = ctk.CTkFrame(box, width=4, fg_color=tag_color, corner_radius=2)
        tag.pack(side="left", fill="y", padx=(5, 10), pady=5)

        info = ctk.CTkFrame(box, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=5)

        lbl_t = ctk.CTkLabel(info, text=title, font=ctk.CTkFont(family="Arial", size=12, weight="bold"))
        lbl_t.pack(anchor="w")

        lbl_d = ctk.CTkLabel(info, text=date_str, font=ctk.CTkFont(family="Arial", size=10), text_color="#6C7280")
        lbl_d.pack(anchor="w")

        if action_cmd:
            btn_act = ctk.CTkButton(
                box, text="Start", width=60, height=26,
                fg_color="#10B981", hover_color="#059669",
                font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
                command=action_cmd
            )
            btn_act.pack(side="right", padx=10, pady=5)

    def build_course_progress_list(self):
        container = ctk.CTkFrame(self.scroll_body, fg_color="#181924", corner_radius=14, border_width=1, border_color="#242634")
        container.pack(fill="x", pady=15)

        lbl_title = ctk.CTkLabel(
            container, text="Active Enrolled Courses",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold")
        )
        lbl_title.pack(anchor="w", padx=20, pady=(15, 10))

        courses = [
            ("CS-301", "Data Structures & Algorithms", "Prof. Robert Chen", "85% Completed"),
            ("CS-304", "Computer Networks & Security", "Prof. Sarah Jenkins", "62% Completed"),
            ("CS-310", "Database Management Systems", "Dr. Alan Turing", "90% Completed")
        ]

        for code, name, instructor, progress in courses:
            row = ctk.CTkFrame(container, fg_color="#12131C", corner_radius=10)
            row.pack(fill="x", padx=20, pady=6)

            lbl_code = ctk.CTkLabel(row, text=code, font=ctk.CTkFont(family="Arial", size=11, weight="bold"), text_color="#8B5CF6")
            lbl_code.pack(side="left", padx=15, pady=10)

            lbl_name = ctk.CTkLabel(row, text=name, font=ctk.CTkFont(family="Arial", size=12, weight="bold"))
            lbl_name.pack(side="left", padx=10, pady=10)

            lbl_inst = ctk.CTkLabel(row, text=instructor, font=ctk.CTkFont(family="Arial", size=11), text_color="#6C7280")
            lbl_inst.pack(side="left", padx=20, pady=10)

            lbl_prog = ctk.CTkLabel(row, text=progress, font=ctk.CTkFont(family="Arial", size=11, weight="bold"), text_color="#10B981")
            lbl_prog.pack(side="right", padx=15, pady=10)

    def toggle_profile_overlay(self):
        """Dynamic Slide-Over Modal Overlay for Profile View"""
        if self.profile_modal_visible:
            self.profile_overlay_frame.grid_forget()
            self.profile_modal_visible = False
        else:
            self.profile_overlay_frame.grid(row=0, column=1, sticky="nse", padx=0, pady=0)
            self.profile_modal_visible = True
            self.build_profile_modal_content()

    def build_profile_modal_content(self):
        for child in self.profile_overlay_frame.winfo_children():
            child.destroy()

        btn_close = ctk.CTkButton(
            self.profile_overlay_frame, text="✕", width=30, fg_color="transparent",
            text_color="#A0A5B5", hover_color="#202330", command=self.toggle_profile_overlay
        )
        btn_close.pack(anchor="e", padx=10, pady=10)

        lbl_avatar = ctk.CTkLabel(
            self.profile_overlay_frame, text="👤", font=ctk.CTkFont(size=50),
            fg_color="#242634", corner_radius=40, width=80, height=80
        )
        lbl_avatar.pack(pady=(10, 10))

        student_name = self.get_student_name()
        student_email = self.get_student_email()
        student_id = str(self.get_student_id())

        lbl_name = ctk.CTkLabel(self.profile_overlay_frame, text=student_name, font=ctk.CTkFont(size=16, weight="bold"))
        lbl_name.pack()

        lbl_role = ctk.CTkLabel(self.profile_overlay_frame, text="Honor Roll Student", font=ctk.CTkFont(size=11), text_color="#8B5CF6")
        lbl_role.pack(pady=(2, 15))

        # Details Cards
        self.create_profile_info_row("Student ID", student_id)
        self.create_profile_info_row("Email Address", student_email)
        self.create_profile_info_row("Department", "Computer Science")
        self.create_profile_info_row("Academic Advisor", "Dr. Alan Turing")

        btn_edit = ctk.CTkButton(
            self.profile_overlay_frame, text="✏ Edit Profile Details",
            fg_color="#3F51B5", hover_color="#303F9F", height=35,
            command=self.edit_profile
        )
        btn_edit.pack(fill="x", padx=20, pady=20)

    def create_profile_info_row(self, label, value):
        box = ctk.CTkFrame(self.profile_overlay_frame, fg_color="#12131C", corner_radius=8)
        box.pack(fill="x", padx=20, pady=5)

        lbl_title = ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=10), text_color="#6C7280")
        lbl_title.pack(anchor="w", padx=10, pady=(5, 0))

        lbl_val = ctk.CTkLabel(box, text=value, font=ctk.CTkFont(size=12, weight="bold"))
        lbl_val.pack(anchor="w", padx=10, pady=(0, 5))

    def apply_global_table_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=35,
            font=("Arial", 11),
            background="#2b2b2b",
            foreground="#ffffff",
            fieldbackground="#2b2b2b",
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold"),
            background="#1f1f1f",
            foreground="#ffffff",
            relief="flat"
        )

    # --- ACTION HANDLERS ---
    def open_courses(self):
        student_id = self.get_student_id()
        if student_id is not None:
            studentCourses(student_id)
        else:
            msg.showerror("Error", "Could not retrieve valid Student ID.")

    def open_lectures(self):
        student_id = self.get_student_id()
        if student_id is not None:
            studentLectures(student_id)

    def take_quiz(self):
        student_id = self.get_student_id()
        if student_id is not None:
            attemptQuiz(student_id)
        else:
            msg.showerror("Error", "Could not retrieve valid Student ID.")

    def open_schedule(self):
        msg.showinfo("Schedule", "Schedule screen is under construction.")

    def open_grades(self):
        msg.showinfo("Grades", "Grades screen is under construction.")

    def edit_profile(self):
        student_id = self.get_student_id()
        if student_id is not None:
            Edit_Profile(student_id)

    def change_password(self):
        student_id = self.get_student_id()
        if student_id is not None:
            Change_Pass(student_id)

    def logout(self):
        if msg.askyesno("Logout", "Are you sure you want to exit?"):
            self.root.destroy()


if __name__ == "__main__":
    StudentDashboard()