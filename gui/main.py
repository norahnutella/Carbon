import tkinter as tk
from tkinter import ttk, messagebox

from db import get_connection
from waste import open_waste_management
from energy import open_energy_management
from transport import open_transport_management
from institution import open_institution_management
from department import open_department_management
from emission_factor import open_emission_factor_management
from reports import open_reports


# ==========================================
# COLORS
# ==========================================

BG_COLOR = "#F4F7F6"
SIDEBAR_COLOR = "#163A35"
SIDEBAR_HOVER = "#24564E"
ACCENT_COLOR = "#2E8B75"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1F2937"
SECONDARY_TEXT = "#6B7280"


# ==========================================
# DATABASE FUNCTIONS
# ==========================================

def get_institutions():
    """Return institution IDs and names for the dashboard selector."""
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT Institution_ID, Name
            FROM Institution
            ORDER BY Name
        """)

        return cursor.fetchall()

    except Exception as e:
        messagebox.showerror(
            "Database Error",
            f"Could not load institutions.\n\n{e}"
        )
        return []

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def get_dashboard_data(institution_id=None):
    """Calculate dashboard totals directly from the three activity tables.

    This version does not require the TOTAL_EMISSIONS view.
    """
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        dept_condition = ""
        params = {}
        if institution_id is not None:
            dept_condition = "WHERE d.Institution_ID = :institution_id"
            params = {"institution_id": institution_id}

        # Institution total = Energy + Transport + Waste
        cursor.execute(f"""
            SELECT NVL((
                SELECT SUM(e.Emission_CO2)
                FROM Energy_Consumption e
                JOIN Department d ON d.Dept_ID = e.Dept_ID
                {dept_condition}
            ), 0)
            + NVL((
                SELECT SUM(t.Emission_CO2)
                FROM Transport t
                JOIN Department d ON d.Dept_ID = t.Dept_ID
                {dept_condition}
            ), 0)
            + NVL((
                SELECT SUM(w.Emission_CO2)
                FROM Waste w
                JOIN Department d ON d.Dept_ID = w.Dept_ID
                {dept_condition}
            ), 0)
            FROM dual
        """, params)
        total_co2 = cursor.fetchone()[0] or 0

        if institution_id is None:
            cursor.execute("SELECT COUNT(*) FROM Department")
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM Department
                WHERE Institution_ID = :institution_id
            """, {"institution_id": institution_id})
        departments = cursor.fetchone()[0]

        def activity_total(table_name):
            cursor.execute(f"""
                SELECT NVL(SUM(x.Emission_CO2), 0)
                FROM {table_name} x
                JOIN Department d ON d.Dept_ID = x.Dept_ID
                {dept_condition}
            """, params)
            return cursor.fetchone()[0] or 0

        energy = activity_total("Energy_Consumption")
        transport = activity_total("Transport")
        waste = activity_total("Waste")

        return (
            float(total_co2),
            departments,
            float(energy),
            float(transport),
            float(waste)
        )

    except Exception as e:
        messagebox.showerror(
            "Database Error",
            f"Could not load dashboard data.\n\n{e}"
        )
        return 0, 0, 0, 0, 0

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ==========================================
# MODULE FUNCTIONS
# ==========================================

def institution_management():
    open_institution_management()


def department_management():
    open_department_management()


def energy_consumption():
    open_energy_management()


def transport_management():
    open_transport_management()


def waste_management():
    open_waste_management()


def emission_factors():
    open_emission_factor_management()


def reports():
    open_reports()


def exit_application():
    root.destroy()


# ==========================================
# SIDEBAR HOVER
# ==========================================

def on_enter(button):
    button.config(bg=SIDEBAR_HOVER)


def on_leave(button):
    button.config(bg=SIDEBAR_COLOR)


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("Carbon Emission Tracking System")
root.geometry("1100x700")
root.configure(bg=BG_COLOR)
root.resizable(False, False)


# ==========================================
# SIDEBAR
# ==========================================

