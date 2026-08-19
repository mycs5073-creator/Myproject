import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect("college_billing.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT UNIQUE,
    student_id TEXT,
    student_name TEXT,
    course TEXT,
    semester TEXT,
    phone TEXT,
    tuition_fee REAL,
    exam_fee REAL,
    library_fee REAL,
    hostel_fee REAL,
    other_fee REAL,
    total REAL,
    paid REAL,
    balance REAL,
    payment_mode TEXT,
    payment_date TEXT
)
""")

conn.commit()


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()
root.title("College fee billing System")
root.geometry("1250x750")
root.configure(bg="#eef2f7")


# ============================================================
# FUNCTIONS
# ============================================================

def calculate_total():
    try:
        tuition = float(tuition_entry.get() or 0)
        exam = float(exam_entry.get() or 0)
        library = float(library_entry.get() or 0)
        hostel = float(hostel_entry.get() or 0)
        other = float(other_entry.get() or 0)
        paid = float(paid_entry.get() or 0)

        total = tuition + exam + library + hostel + other
        balance = total - paid

        if paid > total:
            messagebox.showwarning(
                "Invalid Payment",
                "Paid amount cannot be greater than total amount."
            )
            return

        total_entry.delete(0, tk.END)
        total_entry.insert(0, f"{total:.2f}")

        balance_entry.delete(0, tk.END)
        balance_entry.insert(0, f"{balance:.2f}")

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter valid numeric values for fees."
        )


def generate_invoice():
    invoice = "INV" + datetime.now().strftime("%Y%m%d%H%M%S")

    invoice_entry.delete(0, tk.END)
    invoice_entry.insert(0, invoice)


def save_bill():
    try:
        student_id = student_id_entry.get().strip()
        student_name = name_entry.get().strip()
        course = course_combo.get().strip()
        semester = semester_combo.get().strip()
        phone = phone_entry.get().strip()

        if not student_id or not student_name or not course or not semester:
            messagebox.showwarning(
                "Missing Information",
                "Please enter Student ID, Name, Course and Semester."
            )
            return

        tuition = float(tuition_entry.get() or 0)
        exam = float(exam_entry.get() or 0)
        library = float(library_entry.get() or 0)
        hostel = float(hostel_entry.get() or 0)
        other = float(other_entry.get() or 0)
        paid = float(paid_entry.get() or 0)

        total = tuition + exam + library + hostel + other
        balance = total - paid

        if paid > total:
            messagebox.showerror(
                "Error",
                "Paid amount cannot be greater than total amount."
            )
            return

        invoice_id = invoice_entry.get().strip()

        if not invoice_id:
            generate_invoice()
            invoice_id = invoice_entry.get()

        payment_mode = payment_combo.get()
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO bills (
            invoice_id,
            student_id,
            student_name,
            course,
            semester,
            phone,
            tuition_fee,
            exam_fee,
            library_fee,
            hostel_fee,
            other_fee,
            total,
            paid,
            balance,
            payment_mode,
            payment_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            student_id,
            student_name,
            course,
            semester,
            phone,
            tuition,
            exam,
            library,
            hostel,
            other,
            total,
            paid,
            balance,
            payment_mode,
            payment_date
        ))

        conn.commit()

        messagebox.showinfo(
            "Success",
            f"Bill saved successfully!\nInvoice: {invoice_id}"
        )

        load_bills()

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter valid numeric values."
        )

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Duplicate Invoice",
            "This invoice number already exists."
        )


def load_bills():
    for item in billing_table.get_children():
        billing_table.delete(item)

    cursor.execute("""
    SELECT
        invoice_id,
        student_id,
        student_name,
        course,
        total,
        paid,
        balance,
        payment_mode,
        payment_date
    FROM bills
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    for row in rows:
        billing_table.insert("", tk.END, values=row)


def search_bill():
    search = search_entry.get().strip()

    if not search:
        load_bills()
        return

    for item in billing_table.get_children():
        billing_table.delete(item)

    cursor.execute("""
    SELECT
        invoice_id,
        student_id,
        student_name,
        course,
        total,
        paid,
        balance,
        payment_mode,
        payment_date
    FROM bills
    WHERE invoice_id LIKE ?
       OR student_id LIKE ?
       OR student_name LIKE ?
    ORDER BY id DESC
    """, (
        "%" + search + "%",
        "%" + search + "%",
        "%" + search + "%"
    ))

    rows = cursor.fetchall()

    for row in rows:
        billing_table.insert("", tk.END, values=row)


