import tkinter as tk
from tkinter import ttk


class PomodoroTimer:
    COLORS = {
        "background": "#101820",
        "panel": "#17232d",
        "panel_light": "#20313d",
        "text": "#f4f7f8",
        "muted": "#9aadb8",
        "accent": "#ff6b5f",
        "accent_dark": "#dc5148",
        "green": "#58c7a2",
        "track": "#2b3d49",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Study Timer")
        self.root.geometry("560x700")
        self.root.minsize(480, 620)
        self.root.configure(bg=self.COLORS["background"])
        self.background_image = self._create_background_image(560, 700)
        self.background_canvas = tk.Canvas(
            self.root,
            bg=self.COLORS["background"],
            highlightthickness=0,
            bd=0,
        )
        self.background_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        self.timer_id = None
        self.mode = "Focus"
        self.is_running = False
        self.completed_cycles = 0
        self.remaining_seconds = 25 * 60
        self.total_seconds = self.remaining_seconds

        self.work_minutes = tk.IntVar(value=25)
        self.short_break_minutes = tk.IntVar(value=5)
        self.long_break_minutes = tk.IntVar(value=15)
        self.task = tk.StringVar()
        self.status = tk.StringVar(value="Ready when you are.")
        self.mode_label = tk.StringVar(value="FOCUS SESSION")
        self.cycle_label = tk.StringVar(value="Cycle 1 of 4")
        self.time_label = tk.StringVar(value="25:00")
        self.button_label = tk.StringVar(value="Start focus")

        self._configure_styles()
        self._build_ui()
        self._update_display()

    def _create_background_image(self, width, height):
        image = tk.PhotoImage(width=width, height=height)
        for y in range(height):
            blend = y / max(1, height - 1)
            red = int(12 + 8 * blend)
            green = int(31 + 19 * blend)
            blue = int(43 + 18 * blend)
            image.put(f"#{red:02x}{green:02x}{blue:02x}", to=(0, y, width, y + 1))

        for x, y, radius, color in (
            (70, 110, 80, "#183d49"),
            (500, 555, 115, "#1d3549"),
            (455, 125, 45, "#49333b"),
        ):
            for offset in range(-radius, radius + 1):
                span = int((radius * radius - offset * offset) ** 0.5)
                image.put(
                    color,
                    to=(
                        max(0, x - span),
                        max(0, y + offset),
                        min(width, x + span + 1),
                        min(height, y + offset + 1),
                    ),
                )
        return image

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Timer.Horizontal.TProgressbar",
            troughcolor=self.COLORS["track"],
            background=self.COLORS["accent"],
            bordercolor=self.COLORS["track"],
            lightcolor=self.COLORS["accent"],
            darkcolor=self.COLORS["accent"],
            thickness=8,
        )
        style.configure(
            "TSpinbox",
            fieldbackground=self.COLORS["panel_light"],
            background=self.COLORS["panel_light"],
            foreground=self.COLORS["text"],
            arrowcolor=self.COLORS["muted"],
            borderwidth=0,
        )

    def _build_ui(self):
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        header = tk.Frame(root, bg=self.COLORS["background"])
        header.grid(row=0, column=0, sticky="ew", padx=34, pady=(28, 0))
        header.columnconfigure(0, weight=1)
        tk.Label(
            header,
            text="POMODORO",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["background"],
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text="Study timer",
            font=("Segoe UI", 10),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
        ).grid(row=0, column=1, sticky="e")

        content = tk.Frame(root, bg=self.COLORS["background"])
        content.grid(row=1, column=0, sticky="nsew", padx=34, pady=18)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        task_frame = tk.Frame(content, bg=self.COLORS["background"])
        task_frame.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        task_frame.columnconfigure(0, weight=1)
        tk.Label(
            task_frame,
            text="CURRENT TASK",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
        ).grid(row=0, column=0, sticky="w")
        task_entry = tk.Entry(
            task_frame,
            textvariable=self.task,
            font=("Segoe UI", 13),
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["text"],
            relief="flat",
            bd=0,
            bg=self.COLORS["panel"],
        )
        task_entry.grid(row=1, column=0, sticky="ew", ipady=11, pady=(7, 0))
        task_entry.insert(0, "What are you working on?")
        task_entry.bind("<FocusIn>", self._clear_placeholder)

        timer_panel = tk.Frame(content, bg=self.COLORS["panel"], padx=28, pady=28)
        timer_panel.grid(row=1, column=0, sticky="nsew")
        timer_panel.columnconfigure(0, weight=1)
        timer_panel.rowconfigure(2, weight=1)

        tk.Label(
            timer_panel,
            textvariable=self.mode_label,
            font=("Segoe UI", 10, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["panel"],
        ).grid(row=0, column=0, pady=(3, 5))
        tk.Label(
            timer_panel,
            textvariable=self.cycle_label,
            font=("Segoe UI", 10),
            fg=self.COLORS["muted"],
            bg=self.COLORS["panel"],
        ).grid(row=1, column=0)

        timer_area = tk.Frame(timer_panel, bg=self.COLORS["panel"])
        timer_area.grid(row=2, column=0, sticky="nsew", pady=16)
        timer_area.columnconfigure(0, weight=1)
        timer_area.rowconfigure(0, weight=1)
        tk.Label(
            timer_area,
            textvariable=self.time_label,
            font=("Segoe UI", 72, "bold"),
            fg=self.COLORS["text"],
            bg=self.COLORS["panel"],
        ).grid(row=0, column=0, pady=(16, 14))
        self.progress = ttk.Progressbar(
            timer_area,
            style="Timer.Horizontal.TProgressbar",
            mode="determinate",
            maximum=100,
        )
        self.progress.grid(row=1, column=0, sticky="ew", padx=20)

        controls = tk.Frame(timer_panel, bg=self.COLORS["panel"])
        controls.grid(row=3, column=0, pady=(24, 4))
        controls.columnconfigure(1, weight=1)
        self.start_button = tk.Button(
            controls,
            textvariable=self.button_label,
            command=self.toggle_timer,
            font=("Segoe UI", 11, "bold"),
            fg="#ffffff",
            bg=self.COLORS["accent"],
            activebackground=self.COLORS["accent_dark"],
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=11,
            width=13,
        )
        self.start_button.grid(row=0, column=0, padx=5)
        tk.Button(
            controls,
            text="Reset",
            command=self.reset_timer,
            font=("Segoe UI", 10, "bold"),
            fg=self.COLORS["text"],
            bg=self.COLORS["panel_light"],
            activebackground=self.COLORS["track"],
            activeforeground=self.COLORS["text"],
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=11,
        ).grid(row=0, column=1, padx=5)
        tk.Button(
            controls,
            text="Skip",
            command=self.skip_session,
            font=("Segoe UI", 10, "bold"),
            fg=self.COLORS["muted"],
            bg=self.COLORS["panel"],
            activebackground=self.COLORS["panel_light"],
            activeforeground=self.COLORS["text"],
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=11,
        ).grid(row=0, column=2, padx=5)

        tk.Label(
            content,
            textvariable=self.status,
            font=("Segoe UI", 10),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
        ).grid(row=2, column=0, pady=(13, 16))

        settings = tk.Frame(content, bg=self.COLORS["background"])
        settings.grid(row=3, column=0, sticky="ew")
        for column in range(3):
            settings.columnconfigure(column, weight=1)
        self._duration_control(settings, 0, "Focus", self.work_minutes)
        self._duration_control(settings, 1, "Short break", self.short_break_minutes)
        self._duration_control(settings, 2, "Long break", self.long_break_minutes)

    def _duration_control(self, parent, column, label, variable):
        frame = tk.Frame(parent, bg=self.COLORS["background"])
        frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 5, 0 if column == 2 else 5))
        tk.Label(
            frame,
            text=label.upper(),
            font=("Segoe UI", 8, "bold"),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
        ).pack(anchor="w")
        spinbox = ttk.Spinbox(frame, from_=1, to=90, textvariable=variable, width=5, command=self._duration_changed)
        spinbox.pack(anchor="w", pady=(5, 0), ipady=4)
        spinbox.bind("<FocusOut>", self._duration_changed)

    def _clear_placeholder(self, event):
        if self.task.get() == "What are you working on?":
            self.task.set("")

    def _duration_changed(self, event=None):
        if not self.is_running:
            self._set_mode(self.mode)

    def toggle_timer(self):
        if self.is_running:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self):
        self.is_running = True
        self.button_label.set("Pause")
        self.status.set("Stay with it. One focused session at a time.")
        self._tick()

    def _pause_timer(self):
        self.is_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.button_label.set("Resume")
        self.status.set("Paused. Your session is still here.")

    def _tick(self):
        if not self.is_running:
            return
        self._update_display()
        if self.remaining_seconds <= 0:
            self.root.bell()
            self._advance_mode()
            return
        self.remaining_seconds -= 1
        self.timer_id = self.root.after(1000, self._tick)

    def reset_timer(self):
        self.is_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self._set_mode(self.mode)
        self.button_label.set("Start focus" if self.mode == "Focus" else "Start break")
        self.status.set("Ready when you are.")

    def skip_session(self):
        self.is_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self._advance_mode()

    def _advance_mode(self):
        if self.mode == "Focus":
            self.completed_cycles += 1
            if self.completed_cycles % 4 == 0:
                self._set_mode("Long break")
                self.status.set("Four focus sessions complete. Take a longer break.")
            else:
                self._set_mode("Short break")
                self.status.set("Focus session complete. Take a short break.")
        else:
            self._set_mode("Focus")
            self.status.set("Break over. Ready for another focus session?")
        self.button_label.set("Start focus" if self.mode == "Focus" else "Start break")
        self._update_display()

    def _set_mode(self, mode):
        self.mode = mode
        duration = {
            "Focus": self.work_minutes.get(),
            "Short break": self.short_break_minutes.get(),
            "Long break": self.long_break_minutes.get(),
        }[mode]
        duration = max(1, min(90, duration))
        self.remaining_seconds = duration * 60
        self.total_seconds = self.remaining_seconds
        self.mode_label.set("FOCUS SESSION" if mode == "Focus" else mode.upper())
        self._update_display()

    def _update_display(self):
        minutes, seconds = divmod(max(0, self.remaining_seconds), 60)
        self.time_label.set(f"{minutes:02d}:{seconds:02d}")
        self.root.title(f"{self.time_label.get()} - {self.mode} | Pomodoro")
        progress = 100 * (1 - self.remaining_seconds / self.total_seconds) if self.total_seconds else 0
        self.progress["value"] = progress
        cycle_number = (self.completed_cycles % 4) + (1 if self.mode == "Focus" else 0)
        if self.mode == "Focus":
            cycle_number = min(4, cycle_number)
        else:
            cycle_number = max(1, min(4, self.completed_cycles % 4 or 4))
        self.cycle_label.set(f"Cycle {cycle_number} of 4")


if __name__ == "__main__":
    app = tk.Tk()
    PomodoroTimer(app)
    app.mainloop()
