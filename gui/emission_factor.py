import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from ui import BG, WHITE, TEXT, SECONDARY, ACCENT, DANGER, responsive_window, make_scrollable_table
from validators import is_valid_free_text, is_positive_number


def open_emission_factor_management():
    window = tk.Toplevel()
    window.title("Emission Factor Management")
    window.configure(bg=BG)
    responsive_window(window, 900, 620, 740, 520)

    activity = tk.StringVar()
    name = tk.StringVar()
    value = tk.StringVar()
    unit = tk.StringVar()

    tk.Label(
        window,
        text="🌱 Emission Factor Management",
        font=("Arial", 20, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(pady=(18, 3))

    tk.Label(
        window,
        text="Manage factors used by the Oracle emission calculations",
        font=("Arial", 9),
        bg=BG,
        fg=SECONDARY
    ).pack(pady=(0, 12))

    form = tk.Frame(window, bg=WHITE, bd=1, relief="solid")
    form.pack(fill="x", padx=25)

    tk.Label(
        form, text="Activity Type", bg=WHITE, fg=TEXT,
        font=("Arial", 9, "bold")
    ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

    tk.Label(
        form, text="Factor Name", bg=WHITE, fg=TEXT,
        font=("Arial", 9, "bold")
    ).grid(row=0, column=1, padx=12, pady=(8, 2), sticky="w")

    tk.Label(
        form, text="Factor Value", bg=WHITE, fg=TEXT,
        font=("Arial", 9, "bold")
    ).grid(row=2, column=0, padx=12, pady=(2, 2), sticky="w")

    tk.Label(
        form, text="Unit", bg=WHITE, fg=TEXT,
        font=("Arial", 9, "bold")
    ).grid(row=2, column=1, padx=12, pady=(2, 2), sticky="w")

    ttk.Combobox(
        form,
        textvariable=activity,
        values=["ENERGY", "TRANSPORT", "WASTE"],
        state="readonly",
        width=29
    ).grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")

    tk.Entry(
        form, textvariable=name, width=32
    ).grid(row=1, column=1, padx=12, pady=(0, 8), sticky="ew")

    tk.Entry(
        form, textvariable=value, width=32
    ).grid(row=3, column=0, padx=12, pady=(0, 8), sticky="ew")

    tk.Entry(
        form, textvariable=unit, width=32
    ).grid(row=3, column=1, padx=12, pady=(0, 8), sticky="ew")

    def clear():
        activity.set("")
        name.set("")
        value.set("")
        unit.set("")

    def load():
        for item in tree.get_children():
            tree.delete(item)

        con = cur = None

        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute("""
                SELECT factor_id,
                       activity_type,
                       factor_name,
                       factor_value,
                       unit
                FROM emission_factor
                ORDER BY factor_id
            """)

            for row in cur.fetchall():
                tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    def add():
        factor_name = name.get().strip()
        unit_val = unit.get().strip()
        raw_value = value.get().strip()
        activity_val = activity.get().strip().upper()

        if not activity_val or not factor_name or not raw_value or not unit_val:
            messagebox.showwarning(
                "Missing Information",
                "Please complete all fields."
            )
            return

        if not is_valid_free_text(factor_name, min_len=2, max_len=100):
            messagebox.showerror(
                "Invalid Factor Name",
                "Factor name should be 2-100 characters and may contain "
                "letters, numbers, and basic punctuation (&, ,, ., -, (), /) only."
            )
            return

        if not is_positive_number(raw_value):
            messagebox.showerror(
                "Invalid Factor Value",
                "Factor value must be a number greater than 0 (e.g. 0.85)."
            )
            return

        if not is_valid_free_text(unit_val, min_len=1, max_len=20):
            messagebox.showerror(
                "Invalid Unit",
                "Unit should be 1-20 characters and may contain letters, "
                "numbers, and basic punctuation only (e.g. kg CO2/kWh)."
            )
            return

        con = cur = None

        try:
            v = float(raw_value)

            con = get_connection()
            cur = con.cursor()

            # A factor name may be used in different activities,
            # but it cannot be duplicated within the same activity.
            # Comparison is case-insensitive and ignores leading/trailing spaces.
            cur.execute("""
                SELECT COUNT(*)
                FROM emission_factor
                WHERE UPPER(TRIM(activity_type)) = :1
                  AND UPPER(TRIM(factor_name)) = UPPER(TRIM(:2))
            """, (activity_val, factor_name))

            if cur.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Duplicate Emission Factor",
                    f"The factor '{factor_name}' already exists "
                    f"under the {activity_val} activity.\n\n"
                    "The same factor name can be used under a different "
                    "activity type, but not more than once under the same activity."
                )
                return

            cur.execute(
                "SELECT NVL(MAX(factor_id), 0) + 1 FROM emission_factor"
            )
            fid = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO emission_factor
                    (factor_id, activity_type, factor_name, factor_value, unit)
                VALUES
                    (:1, :2, :3, :4, :5)
            """, (
                fid,
                activity_val,
                factor_name,
                v,
                unit_val
            ))

            con.commit()

            messagebox.showinfo(
                "Success",
                "Emission factor added successfully.\n\n"
                "The new factor is now displayed in the Emission Factor table."
            )

            clear()
            load()

        except Exception as e:
            if con:
                con.rollback()
            messagebox.showerror("Database Error", str(e))

        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    def delete():
        sel = tree.selection()

        if not sel:
            messagebox.showwarning(
                "Select Record",
                "Please select an emission factor."
            )
            return

        fid = tree.item(sel[0])["values"][0]

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete Factor ID {fid}?"
        ):
            return

        con = cur = None

        try:
            con = get_connection()
            cur = con.cursor()

            cur.execute(
                "DELETE FROM emission_factor WHERE factor_id = :1",
                (fid,)
            )

            con.commit()
            load()

        except Exception as e:
            if con:
                con.rollback()
            messagebox.showerror("Database Error", str(e))

        finally:
            if cur:
                cur.close()
            if con:
                con.close()

    buttons = tk.Frame(window, bg=BG)
    buttons.pack(pady=10)

    for text, cmd, color in [
        ("Add Factor", add, "#163A35"),
        ("Delete Selected", delete, DANGER),
        ("Clear", clear, "#6B7280"),
        ("Refresh", load, ACCENT)
    ]:
        tk.Button(
            buttons,
            text=text,
            command=cmd,
            width=14,
            height=1,
            bg=color,
            fg="white",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=4)

    frame, tree = make_scrollable_table(
        window,
        ("ID", "Activity", "Factor Name", "Value", "Unit"),
        {"ID": 55, "Activity": 100, "Factor Name": 210, "Value": 90, "Unit": 180},
        9
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 18)
    )

    load()
