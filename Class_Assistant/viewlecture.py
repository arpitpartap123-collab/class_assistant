import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msg

import customtkinter as ctk

from connection import connect
from ai_pipeline import process_lecture, PDF_DIR


BG = "#0A0F1A"
CARD = "#111827"
CARD_2 = "#0D1522"
BORDER = "#25344A"
TEXT = "#E8EEF7"
MUTED = "#94A3B8"
BLUE_1, BLUE_2 = "#315E9F", "#3D73BC"
PURPLE_1, PURPLE_2 = "#66539A", "#7967B3"
GREEN_1, GREEN_2 = "#3C806B", "#4D9A80"
ORANGE_1, ORANGE_2 = "#9A6B32", "#B47D3A"
RED_1, RED_2 = "#944B55", "#AD5A66"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GradientButton(ctk.CTkFrame):
    """Subtle rounded accent button with a smooth hover animation."""

    def __init__(self, master, text, command, width=120, height=42,
                 color1=BLUE_1, color2=BLUE_2):
        super().__init__(
            master,
            width=width,
            height=height,
            fg_color="transparent",
            corner_radius=14
        )

        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.color1 = color1
        self.color2 = color2

        self.normal_color = color1
        self.hover_color = color2
        self.current_color = color1
        self.animation_id = None
        self.is_hovered = False

        self.grid_propagate(False)
        self.pack_propagate(False)

        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=CARD
        )
        self.canvas.pack(fill="both", expand=True)

        self.draw_button(self.normal_color)

        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)

    def hex_to_rgb(self, value):
        value = value.lstrip("#")
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, value):
        return "#{:02x}{:02x}{:02x}".format(
            max(0, min(255, int(value[0]))),
            max(0, min(255, int(value[1]))),
            max(0, min(255, int(value[2])))
        )

    def draw_button(self, color):
        self.canvas.delete("all")

        radius = 13

        # Main rounded body.
        self.canvas.create_rectangle(
            radius, 0,
            self.width - radius, self.height,
            fill=color,
            outline=color
        )
        self.canvas.create_rectangle(
            0, radius,
            self.width, self.height - radius,
            fill=color,
            outline=color
        )

        for x1, y1, x2, y2, start in [
            (0, 0, radius * 2, radius * 2, 90),
            (self.width - radius * 2, 0, self.width, radius * 2, 0),
            (0, self.height - radius * 2, radius * 2, self.height, 180),
            (self.width - radius * 2, self.height - radius * 2,
             self.width, self.height, 270)
        ]:
            self.canvas.create_arc(
                x1, y1, x2, y2,
                start=start,
                extent=90,
                fill=color,
                outline=color
            )

        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=self.text,
            fill="#F8FAFC",
            font=("Segoe UI", 10, "bold")
        )

    def animate_to(self, target, steps=8, step=0):
        if self.animation_id is not None:
            try:
                self.after_cancel(self.animation_id)
            except Exception:
                pass
            self.animation_id = None

        start_rgb = self.hex_to_rgb(self.current_color)
        target_rgb = self.hex_to_rgb(target)

        ratio = min(step / steps, 1)

        # Smooth ease-out curve.
        ratio = 1 - (1 - ratio) ** 3

        rgb = tuple(
            start_rgb[i] +
            (target_rgb[i] - start_rgb[i]) * ratio
            for i in range(3)
        )

        self.current_color = self.rgb_to_hex(rgb)
        self.draw_button(self.current_color)

        if step < steps:
            self.animation_id = self.after(
                18,
                lambda: self.animate_to(target, steps, step + 1)
            )

    def on_enter(self, event=None):
        self.configure(cursor="hand2")
        self.is_hovered = True
        self.animate_to(self.hover_color)

    def on_leave(self, event=None):
        self.is_hovered = False
        self.animate_to(self.normal_color)

    def on_click(self, event=None):
        self.command()


