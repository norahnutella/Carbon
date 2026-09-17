import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from ui import BG, WHITE, TEXT, SECONDARY, ACCENT, DANGER, responsive_window, make_scrollable_table
from validators import is_valid_date, is_positive_number

def open_waste_management():
    window=tk.Toplevel(); window.title("Waste Management"); window.configure(bg=BG)
    responsive_window(window,950,650,760,540)

    institution_var=tk.StringVar()
    dept_var=tk.StringVar(); date_var=tk.StringVar(); type_var=tk.StringVar()
    qty_var=tk.StringVar(); unit_var=tk.StringVar(); disposal_var=tk.StringVar()
    emission_var=tk.StringVar()
    institution_map={}; dept_map={}

    tk.Label(window,text="♻ Waste Management",font=("Arial",20,"bold"),bg=BG,fg=TEXT).pack(pady=(18,3))
    tk.Label(window,text="Record and monitor waste generation",font=("Arial",9),bg=BG,fg=SECONDARY).pack(pady=(0,12))

    form=tk.Frame(window,bg=WHITE,bd=1,relief="solid"); form.pack(fill="x",padx=25)

    entries=[
        ("Institution",0,0),("Department",0,1),
        ("Date (YYYY-MM-DD)",2,0),("Waste Type",2,1),
        ("Quantity",4,0),("Unit",4,1),
        ("Disposal Method",6,0),("CO₂ Emission (kg)",6,1)
    ]
    for text,r,c in entries:
        tk.Label(form,text=text,bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=r,column=c,padx=12,pady=(7,2),sticky="w")

    institution_box=ttk.Combobox(form,textvariable=institution_var,state="readonly",width=29)
    institution_box.grid(row=1,column=0,padx=12,pady=(0,7),sticky="ew")
    dept_box=ttk.Combobox(form,textvariable=dept_var,state="readonly",width=29)
    dept_box.grid(row=1,column=1,padx=12,pady=(0,7),sticky="ew")
    tk.Entry(form,textvariable=date_var,width=32).grid(row=3,column=0,padx=12,pady=(0,7),sticky="ew")
    type_box=ttk.Combobox(form,textvariable=type_var,values=["Organic","Plastic","Paper"],state="readonly",width=29)
    type_box.grid(row=3,column=1,padx=12,pady=(0,7),sticky="ew")
    tk.Entry(form,textvariable=qty_var,width=32).grid(row=5,column=0,padx=12,pady=(0,7),sticky="ew")
    unit_box=ttk.Combobox(form,textvariable=unit_var,values=["kg"],state="readonly",width=29)
    unit_box.grid(row=5,column=1,padx=12,pady=(0,7),sticky="ew")
    disposal_box=ttk.Combobox(form,textvariable=disposal_var,values=["Recycling","Composting","Landfill","Incineration"],state="readonly",width=29)
    disposal_box.grid(row=7,column=0,padx=12,pady=(0,7),sticky="ew")
    tk.Entry(form,textvariable=emission_var,state="readonly",width=32).grid(row=7,column=1,padx=12,pady=(0,7),sticky="ew")
    date_var.set("2026-09-14")

    def load_departments(*_):
        nonlocal dept_map
        dept_map={}
        dept_var.set("")
        dept_box["values"]=[]
        if not institution_var.get() or institution_var.get() not in institution_map:
            return
        institution_id=institution_map[institution_var.get()]
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute(
                "SELECT dept_id,dept_name FROM department WHERE institution_id=:1 ORDER BY dept_name",
                (institution_id,)
            )
            vals=[]
            for did,name in cur.fetchall():
                s=f"{name} (ID {did})"; dept_map[s]=did; vals.append(s)
            dept_box["values"]=vals
            if vals: dept_box.current(0)
        except Exception as e: messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def load_institutions():
        nonlocal institution_map
        institution_map={}
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute("SELECT institution_id,name FROM institution ORDER BY name")
            vals=[]
            for iid,name in cur.fetchall():
                s=f"{name} (ID {iid})"; institution_map[s]=iid; vals.append(s)
            institution_box["values"]=vals
            if vals:
                institution_box.current(0)
                load_departments()
        except Exception as e: messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    institution_box.bind("<<ComboboxSelected>>", load_departments)

    def fid():
        return {"Organic":6,"Plastic":7,"Paper":8}.get(type_var.get())

    def calculate():
        try:
            q=float(qty_var.get()); factor_id=fid()
            if q<0 or factor_id is None: raise ValueError
            con=get_connection(); cur=con.cursor()
            cur.execute("SELECT factor_value FROM emission_factor WHERE factor_id=:1",(factor_id,))
            factor=cur.fetchone()[0]
            emission_var.set(f"{q*float(factor):.2f}")
            cur.close(); con.close()
        except Exception:
            messagebox.showerror("Invalid Input","Enter a valid quantity and waste type.")

    def clear():
        date_var.set("2026-09-14"); type_var.set(""); qty_var.set(""); unit_var.set("")
        disposal_var.set(""); emission_var.set("")
        if dept_box["values"]: dept_box.current(0)

    def load():
        for item in tree.get_children(): tree.delete(item)
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute("""
                SELECT waste_id,d.dept_name,TO_CHAR(activity_date,'YYYY-MM-DD'),
                       waste_type,quantity,unit,disposal_method,emission_co2
                FROM waste w
                JOIN department d ON d.dept_id=w.dept_id
                ORDER BY waste_id
            """)
            for row in cur.fetchall(): tree.insert("", "end", values=row)
        except Exception as e: messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def add():
        con=cur=None
        try:
            if not institution_var.get():
                messagebox.showwarning("Missing Information","Please select an institution."); return
            if not dept_var.get():
                messagebox.showwarning("Missing Information","Please select a department."); return
            if not is_valid_date(date_var.get()):
                messagebox.showerror("Invalid Date","Please enter a valid date in YYYY-MM-DD format (e.g. 2026-09-14)."); return
            if not type_var.get():
                messagebox.showwarning("Missing Information","Please select a waste type."); return
            if not is_positive_number(qty_var.get()):
                messagebox.showerror("Invalid Quantity","Quantity must be a number greater than 0."); return
            if not unit_var.get():
                messagebox.showwarning("Missing Information","Please select a unit."); return
            if not disposal_var.get():
                messagebox.showwarning("Missing Information","Please select a disposal method."); return

            q=float(qty_var.get()); factor_id=fid()
            con=get_connection(); cur=con.cursor()
            cur.execute("SELECT NVL(MAX(waste_id),0)+1 FROM waste")
            wid=cur.fetchone()[0]
            cur.execute("""
                INSERT INTO waste
                (waste_id,dept_id,factor_id,activity_date,waste_type,quantity,unit,disposal_method)
                VALUES (:1,:2,:3,TO_DATE(:4,'YYYY-MM-DD'),:5,:6,:7,:8)
            """,(wid,dept_map[dept_var.get()],factor_id,date_var.get(),type_var.get(),q,unit_var.get(),disposal_var.get()))
            con.commit()
            cur.execute("SELECT emission_co2 FROM waste WHERE waste_id=:1",(wid,))
            emission=cur.fetchone()[0]
            messagebox.showinfo("Success",f"Waste record added.\nCO₂ Emission: {float(emission):.2f} kg")
            clear(); load()
        except ValueError: messagebox.showerror("Invalid Input","Please complete all fields correctly.")
        except Exception as e:
            if con: con.rollback()
            messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    def delete():
        sel=tree.selection()
        if not sel: messagebox.showwarning("Select Record","Please select a waste record."); return
        wid=tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm Delete",f"Delete Waste ID {wid}?"): return
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor(); cur.execute("DELETE FROM waste WHERE waste_id=:1",(wid,))
            con.commit(); load()
        except Exception as e:
            if con: con.rollback()
            messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    buttons=tk.Frame(window,bg=BG); buttons.pack(pady=8)
    for text,cmd,color in [("Calculate CO₂",calculate,ACCENT),("Add Waste",add,"#163A35"),("Delete Selected",delete,DANGER),("Clear",clear,"#6B7280")]:
        tk.Button(buttons,text=text,command=cmd,width=14,height=1,bg=color,fg="white",bd=0,font=("Arial",9,"bold"),cursor="hand2").pack(side="left",padx=4)

    frame,tree=make_scrollable_table(window,("ID","Department","Date","Type","Quantity","Unit","Disposal","CO₂ (kg)"),
        {"ID":50,"Department":170,"Date":95,"Type":100,"Quantity":80,"Unit":65,"Disposal":120,"CO₂ (kg)":90},8)
    frame.pack(fill="both",expand=True,padx=25,pady=(0,18))
    load_institutions(); load()
