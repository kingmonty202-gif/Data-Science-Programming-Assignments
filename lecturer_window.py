# gui/lecturer_window.py
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from database import get_connection
from booking_rules import get_rule_for_campus


class LecturerWindow:
    """Dashboard for lecturers: make bookings + view history."""

    def __init__(self, root, user, on_logout):
        self.root = root
        self.user = user
        self.on_logout = on_logout

        # Get the lecturer's campus info
        self.campus_id = user.campus_id
        self.campus_name = self._get_campus_name(user.campus_id)

        self.build_ui()

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------
    def _get_campus_name(self, campus_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM campuses WHERE id = ?", (campus_id,))
        row = cursor.fetchone()
        conn.close()
        return row["name"] if row else "Unknown Campus"

    @staticmethod
    def _time_to_minutes(t):
        """Convert 'HH:MM' to total minutes since midnight."""
        h, m = map(int, t.split(":"))
        return h * 60 + m

    # ---------------------------------------------------------------
    # UI
    # ---------------------------------------------------------------
    def build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(self.user.get_dashboard_title())
        self.root.geometry("950x680")
        self.root.configure(bg="#e0f7fa")

        # --- Header ---
        header = tk.Frame(self.root, bg="#0097a7", height=60)
        header.pack(fill="x")
        tk.Label(
            header,
            text=self.user.get_dashboard_title(),
            font=("Times New Roman", 15, "bold"),
            fg="white",
            bg="#0097a7",
        ).pack(side="left", padx=15, pady=12)
        tk.Button(
            header,
            text="Logout",
            command=self.on_logout,
            font=("Times New Roman", 11),
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            width=10,
        ).pack(side="right", padx=15, pady=12)

        # --- Campus + Rule Info Bar ---
        rule = get_rule_for_campus(self.campus_name)
        open_h, close_h = rule.allowed_hours()
        info_text = (
            f"📍 Active Campus: {self.campus_name}   |   "
            f"⏱ Max: {rule.max_duration()}h   |   "
            f"🕐 Hours: {open_h:02d}:00 – {close_h:02d}:00   |   "
            f"⭐ {rule.priority_note()}"
        )
        tk.Label(
            self.root,
            text=info_text,
            font=("Times New Roman", 10, "italic"),
            bg="#e0f7fa",
            fg="#006064",
        ).pack(pady=6)

        # --- Notebook (tabs) ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.booking_tab = tk.Frame(notebook, bg="#e0f7fa")
        self.history_tab = tk.Frame(notebook, bg="#e0f7fa")

        notebook.add(self.booking_tab, text="  Make a Booking  ")
        notebook.add(self.history_tab, text="  My Bookings  ")

        self.build_booking_tab()
        self.build_history_tab()

    # ---------------------------------------------------------------
    # Tab 1: Make a Booking
    # ---------------------------------------------------------------
    def build_booking_tab(self):
        frame = tk.LabelFrame(
            self.booking_tab,
            text="Book a Resource",
            font=("Times New Roman", 12, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
            padx=15,
            pady=15,
        )
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Resource
        tk.Label(frame, text="Resource:", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=0, column=0, sticky="e", pady=8, padx=5
        )
        self.resource_combo = ttk.Combobox(frame, font=("Times New Roman", 11), width=40)
        self.resource_combo.grid(row=0, column=1, pady=8, padx=5)
        self.load_resources()

        # Date
        tk.Label(frame, text="Date (YYYY-MM-DD):", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=1, column=0, sticky="e", pady=8, padx=5
        )
        self.date_entry = tk.Entry(frame, font=("Times New Roman", 11), width=40)
        self.date_entry.grid(row=1, column=1, pady=8, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Start time
        tk.Label(frame, text="Start Time (HH:MM):", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=2, column=0, sticky="e", pady=8, padx=5
        )
        self.time_entry = tk.Entry(frame, font=("Times New Roman", 11), width=40)
        self.time_entry.grid(row=2, column=1, pady=8, padx=5)
        self.time_entry.insert(0, "09:00")

        # Duration
        tk.Label(frame, text="Duration (hours):", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=3, column=0, sticky="e", pady=8, padx=5
        )
        self.duration_entry = tk.Entry(frame, font=("Times New Roman", 11), width=40)
        self.duration_entry.grid(row=3, column=1, pady=8, padx=5)
        self.duration_entry.insert(0, "1")

        # Buttons
        btn_frame = tk.Frame(frame, bg="#e0f7fa")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

        tk.Button(
            btn_frame,
            text="Check Availability",
            command=self.check_availability,
            font=("Times New Roman", 11),
            width=20,
            bg="#00acc1",
            fg="white",
            cursor="hand2",
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Book Resource",
            command=self.make_booking,
            font=("Times New Roman", 11, "bold"),
            width=20,
            bg="#27ae60",
            fg="white",
            cursor="hand2",
        ).pack(side="left", padx=5)

        # Availability message
        self.availability_label = tk.Label(
            frame, text="", font=("Times New Roman", 11, "italic"), bg="#e0f7fa", fg="#00acc1"
        )
        self.availability_label.grid(row=5, column=0, columnspan=2, pady=8)

    def load_resources(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, type, capacity FROM resources WHERE campus_id = ? ORDER BY name",
            (self.campus_id,),
        )
        self.resources = cursor.fetchall()
        conn.close()

        self.resource_combo["values"] = [
            f"{r['name']} ({r['type']}) - cap {r['capacity']}" for r in self.resources
        ]
        if self.resources:
            self.resource_combo.current(0)
        else:
            self.resource_combo["values"] = ["No resources available"]

    def _get_selected_resource(self):
        idx = self.resource_combo.current()
        if idx < 0 or idx >= len(self.resources):
            return None
        return self.resources[idx]

    def has_overlap(self, resource_id, date, start_time, duration):
        """Return True if the resource is already booked for that slot."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT start_time, duration FROM bookings
            WHERE resource_id = ? AND booking_date = ? AND status = 'active'
        """, (resource_id, date))
        existing = cursor.fetchall()
        conn.close()

        new_start = self._time_to_minutes(start_time)
        new_end = new_start + duration * 60

        for row in existing:
            old_start = self._time_to_minutes(row["start_time"])
            old_end = old_start + row["duration"] * 60
            if new_start < old_end and old_start < new_end:
                return True
        return False

    def check_availability(self):
        resource = self._get_selected_resource()
        if not resource:
            messagebox.showerror("Error", "No resource selected.")
            return

        date = self.date_entry.get().strip()
        start = self.time_entry.get().strip()
        try:
            duration = int(self.duration_entry.get().strip())
        except ValueError:
            self.availability_label.config(text="Duration must be a whole number.", fg="red")
            return

        rule = get_rule_for_campus(self.campus_name)
        valid, msg = rule.validate(date, start, duration)
        if not valid:
            self.availability_label.config(text=msg, fg="red")
            return

        if self.has_overlap(resource["id"], date, start, duration):
            self.availability_label.config(
                text="❌ Resource is NOT available at this time.", fg="red"
            )
        else:
            self.availability_label.config(
                text="✅ Resource is AVAILABLE for this time slot.", fg="green"
            )

    def make_booking(self):
        resource = self._get_selected_resource()
        if not resource:
            messagebox.showerror("Error", "No resource selected.")
            return

        date = self.date_entry.get().strip()
        start = self.time_entry.get().strip()
        try:
            duration = int(self.duration_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Duration must be a whole number.")
            return

        # Validate against campus rules
        rule = get_rule_for_campus(self.campus_name)
        valid, msg = rule.validate(date, start, duration)
        if not valid:
            messagebox.showerror("Booking Rejected", msg)
            return

        # Check for clashes
        if self.has_overlap(resource["id"], date, start, duration):
            messagebox.showerror(
                "Booking Rejected",
                "This resource is already booked for the requested time slot.",
            )
            return

        # Save booking
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (user_id, resource_id, campus_id, booking_date, start_time, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.user.user_id, resource["id"], self.campus_id, date, start, duration))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Booking created successfully!")
        self.availability_label.config(text="", fg="#00acc1")
        self.refresh_history()

    # ---------------------------------------------------------------
    # Tab 2: My Bookings
    # ---------------------------------------------------------------
    def build_history_tab(self):
        frame = tk.Frame(self.history_tab, bg="#e0f7fa")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            frame,
            text="Your Booking History",
            font=("Times New Roman", 13, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
        ).pack(pady=5)

        # Treeview
        columns = ("ID", "Resource", "Date", "Start", "Duration (h)", "Status")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=130, anchor="center")
        self.history_tree.pack(fill="both", expand=True, pady=10)

        # Buttons
        btn_frame = tk.Frame(frame, bg="#e0f7fa")
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="Refresh",
            command=self.refresh_history,
            font=("Times New Roman", 11),
            width=15,
            bg="#00acc1",
            fg="white",
            cursor="hand2",
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Cancel Selected Booking",
            command=self.cancel_booking,
            font=("Times New Roman", 11),
            width=22,
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
        ).pack(side="left", padx=5)

        self.refresh_history()

    def refresh_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, r.name AS resource_name, b.booking_date, b.start_time,
                   b.duration, b.status
            FROM bookings b
            JOIN resources r ON b.resource_id = r.id
            WHERE b.user_id = ?
            ORDER BY b.booking_date DESC, b.start_time DESC
        """, (self.user.user_id,))
        for row in cursor.fetchall():
            self.history_tree.insert("", "end", values=(
                row["id"], row["resource_name"], row["booking_date"],
                row["start_time"], row["duration"], row["status"].capitalize()
            ))
        conn.close()

    def cancel_booking(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a booking to cancel.")
            return

        values = self.history_tree.item(selected[0], "values")
        booking_id = values[0]
        booking_date = values[2]
        status = values[5]

        if status.lower() == "cancelled":
            messagebox.showerror("Error", "This booking is already cancelled.")
            return

        # Only allow cancelling future bookings
        if booking_date < datetime.now().strftime("%Y-%m-%d"):
            messagebox.showerror("Error", "You cannot cancel past bookings.")
            return

        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            f"Cancel booking #{booking_id}?\n({values[1]} on {booking_date})"
        )
        if not confirm:
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Booking cancelled.")
        self.refresh_history()