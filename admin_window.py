# gui/admin_window.py
import tkinter as tk
from tkinter import messagebox, ttk
from database import get_connection
from booking_rules import get_rule_for_campus
from reports import campus_summary


class AdminWindow:
    """Dashboard for campus admins: manage resources + view bookings + reports."""

    def __init__(self, root, user, on_logout):
        self.root = root
        self.user = user
        self.on_logout = on_logout
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

    # ---------------------------------------------------------------
    # Main UI
    # ---------------------------------------------------------------
    def build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(self.user.get_dashboard_title())
        self.root.geometry("1000x700")
        self.root.configure(bg="#e0f7fa")

        # --- Header ---
        header = tk.Frame(self.root, bg="#00bcd4", height=60)
        header.pack(fill="x")
        tk.Label(
            header,
            text=f"Campus Admin — {self.campus_name}",
            font=("Times New Roman", 15, "bold"),
            fg="white",
            bg="#00bcd4",
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

        # --- Info bar (policy) ---
        rule = get_rule_for_campus(self.campus_name)
        open_h, close_h = rule.allowed_hours()
        tk.Label(
            self.root,
            text=(f"Active Booking Policy: Max {rule.max_duration()}h  |  "
                  f"Hours {open_h:02d}:00–{close_h:02d}:00  |  {rule.priority_note()}"),
            font=("Times New Roman", 10, "italic"),
            bg="#e0f7fa",
            fg="#006064",
        ).pack(pady=5)

        # --- Notebook (tabs) ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.resources_tab = tk.Frame(notebook, bg="#e0f7fa")
        self.bookings_tab = tk.Frame(notebook, bg="#e0f7fa")
        self.reports_tab = tk.Frame(notebook, bg="#e0f7fa")

        notebook.add(self.resources_tab, text="  Manage Resources  ")
        notebook.add(self.bookings_tab, text="  Campus Bookings  ")
        notebook.add(self.reports_tab, text="  Reports  ")

        self.build_resources_tab()
        self.build_bookings_tab()
        self.build_reports_tab()

    # ---------------------------------------------------------------
    # Tab 1: Manage Resources
    # ---------------------------------------------------------------
    def build_resources_tab(self):
        outer = tk.Frame(self.resources_tab, bg="#e0f7fa")
        outer.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Add resource form ---
        form = tk.LabelFrame(
            outer,
            text="Add New Resource",
            font=("Times New Roman", 12, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
            padx=10,
            pady=10,
        )
        form.pack(fill="x", pady=(0, 10))

        tk.Label(form, text="Name:", font=("Times New Roman", 11), bg="#e0f7fa").grid(
            row=0, column=0, sticky="e", pady=5, padx=5
        )
        self.name_entry = tk.Entry(form, font=("Times New Roman", 11), width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form, text="Type:", font=("Times New Roman", 11), bg="#e0f7fa").grid(
            row=0, column=2, sticky="e", pady=5, padx=5
        )
        self.type_combo = ttk.Combobox(
            form,
            font=("Times New Roman", 11),
            values=["Computer Lab", "Projector", "Seminar Room", "Presentation Equipment"],
            width=22,
            state="readonly",
        )
        self.type_combo.grid(row=0, column=3, pady=5, padx=5)
        self.type_combo.current(0)

        tk.Label(form, text="Capacity:", font=("Times New Roman", 11), bg="#e0f7fa").grid(
            row=1, column=0, sticky="e", pady=5, padx=5
        )
        self.capacity_entry = tk.Entry(form, font=("Times New Roman", 11), width=30)
        self.capacity_entry.grid(row=1, column=1, pady=5, padx=5)
        self.capacity_entry.insert(0, "0")

        tk.Button(
            form,
            text="Add Resource",
            command=self.add_resource,
            font=("Times New Roman", 11, "bold"),
            bg="#27ae60",
            fg="white",
            width=18,
            cursor="hand2",
        ).grid(row=1, column=2, columnspan=2, pady=5, padx=5)

        # --- Resource list ---
        list_frame = tk.LabelFrame(
            outer,
            text="Existing Resources at this Campus",
            font=("Times New Roman", 12, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
            padx=10,
            pady=10,
        )
        list_frame.pack(fill="both", expand=True)

        cols = ("ID", "Name", "Type", "Capacity")
        self.resource_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.resource_tree.heading(c, text=c)
            self.resource_tree.column(c, width=150, anchor="center")
        self.resource_tree.pack(fill="both", expand=True)

        btn_row = tk.Frame(list_frame, bg="#e0f7fa")
        btn_row.pack(pady=8)
        tk.Button(
            btn_row,
            text="Refresh",
            command=self.refresh_resources,
            font=("Times New Roman", 11),
            bg="#00acc1",
            fg="white",
            width=15,
            cursor="hand2",
        ).pack(side="left", padx=5)
        tk.Button(
            btn_row,
            text="Delete Selected",
            command=self.delete_resource,
            font=("Times New Roman", 11),
            bg="#e74c3c",
            fg="white",
            width=18,
            cursor="hand2",
        ).pack(side="left", padx=5)

        self.refresh_resources()

    def refresh_resources(self):
        for row in self.resource_tree.get_children():
            self.resource_tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, type, capacity FROM resources WHERE campus_id = ? ORDER BY name",
            (self.campus_id,),
        )
        for r in cursor.fetchall():
            self.resource_tree.insert("", "end", values=(
                r["id"], r["name"], r["type"], r["capacity"]
            ))
        conn.close()

    def add_resource(self):
        name = self.name_entry.get().strip()
        type_ = self.type_combo.get().strip()
        capacity_raw = self.capacity_entry.get().strip()

        if not name or not type_:
            messagebox.showerror("Error", "Name and Type are required.")
            return

        try:
            capacity = int(capacity_raw)
            if capacity < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Capacity must be a positive whole number.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO resources (name, type, campus_id, capacity) VALUES (?, ?, ?, ?)",
                (name, type_, self.campus_id, capacity),
            )
            conn.commit()
            messagebox.showinfo("Success", f"Resource '{name}' added successfully.")
            self.name_entry.delete(0, tk.END)
            self.capacity_entry.delete(0, tk.END)
            self.capacity_entry.insert(0, "0")
            self.refresh_resources()
        except Exception as e:
            messagebox.showerror(
                "Duplicate Resource",
                f"A resource named '{name}' already exists at this campus.\n\nDetails: {e}",
            )
        finally:
            conn.close()

    def delete_resource(self):
        selected = self.resource_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a resource to delete.")
            return

        values = self.resource_tree.item(selected[0], "values")
        resource_id = values[0]
        resource_name = values[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete resource '{resource_name}'? This cannot be undone."
        )
        if not confirm:
            return

        conn = get_connection()
        cursor = conn.cursor()
        # Check for existing bookings first
        cursor.execute(
            "SELECT COUNT(*) AS c FROM bookings WHERE resource_id = ? AND status = 'active'",
            (resource_id,),
        )
        active = cursor.fetchone()["c"]
        if active > 0:
            conn.close()
            messagebox.showerror(
                "Cannot Delete",
                f"There are {active} active booking(s) for this resource.\n"
                f"Cancel them first before deleting.",
            )
            return

        cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Resource deleted.")
        self.refresh_resources()

    # ---------------------------------------------------------------
    # Tab 2: Campus Bookings
    # ---------------------------------------------------------------
    def build_bookings_tab(self):
        frame = tk.Frame(self.bookings_tab, bg="#e0f7fa")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            frame,
            text=f"All Bookings at {self.campus_name}",
            font=("Times New Roman", 13, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
        ).pack(pady=5)

        cols = ("ID", "Lecturer", "Resource", "Date", "Start", "Duration (h)", "Status")
        self.bookings_tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.bookings_tree.heading(c, text=c)
            self.bookings_tree.column(c, width=120, anchor="center")
        self.bookings_tree.pack(fill="both", expand=True, pady=10)

        tk.Button(
            frame,
            text="Refresh",
            command=self.refresh_bookings,
            font=("Times New Roman", 11),
            bg="#00acc1",
            fg="white",
            width=15,
            cursor="hand2",
        ).pack(pady=5)

        self.refresh_bookings()

    def refresh_bookings(self):
        for row in self.bookings_tree.get_children():
            self.bookings_tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, u.username, r.name AS resource_name,
                   b.booking_date, b.start_time, b.duration, b.status
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN resources r ON b.resource_id = r.id
            WHERE b.campus_id = ?
            ORDER BY b.booking_date DESC, b.start_time DESC
        """, (self.campus_id,))
        for r in cursor.fetchall():
            self.bookings_tree.insert("", "end", values=(
                r["id"], r["username"], r["resource_name"],
                r["booking_date"], r["start_time"], r["duration"],
                r["status"].capitalize()
            ))
        conn.close()

    # ---------------------------------------------------------------
    # Tab 3: Reports
    # ---------------------------------------------------------------
    def build_reports_tab(self):
        frame = tk.Frame(self.reports_tab, bg="#e0f7fa")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            frame,
            text=f"Campus Report — {self.campus_name}",
            font=("Times New Roman", 13, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
        ).pack(pady=10)

        # Stats frame
        self.stats_frame = tk.Frame(frame, bg="#e0f7fa")
        self.stats_frame.pack(pady=10)

        self.stat_labels = {}
        for key, label in [
            ("total_bookings", "Total Bookings"),
            ("most_used_resource", "Most Used Resource"),
            ("most_used_count", "Times Used"),
            ("average_duration", "Average Duration (h)"),
        ]:
            row = tk.Frame(self.stats_frame, bg="#e0f7fa")
            row.pack(pady=4, anchor="w", fill="x")
            tk.Label(
                row, text=f"{label}:", font=("Times New Roman", 12, "bold"),
                bg="#e0f7fa", fg="#00838f", width=22, anchor="e"
            ).pack(side="left", padx=5)
            lbl = tk.Label(row, text="—", font=("Times New Roman", 12), bg="#e0f7fa", fg="#27ae60")
            lbl.pack(side="left", padx=5)
            self.stat_labels[key] = lbl

        tk.Button(
            frame,
            text="Generate Report",
            command=self.generate_report,
            font=("Times New Roman", 11, "bold"),
            bg="#27ae60",
            fg="white",
            width=20,
            cursor="hand2",
        ).pack(pady=20)

        self.generate_report()

    def generate_report(self):
        data = campus_summary(self.campus_id)
        self.stat_labels["total_bookings"].config(text=str(data["total_bookings"]))
        self.stat_labels["most_used_resource"].config(text=data["most_used_resource"])
        self.stat_labels["most_used_count"].config(text=str(data["most_used_count"]))
        self.stat_labels["average_duration"].config(text=str(data["average_duration"]))