import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import os


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Student Records File Management System")
root.geometry("1100x650")
root.minsize(900, 550)

students = []
next_id = 1

# Student fields
fields = [
    "Matric Number",
    "Full Name",
    "Department",
    "Level",
    "Email",
    "Phone"
]


# ================= TITLE =================

title = tk.Label(
    root,
    text="STUDENT RECORDS FILE MANAGEMENT SYSTEM",
    font=("Arial", 18, "bold"),
    bg="navy",
    fg="white",
    pady=15
)
title.pack(fill="x")


# ================= INPUT FORM =================

form = tk.LabelFrame(
    root,
    text="Student Information",
    padx=10,
    pady=10
)
form.pack(fill="x", padx=10, pady=10)

entries = {}

for index, field in enumerate(fields):
    row = index // 3
    column = (index % 3) * 2

    tk.Label(
        form,
        text=field + ":",
        font=("Arial", 10)
    ).grid(
        row=row,
        column=column,
        padx=5,
        pady=7,
        sticky="w"
    )

    entry = tk.Entry(form, width=25)
    entry.grid(
        row=row,
        column=column + 1,
        padx=5,
        pady=7
    )

    entries[field] = entry


# ================= SEARCH SECTION =================

search_frame = tk.Frame(root)
search_frame.pack(fill="x", padx=10, pady=5)

tk.Label(
    search_frame,
    text="Search by name or matric number:"
).pack(side="left", padx=5)

search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side="left", padx=5)


# ================= RECORD TABLE =================

table_frame = tk.Frame(root)
table_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)

columns = ["ID"] + fields

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    tree.heading(column, text=column)
    tree.column(column, width=130, anchor="center")

tree.column("ID", width=45)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


# ================= HELPER FUNCTIONS =================

def get_form_data():
    return {
        field: entries[field].get().strip()
        for field in fields
    }


def clear_form():
    for entry in entries.values():
        entry.delete(0, tk.END)

    tree.selection_remove(tree.selection())


def refresh_table(records=None):
    for item in tree.get_children():
        tree.delete(item)

    display_records = students if records is None else records

    for student in display_records:
        tree.insert(
            "",
            "end",
            values=[student["ID"]] + [
                student[field] for field in fields
            ]
        )


def find_student_by_id(student_id):
    for student in students:
        if student["ID"] == student_id:
            return student

    return None


def get_selected_student():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Selection Required",
            "Please select a student record from the table."
        )
        return None

    values = tree.item(selected[0], "values")
    return find_student_by_id(int(values[0]))


def validate_data(data):
    required = [
        "Matric Number",
        "Full Name",
        "Department",
        "Level"
    ]

    for field in required:
        if not data[field]:
            messagebox.showwarning(
                "Missing Information",
                f"{field} is required."
            )
            return False

    return True


def matric_exists(matric, exclude_id=None):
    for student in students:
        if (
            student["Matric Number"].casefold() == matric.casefold()
            and student["ID"] != exclude_id
        ):
            return True

    return False


