
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------------- DATABASE ----------------

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    semester INTEGER NOT NULL,
    email TEXT,
    phone TEXT
)
""")
conn.commit()


# ---------------- MAIN APPLICATION ----------------

class StudentManagement:

    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1200x720")
        self.root.minsize(950, 600)
        self.root.configure(bg="#f1f5f9")

        self.selected_roll = None

        self.roll = tk.StringVar()
        self.name = tk.StringVar()
        self.course = tk.StringVar()
        self.semester = tk.StringVar()
        self.email = tk.StringVar()
        self.phone = tk.StringVar()
        self.search = tk.StringVar()

        self.create_interface()
        self.show_students()

    # ---------------- INTERFACE ----------------

    def create_interface(self):

        # Sidebar
        sidebar = tk.Frame(
            self.root, bg="#172b4d", width=210
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="🎓 Student\nManagement",
            font=("Arial", 19, "bold"),
            bg="#172b4d",
            fg="white",
            pady=30
        ).pack(fill="x")

        menu = [
            ("Dashboard", self.show_students),
            ("Add Student", self.clear_fields),
            ("View Students", self.show_students),
            ("Search Student", self.focus_search),
            ("Update Student", self.update_student),
            ("Delete Student", self.delete_student),
            ("Exit", self.root.destroy)
        ]

        for title, command in menu:
            tk.Button(
                sidebar,
                text=title,
                command=command,
                bg="#23416b",
                fg="white",
                activebackground="#2563eb",
                activeforeground="white",
                font=("Arial", 11),
                relief="flat",
                cursor="hand2",
                pady=12
            ).pack(fill="x", padx=12, pady=4)

        # Main content
        self.main = tk.Frame(
            self.root, bg="#f1f5f9"
        )
        self.main.pack(
            side="right", fill="both", expand=True
        )

        tk.Label(
            self.main,
            text="Student Management Dashboard",
            font=("Arial", 23, "bold"),
            bg="#f1f5f9",
            fg="#172b4d"
        ).pack(anchor="w", padx=25, pady=20)

        # Dashboard statistics
        stats = tk.Frame(self.main, bg="#f1f5f9")
        stats.pack(fill="x", padx=20)

        self.total_label = self.stat_card(
            stats, "Total Students", "#2563eb"
        )

        self.course_label = self.stat_card(
            stats, "Total Courses", "#059669"
        )

        self.semester_label = self.stat_card(
            stats, "Total Semesters", "#d97706"
        )

        # Student form
        form = tk.LabelFrame(
            self.main,
            text="Student Registration Form",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#172b4d",
            padx=15,
            pady=12
        )
        form.pack(fill="x", padx=25, pady=15)

        fields = [
            ("Roll Number", self.roll),
            ("Full Name", self.name),
            ("Course", self.course),
            ("Semester", self.semester),
            ("Email", self.email),
            ("Phone", self.phone)
        ]

        for i, (label, variable) in enumerate(fields):
            row = i // 3
            col = (i % 3) * 2

            tk.Label(
                form,
                text=label,
                bg="white",
                font=("Arial", 10)
            ).grid(
                row=row * 2,
                column=col,
                sticky="w",
                padx=8,
                pady=4
            )

            tk.Entry(
                form,
                textvariable=variable,
                font=("Arial", 11),
                width=23,
                relief="solid",
                bd=1
            ).grid(
                row=row * 2 + 1,
                column=col,
                padx=8,
                pady=5
            )

        # Action buttons
        actions = tk.Frame(form, bg="white")
        actions.grid(
            row=4, column=0,
            columnspan=6, pady=15
        )

        buttons = [
            ("Add Student", self.add_student, "#16a34a"),
            ("Update", self.update_student, "#2563eb"),
            ("Delete", self.delete_student, "#dc2626"),
            ("Clear", self.clear_fields, "#64748b")
        ]

        for text, command, color in buttons:
            tk.Button(
                actions,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                width=15,
                relief="flat",
                cursor="hand2",
                pady=8
            ).pack(side="left", padx=6)

        # Search bar
        search_frame = tk.Frame(
            self.main, bg="#f1f5f9"
        )
        search_frame.pack(fill="x", padx=25, pady=8)

        tk.Label(
            search_frame,
            text="Search Student:",
            bg="#f1f5f9",
            font=("Arial", 11, "bold")
        ).pack(side="left")

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search,
            font=("Arial", 11),
            width=28
        )
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind(
            "<Return>", lambda event: self.search_student()
        )

        tk.Button(
            search_frame,
            text="Search",
            command=self.search_student,
            bg="#2563eb",
            fg="white",
            width=12
        ).pack(side="left", padx=4)

        tk.Button(
            search_frame,
            text="Show All",
            command=self.reset_search,
            bg="#475569",
            fg="white",
            width=12
        ).pack(side="left", padx=4)

        # Student table
        table_frame = tk.Frame(
            self.main, bg="white"
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5, 20)
        )

        columns = (
            "Roll No", "Name", "Course",
            "Semester", "Email", "Phone"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        for column in columns:
            self.table.heading(
                column, text=column
            )
            self.table.column(
                column, width=120, anchor="center"
            )

        self.table.column("Name", width=160)
        self.table.column("Email", width=190)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")
        self.table.pack(
            side="left", fill="both", expand=True
        )

        self.table.bind(
            "<<TreeviewSelect>>",
            self.select_student
        )

    # ---------------- STATISTICS ----------------

    def stat_card(self, parent, title, color):

        frame = tk.Frame(
            parent, bg=color, padx=18, pady=12
        )
        frame.pack(
            side="left", expand=True,
            fill="x", padx=5
        )

        tk.Label(
            frame,
            text=title,
            bg=color,
            fg="white",
            font=("Arial", 12)
        ).pack()

        value = tk.Label(
            frame,
            text="0",
            bg=color,
            fg="white",
            font=("Arial", 25, "bold")
        )
        value.pack()

        return value

    def update_dashboard(self):

        cursor.execute(
            "SELECT COUNT(*) FROM students"
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT course) FROM students"
        )
        courses = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT semester) FROM students"
        )
        semesters = cursor.fetchone()[0]

        self.total_label.config(text=str(total))
        self.course_label.config(text=str(courses))
        self.semester_label.config(text=str(semesters))

    # ---------------- VALIDATION ----------------

    def get_form_data(self):

        try:
            roll = int(self.roll.get().strip())
            semester = int(self.semester.get().strip())

            if roll <= 0 or semester <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Roll number and semester must be positive integers."
            )
            return None

        name = self.name.get().strip()
        course = self.course.get().strip()
        email = self.email.get().strip()
        phone = self.phone.get().strip()

        if not name or not course:
            messagebox.showerror(
                "Missing Information",
                "Name and Course are required."
            )
            return None

        return (
            roll, name, course,
            semester, email, phone
        )

    # ---------------- ADD STUDENT ----------------

    def add_student(self):

        data = self.get_form_data()

        if data is None:
            return

        try:
            cursor.execute(
                """
                INSERT INTO students
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                data
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Student added successfully!"
            )

            self.clear_fields()
            self.show_students()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error",
                "This Roll Number already exists!"
            )

    # ---------------- VIEW STUDENTS ----------------

    def show_students(self):

        for item in self.table.get_children():
            self.table.delete(item)

        cursor.execute(
            "SELECT * FROM students ORDER BY roll_no"
        )

        for student in cursor.fetchall():
            self.table.insert(
                "", "end", values=student
            )

        self.update_dashboard()

    # ---------------- SELECT STUDENT ----------------

    def select_student(self, event=None):

        selected = self.table.selection()

        if not selected:
            return

        values = self.table.item(
            selected[0], "values"
        )

        self.selected_roll = int(values[0])

        variables = [
            self.roll, self.name, self.course,
            self.semester, self.email, self.phone
        ]

        for variable, value in zip(variables, values):
            variable.set(value)

    # ---------------- UPDATE STUDENT ----------------

    def update_student(self):

        if self.selected_roll is None:
            messagebox.showwarning(
                "Selection Required",
                "Please select a student from the table."
            )
            return

        data = self.get_form_data()

        if data is None:
            return

        try:
            cursor.execute(
                """
                UPDATE students
                SET roll_no=?, name=?, course=?,
                    semester=?, email=?, phone=?
                WHERE roll_no=?
                """,
                data + (self.selected_roll,)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Student updated successfully!"
            )

            self.clear_fields()
            self.show_students()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error",
                "The new Roll Number already exists!"
            )

    # ---------------- DELETE STUDENT ----------------

    def delete_student(self):

        if self.selected_roll is None:
            messagebox.showwarning(
                "Selection Required",
                "Please select a student first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?"
        )

        if confirm:
            cursor.execute(
                "DELETE FROM students WHERE roll_no=?",
                (self.selected_roll,)
            )

            conn.commit()

            messagebox.showinfo(
                "Deleted",
                "Student deleted successfully!"
            )

            self.clear_fields()
            self.show_students()

    # ---------------- SEARCH STUDENT ----------------

    def search_student(self):

        keyword = self.search.get().strip()

        for item in self.table.get_children():
            self.table.delete(item)

        cursor.execute(
            """
            SELECT * FROM students
            WHERE CAST(roll_no AS TEXT) LIKE ?
               OR name LIKE ?
            ORDER BY roll_no
            """,
            (f"%{keyword}%", f"%{keyword}%")
        )

        for student in cursor.fetchall():
            self.table.insert(
                "", "end", values=student
            )

    def reset_search(self):
        self.search.set("")
        self.show_students()

    def focus_search(self):
        self.search_entry.focus_set()

    # ---------------- CLEAR FORM ----------------

    def clear_fields(self):

        for variable in [
            self.roll, self.name, self.course,
            self.semester, self.email, self.phone
        ]:
            variable.set("")

        self.selected_roll = None

        for item in self.table.selection():
            self.table.selection_remove(item)


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    root = tk.Tk()

    app = StudentManagement(root)

    def close_application():
        conn.close()
        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        close_application
    )

    root.mainloop
