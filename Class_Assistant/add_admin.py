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

        self.root.geometry("520x680")
        self.root.title("Add Admin")
        self.root.resizable(False, False)

        # Focus modal window cleanly without topmost z-index conflict
        self.root.grab_set()
        self.root.focus_force()

        self.conn = connect()
        self.cur = self.conn.cursor()

        self.mainlabel = ctk.CTkLabel(
            self.root,
            text="Add Admin",
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
            self.card_frame, values=["Male", "Female", "others"],
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

        # Role
        self.lb6 = ctk.CTkLabel(self.card_frame, text="Enter role :-", font=font_label)
        self.lb6.grid(row=5, column=0, sticky="w", padx=20, pady=10)
        self.txt6 = ctk.CTkOptionMenu(
            self.card_frame, values=["Admin", "Super-Admin"],
            width=220, height=35, corner_radius=8, fg_color="#3a3a3a", button_color="#4a4a4a"
        )
        self.txt6.grid(row=5, column=1, padx=(0, 20), pady=10)
        self.txt6.set("Admin")

        # Password
        self.lb7 = ctk.CTkLabel(self.card_frame, text="Enter password :-", font=font_label)
        self.lb7.grid(row=6, column=0, sticky="w", padx=20, pady=10)
        self.txt7 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8, show="*")
        self.txt7.grid(row=6, column=1, padx=(0, 20), pady=10)

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

    def add_record(self):
        name = self.txt1.get().strip()
        gender = self.txt2.get().strip()
        mobile = self.txt3.get().strip()
        email = self.txt4.get().strip()
        role = self.txt6.get().strip()
        password = self.txt7.get().strip()

        # Validation Checks
        if not name or not gender or not mobile or not email or not password or not role:
            tkinter.messagebox.showerror("Error", "Please fill all fields", parent=self.root)
        elif not (mobile.isdigit() and len(mobile) == 10):
            tkinter.messagebox.showerror("Error", "Mobile number must contain exactly 10 digits", parent=self.root)
        elif "@" not in email:
            tkinter.messagebox.showerror("Error", "Please enter a valid email address containing '@'", parent=self.root)
        else:
            q = "INSERT INTO admin (name, gender, mobile, email, role, password) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cur.execute(q, (name, gender, mobile, email, role, password))
            self.conn.commit()

            tkinter.messagebox.showinfo("Success", "Admin Added Successfully", parent=self.root)
            self.root.destroy()


# Alias for compatibility with import strategies
Add_admin = Demo

if __name__ == "__main__":
    app = Demo()
    app.root.mainloop()