def delete_bill():
    selected = billing_table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Bill",
            "Please select a bill to delete."
        )
        return

    item = billing_table.item(selected[0])
    invoice_id = item["values"][0]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete invoice {invoice_id}?"
    )

    if confirm:
        cursor.execute(
            "DELETE FROM bills WHERE invoice_id = ?",
            (invoice_id,)
        )

        conn.commit()
        load_bills()

        messagebox.showinfo(
            "Deleted",
            "Bill deleted successfully."
        )


def select_bill(event):
    selected = billing_table.selection()

    if not selected:
        return

    item = billing_table.item(selected[0])
    invoice_id = item["values"][0]

    cursor.execute(
        "SELECT * FROM bills WHERE invoice_id = ?",
        (invoice_id,)
    )

    row = cursor.fetchone()

    if row:
        clear_fields()

        invoice_entry.insert(0, row[1])
        student_id_entry.insert(0, row[2])
        name_entry.insert(0, row[3])

        course_combo.set(row[4])
        semester_combo.set(row[5])

        phone_entry.insert(0, row[6])

        tuition_entry.insert(0, row[7])
        exam_entry.insert(0, row[8])
        library_entry.insert(0, row[9])
        hostel_entry.insert(0, row[10])
        other_entry.insert(0, row[11])

        total_entry.insert(0, row[12])
        paid_entry.insert(0, row[13])
        balance_entry.insert(0, row[14])

        payment_combo.set(row[15])


def clear_fields():
    entries = [
        invoice_entry,
        student_id_entry,
        name_entry,
        phone_entry,
        tuition_entry,
        exam_entry,
        library_entry,
        hostel_entry,
        other_entry,
        total_entry,
        paid_entry,
        balance_entry
    ]

    for entry in entries:
        entry.delete(0, tk.END)

    course_combo.set("")
    semester_combo.set("")
    payment_combo.set("Cash")


def show_receipt():
    selected = billing_table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Bill",
            "Please select a bill first."
        )
        return

    item = billing_table.item(selected[0])
    invoice_id = item["values"][0]

    cursor.execute(
        "SELECT * FROM bills WHERE invoice_id = ?",
        (invoice_id,)
    )

    row = cursor.fetchone()

    if not row:
        return

    receipt_window = tk.Toplevel(root)
    receipt_window.title("College Fee Receipt")
    receipt_window.geometry("600x650")
    receipt_window.configure(bg="white")

    receipt = tk.Text(
        receipt_window,
        font=("Courier New", 11),
        bg="white",
        relief=tk.FLAT
    )

    receipt.pack(
        fill=tk.BOTH,
        expand=True,
        padx=20,
        pady=20
    )

    receipt_text = f"""
================================================
              COLLEGE FEE RECEIPT
================================================

Invoice No.     : {row[1]}
Date            : {row[16]}

Student ID      : {row[2]}
Student Name    : {row[3]}
Course          : {row[4]}
Semester        : {row[5]}
Phone           : {row[6]}

------------------------------------------------
FEE DETAILS
------------------------------------------------

Tuition Fee     : Rs. {row[7]:.2f}
Exam Fee        : Rs. {row[8]:.2f}
Library Fee     : Rs. {row[9]:.2f}
Hostel Fee      : Rs. {row[10]:.2f}
Other Charges   : Rs. {row[11]:.2f}

------------------------------------------------
Total Amount    : Rs. {row[12]:.2f}
Paid Amount     : Rs. {row[13]:.2f}
Balance         : Rs. {row[14]:.2f}

Payment Mode    : {row[15]}

------------------------------------------------

        Thank you for your payment!

================================================
"""

    receipt.insert(tk.END, receipt_text)
    receipt.config(state=tk.DISABLED)


# ============================================================
# TITLE
# ============================================================

title_frame = tk.Frame(
    root,
    bg="#17365d",
    height=70
)

title_frame.pack(
    fill=tk.X
)

title_label = tk.Label(
    title_frame,
    text="COLLEGE FEES BILLING SYSTEM",
    font=("Arial", 24, "bold"),
    bg="#17365d",
    fg="white"
)

title_label.pack(
    pady=18
)


