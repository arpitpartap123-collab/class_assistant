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

# Import profile module
import edit_profile

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class admindashboard:
    def __init__(self, admin_detail=None):
        self.admin_detail = admin_detail
        print("Logged in user details:", self.admin_detail)

        self.root = ctk.CTk()
        self.root.title("AI College Agent - Admin Dashboard")
        self.root.geometry("1100x650")
        self.root.after(0, lambda: self.root.state("zoomed"))

        # Configure global table styles for manage tables
        self.apply_global_table_style()

        # Check if current user is Super Admin (Checking index 1)
        self.is_super_admin_user = self.is_super_admin()

        # Native Tkinter top menu
        self.mainMenu = Menu(self.root)
        self.root.config(menu=self.mainMenu)

        # Admin Menu (Only Add/Manage Admin if Super Admin)
        self.adminMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Admin Menu", menu=self.adminMenu)
        if self.is_super_admin_user:
            self.adminMenu.add_command(label="Add Admin", command=self.openadd_admin)
            self.adminMenu.add_command(label="Manage Admin", command=self.manage_admin)

        # User / Student Menu
        self.userMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="User Menu", menu=self.userMenu)
        self.userMenu.add_command(label="Add User", command=self.open_add_user)

        # ONLY SHOW MANAGE USER TO SUPER ADMIN IN TOP MENU
        if self.is_super_admin_user:
            self.userMenu.add_command(label="Manage User", command=self.open_manage_user)

        # Department Menu
        self.deptMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Department Menu", menu=self.deptMenu)
        self.deptMenu.add_command(label="Add Department", command=self.open_add_dept)
        self.deptMenu.add_command(label="Manage Department", command=self.open_manage_dept)

        # Profile Menu
        self.profileMenu = Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label="Profile", menu=self.profileMenu)
        self.profileMenu.add_command(label="Edit Profile", command=self.edit_profile)
        self.profileMenu.add_command(label="Change Password", command=self.change_password)
        self.profileMenu.add_command(label="Logout", command=self.logout)

        # Main Layout: Left Sidebar + Right Content Area
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR NAVIGATION ---
        self.sidebar_frame = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color="#12131C")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(11, weight=1)  # Spacer pushes logout to bottom

        # App Brand Title
        self.lbl_logo = ctk.CTkLabel(
            self.sidebar_frame, text="AI College Agent",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="#4361EE"
        )
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 2))

        self.lbl_sublogo = ctk.CTkLabel(
            self.sidebar_frame, text="Admin Panel",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color="#8A8D9B"
        )
        self.lbl_sublogo.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Dashboard Button
        self.btn_dash = ctk.CTkButton(
            self.sidebar_frame, text="🏠  Dashboard", anchor="w",
            fg_color="#3F51B5", hover_color="#303F9F", height=38, corner_radius=8
        )
        self.btn_dash.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        # User / Student Sidebar Buttons
        self.btn_add_user = ctk.CTkButton(
            self.sidebar_frame, text="🎓  Add User", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.open_add_user
        )
        self.btn_add_user.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        # ONLY SHOW MANAGE USER BUTTON IN SIDEBAR TO SUPER ADMIN
        if self.is_super_admin_user:
            self.btn_manage_user = ctk.CTkButton(
                self.sidebar_frame, text="👥  Manage User", anchor="w",
                fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
                command=self.open_manage_user
            )
            self.btn_manage_user.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        # Department Actions
        self.btn_add_dept = ctk.CTkButton(
            self.sidebar_frame, text="🏛  Add Department", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.open_add_dept
        )
        self.btn_add_dept.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        self.btn_manage_dept = ctk.CTkButton(
            self.sidebar_frame, text="📋  Manage Department", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.open_manage_dept
        )
        self.btn_manage_dept.grid(row=6, column=0, padx=15, pady=5, sticky="ew")

        # Admin Operations (Only render sidebar buttons if Super Admin)
        if self.is_super_admin_user:
            self.btn_add_admin = ctk.CTkButton(
                self.sidebar_frame, text="👤  Add Admin", anchor="w",
                fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
                command=self.openadd_admin
            )
            self.btn_add_admin.grid(row=7, column=0, padx=15, pady=5, sticky="ew")

            self.btn_manage_admin = ctk.CTkButton(
                self.sidebar_frame, text="⚙  Manage Admin", anchor="w",
                fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
                command=self.manage_admin
            )
            self.btn_manage_admin.grid(row=8, column=0, padx=15, pady=5, sticky="ew")

        # Profile Actions
        self.btn_edit_prof = ctk.CTkButton(
            self.sidebar_frame, text="✏  Edit Profile", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.edit_profile
        )
        self.btn_edit_prof.grid(row=9, column=0, padx=15, pady=5, sticky="ew")

        self.btn_change_pass = ctk.CTkButton(
            self.sidebar_frame, text="🔒  Change Password", anchor="w",
            fg_color="transparent", text_color="#A0A5B5", hover_color="#202330", height=38,
            command=self.change_password
        )
        self.btn_change_pass.grid(row=10, column=0, padx=15, pady=5, sticky="ew")

        # Logout Button
        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame, text="🚪  Logout", anchor="w",
            fg_color="transparent", text_color="#E74C3C", hover_color="#202330", height=38,
            command=self.logout
        )
        self.btn_logout.grid(row=12, column=0, padx=15, pady=20, sticky="ew")

        # --- MAIN RIGHT CONTENT AREA ---
        self.main_content = ctk.CTkFrame(self.root, fg_color="#0A0B10", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Header Bar
        admin_name = self.admin_detail[0] if self.admin_detail and len(self.admin_detail) > 0 else "Admin User"

        self.lbl_dash_title = ctk.CTkLabel(
            self.main_content, text="Dashboard",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold")
        )
        self.lbl_dash_title.pack(anchor="w", padx=30, pady=(20, 10))

        self.lbl_welcome = ctk.CTkLabel(
            self.main_content, text=f"Welcome back, {admin_name}",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        self.lbl_welcome.pack(anchor="w", padx=30, pady=(10, 20))

        # Stats Cards Grid
        self.cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=30, pady=10)

        self.create_stat_card(self.cards_frame, col=0, count="4", label="Departments", circle_color="#3F51B5")
        self.create_stat_card(self.cards_frame, col=1, count="6", label="Courses", circle_color="#8E24AA")
        self.create_stat_card(self.cards_frame, col=2, count="18", label="Teachers", circle_color="#4CAF50")

        # Announcements
        self.lbl_announcements = ctk.CTkLabel(
            self.main_content, text="Recent Announcements",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold")
        )
        self.lbl_announcements.pack(anchor="w", padx=30, pady=(30, 10))

        self.create_announcement_item("Fall 2026 Admissions Now Open", "2026-05-11")
        self.create_announcement_item("Annual Tech Fest - InnovateX 2026", "2026-05-11")

        # Run mainloop ONLY when running this file directly (standalone execution)
        if __name__ == "__main__":
            self.root.mainloop()

    def is_super_admin(self):
        """Checks if index 1 of self.admin_detail contains the Super Admin role/status."""
        if self.admin_detail and len(self.admin_detail) > 1:
            status = str(self.admin_detail[1]).strip().lower()
            return status in ["superadmin", "super admin", "super_admin"]
        return False

    def create_stat_card(self, parent, col, count, label, circle_color):
        card = ctk.CTkFrame(parent, fg_color="#181924", corner_radius=12, width=220, height=100)
        card.grid(row=0, column=col, padx=10, pady=10)

        circle = ctk.CTkLabel(
            card, text=count, font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            fg_color=circle_color, text_color="white", width=36, height=36, corner_radius=18
        )
        circle.pack(anchor="w", padx=15, pady=(15, 5))

        lbl = ctk.CTkLabel(card, text=label, font=ctk.CTkFont(family="Arial", size=12), text_color="#A0A5B5")
        lbl.pack(anchor="w", padx=15, pady=(0, 15))

    def create_announcement_item(self, title, date_str):
        box = ctk.CTkFrame(self.main_content, fg_color="#181924", corner_radius=10, height=45)
        box.pack(fill="x", padx=30, pady=6)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Arial", size=13, weight="bold"))
        lbl_t.pack(side="left", padx=20, pady=10)

        lbl_d = ctk.CTkLabel(box, text=date_str, font=ctk.CTkFont(family="Arial", size=11), text_color="#6C7280")
        lbl_d.pack(side="right", padx=20, pady=10)

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
        style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "#ffffff")]
        )

    # User / Student Handlers
    def open_add_user(self):
        try:
            add_user.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Add User: {e}")

    def open_manage_user(self):
        if not self.is_super_admin_user:
            msg.showwarning("Access Denied", "Only Super Admins are allowed to access Manage Users.")
            return

        try:
            manage_user.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Manage User: {e}")

    # Admin Handlers
    def openadd_admin(self):
        if not self.is_super_admin_user:
            msg.showwarning("Access Denied", "Only Super Admins are allowed to access Add Admin.")
            return

        try:
            add_admin.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Add Admin: {e}")

    def manage_admin(self):
        if not self.is_super_admin_user:
            msg.showwarning("Access Denied", "Only Super Admins are allowed to access Manage Admin.")
            return

        try:
            manage_admin.Demo(self.root)
        except Exception as e:
            msg.showerror("Error", f"Failed to open Manage Admin: {e}")

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
    app = admindashboard()