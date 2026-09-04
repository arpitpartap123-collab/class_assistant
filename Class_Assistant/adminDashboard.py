import customtkinter as ctk
import tkinter.messagebox as msg
from tkinter import Menu, ttk
import change_pass

# Import existing admin modules
import add_admin
import manage_admin

# Import user / student modules
import add_user
import manage_user

# Import department modules
import add_dept
import manage_dept

# Import course modules
import add_courses
import manage_courses

# Import lecture modules
import add_lecture
import viewlecture
import viewquestions

# Import AI notes module
import veiwnotes

# Import quiz module
import veiwquizadmin

# Import profile module
import edit_profile

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Modern Theme Palette
COLOR_BG_DARK = "#0D0E15"
COLOR_SIDEBAR = "#13151F"
COLOR_CARD = "#1A1C29"
COLOR_CARD_HOVER = "#222536"
COLOR_ACCENT = "#4361EE"
COLOR_ACCENT_HOVER = "#3046B5"
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#8A8D9B"
COLOR_RED = "#E74C3C"


class AnimatedSidebarButton(ctk.CTkButton):
    """Custom sidebar navigation button with smooth hover animation effects."""

    def __init__(self, master, icon, text, command=None, **kwargs):
        display_text = f"{icon}   {text}"
        super().__init__(
            master,
            text=display_text,
            anchor="w",
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color=COLOR_TEXT_SECONDARY,
            hover_color=COLOR_CARD_HOVER,
            font=ctk.CTkFont(family="Arial", size=13, weight="normal"),
            command=command,
            **kwargs
        )
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _on_hover(self, _event=None):
        self.configure(text_color=COLOR_TEXT_PRIMARY)

    def _on_leave(self, _event=None):
        self.configure(text_color=COLOR_TEXT_SECONDARY)


