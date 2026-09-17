import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from ui import BG, WHITE, TEXT, SECONDARY, ACCENT, DANGER, responsive_window, make_scrollable_table
from validators import is_valid_phone, is_valid_free_text

def open_institution_management():
    window = tk.Toplevel()
    window.title("Institution Management")
    window.configure(bg=BG)
    responsive_window(window, 950, 650, 760, 540)

    name = tk.StringVar()
    type_var = tk.StringVar()
    address = tk.StringVar()
    contact = tk.StringVar()

    tk.Label(window, text="🏫 Institution Management",
             font=("Arial", 20, "bold"), bg=BG, fg=TEXT).pack(pady=(18, 3))
    tk.Label(window, text="Manage institutions",
             font=("Arial", 9), bg=BG, fg=SECONDARY).pack(pady=(0, 12))

    form = tk.Frame(window, bg=WHITE, bd=1, relief="solid")
    form.pack(fill="x", padx=25)

    fields = [
        ("Institution Name", name),
        ("Type", type_var),
        ("Address", address),
        ("Contact No.", contact)
    ]

    for i, (label, var) in enumerate(fields):
        r, c = divmod(i, 2)
        tk.Label(form, text=label, bg=WHITE, fg=TEXT,
                 font=("Arial", 9, "bold")).grid(row=r*2, column=c, padx=12, pady=(10,2), sticky="w")
        if label == "Type":
            widget = ttk.Combobox(form, textvariable=var,
                                  values=["Educational Institution","University","College","School","Other"],
                                  state="readonly", width=28)
        else:
            widget = tk.Entry(form, textvariable=var, width=31)
        widget.grid(row=r*2+1, column=c, padx=12, pady=(0,10), sticky="ew")

    def clear():
        name.set(""); type_var.set(""); address.set(""); contact.set("")

    def load():
        for item in tree.get_children():
            tree.delete(item)
        con = cur = None
        try:
            con = get_connection(); cur = con.cursor()
            cur.execute("SELECT institution_id,name,type,address,contact_no FROM institution ORDER BY institution_id")
            for row in cur.fetchall():
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def add():
        n = name.get().strip()
        addr = address.get().strip()
        phone = contact.get().strip()

        if not n or not type_var.get() or not addr or not phone:
            messagebox.showwarning("Missing Information", "Please complete all fields.")
            return

        if not is_valid_free_text(n, min_len=2, max_len=100):
            messagebox.showerror(
                "Invalid Institution Name",
                "Institution name should be 2-100 characters and may contain letters, "
                "numbers, and basic punctuation (&, ,, ., -, (), /) only."
            )
            return

        if not is_valid_free_text(addr, min_len=5, max_len=150):
            messagebox.showerror(
                "Invalid Address",
                "Address should be 5-150 characters and may contain letters, numbers, "
                "and basic punctuation (&, ,, ., -, (), /) only."
            )
            return

        if not is_valid_phone(phone):
            messagebox.showerror(
                "Invalid Contact Number",
                "Contact number should contain 7-15 digits, optionally starting with '+' "
                "and using spaces or hyphens as separators (e.g. +91 98765 43210)."
            )
            return

        con = cur = None
        try:
            con = get_connection(); cur = con.cursor()
            cur.execute("SELECT NVL(MAX(institution_id),0)+1 FROM institution")
            new_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO institution
                (institution_id,name,type,address,contact_no)
                VALUES (:1,:2,:3,:4,:5)
            """, (new_id, n, type_var.get(), addr, phone))
            con.commit()
            messagebox.showinfo("Success", "Institution added successfully.")
            clear(); load()
        except Exception as e:
            if con: con.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def delete():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select an institution.")
            return
        institution_id = tree.item(selected[0])["values"][0]
        if not messagebox.askyesno("Confirm Delete", f"Delete Institution ID {institution_id}?"):
            return
        con = cur = None
        try:
            con = get_connection(); cur = con.cursor()
            cur.execute("DELETE FROM institution WHERE institution_id=:1", (institution_id,))
            con.commit(); load(); clear()
        except Exception as e:
            if con: con.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    buttons = tk.Frame(window, bg=BG)
    buttons.pack(pady=12)
    for text, cmd, color in [
        ("Add Institution", add, "#163A35"),
        ("Delete Selected", delete, DANGER),
        ("Clear", clear, "#6B7280"),
        ("Refresh", load, ACCENT)
    ]:
        tk.Button(buttons, text=text, command=cmd, width=15, height=1,
                  bg=color, fg="white", bd=0, font=("Arial", 9, "bold"),
                  cursor="hand2").pack(side="left", padx=4)

    frame, tree = make_scrollable_table(
        window,
        ("ID","Name","Type","Address","Contact"),
        {"ID":60,"Name":180,"Type":150,"Address":240,"Contact":120},
        10
    )
    frame.pack(fill="both", expand=True, padx=25, pady=(0,20))
    load()
