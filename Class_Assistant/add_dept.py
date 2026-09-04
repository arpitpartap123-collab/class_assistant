import customtkinter as ctk
import tkinter.messagebox
from connection import connect

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Add_dept:
    def __init__(self, parent=None):
        if parent:
            self.root = ctk.CTkToplevel(parent)
        else:
            self.root = ctk.CTk()

        # Decent geometry to hold expanded content comfortably
        self.root.geometry("600x650")
        self.root.title("Add Department")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.conn = connect()
        self.cur = self.conn.cursor()

        # Page Heading
        self.mainlabel = ctk.CTkLabel(
            self.root,
            text="Add Department",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold")
        )
        self.mainlabel.pack(pady=(30, 15))

        # Card Frame Container
        self.card_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.card_frame.pack(padx=30, pady=10, fill="both", expand=True)

        font_label = ctk.CTkFont(family="Arial", size=13, weight="bold")

        # Department Name Row
        self.lb1 = ctk.CTkLabel(self.card_frame, text="Department Name :-", font=font_label)
        self.lb1.grid(row=0, column=0, sticky="nw", padx=(25, 10), pady=(30, 15))

        self.txt1 = ctk.CTkEntry(
            self.card_frame,
            width=320,
            height=38,
            corner_radius=8,
            placeholder_text="Enter department name..."
        )
        self.txt1.grid(row=0, column=1, padx=(0, 25), pady=(30, 15), sticky="w")

        # Description Row (CTkTextbox for multi-line text up to 500-600 words)
        self.lb2 = ctk.CTkLabel(self.card_frame, text="Description :-", font=font_label)
        self.lb2.grid(row=1, column=0, sticky="nw", padx=(25, 10), pady=15)

        self.txt2 = ctk.CTkTextbox(
            self.card_frame,
            width=320,
            height=260,
            corner_radius=8,
            wrap="word",
            font=ctk.CTkFont(family="Arial", size=12)
        )
        self.txt2.grid(row=1, column=1, padx=(0, 25), pady=15, sticky="w")

        # Submit Button
        self.bt1 = ctk.CTkButton(
            self.root,
            text="Submit",
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            width=200,
            height=42,
            corner_radius=10,
            command=self.add_record
        )
        self.bt1.pack(pady=(15, 25))

    def add_record(self):
        dept_name = self.txt1.get().strip()
        # Extract all text from CTkTextbox from character index 1.0 to end
        description = self.txt2.get("1.0", "end-1c").strip()

        if not dept_name or not description:
            tkinter.messagebox.showerror("Error", "Please fill all fields")
        else:
            q = "INSERT INTO department (name, description) VALUES (%s, %s)"
            self.cur.execute(q, (dept_name, description))
            self.conn.commit()

            tkinter.messagebox.showinfo("Success", "Department Added Successfully")
            self.root.destroy()


if __name__ == "__main__":
    app = Demo()
    app.root.mainloop()