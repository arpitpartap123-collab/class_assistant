import customtkinter as ctk
import tkinter.messagebox
from connection import connect

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Change_Pass:
    def __init__(self, parent=None, admin_id=None):
        self.student_id = admin_id
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)
            self.root.grab_set()
            self.root.focus_force()
        else:
            self.root = ctk.CTk()

        self.root.geometry("450x480")
        self.root.title("Change Password")
        self.root.resizable(False, False)

        self.conn = connect()
        self.cur = self.conn.cursor()

        self.student_id = admin_id

        self.mainlabel = ctk.CTkLabel(
            self.root,
            text="Change Password",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold")
        )
        self.mainlabel.pack(pady=(25, 15))

        self.card_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.card_frame.pack(padx=25, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13)

        # Current Password
        self.lb1 = ctk.CTkLabel(self.card_frame, text="Current Password :-", font=font_label)
        self.lb1.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        self.txt1 = ctk.CTkEntry(self.card_frame, width=200, height=35, corner_radius=8, show="*")
        self.txt1.grid(row=0, column=1, padx=(0, 20), pady=15)

        # New Password
        self.lb2 = ctk.CTkLabel(self.card_frame, text="New Password :-", font=font_label)
        self.lb2.grid(row=1, column=0, sticky="w", padx=20, pady=15)
        self.txt2 = ctk.CTkEntry(self.card_frame, width=200, height=35, corner_radius=8, show="*")
        self.txt2.grid(row=1, column=1, padx=(0, 20), pady=15)

        # Confirm New Password
        self.lb3 = ctk.CTkLabel(self.card_frame, text="Confirm Password :-", font=font_label)
        self.lb3.grid(row=2, column=0, sticky="w", padx=20, pady=15)
        self.txt3 = ctk.CTkEntry(self.card_frame, width=200, height=35, corner_radius=8, show="*")
        self.txt3.grid(row=2, column=1, padx=(0, 20), pady=15)

        # Submit Button
        self.bt1 = ctk.CTkButton(
            self.root,
            text="Submit",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            width=180,
            height=40,
            corner_radius=10,
            command=self.change_password
        )
        self.bt1.pack(pady=15)


    def change_password(self):
        current = self.txt1.get().strip()
        new = self.txt2.get().strip()
        confirm = self.txt3.get().strip()

        # Validation Checks
        if not current or not new or not confirm:
            tkinter.messagebox.showerror(
                "Error",
                "Please fill all fields",
                parent=self.root
            )
            return

        # Check if new password is same as current password
        if new == current:
            tkinter.messagebox.showerror(
                "Error",
                "New password cannot be the same as current password",
                parent=self.root
            )
            return

        # Check if new password and confirm password are same
        if new != confirm:
            tkinter.messagebox.showerror(
                "Error",
                "New password and confirm password do not match",
                parent=self.root
            )
            return

        # Verify the current password matches what's on file for this admin
        q = "SELECT password FROM students WHERE id=%s"
        self.cur.execute(q, (self.student_id,))
        result = self.cur.fetchone()

        if not result or result[0] != current:
            tkinter.messagebox.showerror(
                "Error",
                "Current password is incorrect",
                parent=self.root
            )
            return

        # Update password
        q2 = "UPDATE students SET password=%s WHERE id=%s"
        self.cur.execute(q2, (new, self.student_id))
        self.conn.commit()

        tkinter.messagebox.showinfo(
            "Success",
            "Password Changed Successfully",
            parent=self.root
        )

        self.root.destroy()




if __name__ == "__main__":
    app = Change_Pass()
    app.root.mainloop()