def save_records():
    """Save records automatically to the JSON data file."""
    try:
        with open(
            "student_records.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(students, file, indent=4, ensure_ascii=False)

    except OSError as error:
        messagebox.showerror(
            "Save Error",
            f"Could not save records:\n{error}"
        )


# ================= LOAD SAVED RECORDS =================

def load_saved_records():
    global next_id

    filename = "student_records.json"

    if not os.path.exists(filename):
        return

    try:
        with open(filename, "r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError("The file must contain a list of records.")

        loaded = []
        used_ids = set()
        used_matric = set()

        for record in records:
            if not isinstance(record, dict):
                raise ValueError("A student record is not valid.")

            matric = str(record.get("Matric Number", "")).strip()
            name = str(record.get("Full Name", "")).strip()
            department = str(record.get("Department", "")).strip()
            level = str(record.get("Level", "")).strip()

            if not matric or not name or not department or not level:
                raise ValueError("A record is missing required information.")

            if matric.casefold() in used_matric:
                raise ValueError("Duplicate matriculation number found.")

            used_matric.add(matric.casefold())

            student_id = int(record.get("ID", 0))

            if student_id <= 0 or student_id in used_ids:
                student_id = max(used_ids, default=0) + 1

            used_ids.add(student_id)

            student = {
                "ID": student_id,
                **{
                    field: str(record.get(field, ""))
                    for field in fields
                }
            }

            loaded.append(student)

        students.clear()
        students.extend(loaded)

        next_id = max(
            (student["ID"] for student in students),
            default=0
        ) + 1

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        messagebox.showerror(
            "Load Error",
            f"Could not load saved records:\n{error}"
        )


# ================= ADD RECORD =================

def add_record():
    global next_id

    data = get_form_data()

    if not validate_data(data):
        return

    if matric_exists(data["Matric Number"]):
        messagebox.showerror(
            "Duplicate Record",
            "This matriculation number already exists."
        )
        return

    student = {
        "ID": next_id,
        **data
    }

    students.append(student)
    next_id += 1

    save_records()
    refresh_table()
    clear_form()

    messagebox.showinfo(
        "Success",
        "Student record added successfully."
    )


# ================= SEARCH RECORD =================

def search_record():
    keyword = search_entry.get().strip().casefold()

    if not keyword:
        refresh_table()
        return

    results = [
        student for student in students
        if keyword in student["Full Name"].casefold()
        or keyword in student["Matric Number"].casefold()
    ]

    refresh_table(results)

    if not results:
        messagebox.showinfo(
            "Search Results",
            "No matching student record found."
        )


def show_all_records():
    search_entry.delete(0, tk.END)
    refresh_table()


# ================= SELECT RECORD =================

def select_record(event=None):
    selected = tree.selection()

    if not selected:
        return

    values = tree.item(selected[0], "values")

    for index, field in enumerate(fields, start=1):
        entries[field].delete(0, tk.END)
        entries[field].insert(0, values[index])


# ================= UPDATE RECORD =================

def update_record():
    student = get_selected_student()

    if student is None:
        return

    data = get_form_data()

    if not validate_data(data):
        return

    if matric_exists(
        data["Matric Number"],
        exclude_id=student["ID"]
    ):
        messagebox.showerror(
            "Duplicate Record",
            "Another student already uses this matric number."
        )
        return

    student.update(data)

    save_records()
    refresh_table()
    clear_form()

    messagebox.showinfo(
        "Success",
        "Student record updated successfully."
    )


# ================= DELETE RECORD =================

def delete_record():
    student = get_selected_student()

    if student is None:
        return

    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Delete the record for {student['Full Name']}?"
    )

    if not confirm:
        return

    students.remove(student)

    save_records()
    refresh_table()
    clear_form()

    messagebox.showinfo(
        "Success",
        "Student record deleted successfully."
    )


# ================= EXPORT RECORDS =================

def export_records():
    if not students:
        messagebox.showwarning(
            "No Records",
            "There are no records to export."
        )
        return

    filename = filedialog.asksaveasfilename(
        title="Export Student Records",
        defaultextension=".csv",
        filetypes=[
            ("CSV Files", "*.csv"),
            ("JSON Files", "*.json")
        ]
    )

    if not filename:
        return

    try:
        if filename.lower().endswith(".json"):
            with open(
                filename, "w", encoding="utf-8"
            ) as file:
                json.dump(
                    students,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        else:
            with open(
                filename, "w", newline="", encoding="utf-8-sig"
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["ID"] + fields
                )
                writer.writeheader()
                writer.writerows(students)

        messagebox.showinfo(
            "Export Successful",
            f"Records exported successfully to:\n{filename}"
        )

    except (OSError, csv.Error, TypeError, ValueError) as error:
        messagebox.showerror(
            "Export Error",
            f"Could not export records:\n{error}"
        )


# ================= IMPORT RECORDS =================

def import_records():
    global next_id

    filename = filedialog.askopenfilename(
        title="Import Student Records",
        filetypes=[
            ("CSV Files", "*.csv"),
            ("JSON Files", "*.json")
        ]
    )

    if not filename:
        return

    try:
        if filename.lower().endswith(".json"):
            with open(filename, "r", encoding="utf-8-sig") as file:
                imported = json.load(file)

            if not isinstance(imported, list):
                raise ValueError("JSON file must contain a list of records.")

        else:
            with open(
                filename, "r", newline="", encoding="utf-8-sig"
            ) as file:
                imported = list(csv.DictReader(file))

        if not all(isinstance(row, dict) for row in imported):
            raise ValueError("The file contains an invalid record.")

        prepared = []
        seen_matric = set()

        # Validate the entire file before changing the database.
        existing_matric = {
            student["Matric Number"].casefold()
            for student in students
        }

        for row in imported:
            data = {
                field: str(row.get(field, "") or "").strip()
                for field in fields
            }

            if not all(
                data[field]
                for field in [
                    "Matric Number",
                    "Full Name",
                    "Department",
                    "Level"
                ]
            ):
                raise ValueError(
                    "Every imported record must include matric number, "
                    "full name, department, and level."
                )

            matric_key = data["Matric Number"].casefold()

            if (
                matric_key in existing_matric
                or matric_key in seen_matric
            ):
                raise ValueError(
                    f"Duplicate matric number: {data['Matric Number']}"
                )

            seen_matric.add(matric_key)
            prepared.append(data)

        for data in prepared:
            students.append({
                "ID": next_id,
                **data
            })
            next_id += 1

        save_records()
        refresh_table()

        messagebox.showinfo(
            "Import Successful",
            f"{len(prepared)} student record(s) imported successfully."
        )

    except (
        OSError,
        csv.Error,
        json.JSONDecodeError,
        ValueError,
        TypeError
    ) as error:
        messagebox.showerror(
            "Import Error",
            f"Could not import records:\n{error}"
        )


# ================= BUTTONS =================

button_frame = tk.Frame(root)
button_frame.pack(pady=12)

tk.Button(
    button_frame,
    text="Add Record",
    width=15,
    command=add_record
).grid(row=0, column=0, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Search",
    width=15,
    command=search_record
).grid(row=0, column=1, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Update Record",
    width=15,
    command=update_record
).grid(row=0, column=2, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Delete Record",
    width=15,
    command=delete_record
).grid(row=0, column=3, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Export Records",
    width=15,
    command=export_records
).grid(row=1, column=0, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Import Records",
    width=15,
    command=import_records
).grid(row=1, column=1, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Show All",
    width=15,
    command=show_all_records
).grid(row=1, column=2, padx=5, pady=5)

tk.Button(
    button_frame,
    text="Clear Fields",
    width=15,
    command=clear_form
).grid(row=1, column=3, padx=5, pady=5)


# ================= START APPLICATION =================

tree.bind("<<TreeviewSelect>>", select_record)

load_saved_records()
refresh_table()

root.mainloop()
