import tkinter.ttk as ttk
import customtkinter as ctk
from connection import connect

# Configure CustomTkinter default theme settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Theme Color Palette based on dashboard UI
BG_DARK = "#0f0e17"
CARD_BG = "#16151f"
CARD_INNER = "#1e1c2a"
BORDER_COLOR = "#2a273a"
ACCENT_PURPLE = "#7b5bf2"
ACCENT_BLUE = "#3b82f6"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#94a3b8"
DANGER_RED = "#ef4444"


class studentCourses:
    def __init__(self, studentId):
        self.studentId = studentId

        self.root = ctk.CTkToplevel()
        self.root.title("My Department and Courses")
        self.root.configure(fg_color=BG_DARK)
        self.center_window(950, 700)

        # Force window to the front
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(10, lambda: self.root.attributes("-topmost", False))

        self.conn = connect()
        self.cr = self.conn.cursor()

        # Header Title
        ctk.CTkLabel(
            self.root,
            text="My Department and Course",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT_WHITE
        ).pack(pady=(20, 10))

        self.style_treeview()
        self.buildDetails()
        self.buildOtherCourses()

        # Close Button
        ctk.CTkButton(
            self.root,
            text="Close",
            width=260,
            height=40,
            fg_color=DANGER_RED,
            hover_color="#dc2626",
            font=("Segoe UI", 14, "bold"),
            corner_radius=8,
            command=lambda: self.root.destroy()
        ).pack(pady=16)

        self.root.mainloop()

    def center_window(self, width, height):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")

        # Configure Table Colors
        style.configure(
            "Treeview",
            background=CARD_BG,
            foreground=TEXT_WHITE,
            fieldbackground=CARD_BG,
            rowheight=35,
            font=("Segoe UI", 11),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=CARD_INNER,
            foreground=ACCENT_PURPLE,
            font=("Segoe UI", 12, "bold"),
            relief="flat"
        )
        style.map("Treeview", background=[("selected", ACCENT_PURPLE)])
        style.map("Treeview.Heading", background=[("active", CARD_INNER)])

    def buildDetails(self):
        # Query matches exact schema: JOIN courses on c.id = s.course_id and JOIN department on d.name = c.department_name
        q = """SELECT c.name, c.description, c.semester, c.duration, d.name
               FROM students s
               JOIN courses c ON c.id = s.course_id
               JOIN department d ON d.name = c.department_name
               WHERE s.id = %s"""
        self.cr.execute(q, (self.studentId,))
        row = self.cr.fetchone()

        card = ctk.CTkFrame(
            self.root,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.pack(pady=15, padx=40, fill="x")

        if row is None:
            ctk.CTkLabel(
                card,
                text="No course has been assigned to you yet.",
                font=("Segoe UI", 16),
                text_color=TEXT_MUTED
            ).pack(pady=40)
            self.departmentName = None
            return

        name, description, semester, duration, department = row
        self.departmentName = department

        ctk.CTkLabel(
            card,
            text=name,
            font=("Segoe UI", 22, "bold"),
            text_color=ACCENT_PURPLE
        ).pack(pady=(20, 2))

        ctk.CTkLabel(
            card,
            text=f"{department} Department",
            font=("Segoe UI", 14, "bold"),
            text_color=ACCENT_BLUE
        ).pack()

        ctk.CTkLabel(
            card,
            text=description or "No description available",
            font=("Segoe UI", 12),
            text_color=TEXT_MUTED,
            wraplength=760,
            justify="center"
        ).pack(pady=14, padx=30)

        row_frame = ctk.CTkFrame(card, fg_color="transparent")
        row_frame.pack(pady=(0, 20))

        for title, value in [("Semesters", semester), ("Duration", duration)]:
            box = ctk.CTkFrame(
                row_frame,
                fg_color=CARD_INNER,
                corner_radius=10,
                border_width=1,
                border_color=BORDER_COLOR,
                width=180,
                height=70
            )
            box.pack(side="left", padx=12)
            box.pack_propagate(False)

            ctk.CTkLabel(
                box,
                text=str(value),
                font=("Segoe UI", 20, "bold"),
                text_color=ACCENT_PURPLE
            ).pack(pady=(10, 0))

            ctk.CTkLabel(
                box,
                text=title,
                font=("Segoe UI", 11),
                text_color=TEXT_MUTED
            ).pack()

    def buildOtherCourses(self):
        if self.departmentName is None:
            return

        ctk.CTkLabel(
            self.root,
            text="Other courses in my department",
            font=("Segoe UI", 16, "bold"),
            text_color=TEXT_WHITE
        ).pack(pady=(10, 8))

        wrapper = ctk.CTkFrame(
            self.root,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER_COLOR
        )
        wrapper.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        table = ttk.Treeview(
            wrapper,
            columns=("name", "semesters", "duration", "lectures"),
            show="headings",
            height=5
        )
        for key, title, width in [("name", "Course", 260), ("semesters", "Semesters", 130),
                                  ("duration", "Duration", 150), ("lectures", "Lectures", 130)]:
            table.heading(key, text=title)
            table.column(key, width=width, anchor="center")

        table.pack(fill="both", expand=True, padx=12, pady=12)

        # Query matches exact schema: JOIN courses on c.department_name = d.name
        q = """SELECT c.name, c.semester, c.duration,
                      (SELECT COUNT(*) FROM lectures l WHERE l.course_id = c.id)
               FROM courses c JOIN department d ON d.name = c.department_name
               WHERE d.name = %s ORDER BY c.name"""
        self.cr.execute(q, (self.departmentName,))

        for record in self.cr.fetchall():
            table.insert("", "end", values=record)


if __name__ == "__main__":
    studentCourses(1)