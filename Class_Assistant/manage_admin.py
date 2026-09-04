import customtkinter as ctk
import tkinter.messagebox
import tkinter.ttk as ttk
from connection import connect

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Demo:
    def __init__(self, parent=None):
        if parent:
            self.root = ctk.CTkToplevel(parent)
            self.root.transient(parent)
            self.root.grab_set()
            self.root.focus_force()
        else:
            self.root = ctk.CTk()

        self.root.geometry("1100x650")
        self.root.title("Manage Admin")

        self.conn = connect()
        self.cur = self.conn.cursor()

        # Explicitly configure TTK style on this active window
        self.apply_table_style()

        # Page Title
        self.label = ctk.CTkLabel(
            self.root,
            text="Manage Admin",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold")
        )
        self.label.pack(pady=(20, 10))

        # Control Frame (Search & Action Buttons)
        self.frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.frame.pack(padx=20, pady=10, fill="x")

        self.lb1 = ctk.CTkLabel(
            self.frame,
            text="Search Admin :-",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold")
        )
        self.lb1.grid(row=0, column=0, padx=(20, 10), pady=15)

        self.txt1 = ctk.CTkEntry(
            self.frame,
            placeholder_text="Enter name...",
            width=200,
            height=35,
            corner_radius=8
        )
        self.txt1.grid(row=0, column=1, padx=10, pady=15)
        self.txt1.bind("<Return>", lambda event: self.search_product())

        self.bt1 = ctk.CTkButton(
            self.frame,
            text="Find admin",
            width=110,
            height=35,
            corner_radius=8,
            command=self.search_product
        )
        self.bt1.grid(row=0, column=2, padx=8, pady=15)

        self.bt2 = ctk.CTkButton(
            self.frame,
            text="Refresh",
            width=100,
            height=35,
            corner_radius=8,
            fg_color="#4A4A4A",
            hover_color="#5A5A5A",
            command=self.refresh_values
        )
        self.bt2.grid(row=0, column=3, padx=8, pady=15)

        self.bt3 = ctk.CTkButton(
            self.frame,
            text="Update",
            width=100,
            height=35,
            corner_radius=8,
            command=self.update
        )
        self.bt3.grid(row=0, column=4, padx=8, pady=15)

        self.bt4 = ctk.CTkButton(
            self.frame,
            text="Delete",
            width=100,
            height=35,
            corner_radius=8,
            fg_color="#C0392B",
            hover_color="#E74C3C",
            command=self.delete
        )
        self.bt4.grid(row=0, column=5, padx=(8, 20), pady=15)

        # Data Table Container Frame
        self.table_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.table_frame.pack(pady=15, padx=20, expand=True, fill='both')

        columns = ["id", "name", "gender", "mobile", "email", "status", "password", "role"]
        self.admin_table = ttk.Treeview(self.table_frame, columns=columns, show='headings')

        for i in columns:
            self.admin_table.heading(i, text=i.capitalize())
            self.admin_table.column(i, anchor="center")

        self.admin_table.pack(pady=15, padx=15, expand=True, fill='both')

        self.get_values()

    def apply_table_style(self):
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

    def update_table_data(self, rows):
        for i in self.admin_table.get_children():
            self.admin_table.delete(i)
        for index, row in enumerate(rows):
            self.admin_table.insert('', values=row, index=index)

    def get_values(self):
        q = "SELECT * FROM admin"
        self.cur.execute(q)
        result = self.cur.fetchall()
        self.update_table_data(result)

    def search_product(self):
        val = self.txt1.get().strip()
        if not val:
            self.get_values()
            return
        q = "SELECT * FROM admin WHERE LOWER(name) LIKE LOWER(%s)"
        self.cur.execute(q, (f"%{val}%",))
        result = self.cur.fetchall()
        self.update_table_data(result)

    def refresh_values(self):
        self.txt1.delete(0, 'end')
        self.get_values()

    def close_update_window(self):
        if hasattr(self, 'root1') and self.root1.winfo_exists():
            self.root1.grab_release()
            self.root1.withdraw()
            self.root1.after(10, self.root1.destroy)

    def update(self):
        treeviewid = self.admin_table.selection()
        if len(treeviewid) == 0:
            tkinter.messagebox.showerror("Error", "Please select row to update", parent=self.root)
            return

        self.item = self.admin_table.item(treeviewid).get("values")

        self.root1 = ctk.CTkToplevel(self.root)
        self.root1.geometry("500x600")
        self.root1.title("Update Admin")

        # Handle window close button (X) safely
        self.root1.protocol("WM_DELETE_WINDOW", self.close_update_window)

        # Modal layering setup
        self.root1.transient(self.root)
        self.root1.grab_set()
        self.root1.lift()
        self.root1.focus_force()

        self.mainlabel = ctk.CTkLabel(
            self.root1,
            text="Update Admin",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        self.mainlabel.pack(pady=(15, 10))

        self.card_frame = ctk.CTkScrollableFrame(self.root1, fg_color="#2b2b2b", corner_radius=15)
        self.card_frame.pack(padx=20, pady=5, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13)

        # ID
        self.lb0 = ctk.CTkLabel(self.card_frame, text="ID :-", font=font_label)
        self.lb0.grid(row=0, column=0, sticky="w", padx=20, pady=8)
        self.txt0 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt0.grid(row=0, column=1, padx=(0, 20), pady=8)
        self.txt0.insert(0, self.item[0])
        self.txt0.configure(state="readonly")

        # Name
        self.lb1_up = ctk.CTkLabel(self.card_frame, text="Enter Name :-", font=font_label)
        self.lb1_up.grid(row=1, column=0, sticky="w", padx=20, pady=8)
        self.txt1_up = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt1_up.grid(row=1, column=1, padx=(0, 20), pady=8)
        self.txt1_up.insert(0, self.item[1])

        # Gender
        self.lb2 = ctk.CTkLabel(self.card_frame, text="Enter Gender :-", font=font_label)
        self.lb2.grid(row=2, column=0, sticky="w", padx=20, pady=8)
        self.txt2 = ctk.CTkOptionMenu(
            self.card_frame,
            values=["Male", "Female", "others"],
            width=220,
            height=35,
            corner_radius=8,
            fg_color="#3a3a3a",
            button_color="#4a4a4a"
        )
        self.txt2.grid(row=2, column=1, padx=(0, 20), pady=8)
        self.txt2.set(self.item[2])

        # Mobile
        self.lb3 = ctk.CTkLabel(self.card_frame, text="Enter Mobile :-", font=font_label)
        self.lb3.grid(row=3, column=0, sticky="w", padx=20, pady=8)
        self.txt3 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt3.grid(row=3, column=1, padx=(0, 20), pady=8)
        self.txt3.insert(0, self.item[3])

        # Email
        self.lb4 = ctk.CTkLabel(self.card_frame, text="Enter Email :-", font=font_label)
        self.lb4.grid(row=4, column=0, sticky="w", padx=20, pady=8)
        self.txt4 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt4.grid(row=4, column=1, padx=(0, 20), pady=8)
        self.txt4.insert(0, self.item[4])

        # Status
        self.lb5 = ctk.CTkLabel(self.card_frame, text="Status :-", font=font_label)
        self.lb5.grid(row=5, column=0, sticky="w", padx=20, pady=8)
        self.txt5 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8)
        self.txt5.grid(row=5, column=1, padx=(0, 20), pady=8)
        self.txt5.insert(0, self.item[5])

        # Role
        self.lb6 = ctk.CTkLabel(self.card_frame, text="Enter role :-", font=font_label)
        self.lb6.grid(row=6, column=0, sticky="w", padx=20, pady=8)
        self.txt6 = ctk.CTkOptionMenu(
            self.card_frame,
            values=["Super-Admin", "Admin"],
            width=220,
            height=35,
            corner_radius=8,
            fg_color="#3a3a3a",
            button_color="#4a4a4a"
        )
        self.txt6.grid(row=6, column=1, padx=(0, 20), pady=8)
        self.txt6.set(self.item[7])

        # Password
        self.lb7 = ctk.CTkLabel(self.card_frame, text="Enter password :-", font=font_label)
        self.lb7.grid(row=7, column=0, sticky="w", padx=20, pady=8)
        self.txt7 = ctk.CTkEntry(self.card_frame, width=220, height=35, corner_radius=8, show="*")
        self.txt7.grid(row=7, column=1, padx=(0, 20), pady=8)
        self.txt7.insert(0, self.item[6])

        # Submit Button
        self.bt1_up = ctk.CTkButton(
            self.root1,
            text="Submit",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            width=180,
            height=40,
            corner_radius=10,
            command=self.modify
        )
        self.bt1_up.pack(pady=15)

    def modify(self):
        admin_id = self.txt0.get()
        name = self.txt1_up.get().strip()
        gender = self.txt2.get().strip()
        mobile = self.txt3.get().strip()
        email = self.txt4.get().strip()
        status = self.txt5.get().strip()
        password = self.txt7.get().strip()
        role = self.txt6.get().strip()

        # Validation Checks
        if not name or not gender or not mobile or not email or not status or not password or not role:
            tkinter.messagebox.showerror("Error", "Please fill all fields", parent=self.root1)
        elif not (mobile.isdigit() and len(mobile) == 10):
            tkinter.messagebox.showerror("Error", "Mobile number must contain exactly 10 digits", parent=self.root1)
        elif "@" not in email:
            tkinter.messagebox.showerror("Error", "Please enter a valid email address containing '@'", parent=self.root1)
        else:
            q = "UPDATE admin SET name=%s, gender=%s, mobile=%s, email=%s, status=%s, password=%s, role=%s WHERE id=%s"
            self.cur.execute(q, (name, gender, mobile, email, status, password, role, admin_id))
            self.conn.commit()

            tkinter.messagebox.showinfo("Success", "Admin Updated", parent=self.root1)
            self.close_update_window()
            self.get_values()

    def delete(self):
        treeviewid = self.admin_table.selection()
        if len(treeviewid) == 0:
            tkinter.messagebox.showwarning("Warning!!", "Please select item to delete", parent=self.root)
        else:
            if tkinter.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this admin record?", parent=self.root):
                self.del_id = self.admin_table.item(treeviewid).get("values")[0]
                q3 = "DELETE FROM admin WHERE id=%s"
                self.cur.execute(q3, (self.del_id,))
                self.conn.commit()

                tkinter.messagebox.showinfo("Success!", "Row deleted Successfully!!", parent=self.root)
                self.get_values()


# Alias for compatibility with import strategies
Manage_admin = Demo

if __name__ == "__main__":
    app = Demo()
    app.root.mainloop()