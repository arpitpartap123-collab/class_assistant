"""
main_navigator.py
Main entry-point landing screen for Class Plus Assistant (Class Assistant).

Presents four animated action cards:
    - Teacher / HOD Login  -> admin_login.AdminLogin
    - Student Login        -> user_login.userLogin
    - New Registration     -> add_user.Demo
    - Exit                 -> closes the app

Features:
    - Live Date and Time updates in the header
    - Animated action cards with entrance slide-in & smooth hover effects
    - Pulsing underline effect beneath the main title

Does NOT modify admin_login.py, user_login.py, or add_user.py.
Run this file directly to launch the app.
"""

import time
import customtkinter as ctk
import tkinter.messagebox

import admin_login
import user_login
import add_user

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ---- Palette (matches existing screens) ----
BG_WINDOW = "#1b1b1b"
BG_CARD = "#2b2b2b"
BG_CARD_HOVER = "#343d47"
ACCENT = "#1f6aa5"
ACCENT_LIGHT = "#3a9bde"
TEXT_MAIN = "#e6e6e6"
TEXT_DIM = "#9b9b9b"
EXIT_RED = "#7a2626"
EXIT_RED_HOVER = "#B22222"

CARD_W, CARD_H = 460, 84
HOVER_STEP_MS = 12
ENTRANCE_STEP_MS = 12
ENTRANCE_STAGGER_MS = 90


def _lerp_hex(c1, c2, t):
    """Linearly interpolate between two hex colors, t in [0, 1]."""
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class ActionCard(ctk.CTkFrame):
    """
    A large animated action button used on the navigator screen.
    Hover: background + accent bar smoothly lerp color, icon badge glows.
    """

    def __init__(self, master, icon, title, subtitle, command,
                 accent=ACCENT, hover_bg=BG_CARD_HOVER, base_bg=BG_CARD, **kwargs):
        super().__init__(master, width=CARD_W, height=CARD_H, corner_radius=16,
                          fg_color=base_bg, border_width=1, border_color="#3a3a3a", **kwargs)
        self.pack_propagate(False)

        self._command = command
        self._accent = accent
        self._hover_bg = hover_bg
        self._base_bg = base_bg
        self._hover_job = None
        self._hover_progress = 0.0  # 0 = idle, 1 = fully hovered

        # left accent bar (glows on hover)
        self.accent_bar = ctk.CTkFrame(self, width=5, corner_radius=3, fg_color="#3a3a3a")
        self.accent_bar.place(x=0, rely=0.5, anchor="w", relheight=0.7)

        # icon badge
        self.badge = ctk.CTkFrame(self, width=48, height=48, corner_radius=24, fg_color="#3a3a3a")
        self.badge.place(x=22, rely=0.5, anchor="w")
        self.badge.pack_propagate(False)
        self.icon_label = ctk.CTkLabel(self.badge, text=icon, font=ctk.CTkFont(size=20))
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # title + subtitle
        self.title_label = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color=TEXT_MAIN, anchor="w"
        )
        self.title_label.place(x=88, y=22, anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self, text=subtitle, font=ctk.CTkFont(family="Arial", size=11),
            text_color=TEXT_DIM, anchor="w"
        )
        self.subtitle_label.place(x=88, y=48, anchor="w")

        # chevron on the right, glows in on hover
        self.chevron = ctk.CTkLabel(self, text="›", font=ctk.CTkFont(size=22, weight="bold"), text_color="#3a3a3a")
        self.chevron.place(relx=1.0, x=-22, rely=0.5, anchor="e")

        for widget in (self, self.badge, self.icon_label, self.title_label, self.subtitle_label, self.chevron):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

    def _on_enter(self, _event=None):
        self._animate_hover(target=1.0)

    def _on_leave(self, _event=None):
        self._animate_hover(target=0.0)

    def _on_click(self, _event=None):
        if self._command:
            self._command()

    def _animate_hover(self, target):
        if self._hover_job:
            self.after_cancel(self._hover_job)

        def step():
            delta = (target - self._hover_progress) * 0.35
            self._hover_progress += delta
            if abs(target - self._hover_progress) < 0.02:
                self._hover_progress = target
            t = self._hover_progress
            self.configure(fg_color=_lerp_hex(self._base_bg, self._hover_bg, t),
                            border_color=_lerp_hex("#3a3a3a", self._accent, t))
            self.accent_bar.configure(fg_color=_lerp_hex("#3a3a3a", self._accent, t))
            self.badge.configure(fg_color=_lerp_hex("#3a3a3a", self._accent, t))
            self.chevron.configure(text_color=_lerp_hex("#3a3a3a", self._accent, t))
            if self._hover_progress != target:
                self._hover_job = self.after(HOVER_STEP_MS, step)
            else:
                self._hover_job = None

        step()

    def slide_in(self, final_x, final_y, delay=0):
        """Entrance animation: card eases upward into place from below."""
        self.place(x=final_x, y=final_y + 40)

        def start():
            steps = 14
            state = {"i": 0}

            def frame():
                state["i"] += 1
                t = state["i"] / steps
                eased = 1 - (1 - t) ** 3  # ease-out cubic
                y = final_y + 40 * (1 - eased)
                self.place(x=final_x, y=y)
                if state["i"] < steps:
                    self.after(ENTRANCE_STEP_MS, frame)

            frame()

        self.after(delay, start)


