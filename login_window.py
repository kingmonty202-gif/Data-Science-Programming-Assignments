# gui/login_window.py
import tkinter as tk
from tkinter import messagebox, ttk
from auth import login_user, register_user
from database import get_connection


class LoginWindow:
    """Login screen — first thing the user sees."""

    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Smart Campus Resource Booking - Login")
        self.root.geometry("450x400")
        self.root.configure(bg="#e0f7fa")
        self.build_ui()

    def build_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        tk.Label(
            self.root,
            text="Smart Campus Booking System",
            font=("Times New Roman", 16, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
        ).pack(pady=20)

        tk.Label(
            self.root,
            text="Richfield Graduate Institution",
            font=("Times New Roman", 11, "italic"),
            bg="#e0f7fa",
            fg="#546e7a",
        ).pack()

        # Login form frame
        frame = tk.Frame(self.root, bg="#e0f7fa")
        frame.pack(pady=20)

        tk.Label(frame, text="Username:", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=0, column=0, sticky="e", pady=8, padx=5
        )
        self.username_entry = tk.Entry(frame, font=("Times New Roman", 12), width=25)
        self.username_entry.grid(row=0, column=1, pady=8, padx=5)

        tk.Label(frame, text="Password:", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=1, column=0, sticky="e", pady=8, padx=5
        )
        self.password_entry = tk.Entry(frame, show="*", font=("Times New Roman", 12), width=25)
        self.password_entry.grid(row=1, column=1, pady=8, padx=5)

        # Buttons
        tk.Button(
            self.root,
            text="Login",
            command=self.login,
            font=("Times New Roman", 12, "bold"),
            width=15,
            bg="#00acc1",
            fg="white",
            cursor="hand2",
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Register as Lecturer",
            command=self.open_register,
            font=("Times New Roman", 11),
            width=20,
            bg="#26c6da",
            fg="white",
            cursor="hand2",
        ).pack(pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        user = login_user(username, password)
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def open_register(self):
        RegisterWindow(self.root, self.build_ui)


class RegisterWindow:
    """Popup for lecturers to create an account."""

    def __init__(self, parent, on_close):
        self.parent = parent
        self.on_close = on_close
        self.win = tk.Toplevel(parent)
        self.win.title("Register Lecturer")
        self.win.geometry("400x350")
        self.win.configure(bg="#e0f7fa")
        self.build_ui()

    def build_ui(self):
        tk.Label(
            self.win,
            text="Register New Lecturer",
            font=("Times New Roman", 14, "bold"),
            bg="#e0f7fa",
            fg="#00838f",
        ).pack(pady=15)

        frame = tk.Frame(self.win, bg="#e0f7fa")
        frame.pack(pady=10)

        tk.Label(frame, text="Username:", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=0, column=0, sticky="e", pady=8, padx=5
        )
        self.username_entry = tk.Entry(frame, font=("Times New Roman", 12), width=22)
        self.username_entry.grid(row=0, column=1, pady=8, padx=5)

        tk.Label(frame, text="Password:", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=1, column=0, sticky="e", pady=8, padx=5
        )
        self.password_entry = tk.Entry(frame, show="*", font=("Times New Roman", 12), width=22)
        self.password_entry.grid(row=1, column=1, pady=8, padx=5)

        tk.Label(frame, text="Campus:", font=("Times New Roman", 12), bg="#e0f7fa").grid(
            row=2, column=0, sticky="e", pady=8, padx=5
        )
        self.campus_combo = ttk.Combobox(frame, font=("Times New Roman", 12), width=20)
        self.campus_combo.grid(row=2, column=1, pady=8, padx=5)
        self.load_campuses()

        tk.Button(
            self.win,
            text="Register",
            command=self.register,
            font=("Times New Roman", 12, "bold"),
            width=15,
            bg="#27ae60",
            fg="white",
            cursor="hand2",
        ).pack(pady=20)

    def load_campuses(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM campuses ORDER BY name")
        self.campuses = cursor.fetchall()
        conn.close()

        self.campus_combo["values"] = [c["name"] for c in self.campuses]
        if self.campuses:
            self.campus_combo.current(0)

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        campus_name = self.campus_combo.get()

        if not username or not password or not campus_name:
            messagebox.showerror("Error", "All fields are required.")
            return

        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters.")
            return

        campus_id = next(
            (c["id"] for c in self.campuses if c["name"] == campus_name), None
        )
        success, msg = register_user(username, password, "lecturer", campus_id)

        if success:
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            self.win.destroy()
            self.on_close()
        else:
            messagebox.showerror("Error", msg)