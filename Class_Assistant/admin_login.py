from unittest import result

import customtkinter as ctk
import tkinter.messagebox
from connection import connect
import adminDashboard

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AdminLogin:
    def __init__(self, parent=None):
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)
            self.root.grab_set()
            self.root.focus_force()
        else:
            self.root = ctk.CTk()

        self.root.geometry("450x500")
        self.root.title("Admin Login")
        self.root.resizable(False, False)
        self.root.after(0, lambda: self.root.state("zoomed"))

        self.center_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.conn = connect()
        self.cur = self.conn.cursor()

        # Title Label
        self.main_label = ctk.CTkLabel(
            self.center_frame,
            text="Admin Login",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold")
        )
        self.main_label.pack(pady=(40, 20))

        # Card Frame
        self.card_frame = ctk.CTkFrame(self.center_frame, fg_color="#2b2b2b", corner_radius=15, width=360)
        self.card_frame.pack(padx=30, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13)

        # Email / Admin ID Input
        self.lb_email = ctk.CTkLabel(self.card_frame, text="Email or Mobile :-", font=font_label)
        self.lb_email.pack(anchor="w", padx=25, pady=(25, 5))

        self.txt_email = ctk.CTkEntry(
            self.card_frame,
            placeholder_text="Enter email or mobile...",
            width=330,
            height=38,
            corner_radius=8
        )
        self.txt_email.pack(padx=25, pady=(0, 15))

        # Password Input
        self.lb_password = ctk.CTkLabel(self.card_frame, text="Password :-", font=font_label)
        self.lb_password.pack(anchor="w", padx=25, pady=(5, 5))

        self.txt_password = ctk.CTkEntry(
            self.card_frame,
            placeholder_text="Enter password...",
            width=330,
            height=38,
            corner_radius=8,
            show="*"
        )
        self.txt_password.pack(padx=25, pady=(0, 20))
        self.txt_password.bind("<Return>", lambda event: self.login())

        # Login Button
        self.btn_login = ctk.CTkButton(
            self.card_frame,
            text="Login",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            width=180,
            height=40,
            corner_radius=10,
            command=self.login
        )
        self.btn_login.pack(pady=15)

        self.root.focus_force()

    def login(self):
        login_input = self.txt_email.get().strip()
        password = self.txt_password.get().strip()

        if not login_input or not password:
            tkinter.messagebox.showerror("Error", "Please fill all fields", parent=self.root)
            return

        # Fetch admin details matching email/mobile AND password
        q = "SELECT id, status, name, role FROM admin WHERE (email = %s OR mobile = %s) AND password = %s"
        self.cur.execute(q, (login_input, login_input, password))
        self.result = self.cur.fetchone()
        print(self.result)

        if self.result:
            admin_id = self.result[0]
            status = str(self.result[1]).strip().lower()

            # Check if admin status is inactive
            if status == "inactive":
                tkinter.messagebox.showwarning("Warning", "admin is inactive try again later", parent=self.root)
            else:
                tkinter.messagebox.showinfo("Success", "admin login successfully", parent=self.root)
                parent = self.root.master
                self.root.destroy()
                if parent and parent.winfo_exists():
                    parent.destroy()
                app = adminDashboard.admindashboard(self.result)
                app.root.mainloop()
        else:
            tkinter.messagebox.showerror("Error", "Invalid Credentials", parent=self.root)


if __name__ == "__main__":
    app = AdminLogin()
    app.root.mainloop()