class MainNavigator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Class Plus Assistant — Portal Navigator")
        self.root.geometry("640x660")
        self.root.resizable(False, False)
        self.root.configure(fg_color=BG_WINDOW)
        self.root.after(0, lambda: self.root.state("zoomed"))

        self.center_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # ---- Live Clock Badge ----
        self.clock_label = ctk.CTkLabel(
            self.center_frame, text="", font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            text_color=ACCENT_LIGHT, fg_color="#252525", corner_radius=12, height=26, width=280
        )
        self.clock_label.pack(pady=(20, 0))
        self._update_time()

        # ---- Header ----
        self.header = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.header.pack(pady=(15, 10))

        # Unique Main Heading
        self.title_label = ctk.CTkLabel(
            self.header, text="Class Plus Assistant Portal",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="white"
        )
        self.title_label.pack()

        self.subtitle_label = ctk.CTkLabel(
            self.header, text="Choose how you'd like to continue",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=TEXT_DIM
        )
        self.subtitle_label.pack(pady=(4, 0))

        # Animated glowing underline beneath the title
        self.underline = ctk.CTkCanvas(self.header, width=160, height=4, bg=BG_WINDOW, highlightthickness=0)
        self.underline.pack(pady=(12, 0))
        self._underline_line = self.underline.create_rectangle(0, 0, 160, 4, fill=ACCENT, width=0)
        self._pulse_direction = 1
        self._pulse_t = 0.0
        self._pulse_underline()

        # ---- Card container (cards are entrance-animated via place()) ----
        self.card_area = ctk.CTkFrame(self.center_frame, fg_color="transparent", width=CARD_W, height=380)
        self.card_area.pack(pady=(25, 0), anchor="center")
        self.card_area.pack_propagate(False)

        cards = [
            dict(icon="🎓", title="Teacher / HOD Login", subtitle="Access the admin dashboard",
                 command=self.open_admin_login, accent=ACCENT_LIGHT),
            dict(icon="🧑‍🎓", title="Student Login", subtitle="Access your student dashboard",
                 command=self.open_student_login, accent=ACCENT_LIGHT),
            dict(icon="📝", title="New Registration", subtitle="Register a new student account",
                 command=self.open_registration, accent=ACCENT_LIGHT),
            dict(icon="⏻", title="Exit", subtitle="Close the application",
                 command=self.exit_app, accent=EXIT_RED_HOVER, hover_bg="#3a2323"),
        ]

        self._cards = []
        y = 0
        for i, c in enumerate(cards):
            card = ActionCard(
                self.card_area, icon=c["icon"], title=c["title"], subtitle=c["subtitle"],
                command=c["command"], accent=c["accent"], hover_bg=c.get("hover_bg", BG_CARD_HOVER)
            )
            card.slide_in(final_x=0, final_y=y, delay=i * ENTRANCE_STAGGER_MS)
            self._cards.append(card)
            y += CARD_H + 18

        # ---- Footer ----
        self.footer = ctk.CTkLabel(
            self.center_frame, text="Class Plus Assistant  •  v1.0",
            font=ctk.CTkFont(family="Arial", size=10), text_color="#555555"
        )
        self.footer.pack(side="bottom", pady=14)

        self.root.update_idletasks()
        self.root.deiconify()

    # ---- live date and time ticker ----
    def _update_time(self):
        current_time_str = time.strftime("📅 %a, %b %d, %Y  |  ⏰ %I:%M:%S %p")
        self.clock_label.configure(text=current_time_str)
        self.root.after(1000, self._update_time)

    # ---- animated title underline (breathing glow) ----
    def _pulse_underline(self):
        self._pulse_t += 0.04 * self._pulse_direction
        if self._pulse_t >= 1.0:
            self._pulse_t = 1.0
            self._pulse_direction = -1
        elif self._pulse_t <= 0.0:
            self._pulse_t = 0.0
            self._pulse_direction = 1
        color = _lerp_hex(ACCENT, ACCENT_LIGHT, self._pulse_t)
        self.underline.itemconfig(self._underline_line, fill=color)
        self.root.after(40, self._pulse_underline)

    # ---- navigation actions ----
    def open_admin_login(self):
        self.root.withdraw()
        app = admin_login.AdminLogin(self.root)
        self.root.wait_window(app.root)
        if self.root.winfo_exists():
            self.root.deiconify()

    def open_student_login(self):
        self.root.withdraw()
        app = user_login.userLogin(self.root)
        self.root.wait_window(app.root)
        if self.root.winfo_exists():
            self.root.deiconify()

    def open_registration(self):
        self.root.withdraw()
        app = add_user.Demo(self.root)
        self.root.wait_window(app.root)
        if self.root.winfo_exists():
            self.root.deiconify()

    def exit_app(self):
        if tkinter.messagebox.askyesno("Exit", "Are you sure you want to exit?", parent=self.root):
            self.root.destroy()


if __name__ == "__main__":
    nav = MainNavigator()
    nav.root.mainloop()