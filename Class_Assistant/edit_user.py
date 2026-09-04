import customtkinter as ctk
import tkinter.messagebox
from connection import connect
import admin_login

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Edit_Profile:
    def __init__(self, parent=None, admin_id=None):
        self.student_id = admin_id
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)
            self.root.grab_set()
            self.root.focus_force()
        else:
            self.root = ctk.CTk()

        self.root.geometry("500x500")
        self.root.title("Edit Profile")
        self.root.resizable(False, False)

        self.conn = connect()
        self.cur = self.conn.cursor()

        self.student_id = admin_id

        self.mainlabel = ctk.CTkLabel(
            self.root,
            text="Edit Profile",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold")
        )
        self.mainlabel.pack(pady=(25, 15))

        self.card_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.card_frame.pack(padx=25, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13)

        # Name
        self.lb1 = ctk.CTkLabel(self.card_frame, text="Name :-", font=font_label)
        self.lb1.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        self.txt1 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt1.grid(row=0, column=1, padx=(0, 20), pady=15)

        # Mobile
        self.lb2 = ctk.CTkLabel(self.card_frame, text="Mobile :-", font=font_label)
        self.lb2.grid(row=1, column=0, sticky="w", padx=20, pady=15)
        self.txt2 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt2.grid(row=1, column=1, padx=(0, 20), pady=15)

        # Email
        self.lb3 = ctk.CTkLabel(self.card_frame, text="Email :-", font=font_label)
        self.lb3.grid(row=2, column=0, sticky="w", padx=20, pady=15)
        self.txt3 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt3.grid(row=2, column=1, padx=(0, 20), pady=15)

        self.load_current_values()

        # Submit Button
        self.bt1 = ctk.CTkButton(
            self.root,
            text="Submit",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            width=180,
            height=40,
            corner_radius=10,
            command=self.update
        )
        self.bt1.pack(pady=15)

    def load_current_values(self):
        # Pre-fill fields with the admin's current values, same as manage_admin's update popup
        if not self.student_id:
            return
        q = "SELECT name, mobile, email FROM students WHERE id=%s"
        self.cur.execute(q, (self.student_id,))
        result = self.cur.fetchone()
        if result:
            self.txt1.insert(0, result[0])
            self.txt2.insert(0, result[1])
            self.txt3.insert(0, result[2])

    def update(self):
        name = self.txt1.get().strip()
        mobile = self.txt2.get().strip()
        email = self.txt3.get().strip()

        # Validation Checks
        if not name or not mobile or not email:
            tkinter.messagebox.showerror("Error", "Please fill all fields", parent=self.root)
        elif not (mobile.isdigit() and len(mobile) == 10):
            tkinter.messagebox.showerror("Error", "Mobile number must contain exactly 10 digits", parent=self.root)
        elif "@" not in email:
            tkinter.messagebox.showerror("Error", "Please enter a valid email address containing '@'", parent=self.root)
        else:
            q = "UPDATE students SET name=%s, mobile=%s, email=%s WHERE id=%s"
            self.cur.execute(q, (name, mobile, email, self.student_id))
            self.conn.commit()

            tkinter.messagebox.showinfo("Success", "Profile Updated Successfully", parent=self.root)
            self.root.destroy()


if __name__ == "__main__":
    app = Edit_Profile()
    app.root.mainloop()