class admindashboard:
    def __init__(self, admin_detail=None):
        self.admin_detail = admin_detail
        print("Logged in user details:", self.admin_detail)

        self.root = ctk.CTk()
        self.root.title("AI College Agent - Admin Dashboard")
        self.root.geometry("1180x720")
        self.root.after(0, lambda: self.root.state("zoomed"))

        self.apply_global_table_style()
        self.is_super_admin_user = self.is_super_admin()

        # ---- Native Top Cascade Menu ----
        self.mainMenu = Menu(self.root)
        self.root.config(menu=self.mainMenu)

        if self.is_super_admin_user:
            self.adminMenu = Menu(self.mainMenu, tearoff=0)
            self.mainMenu.add_cascade(label="Faculty Menu", menu=self.adminMenu)
            self.adminMenu.add_command(label="Add Faculty", command=self.openadd_admin)
            self.adminMenu.add_command(label="Manage Faculty", command=self.manage_admin)

        self.userMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Student Menu", menu=self.userMenu)
        self.userMenu.add_command(label="Add Student", command=self.open_add_user)
        self.userMenu.add_command(label="Manage Student", command=self.open_manage_user)

        self.deptMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Department Menu", menu=self.deptMenu)
        self.deptMenu.add_command(label="Add Department", command=self.open_add_dept)
        self.deptMenu.add_command(label="Manage Department", command=self.open_manage_dept)

        self.courseMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Course Menu", menu=self.courseMenu)
        self.courseMenu.add_command(label="Add Course", command=self.open_add_course)
        self.courseMenu.add_command(label="Manage Course", command=self.open_manage_course)

        self.lectureMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Lecture Menu", menu=self.lectureMenu)
        self.lectureMenu.add_command(label="Add Lecture", command=self.open_add_lecture)
        self.lectureMenu.add_command(label="View Lectures", command=self.open_view_lecture)
        self.lectureMenu.add_command(label="View Questions", command=self.open_view_questions)
        self.lectureMenu.add_command(label="AI Notes Review", command=self.open_view_notes)

        # Quiz Menu (Top Navigation)
        self.quizMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Quiz Activity", menu=self.quizMenu)
        self.quizMenu.add_command(label="View Quiz Activity", command=self.open_quiz_activity)

        self.profileMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Profile", menu=self.profileMenu)
        self.profileMenu.add_command(label="Edit Profile", command=self.edit_profile)
        self.profileMenu.add_command(label="Change Password", command=self.change_password)
        self.profileMenu.add_command(label="Logout", command=self.logout)

        # ---- Layout Frame Distribution ----
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # ---- SIDEBAR CONTAINER ----
        self.sidebar_outer = ctk.CTkFrame(self.root, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar_outer.grid(row=0, column=0, sticky="nsew")
        self.sidebar_outer.grid_rowconfigure(1, weight=1)

        # Sidebar Header Branding
        self.brand_frame = ctk.CTkFrame(self.sidebar_outer, fg_color="transparent")
        self.brand_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.lbl_logo = ctk.CTkLabel(
            self.brand_frame, text="⚡ Class Pulse",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.lbl_logo.pack(anchor="w")

        self.lbl_sublogo = ctk.CTkLabel(
            self.brand_frame, text="Admin Operations Panel",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_sublogo.pack(anchor="w", pady=(2, 0))

        # ---- SCROLLABLE SIDEBAR NAVIGATION AREA ----
        self.sidebar = ctk.CTkScrollableFrame(
            self.sidebar_outer, fg_color="transparent", width=220,
            scrollbar_button_color="#1E2130", scrollbar_button_hover_color=COLOR_ACCENT
        )
        self.sidebar.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # --- Section 1: Main Menu ---
        self._create_section_header("MAIN MENU")

        self.btn_dash = ctk.CTkButton(
            self.sidebar, text="🏠   Dashboard", anchor="w",
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, height=40, corner_radius=8,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold")
        )
        self.btn_dash.pack(fill="x", pady=3)

        # --- Section 2: Academics & Student Management ---
        self._create_section_header("ACADEMICS & STUDENTS")
        AnimatedSidebarButton(self.sidebar, "🎓", "Add Student", command=self.open_add_user).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "👥", "Manage Student", command=self.open_manage_user).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "🏛", "Add Department", command=self.open_add_dept).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "📋", "Manage Dept", command=self.open_manage_dept).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "📘", "Add Course", command=self.open_add_course).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "📖", "Manage Course", command=self.open_manage_course).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "📚", "Add Lecture", command=self.open_add_lecture).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "🗂", "View Lectures", command=self.open_view_lecture).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "❓", "View Questions", command=self.open_view_questions).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "📌", "AI Notes Review", command=self.open_view_notes).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "📝", "Quiz Activity", command=self.open_quiz_activity).pack(fill="x", pady=2)

        # --- Section 3: Faculty Operations (Super Admin Only) ---
        if self.is_super_admin_user:
            self._create_section_header("FACULTY CONTROL")
            AnimatedSidebarButton(self.sidebar, "👤", "Add Faculty", command=self.openadd_admin).pack(fill="x", pady=2)
            AnimatedSidebarButton(self.sidebar, "⚙", "Manage Faculty", command=self.manage_admin).pack(fill="x", pady=2)

        # --- Section 4: Account & Profile ---
        self._create_section_header("ACCOUNT")
        AnimatedSidebarButton(self.sidebar, "✏", "Edit Profile", command=self.edit_profile).pack(fill="x", pady=2)
        AnimatedSidebarButton(self.sidebar, "🔒", "Change Password", command=self.change_password).pack(fill="x", pady=2)

        # ---- SIDEBAR FOOTER (LOGOUT) ----
        self.logout_frame = ctk.CTkFrame(self.sidebar_outer, fg_color="transparent")
        self.logout_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")

        self.btn_logout = ctk.CTkButton(
            self.logout_frame, text="🚪   Logout System", anchor="w",
            fg_color="transparent", text_color=COLOR_RED, hover_color="#2A1616",
            height=40, corner_radius=8, font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            command=self.logout
        )
        self.btn_logout.pack(fill="x")

        # ---- MAIN RIGHT CONTENT AREA ----
        self.main_content = ctk.CTkFrame(self.root, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Top Welcome Header
        admin_name = "Admin User"
        if self.admin_detail and len(self.admin_detail) > 2:
            admin_name = str(self.admin_detail[2]).strip() or "Admin User"
        elif self.admin_detail and len(self.admin_detail) > 1:
            admin_name = str(self.admin_detail[1]).strip() or "Admin User"

        self.header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=35, pady=(25, 10))

        self.lbl_dash_title = ctk.CTkLabel(
            self.header_frame, text="System Overview",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_dash_title.pack(anchor="w")

        self.lbl_welcome = ctk.CTkLabel(
            self.header_frame, text=f"Welcome Back, {admin_name}",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.lbl_welcome.pack(anchor="w", pady=(2, 0))

        # Animated Quick Stats Cards Grid
        self.cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=30, pady=10)

        self.create_stat_card(self.cards_frame, col=0, count="4", label="Active Departments", circle_color="#3F51B5")
        self.create_stat_card(self.cards_frame, col=1, count="6", label="Registered Courses", circle_color="#8E24AA")
        self.create_stat_card(self.cards_frame, col=2, count="18", label="Total Faculty Staff", circle_color="#4CAF50")

        # Announcements
        self.lbl_announcements = ctk.CTkLabel(
            self.main_content, text="Recent Announcements",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.lbl_announcements.pack(anchor="w", padx=35, pady=(30, 10))

        self.create_announcement_item("Fall Admissions & Registrations Now Open", "2026-08-21")
        self.create_announcement_item("Annual Tech Fest - InnovateX Scheduled", "2026-08-21")

    def _create_section_header(self, text):
        """Helper to create sub-headers inside the scrollable navigation sidebar."""
        lbl = ctk.CTkLabel(
            self.sidebar, text=text,
            font=ctk.CTkFont(family="Arial", size=10, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY, anchor="w"
        )
        lbl.pack(fill="x", padx=8, pady=(16, 4))

    def is_super_admin(self):
        if self.admin_detail and len(self.admin_detail) > 3:
            status = str(self.admin_detail[3]).strip().lower()
            return status in ["superadmin", "super admin", "super_admin", "super-admin"]
        return False

    def create_stat_card(self, parent, col, count, label, circle_color):
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=14, width=220, height=110)
        card.grid(row=0, column=col, padx=12, pady=10)

        circle = ctk.CTkLabel(
            card, text=count, font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            fg_color=circle_color, text_color="white", width=40, height=40, corner_radius=20
        )
        circle.pack(anchor="w", padx=16, pady=(16, 6))

        lbl = ctk.CTkLabel(card, text=label, font=ctk.CTkFont(family="Arial", size=12), text_color=COLOR_TEXT_SECONDARY)
        lbl.pack(anchor="w", padx=16, pady=(0, 16))

    def create_announcement_item(self, title, date_str):
        box = ctk.CTkFrame(self.main_content, fg_color=COLOR_CARD, corner_radius=10, height=48)
        box.pack(fill="x", padx=35, pady=6)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color=COLOR_TEXT_PRIMARY)
        lbl_t.pack(side="left", padx=20, pady=12)

        lbl_d = ctk.CTkLabel(box, text=date_str, font=ctk.CTkFont(family="Arial", size=11), text_color=COLOR_TEXT_SECONDARY)
        lbl_d.pack(side="right", padx=20, pady=12)

    def apply_global_table_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=36,
            font=("Arial", 11),
            background="#1A1C29",
            foreground="#ffffff",
            fieldbackground="#1A1C29",
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold"),
            background="#13151F",
            foreground="#ffffff",
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", "#4361EE")],
            foreground=[("selected", "#ffffff")]
        )

    # Quiz Handlers
    def open_quiz_activity(self):
        try:
            veiwquizadmin.viewQuizAdmin()
        except Exception as e:
            msg.showerror("Error", f"Failed to open Quiz Activity: {e}")

    # Course Handlers
    def open_add_course(self):
        try:
            add_courses.Add_Course(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Add Course: {e}")

    def open_manage_course(self):
        try:
            manage_courses.Manage_Course(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Manage Course: {e}")

    # Lecture & AI Notes Handlers
    def open_add_lecture(self):
        try:
            add_lecture.Main(self.admin_detail)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Add Lecture: {e}")

    def open_view_lecture(self):
        try:
            viewlecture.viewLecture()
        except Exception as e:
            msg.showerror("Error", f"Failed to open View Lectures: {e}")

    def open_view_questions(self):
        try:
            viewquestions.viewQuestions(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open View Questions: {e}")

    def open_view_notes(self):
        try:
            veiwnotes.viewNotes(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open AI Notes Review: {e}")

    # User / Student Handlers
    def open_add_user(self):
        try:
            add_user.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Add Student: {e}")

    def open_manage_user(self):
        try:
            manage_user.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Manage Student: {e}")

    # Admin Handlers
    def openadd_admin(self):
        if not self.is_super_admin_user:
            msg.showwarning("Access Denied", "Only Super Admins are allowed to access Add Faculty.")
            return
        try:
            add_admin.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Add Faculty: {e}")

    def manage_admin(self):
        if not self.is_super_admin_user:
            msg.showwarning("Access Denied", "Only Super Admins are allowed to access Manage Faculty.")
            return
        try:
            manage_admin.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Manage Faculty: {e}")

    # Department Handlers
    def open_add_dept(self):
        try:
            add_dept.Add_dept(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Add Department: {e}")

    def open_manage_dept(self):
        try:
            manage_dept.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Manage Department: {e}")

    # Profile Handlers
    def edit_profile(self):
        if self.admin_detail:
            admin_id = self.admin_detail[0]
            edit_profile.Edit_Profile(self.root, admin_id)
        else:
            msg.showerror("Error", "Admin information not found")

    def change_password(self):
        if self.admin_detail:
            admin_id = self.admin_detail[0]
            change_pass.Change_Password(self.root, admin_id)
        else:
            msg.showerror("Error", "Admin information not found")

    def logout(self):
        if msg.askyesno("Logout", "Are you sure you want to log out?"):
            self.root.destroy()


if __name__ == "__main__":
    sample_admin = (1, "John Doe", "john@example.com", "Super Admin")
    app = admindashboard(admin_detail=sample_admin)
    app.root.mainloop()