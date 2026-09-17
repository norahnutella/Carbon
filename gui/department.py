import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from ui import BG, WHITE, TEXT, SECONDARY, ACCENT, DANGER, responsive_window, make_scrollable_table
from validators import is_valid_name, is_valid_free_text

def open_department_management():
    window = tk.Toplevel()
    window.title("Department Management")
    window.configure(bg=BG)
    responsive_window(window, 950, 650, 760, 540)

    dept_name = tk.StringVar()
    location = tk.StringVar()
    head = tk.StringVar()
    institution_var = tk.StringVar()
    institution_map = {}

    tk.Label(window, text="🏢 Department Management",
             font=("Arial", 20, "bold"), bg=BG, fg=TEXT).pack(pady=(18,3))
    tk.Label(window, text="Manage departments and institution associations",
             font=("Arial", 9), bg=BG, fg=SECONDARY).pack(pady=(0,12))

    form = tk.Frame(window, bg=WHITE, bd=1, relief="solid")
    form.pack(fill="x", padx=25)

    tk.Label(form,text="Institution",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=0,column=0,padx=12,pady=(10,2),sticky="w")
    inst_box = ttk.Combobox(form,textvariable=institution_var,state="readonly",width=28)
    inst_box.grid(row=1,column=0,padx=12,pady=(0,10),sticky="ew")

    tk.Label(form,text="Department Name",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=0,column=1,padx=12,pady=(10,2),sticky="w")
    tk.Entry(form,textvariable=dept_name,width=31).grid(row=1,column=1,padx=12,pady=(0,10),sticky="ew")

    tk.Label(form,text="Location",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=2,column=0,padx=12,pady=(2,2),sticky="w")
    tk.Entry(form,textvariable=location,width=31).grid(row=3,column=0,padx=12,pady=(0,10),sticky="ew")

    tk.Label(form,text="Department Head",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=2,column=1,padx=12,pady=(2,2),sticky="w")
    tk.Entry(form,textvariable=head,width=31).grid(row=3,column=1,padx=12,pady=(0,10),sticky="ew")

    def load_institutions():
        nonlocal institution_map
        institution_map = {}
        con = cur = None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute("SELECT institution_id,name FROM institution ORDER BY name")
            names=[]
            for iid,n in cur.fetchall():
                display=f"{n} (ID {iid})"
                institution_map[display]=iid
                names.append(display)
            inst_box["values"]=names
            if names and not institution_var.get():
                inst_box.set(names[0])
        except Exception as e:
            messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def clear():
        dept_name.set(""); location.set(""); head.set("")
        if inst_box["values"]:
            inst_box.current(0)

    def load():
        for item in tree.get_children(): tree.delete(item)
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute("""
                SELECT d.dept_id,i.name,d.dept_name,d.location,d.head_name
                FROM department d
                JOIN institution i ON i.institution_id=d.institution_id
                ORDER BY d.dept_id
            """)
            for row in cur.fetchall(): tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def add():
        d_name = dept_name.get().strip()
        loc = location.get().strip()
        head_name = head.get().strip()

        if not institution_var.get():
            messagebox.showwarning("Missing Information","Please select an institution.")
            return

        if not d_name:
            messagebox.showwarning("Missing Information","Please enter a department name.")
            return

        if not is_valid_free_text(d_name, min_len=2, max_len=100):
            messagebox.showerror(
                "Invalid Department Name",
                "Department name should be 2-100 characters and may contain letters, "
                "numbers, and basic punctuation (&, ,, ., -, (), /) only."
            )
            return

        if loc and not is_valid_free_text(loc, min_len=2, max_len=100):
            messagebox.showerror(
                "Invalid Location",
                "Location should be 2-100 characters and may contain letters, numbers, "
                "and basic punctuation (&, ,, ., -, (), /) only."
            )
            return

        if head_name and not is_valid_name(head_name):
            messagebox.showerror(
                "Invalid Department Head Name",
                "Department head name should contain only letters, spaces, apostrophes, "
                "hyphens and periods (e.g. 'Dr. Maria O'Neil')."
            )
            return

        con=cur=None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute("SELECT NVL(MAX(dept_id),0)+1 FROM department")
            did=cur.fetchone()[0]
            cur.execute("""
                INSERT INTO department
                (dept_id,institution_id,dept_name,location,head_name)
                VALUES (:1,:2,:3,:4,:5)
            """,(did,institution_map[institution_var.get()],d_name,loc,head_name))
            con.commit(); messagebox.showinfo("Success","Department added successfully.")
            clear(); load()
        except Exception as e:
            if con: con.rollback()
            messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def delete():
        selected=tree.selection()
        if not selected:
            messagebox.showwarning("Select Record","Please select a department.")
            return
        did=tree.item(selected[0])["values"][0]
        if not messagebox.askyesno("Confirm Delete",f"Delete Department ID {did}?"): return
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute("DELETE FROM department WHERE dept_id=:1",(did,))
            con.commit(); load(); clear()
        except Exception as e:
            if con: con.rollback()
            messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    buttons=tk.Frame(window,bg=BG); buttons.pack(pady=12)
    for text,cmd,color in [("Add Department",add,"#163A35"),("Delete Selected",delete,DANGER),("Clear",clear,"#6B7280"),("Refresh",load,ACCENT)]:
        tk.Button(buttons,text=text,command=cmd,width=15,height=1,bg=color,fg="white",bd=0,font=("Arial",9,"bold"),cursor="hand2").pack(side="left",padx=4)

    frame,tree=make_scrollable_table(
        window,("ID","Institution","Department","Location","Head"),
        {"ID":55,"Institution":180,"Department":200,"Location":160,"Head":160},10)
    frame.pack(fill="both",expand=True,padx=25,pady=(0,20))
    load_institutions(); load()