def setup_treeview():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("Lecture.Treeview", background=CARD_2, foreground=TEXT,
                    fieldbackground=CARD_2, borderwidth=0, rowheight=44,
                    font=("Segoe UI", 11))
    style.configure("Lecture.Treeview.Heading", background="#182437",
                    foreground="#E2E8F0", borderwidth=0,
                    font=("Segoe UI", 11, "bold"), padding=(10, 12))
    style.map("Lecture.Treeview", background=[("selected", "#315E9F")],
              foreground=[("selected", "#FFFFFF")])
    style.map("Lecture.Treeview.Heading", background=[("active", "#24344D")])
    style.configure("Lecture.Vertical.TScrollbar", background="#1C293B",
                    troughcolor=CARD_2, bordercolor=CARD_2,
                    arrowcolor="#7F8FA5", relief="flat")


setup_treeview()


class viewLecture:
    def __init__(self):
        self.root = ctk.CTkToplevel()
        self.root.title("View Lectures")
        self.root.configure(fg_color=BG)
        self.root.state("zoomed")

        self.conn = connect()
        self.cr = self.conn.cursor()

        header = ctk.CTkFrame(self.root, fg_color=CARD, corner_radius=20,
                              border_width=1, border_color=BORDER)
        header.pack(fill="x", padx=32, pady=(24, 12))
        ctk.CTkLabel(header, text="LECTURES", font=("Segoe UI", 28, "bold"),
                     text_color="#78A6D8").pack(pady=(18, 2))
        ctk.CTkLabel(header,
                     text="Manage lectures, PDFs and AI-generated content",
                     font=("Segoe UI", 12), text_color=MUTED).pack(pady=(0, 4))
        ctk.CTkLabel(header,
                     text="Right click a lecture for additional actions",
                     font=("Segoe UI", 10), text_color="#718198").pack(pady=(0, 18))

        bar = ctk.CTkFrame(self.root, fg_color=CARD, corner_radius=18,
                           border_width=1, border_color=BORDER)
        bar.pack(fill="x", padx=32, pady=8)
        self.searchField = ctk.CTkEntry(
            bar, width=330, height=42, corner_radius=12,
            placeholder_text="Search title or course...",
            placeholder_text_color="#718198", fg_color=CARD_2,
            border_color="#2A3A52", border_width=1, text_color=TEXT,
            font=("Segoe UI", 12))
        self.searchField.grid(row=0, column=0, padx=(18, 8), pady=16)

        buttons = [
            ("Search", self.searchLecture, 115, BLUE_1, BLUE_2),
            ("Refresh", self.refreshData, 115, PURPLE_1, PURPLE_2),
            ("Open PDF", self.openPdf, 125, GREEN_1, GREEN_2),
            ("Regenerate AI", self.regenerate, 145, ORANGE_1, ORANGE_2),
            ("Delete", self.deleteLecture, 110, RED_1, RED_2)
        ]
        for col, (text, command, width, c1, c2) in enumerate(buttons, start=1):
            GradientButton(bar, text, command, width, 42, c1, c2).grid(
                row=0, column=col, padx=(7, 18 if col == len(buttons) else 7), pady=16)

        wrapper = ctk.CTkFrame(self.root, fg_color=CARD, corner_radius=20,
                               border_width=1, border_color=BORDER)
        wrapper.pack(fill="both", expand=True, padx=32, pady=(8, 28))
        tableFrame = ctk.CTkFrame(wrapper, fg_color=CARD_2, corner_radius=14)
        tableFrame.pack(fill="both", expand=True, padx=14, pady=14)

        columns = ("id", "title", "course", "pdf", "notes", "questions", "status", "created")
        self.table = ttk.Treeview(tableFrame, columns=columns, show="headings",
                                  style="Lecture.Treeview")
        for key, title, width in [
            ("id", "ID", 60), ("title", "Lecture Title", 250),
            ("course", "Course", 140), ("pdf", "PDF File", 220),
            ("notes", "Notes", 90), ("questions", "Questions", 100),
            ("status", "Status", 110), ("created", "Uploaded", 160)]:
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor="center")

        scroll = ttk.Scrollbar(tableFrame, orient="vertical", command=self.table.yview,
                               style="Lecture.Vertical.TScrollbar")
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", pady=8)
        self.table.pack(fill="both", expand=True, padx=8, pady=8)
        self.table.bind("<Button-3>", self.showPopupMenu)

        self.getLectureInfo()
        self.root.protocol("WM_DELETE_WINDOW", self.closeWindow)
        self.root.mainloop()

    def getLectureInfo(self, keyword=None):
        base = """SELECT l.id, l.title, c.name, l.pdf_file,
                         (SELECT COUNT(*) FROM notes n WHERE n.lecture_id = l.id),
                         (SELECT COUNT(*) FROM questions q WHERE q.lecture_id = l.id),
                         l.status, l.created_at
                  FROM lectures l JOIN courses c ON c.id = l.course_id"""
        if keyword:
            self.cr.execute(base + " WHERE l.title LIKE %s OR c.name LIKE %s ORDER BY l.id",
                            (f"%{keyword}%", f"%{keyword}%"))
        else:
            self.cr.execute(base + " ORDER BY l.id")
        for row in self.table.get_children():
            self.table.delete(row)
        for record in self.cr.fetchall():
            self.table.insert("", "end", values=record)

    def searchLecture(self):
        self.getLectureInfo(self.searchField.get().strip())

    def refreshData(self):
        self.searchField.delete(0, "end")
        self.getLectureInfo()

    def selectedRow(self):
        selected = self.table.selection()
        if not selected:
            msg.showwarning("Warning", "Please select a lecture first", parent=self.root)
            return None
        return self.table.item(selected[0])["values"]

    def openPdf(self):
        data = self.selectedRow()
        if data is None:
            return
        path = os.path.join(PDF_DIR, str(data[3]))
        if not os.path.exists(path):
            msg.showerror("Error", f"The file is missing from {PDF_DIR}", parent=self.root)
            return
        os.startfile(os.path.abspath(path))

    def regenerate(self):
        data = self.selectedRow()
        if data is None:
            return
        confirm = msg.askyesno(
            "Confirm",
            f"Regenerate the notes and questions for '{data[1]}'?\n\n"
            "The existing notes and questions will be replaced.",
            parent=self.root)
        if not confirm:
            return
        try:
            notes, questions = process_lecture(data[0])
            msg.showinfo("Success",
                         f"Regenerated.\n\nNotes: {notes}\nQuestions: {questions}",
                         parent=self.root)
        except Exception as e:
            msg.showerror("Error", str(e), parent=self.root)
        self.refreshData()

    def deleteLecture(self):
        data = self.selectedRow()
        if data is None:
            return
        confirm = msg.askyesno(
            "Confirm",
            f"Delete lecture '{data[1]}'?\n\n"
            "Its notes, questions and quiz attempts will also be deleted.",
            parent=self.root)
        if not confirm:
            return
        path = os.path.join(PDF_DIR, str(data[3]))
        self.cr.execute("DELETE FROM lectures WHERE id = %s", (data[0],))
        self.conn.commit()
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError as e:
                print("Could not delete the PDF file:", e)
        msg.showinfo("Success", "Lecture has been deleted", parent=self.root)
        self.refreshData()

    def showPopupMenu(self, event):
        item = self.table.identify_row(event.y)
        if not item:
            return
        self.table.selection_set(item)
        popup = tk.Menu(self.root, tearoff=0, bg="#111827", fg="#F8FAFC",
                        activebackground="#2563EB", activeforeground="#FFFFFF",
                        borderwidth=0, relief="flat", font=("Segoe UI", 10))
        popup.add_command(label="Open PDF", command=self.openPdf)
        popup.add_command(label="Regenerate AI content", command=self.regenerate)
        popup.add_separator()
        popup.add_command(label="Delete", command=self.deleteLecture)
        popup.post(event.x_root, event.y_root)

    def closeWindow(self):
        try:
            if self.cr:
                self.cr.close()
        except Exception:
            pass
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    viewLecture()