# ============================================================
# MAIN CONTAINER
# ============================================================

main_frame = tk.Frame(
    root,
    bg="#eef2f7"
)

main_frame.pack(
    fill=tk.BOTH,
    expand=True,
    padx=15,
    pady=15
)


# ============================================================
# STUDENT INFORMATION
# ============================================================

student_frame = tk.LabelFrame(
    main_frame,
    text="Student Information",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=10
)

student_frame.pack(
    fill=tk.X
)


# Invoice
tk.Label(
    student_frame,
    text="Invoice No:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(row=0, column=0, padx=8, pady=8, sticky="w")

invoice_entry = tk.Entry(
    student_frame,
    width=25,
    font=("Arial", 10)
)

invoice_entry.grid(
    row=0,
    column=1,
    padx=8
)

tk.Button(
    student_frame,
    text="Generate",
    command=generate_invoice,
    bg="#2e75b6",
    fg="white",
    width=10
).grid(
    row=0,
    column=2,
    padx=5
)


# Student ID
tk.Label(
    student_frame,
    text="Student ID:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(row=0, column=3, padx=8, pady=8)

student_id_entry = tk.Entry(
    student_frame,
    width=22,
    font=("Arial", 10)
)

student_id_entry.grid(
    row=0,
    column=4,
    padx=8
)


# Student Name
tk.Label(
    student_frame,
    text="Student Name:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(row=1, column=0, padx=8, pady=8, sticky="w")

name_entry = tk.Entry(
    student_frame,
    width=25,
    font=("Arial", 10)
)

name_entry.grid(
    row=1,
    column=1,
    padx=8
)


# Course
tk.Label(
    student_frame,
    text="Course:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(row=1, column=3, padx=8)

course_combo = ttk.Combobox(
    student_frame,
    values=[
        "BCA",
        "BBA",
        "B.Tech",
        "MCA",
        "MBA",
        "B.Sc",
        "M.Sc"
    ],
    width=19,
    state="readonly"
)

course_combo.grid(
    row=1,
    column=4,
    padx=8
)


# Semester
tk.Label(
    student_frame,
    text="Semester:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(row=2, column=0, padx=8, pady=8)

semester_combo = ttk.Combobox(
    student_frame,
    values=[
        "1st",
        "2nd",
        "3rd",
        "4th",
        "5th",
        "6th",
        "7th",
        "8th"
    ],
    width=22,
    state="readonly"
)

semester_combo.grid(
    row=2,
    column=1,
    padx=8
)


# Phone
tk.Label(
    student_frame,
    text="Phone:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(row=2, column=3, padx=8)

phone_entry = tk.Entry(
    student_frame,
    width=22,
    font=("Arial", 10)
)

phone_entry.grid(
    row=2,
    column=4,
    padx=8
)


# ============================================================
# FEE INFORMATION
# ============================================================

fee_frame = tk.LabelFrame(
    main_frame,
    text="Fee Information",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=10
)

fee_frame.pack(
    fill=tk.X,
    pady=10
)


def create_fee_entry(parent, text, row, column):
    tk.Label(
        parent,
        text=text,
        bg="white",
        font=("Arial", 10, "bold")
    ).grid(
        row=row,
        column=column,
        padx=8,
        pady=6,
        sticky="w"
    )

    entry = tk.Entry(
        parent,
        width=18,
        font=("Arial", 10)
    )

    entry.grid(
        row=row,
        column=column + 1,
        padx=8,
        pady=6
    )

    return entry


tuition_entry = create_fee_entry(
    fee_frame,
    "Tuition Fee:",
    0,
    0
)

exam_entry = create_fee_entry(
    fee_frame,
    "Exam Fee:",
    0,
    2
)

library_entry = create_fee_entry(
    fee_frame,
    "Library Fee:",
    1,
    0
)

hostel_entry = create_fee_entry(
    fee_frame,
    "Hostel Fee:",
    1,
    2
)

other_entry = create_fee_entry(
    fee_frame,
    "Other Charges:",
    2,
    0
)

total_entry = create_fee_entry(
    fee_frame,
    "Total Amount:",
    2,
    2
)


# Paid amount
tk.Label(
    fee_frame,
    text="Paid Amount:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(
    row=3,
    column=0,
    padx=8,
    pady=6
)

paid_entry = tk.Entry(
    fee_frame,
    width=18,
    font=("Arial", 10)
)

paid_entry.grid(
    row=3,
    column=1,
    padx=8
)


# Balance
tk.Label(
    fee_frame,
    text="Balance:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(
    row=3,
    column=2,
    padx=8,
    pady=6
)

balance_entry = tk.Entry(
    fee_frame,
    width=18,
    font=("Arial", 10)
)

balance_entry.grid(
    row=3,
    column=3,
    padx=8
)


# Payment Mode
tk.Label(
    fee_frame,
    text="Payment Mode:",
    bg="white",
    font=("Arial", 10, "bold")
).grid(
    row=4,
    column=0,
    padx=8,
    pady=6
)

payment_combo = ttk.Combobox(
    fee_frame,
    values=[
        "Cash",
        "UPI",
        "Debit Card",
        "Credit Card",
        "Bank Transfer"
    ],
    width=16,
    state="readonly"
)

payment_combo.set("Cash")

payment_combo.grid(
    row=4,
    column=1,
    padx=8
)


# ============================================================
# BUTTONS
# ============================================================

button_frame = tk.Frame(
    main_frame,
    bg="#eef2f7"
)

button_frame.pack(
    fill=tk.X,
    pady=5
)


button_style = {
    "font": ("Arial", 10, "bold"),
    "width": 15,
    "height": 1
}


tk.Button(
    button_frame,
    text="Calculate",
    command=calculate_total,
    bg="#2e75b6",
    fg="white",
    **button_style
).pack(side=tk.LEFT, padx=5)

tk.Button(
    button_frame,
    text="Save Bill",
    command=save_bill,
    bg="#28a745",
    fg="white",
    **button_style
).pack(side=tk.LEFT, padx=5)

tk.Button(
    button_frame,
    text="Receipt",
    command=show_receipt,
    bg="#6f42c1",
    fg="white",
    **button_style
).pack(side=tk.LEFT, padx=5)

tk.Button(
    button_frame,
    text="Clear",
    command=clear_fields,
    bg="#6c757d",
    fg="white",
    **button_style
).pack(side=tk.LEFT, padx=5)

tk.Button(
    button_frame,
    text="Delete",
    command=delete_bill,
    bg="#dc3545",
    fg="white",
    **button_style
).pack(side=tk.LEFT, padx=5)


# ============================================================
# SEARCH
# ============================================================

search_frame = tk.Frame(
    main_frame,
    bg="#eef2f7"
)

search_frame.pack(
    fill=tk.X,
    pady=8
)

tk.Label(
    search_frame,
    text="Search:",
    font=("Arial", 11, "bold"),
    bg="#eef2f7"
).pack(
    side=tk.LEFT
)

search_entry = tk.Entry(
    search_frame,
    width=35,
    font=("Arial", 10)
)

search_entry.pack(
    side=tk.LEFT,
    padx=8
)

tk.Button(
    search_frame,
    text="Search Bill",
    command=search_bill,
    bg="#17a2b8",
    fg="white",
    font=("Arial", 10, "bold"),
    width=12
).pack(
    side=tk.LEFT
)


# ============================================================
# BILLING HISTORY
# ============================================================

history_frame = tk.LabelFrame(
    main_frame,
    text="Billing History",
    font=("Arial", 12, "bold"),
    bg="white"
)

history_frame.pack(
    fill=tk.BOTH,
    expand=True
)


columns = (
    "Invoice",
    "Student ID",
    "Student Name",
    "Course",
    "Total",
    "Paid",
    "Balance",
    "Payment",
    "Date"
)

billing_table = ttk.Treeview(
    history_frame,
    columns=columns,
    show="headings"
)


for column in columns:
    billing_table.heading(
        column,
        text=column
    )

    billing_table.column(
        column,
        width=120,
        anchor="center"
    )


billing_table.pack(
    fill=tk.BOTH,
    expand=True,
    padx=5,
    pady=5
)


# Scrollbar
scrollbar = ttk.Scrollbar(
    history_frame,
    orient=tk.VERTICAL,
    command=billing_table.yview
)

billing_table.configure(
    yscrollcommand=scrollbar.set
)

scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)


billing_table.bind(
    "<Double-1>",
    select_bill
)


# ============================================================
# LOAD DATA
# ============================================================

load_bills()


# ============================================================
# CLOSE DATABASE
# ============================================================

def close_application():
    conn.close()
    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()