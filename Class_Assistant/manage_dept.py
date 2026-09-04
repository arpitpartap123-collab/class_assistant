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
            self.root.lift()
            self.root.focus_force()
            self.root.grab_set()
        else:
            self.root = ctk.CTk()

        self.root.geometry("1100x650")
        self.root.title("Manage Department")

        self.conn = connect()
        self.cur = self.conn.cursor()

        # Apply global dark table styling
        self.apply_table_style()

        # Page Title
        self.label = ctk.CTkLabel(
            self.root,
            text="Manage Department",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold")
        )
        self.label.pack(pady=(20, 10))

        # Control Frame (Search & Action Buttons)
        self.frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.frame.pack(padx=20, pady=10, fill="x")

        self.lb1 = ctk.CTkLabel(
            self.frame,
            text="Search Dept :-",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold")
        )
        self.lb1.grid(row=0, column=0, padx=(20, 10), pady=15)

        self.txt1 = ctk.CTkEntry(
            self.frame,
            placeholder_text="Enter department name...",
            width=220,
            height=35,
            corner_radius=8
        )
        self.txt1.grid(row=0, column=1, padx=10, pady=15)
        self.txt1.bind("<Return>", lambda event: self.search_dept())

        self.bt1 = ctk.CTkButton(
            self.frame,
            text="Find Dept",
            width=110,
            height=35,
            corner_radius=8,
            command=self.search_dept
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
            fg_color="#1F6AA5",
            hover_color="#144870",
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

        columns = ["name", "description"]
        self.dept_table = ttk.Treeview(self.table_frame, columns=columns, show='headings')

        self.dept_table.heading("name", text="Department Name")
        self.dept_table.column("name", anchor="w", width=250)

        self.dept_table.heading("description", text="Description")
        self.dept_table.column("description", anchor="w", width=650)

        self.dept_table.pack(pady=15, padx=15, expand=True, fill='both')

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
        for i in self.dept_table.get_children():
            self.dept_table.delete(i)
        for index, row in enumerate(rows):
            self.dept_table.insert('', values=row, index=index)

    def get_values(self):
        q = "SELECT name, description FROM department"
        self.cur.execute(q)
        result = self.cur.fetchall()
        self.update_table_data(result)

    def search_dept(self):
        val = self.txt1.get().strip()
        if not val:
            tkinter.messagebox.showwarning(
                "Input Required", "Please enter a department name to search.")
            self.get_values()
            return
        q = "SELECT name, description FROM department WHERE LOWER(name) LIKE LOWER(%s)"
        self.cur.execute(q, (f"%{val.lower()}%",))
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
        treeviewid = self.dept_table.selection()
        if len(treeviewid) == 0:
            tkinter.messagebox.showerror("Error", "Please select a row to update", parent=self.root)
            return

        self.item = self.dept_table.item(treeviewid).get("values")
        self.original_name = self.item[0]

        # Create pop-up window
        self.root1 = ctk.CTkToplevel(self.root)
        self.root1.geometry("550x550")
        self.root1.title("Update Department")

        # Keep pop-up open and focused over parent window cleanly
        self.root1.protocol("WM_DELETE_WINDOW", self.close_update_window)
        self.root1.transient(self.root)
        self.root1.grab_set()
        self.root1.lift()
        self.root1.focus_force()

        self.mainlabel = ctk.CTkLabel(
            self.root1,
            text="Update Department",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        self.mainlabel.pack(pady=(20, 10))

        self.card_frame = ctk.CTkFrame(self.root1, fg_color="#2b2b2b", corner_radius=15)
        self.card_frame.pack(padx=20, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13, weight="bold")

        # Name Row
        self.lb1_up = ctk.CTkLabel(self.card_frame, text="Department Name :-", font=font_label)
        self.lb1_up.grid(row=0, column=0, sticky="nw", padx=(20, 10), pady=(25, 10))

        self.txt1_up = ctk.CTkEntry(self.card_frame, width=280, height=35, corner_radius=8)
        self.txt1_up.grid(row=0, column=1, padx=(0, 20), pady=(25, 10), sticky="w")
        self.txt1_up.insert(0, self.item[0])

        # Description Row
        self.lb2_up = ctk.CTkLabel(self.card_frame, text="Description :-", font=font_label)
        self.lb2_up.grid(row=1, column=0, sticky="nw", padx=(20, 10), pady=10)

        self.txt2_up = ctk.CTkTextbox(
            self.card_frame,
            width=280,
            height=200,
            corner_radius=8,
            wrap="word",
            font=ctk.CTkFont(family="Arial", size=12)
        )
        self.txt2_up.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="w")
        self.txt2_up.insert("1.0", self.item[1])

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
        self.bt1_up.pack(pady=(10, 20))

    def modify(self):
        new_name = self.txt1_up.get().strip()
        new_description = self.txt2_up.get("1.0", "end-1c").strip()

        if not new_name or not new_description:
            tkinter.messagebox.showerror("Error", "Please fill all fields", parent=self.root1)
        else:
            q = "UPDATE department SET name=%s, description=%s WHERE name=%s"
            self.cur.execute(q, (new_name, new_description, self.original_name))
            self.conn.commit()

            tkinter.messagebox.showinfo("Success", "Department Updated Successfully", parent=self.root1)
            self.close_update_window()
            self.get_values()

    def delete(self):
        treeviewid = self.dept_table.selection()
        if len(treeviewid) == 0:
            tkinter.messagebox.showwarning("Warning!!", "Please select an item to delete", parent=self.root)
        else:
            if tkinter.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this department?", parent=self.root):
                del_name = self.dept_table.item(treeviewid).get("values")[0]
                q = "DELETE FROM department WHERE name=%s"
                self.cur.execute(q, (del_name,))
                self.conn.commit()

                tkinter.messagebox.showinfo("Success!", "Department deleted successfully!", parent=self.root)
                self.get_values()


# Class Aliases to cover import name variations from the dashboard
Manage_dept = Demo
Manage_department = Demo

if __name__ == "__main__":
    app = Demo()
    app.root.mainloop()