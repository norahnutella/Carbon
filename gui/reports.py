import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

from db import get_connection

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ==========================================
# COLORS
# ==========================================

BG_COLOR = "#F4F7F6"
ACCENT_COLOR = "#2E8B75"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1F2937"
SECONDARY_TEXT = "#6B7280"


# ==========================================
# OPEN REPORTS WINDOW
# ==========================================

def open_reports():

    window = tk.Toplevel()

    window.title("Reports & Analytics")
    window.geometry("980x600")
    window.configure(bg=BG_COLOR)
    window.resizable(False, False)


    # ==========================================
    # SCROLLABLE CONTAINER
    # ==========================================
    # The window itself is fixed-size, so everything below is placed
    # inside a canvas + scrollbar instead of packing straight into
    # `window`. This lets the whole report scroll when its content is
    # taller than the visible window.

    main_canvas = tk.Canvas(
        window,
        bg=BG_COLOR,
        highlightthickness=0
    )

    main_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    main_scrollbar = ttk.Scrollbar(
        window,
        orient="vertical",
        command=main_canvas.yview
    )

    main_scrollbar.pack(
        side="right",
        fill="y"
    )

    main_canvas.configure(yscrollcommand=main_scrollbar.set)

    scrollable_frame = tk.Frame(
        main_canvas,
        bg=BG_COLOR
    )

    scrollable_frame_id = main_canvas.create_window(
        (0, 0),
        window=scrollable_frame,
        anchor="nw"
    )

    def _on_frame_configure(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", _on_frame_configure)

    def _on_canvas_configure(event):
        main_canvas.itemconfig(scrollable_frame_id, width=event.width)

    main_canvas.bind("<Configure>", _on_canvas_configure)

    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(event):
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_mousewheel(event):
        main_canvas.unbind_all("<MouseWheel>")

    main_canvas.bind("<Enter>", _bind_mousewheel)
    main_canvas.bind("<Leave>", _unbind_mousewheel)


    # ==========================================
    # HEADER
    # ==========================================

    header = tk.Frame(
        scrollable_frame,
        bg=BG_COLOR
    )

    header.pack(
        fill="x",
        padx=35,
        pady=(20, 5)
    )

    title = tk.Label(
        header,
        text="Reports & Analytics",
        font=("Arial", 25, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )

    title.pack(anchor="w")


    subtitle = tk.Label(
        header,
        text="Analyze institutional carbon emission data",
        font=("Arial", 11),
        bg=BG_COLOR,
        fg=SECONDARY_TEXT
    )

    subtitle.pack(
        anchor="w",
        pady=(5, 0)
    )


    # ==========================================
    # SUMMARY CARDS
    # ==========================================

    cards_frame = tk.Frame(
        scrollable_frame,
        bg=BG_COLOR
    )

    cards_frame.pack(
        fill="x",
        padx=35,
        pady=15
    )


    def create_card(parent, title, value, description):

        card = tk.Frame(
            parent,
            bg=CARD_COLOR,
            width=220,
            height=100,
            highlightbackground="#E5E7EB",
            highlightthickness=1
        )

        card.pack(
            side="left",
            padx=6,
            expand=True,
            fill="both"
        )

        card.pack_propagate(False)


        tk.Label(
            card,
            text=title,
            font=("Arial", 10),
            bg=CARD_COLOR,
            fg=SECONDARY_TEXT
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 2)
        )


        value_label = tk.Label(
            card,
            text=value,
            font=("Arial", 16, "bold"),
            bg=CARD_COLOR,
            fg=ACCENT_COLOR
        )

        value_label.pack(
            anchor="w",
            padx=18
        )


        tk.Label(
            card,
            text=description,
            font=("Arial", 9),
            bg=CARD_COLOR,
            fg=SECONDARY_TEXT
        ).pack(
            anchor="w",
            padx=18
        )


        return value_label


    total_label = create_card(
        cards_frame,
        "TOTAL CO₂",
        "0.00 kg",
        "Overall emissions"
    )


    department_label = create_card(
        cards_frame,
        "DEPARTMENTS",
        "0",
        "Registered departments"
    )


    highest_label = create_card(
        cards_frame,
        "HIGHEST EMITTER",
        "N/A",
        "Highest department"
    )


    # ==========================================
    # ACTIVITY REPORT FRAME
    # ==========================================

    activity_frame = tk.Frame(
        scrollable_frame,
        bg=BG_COLOR
    )

    activity_frame.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=5
    )


    # ==========================================
    # CHART FRAME
    # ==========================================

    chart_frame = tk.Frame(
        activity_frame,
        bg=CARD_COLOR,
        highlightbackground="#E5E7EB",
        highlightthickness=1
    )

    chart_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )


    chart_title = tk.Label(
        chart_frame,
        text="Emission by Activity Type",
        font=("Arial", 15, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )

    chart_title.pack(
        anchor="w",
        padx=15,
        pady=(12, 5)
    )


    chart_container = tk.Frame(
        chart_frame,
        bg=CARD_COLOR
    )

    chart_container.pack(
        fill="both",
        expand=True
    )


    # ==========================================
    # DEPARTMENT TABLE FRAME
    # ==========================================

    department_frame = tk.Frame(
        activity_frame,
        bg=CARD_COLOR,
        highlightbackground="#E5E7EB",
        highlightthickness=1
    )

    department_frame.pack(
        side="right",
        fill="both",
        expand=True,
        padx=(8, 0)
    )


    department_title = tk.Label(
        department_frame,
        text="Department-wise Emissions",
        font=("Arial", 15, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )

    department_title.pack(
        anchor="w",
        padx=15,
        pady=(12, 10)
    )


    # ==========================================
    # DEPARTMENT TREEVIEW
    # ==========================================

    department_columns = (
        "dept_id",
        "dept_name",
        "institution",
        "emission"
    )


    department_tree = ttk.Treeview(
        department_frame,
        columns=department_columns,
        show="headings",
        height=10
    )


    department_tree.heading(
        "dept_id",
        text="ID"
    )

    department_tree.heading(
        "dept_name",
        text="Department"
    )

    department_tree.heading(
        "institution",
        text="Institution"
    )

    department_tree.heading(
        "emission",
        text="CO₂ (kg)"
    )


    department_tree.column(
        "dept_id",
        width=50,
        anchor="center"
    )

    department_tree.column(
        "dept_name",
        width=170,
        anchor="w"
    )

    department_tree.column(
        "institution",
        width=140,
        anchor="w"
    )

    department_tree.column(
        "emission",
        width=90,
        anchor="center"
    )


    department_tree.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=5
    )


    # ==========================================
    # TOP EMITTING DEPARTMENTS CHART FRAME
    # ==========================================

    top_dept_frame = tk.Frame(
        scrollable_frame,
        bg=CARD_COLOR,
        highlightbackground="#E5E7EB",
        highlightthickness=1
    )

    top_dept_frame.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=(8, 5)
    )


    top_dept_title = tk.Label(
        top_dept_frame,
        text="Top Emitting Departments by Institution",
        font=("Arial", 15, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )

    top_dept_title.pack(
        anchor="w",
        padx=15,
        pady=(12, 5)
    )


    top_dept_chart_container = tk.Frame(
        top_dept_frame,
        bg=CARD_COLOR
    )

    top_dept_chart_container.pack(
        fill="both",
        expand=True
    )


    # ==========================================
    # DETAILED RECORDS FRAME
    # ==========================================

    detail_frame = tk.Frame(
        scrollable_frame,
        bg=CARD_COLOR,
        highlightbackground="#E5E7EB",
        highlightthickness=1
    )

    detail_frame.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=(8, 5)
    )


    detail_title = tk.Label(
        detail_frame,
        text="Detailed Emission Records",
        font=("Arial", 15, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )

    detail_title.pack(
        anchor="w",
        padx=15,
        pady=(10, 5)
    )


    # ==========================================
    # DETAIL TABLE CONTAINER
    # ==========================================

    detail_table_frame = tk.Frame(
        detail_frame,
        bg=CARD_COLOR
    )

    detail_table_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=5
    )


    # ==========================================
    # DETAIL TREEVIEW
    # ==========================================

    detail_columns = (
        "record_id",
        "dept_name",
        "activity_type",
        "activity_id",
        "quantity",
        "factor",
        "emission",
        "date"
    )


    detail_tree = ttk.Treeview(
        detail_table_frame,
        columns=detail_columns,
        show="headings",
        height=7
    )


    detail_tree.heading(
        "record_id",
        text="Record ID"
    )

    detail_tree.heading(
        "dept_name",
        text="Department"
    )

    detail_tree.heading(
        "activity_type",
        text="Activity"
    )

    detail_tree.heading(
        "activity_id",
        text="Activity ID"
    )

    detail_tree.heading(
        "quantity",
        text="Quantity"
    )

    detail_tree.heading(
        "factor",
        text="Factor"
    )

    detail_tree.heading(
        "emission",
        text="CO₂ (kg)"
    )

    detail_tree.heading(
        "date",
        text="Date"
    )


    detail_tree.column(
        "record_id",
        width=70,
        anchor="center"
    )

    detail_tree.column(
        "dept_name",
        width=220,
        anchor="w"
    )

    detail_tree.column(
        "activity_type",
        width=100,
        anchor="center"
    )

    detail_tree.column(
        "activity_id",
        width=80,
        anchor="center"
    )

    detail_tree.column(
        "quantity",
        width=80,
        anchor="center"
    )

    detail_tree.column(
        "factor",
        width=70,
        anchor="center"
    )

    detail_tree.column(
        "emission",
        width=90,
        anchor="center"
    )

    detail_tree.column(
        "date",
        width=100,
        anchor="center"
    )


    detail_tree.pack(
        side="left",
        fill="both",
        expand=True
    )


    # ==========================================
    # SCROLLBAR
    # ==========================================

    scrollbar = ttk.Scrollbar(
        detail_table_frame,
        orient="vertical",
        command=detail_tree.yview
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )


    detail_tree.configure(
        yscrollcommand=scrollbar.set
    )


    # ==========================================
    # LOAD REPORTS
    # ==========================================

    def load_reports():

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            # Build one logical emission set directly from the three
            # activity tables. No TOTAL_EMISSIONS view is required.
            activity_sql = """
                SELECT e.energy_id AS record_id, e.dept_id, d.dept_name,
                       'Energy' AS activity_type, e.energy_id AS activity_id,
                       e.quantity AS quantity, f.factor_value,
                       e.emission_co2, e.activity_date AS record_date
                FROM energy_consumption e
                JOIN department d ON d.dept_id = e.dept_id
                JOIN emission_factor f ON f.factor_id = e.factor_id
                UNION ALL
                SELECT t.transport_id, t.dept_id, d.dept_name,
                       'Transport', t.transport_id,
                       t.distance_km, f.factor_value,
                       t.emission_co2, t.activity_date
                FROM transport t
                JOIN department d ON d.dept_id = t.dept_id
                JOIN emission_factor f ON f.factor_id = t.factor_id
                UNION ALL
                SELECT w.waste_id, w.dept_id, d.dept_name,
                       'Waste', w.waste_id,
                       w.quantity, f.factor_value,
                       w.emission_co2, w.activity_date
                FROM waste w
                JOIN department d ON d.dept_id = w.dept_id
                JOIN emission_factor f ON f.factor_id = w.factor_id
            """

            # TOTAL CO2
            cursor.execute(f"""
                SELECT NVL(SUM(emission_co2), 0)
                FROM ({activity_sql})
            """)
            total_co2 = float(cursor.fetchone()[0] or 0)

            # DEPARTMENT COUNT
            cursor.execute("SELECT COUNT(*) FROM department")
            department_count = cursor.fetchone()[0]

            # HIGHEST EMISSION DEPARTMENT
            cursor.execute(f"""
                SELECT dept_name, total_co2
                FROM (
                    SELECT dept_name, SUM(emission_co2) AS total_co2
                    FROM ({activity_sql})
                    GROUP BY dept_name
                    ORDER BY total_co2 DESC
                )
                WHERE ROWNUM = 1
            """)
            highest_result = cursor.fetchone()
            highest_department = highest_result[0] if highest_result else "N/A"

            total_label.config(text=f"{total_co2:.2f} kg")
            department_label.config(text=str(department_count))
            highest_label.config(text=highest_department)

            # ACTIVITY EMISSIONS
            cursor.execute(f"""
                SELECT activity_type, NVL(SUM(emission_co2), 0)
                FROM ({activity_sql})
                GROUP BY activity_type
            """)
            activity_rows = cursor.fetchall()

            activity_values = {"Energy": 0, "Transport": 0, "Waste": 0}
            for activity, value in activity_rows:
                activity_values[activity] = float(value or 0)

            for widget in chart_container.winfo_children():
                widget.destroy()

            figure = plt.Figure(figsize=(5.2, 3.0), dpi=90)
            axis = figure.add_subplot(111)
            activities = ["Energy", "Transport", "Waste"]
            values = [activity_values[a] for a in activities]
            axis.bar(activities, values)
            axis.set_title("Energy vs Transport vs Waste")
            axis.set_ylabel("CO₂ (kg)")
            axis.grid(axis="y", linestyle="--", alpha=0.3)
            figure.tight_layout()

            canvas = FigureCanvasTkAgg(figure, master=chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

            # DEPARTMENT REPORT
            for item in department_tree.get_children():
                department_tree.delete(item)

            cursor.execute(f"""
                SELECT d.dept_id, d.dept_name, NVL(i.name, 'Unassigned') AS institution_name,
                       NVL(SUM(a.emission_co2), 0)
                FROM department d
                LEFT JOIN institution i ON i.institution_id = d.institution_id
                LEFT JOIN ({activity_sql}) a ON d.dept_id = a.dept_id
                GROUP BY d.dept_id, d.dept_name, i.name
                ORDER BY NVL(SUM(a.emission_co2), 0) DESC
            """)

            for row in cursor.fetchall():
                department_tree.insert("", "end", values=(row[0], row[1], row[2], f"{float(row[3] or 0):.2f}"))


            # ==========================================
            # TOP EMITTING DEPARTMENTS CHART
            # ==========================================

            cursor.execute(f"""
                SELECT dept_name, institution_name, total_co2
                FROM (
                    SELECT d.dept_name AS dept_name,
                           NVL(i.name, 'Unassigned') AS institution_name,
                           NVL(SUM(a.emission_co2), 0) AS total_co2
                    FROM department d
                    LEFT JOIN institution i ON i.institution_id = d.institution_id
                    LEFT JOIN ({activity_sql}) a ON d.dept_id = a.dept_id
                    GROUP BY d.dept_name, i.name
                    ORDER BY total_co2 DESC
                )
                WHERE ROWNUM <= 8
            """)
            top_dept_rows = cursor.fetchall()

            for widget in top_dept_chart_container.winfo_children():
                widget.destroy()

            if top_dept_rows:
                # Reverse so the highest emitter ends up at the top of the
                # horizontal bar chart (matplotlib draws bottom-to-top).
                chart_rows = list(reversed(top_dept_rows))
                dept_labels = [f"{name} ({institution})" for name, institution, _ in chart_rows]
                dept_values = [float(value or 0) for _, _, value in chart_rows]

                top_figure = plt.Figure(figsize=(9.0, 3.4), dpi=90)
                top_axis = top_figure.add_subplot(111)
                bars = top_axis.barh(dept_labels, dept_values, color=ACCENT_COLOR)
                top_axis.set_xlabel("CO₂ (kg)")
                top_axis.set_title("Highest CO₂-Emitting Departments")
                top_axis.grid(axis="x", linestyle="--", alpha=0.3)
                top_axis.tick_params(axis="y", labelsize=8)

                max_value = max(dept_values) if dept_values else 0
                for bar, value in zip(bars, dept_values):
                    top_axis.text(
                        bar.get_width() + max_value * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f"{value:.1f}",
                        va="center",
                        fontsize=8
                    )

                top_figure.tight_layout()

                top_canvas = FigureCanvasTkAgg(top_figure, master=top_dept_chart_container)
                top_canvas.draw()
                top_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
            else:
                tk.Label(
                    top_dept_chart_container,
                    text="No emission data available yet.",
                    bg=CARD_COLOR,
                    fg=SECONDARY_TEXT,
                    font=("Arial", 10)
                ).pack(pady=20)

            # DETAILED EMISSION RECORDS
            for item in detail_tree.get_children():
                detail_tree.delete(item)

            cursor.execute(f"""
                SELECT record_id, dept_name, activity_type, activity_id,
                       quantity, factor_value, emission_co2, record_date
                FROM ({activity_sql})
                ORDER BY record_date DESC
            """)

            for row in cursor.fetchall():
                record_date = row[7].strftime("%Y-%m-%d") if row[7] else ""
                detail_tree.insert(
                    "", "end",
                    values=(
                        row[0], row[1], row[2], row[3],
                        f"{float(row[4] or 0):.2f}",
                        f"{float(row[5] or 0):.2f}",
                        f"{float(row[6] or 0):.2f}",
                        record_date
                    )
                )

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not load reports.\n\n{e}"
            )

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    # ==========================================
    # INITIAL LOAD
    # ==========================================

    load_reports()


    # ==========================================
    # BUTTON FRAME
    # ==========================================

    button_frame = tk.Frame(
        scrollable_frame,
        bg=BG_COLOR
    )

    button_frame.pack(
        pady=(5, 15)
    )


    # ==========================================
    # EXPORT CSV
    # ==========================================

    def export_csv():

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT record_id, dept_name, activity_type, activity_id,
                       quantity, factor_value, emission_co2, record_date
                FROM (
                    SELECT e.energy_id AS record_id, d.dept_name,
                           'Energy' AS activity_type, e.energy_id AS activity_id,
                           e.quantity AS quantity, f.factor_value,
                           e.emission_co2, e.activity_date AS record_date
                    FROM energy_consumption e
                    JOIN department d ON d.dept_id = e.dept_id
                    JOIN emission_factor f ON f.factor_id = e.factor_id
                    UNION ALL
                    SELECT t.transport_id, d.dept_name,
                           'Transport', t.transport_id,
                           t.distance_km, f.factor_value,
                           t.emission_co2, t.activity_date
                    FROM transport t
                    JOIN department d ON d.dept_id = t.dept_id
                    JOIN emission_factor f ON f.factor_id = t.factor_id
                    UNION ALL
                    SELECT w.waste_id, d.dept_name,
                           'Waste', w.waste_id,
                           w.quantity, f.factor_value,
                           w.emission_co2, w.activity_date
                    FROM waste w
                    JOIN department d ON d.dept_id = w.dept_id
                    JOIN emission_factor f ON f.factor_id = w.factor_id
                )
                ORDER BY record_date DESC
            """)

            rows = cursor.fetchall()

            if not rows:
                messagebox.showinfo(
                    "No Data",
                    "There are no emission records to export."
                )
                return

            file_path = filedialog.asksaveasfilename(
                title="Save Emission Report",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="carbon_emission_report.csv"
            )

            if not file_path:
                return

            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                writer.writerow([
                    "Record ID",
                    "Department",
                    "Activity Type",
                    "Activity ID",
                    "Quantity",
                    "Emission Factor",
                    "CO2 Emission (kg)",
                    "Date"
                ])

                for row in rows:
                    record_date = ""

                    if row[7]:
                        record_date = row[7].strftime("%Y-%m-%d")

                    writer.writerow([
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        f"{row[4]:.2f}",
                        f"{row[5]:.2f}",
                        f"{row[6]:.2f}",
                        record_date
                    ])

            messagebox.showinfo(
                "Export Successful",
                f"Report exported successfully.\n\nSaved to:\n{file_path}"
            )

        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Could not export report.\n\n{e}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    # ==========================================
    # REFRESH BUTTON
    # ==========================================

    refresh_button = tk.Button(
        button_frame,
        text="⟳  Refresh Report",
        command=load_reports,
        font=("Arial", 10, "bold"),
        bg=ACCENT_COLOR,
        fg="white",
        activebackground="#246F5E",
        activeforeground="white",
        bd=0,
        padx=20,
        pady=8,
        cursor="hand2"
    )

    refresh_button.pack(
        side="left",
        padx=5
    )


    # ==========================================
    # EXPORT BUTTON
    # ==========================================

    export_button = tk.Button(
        button_frame,
        text="📁  Export CSV",
        command=export_csv,
        font=("Arial", 10, "bold"),
        bg=ACCENT_COLOR,
        fg="white",
        activebackground="#246F5E",
        activeforeground="white",
        bd=0,
        padx=20,
        pady=8,
        cursor="hand2"
    )

    export_button.pack(
        side="left",
        padx=5
    )


    # ==========================================
    # CLOSE BUTTON
    # ==========================================

    close_button = tk.Button(
        button_frame,
        text="Close",
        command=window.destroy,
        font=("Arial", 10, "bold"),
        bg="#E5E7EB",
        fg=TEXT_COLOR,
        activebackground="#D1D5DB",
        bd=0,
        padx=25,
        pady=8,
        cursor="hand2"
    )

    close_button.pack(
        side="left",
        padx=5
    )