sidebar = tk.Frame(
    root,
    bg=SIDEBAR_COLOR,
    width=250,
    height=700
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


# ==========================================
# LOGO
# ==========================================

logo_frame = tk.Frame(
    sidebar,
    bg=SIDEBAR_COLOR
)

logo_frame.pack(pady=30)

logo_icon = tk.Label(
    logo_frame,
    text="♻",
    font=("Arial", 32),
    bg=SIDEBAR_COLOR,
    fg="#8FE3CF"
)

logo_icon.pack()

logo_text = tk.Label(
    logo_frame,
    text="CarbonTrack",
    font=("Arial", 20, "bold"),
    bg=SIDEBAR_COLOR,
    fg="white"
)

logo_text.pack()

logo_subtitle = tk.Label(
    logo_frame,
    text="Emission Management",
    font=("Arial", 9),
    bg=SIDEBAR_COLOR,
    fg="#B8D4CE"
)

logo_subtitle.pack(pady=3)


# ==========================================
# SIDEBAR BUTTON
# ==========================================

def create_sidebar_button(text, command):
    button = tk.Button(
        sidebar,
        text=text,
        command=command,
        font=("Arial", 11),
        bg=SIDEBAR_COLOR,
        fg="white",
        activebackground=SIDEBAR_HOVER,
        activeforeground="white",
        bd=0,
        relief="flat",
        anchor="w",
        padx=25,
        height=2,
        cursor="hand2"
    )

    button.pack(
        fill="x",
        pady=2
    )

    button.bind(
        "<Enter>",
        lambda event: on_enter(button)
    )

    button.bind(
        "<Leave>",
        lambda event: on_leave(button)
    )

    return button


# ==========================================
# NAVIGATION BUTTONS
# ==========================================

create_sidebar_button(
    "  🏠   Dashboard",
    lambda: None
)

create_sidebar_button(
    "  🏫   Institutions",
    institution_management
)

create_sidebar_button(
    "  🏢   Departments",
    department_management
)

create_sidebar_button(
    "  ⚡   Energy Consumption",
    energy_consumption
)

create_sidebar_button(
    "  🚗   Transport Management",
    transport_management
)

create_sidebar_button(
    "  ♻   Waste Management",
    waste_management
)

create_sidebar_button(
    "  🌱   Emission Factors",
    emission_factors
)

create_sidebar_button(
    "  📊   Reports & Analytics",
    reports
)


# ==========================================
# EXIT BUTTON
# ==========================================

exit_button = tk.Button(
    sidebar,
    text="  ✕   Exit",
    command=exit_application,
    font=("Arial", 11),
    bg=SIDEBAR_COLOR,
    fg="#FFB4B4",
    activebackground=SIDEBAR_HOVER,
    activeforeground="white",
    bd=0,
    relief="flat",
    anchor="w",
    padx=25,
    height=2,
    cursor="hand2"
)

exit_button.pack(
    side="bottom",
    fill="x",
    pady=20
)


# ==========================================
# MAIN CONTENT
# ==========================================

content = tk.Frame(
    root,
    bg=BG_COLOR,
    width=850,
    height=700
)

content.pack(
    side="right",
    fill="both",
    expand=True
)


# ==========================================
# HEADER
# ==========================================

header = tk.Frame(
    content,
    bg=BG_COLOR
)

header.pack(
    fill="x",
    padx=40,
    pady=(30, 10)
)

welcome = tk.Label(
    header,
    text="Carbon Emission Dashboard",
    font=("Arial", 25, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

welcome.pack(anchor="w")

subtitle = tk.Label(
    header,
    text="Monitor and manage institutional carbon emissions",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg=SECONDARY_TEXT
)

subtitle.pack(
    anchor="w",
    pady=(5, 0)
)


# ==========================================
# INSTITUTION FILTER
# ==========================================

filter_frame = tk.Frame(
    content,
    bg=BG_COLOR
)

filter_frame.pack(
    fill="x",
    padx=40,
    pady=(8, 0)
)

filter_label = tk.Label(
    filter_frame,
    text="View Institution:",
    font=("Arial", 11, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

filter_label.pack(side="left", padx=(0, 10))

institution_combo = ttk.Combobox(
    filter_frame,
    state="readonly",
    width=35,
    font=("Arial", 10)
)

institution_combo.pack(side="left")

refresh_button = tk.Button(
    filter_frame,
    text="⟳  Refresh",
    font=("Arial", 10, "bold"),
    bg=ACCENT_COLOR,
    fg="white",
    activebackground="#246F5E",
    activeforeground="white",
    bd=0,
    padx=15,
    pady=6,
    cursor="hand2"
)

refresh_button.pack(side="left", padx=10)


# ==========================================
# DASHBOARD CARDS
# ==========================================

cards_frame = tk.Frame(
    content,
    bg=BG_COLOR
)

cards_frame.pack(
    fill="x",
    padx=40,
    pady=18
)


def create_card(parent, title, value, description):
    card = tk.Frame(
        parent,
        bg=CARD_COLOR,
        width=175,
        height=130,
        highlightbackground="#E5E7EB",
        highlightthickness=1
    )

    card.pack(
        side="left",
        padx=7,
        expand=True,
        fill="both"
    )

    card.pack_propagate(False)

    title_label = tk.Label(
        card,
        text=title,
        font=("Arial", 10),
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT
    )

    title_label.pack(
        anchor="w",
        padx=18,
        pady=(18, 3)
    )

    value_label = tk.Label(
        card,
        text=value,
        font=("Arial", 21, "bold"),
        bg=CARD_COLOR,
        fg=ACCENT_COLOR
    )

    value_label.pack(
        anchor="w",
        padx=18
    )

    desc_label = tk.Label(
        card,
        text=description,
        font=("Arial", 9),
        bg=CARD_COLOR,
        fg=SECONDARY_TEXT
    )

    desc_label.pack(
        anchor="w",
        padx=18,
        pady=3
    )


def clear_cards():
    for widget in cards_frame.winfo_children():
        widget.destroy()


def update_dashboard(event=None):
    selected = institution_combo.get()

    if not selected:
        institution_id = None
        institution_name = "All Institutions"
    elif selected == "All Institutions":
        institution_id = None
        institution_name = "All Institutions"
    else:
        institution_id = institution_map.get(selected)
        institution_name = selected

    total_co2, departments, energy, transport, waste = \
        get_dashboard_data(institution_id)

    clear_cards()

    create_card(
        cards_frame,
        "TOTAL CO₂",
        f"{total_co2:.2f} kg",
        institution_name
    )

    create_card(
        cards_frame,
        "DEPARTMENTS",
        str(departments),
        "Registered departments"
    )

    create_card(
        cards_frame,
        "ENERGY",
        f"{energy:.2f} kg",
        "Energy emissions"
    )

    create_card(
        cards_frame,
        "TRANSPORT",
        f"{transport:.2f} kg",
        "Transport emissions"
    )

    create_card(
        cards_frame,
        "WASTE",
        f"{waste:.2f} kg",
        "Waste emissions"
    )


# ==========================================
# LOAD INSTITUTIONS
# ==========================================

institution_rows = get_institutions()

institution_map = {}

for institution_id, institution_name in institution_rows:
    institution_map[institution_name] = institution_id

institution_names = ["All Institutions"] + list(institution_map.keys())

institution_combo["values"] = institution_names
institution_combo.set("All Institutions")
institution_combo.bind(
    "<<ComboboxSelected>>",
    update_dashboard
)

refresh_button.config(
    command=update_dashboard
)


# ==========================================
# INITIAL DASHBOARD
# ==========================================

update_dashboard()


# ==========================================
# QUICK ACTIONS
# ==========================================

quick_title = tk.Label(
    content,
    text="Quick Actions",
    font=("Arial", 17, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

quick_title.pack(
    anchor="w",
    padx=40,
    pady=(5, 15)
)

quick_frame = tk.Frame(
    content,
    bg=BG_COLOR
)

quick_frame.pack(
    fill="x",
    padx=40
)


def create_action_button(parent, text, command):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        activebackground="#E8F5F1",
        activeforeground=ACCENT_COLOR,
        bd=1,
        relief="solid",
        cursor="hand2",
        width=22,
        height=3
    )

    return button


# ==========================================
# QUICK ACTION ROW 1
# ==========================================

create_action_button(
    quick_frame,
    "🏫  Add Institution",
    institution_management
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)

create_action_button(
    quick_frame,
    "🏢  Manage Departments",
    department_management
).grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)

create_action_button(
    quick_frame,
    "⚡  Add Energy Data",
    energy_consumption
).grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)


# ==========================================
# QUICK ACTION ROW 2
# ==========================================

create_action_button(
    quick_frame,
    "📊  View Reports",
    reports
).grid(
    row=1,
    column=0,
    padx=5,
    pady=15
)

create_action_button(
    quick_frame,
    "🚗  Add Transport Data",
    transport_management
).grid(
    row=1,
    column=1,
    padx=5,
    pady=15
)

create_action_button(
    quick_frame,
    "♻  Add Waste Data",
    waste_management
).grid(
    row=1,
    column=2,
    padx=5,
    pady=15
)


# ==========================================
# FOOTER
# ==========================================

footer = tk.Label(
    content,
    text="Carbon Emission Tracking System  •  Oracle Database + Python Tkinter",
    font=("Arial", 9),
    bg=BG_COLOR,
    fg="#9CA3AF"
)

footer.pack(
    side="bottom",
    pady=20
)


# ==========================================
# START APPLICATION

root.mainloop()
