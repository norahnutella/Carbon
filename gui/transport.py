import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from ui import BG, WHITE, TEXT, SECONDARY, ACCENT, DANGER, responsive_window, make_scrollable_table
from validators import is_valid_date, is_positive_number

def open_transport_management():
    window=tk.Toplevel(); window.title("Transport Management"); window.configure(bg=BG)
    responsive_window(window,950,650,760,540)

    institution_var=tk.StringVar()
    dept_var=tk.StringVar(); date_var=tk.StringVar(); mode_var=tk.StringVar()
    distance_var=tk.StringVar(); emission_var=tk.StringVar()
    institution_map={}; dept_map={}

    tk.Label(window,text="🚗 Transport Management",font=("Arial",20,"bold"),bg=BG,fg=TEXT).pack(pady=(18,3))
    tk.Label(window,text="Record transportation-related emissions",font=("Arial",9),bg=BG,fg=SECONDARY).pack(pady=(0,12))

    form=tk.Frame(window,bg=WHITE,bd=1,relief="solid"); form.pack(fill="x",padx=25)

    tk.Label(form,text="Institution",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=0,column=0,padx=12,pady=(8,2),sticky="w")
    tk.Label(form,text="Department",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=0,column=1,padx=12,pady=(8,2),sticky="w")
    institution_box=ttk.Combobox(form,textvariable=institution_var,state="readonly",width=29)
    institution_box.grid(row=1,column=0,padx=12,pady=(0,8),sticky="ew")
    dept_box=ttk.Combobox(form,textvariable=dept_var,state="readonly",width=29)
    dept_box.grid(row=1,column=1,padx=12,pady=(0,8),sticky="ew")

    tk.Label(form,text="Date (YYYY-MM-DD)",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=2,column=0,padx=12,pady=(2,2),sticky="w")
    tk.Label(form,text="Transport Mode",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=2,column=1,padx=12,pady=(2,2),sticky="w")
    tk.Entry(form,textvariable=date_var,width=32).grid(row=3,column=0,padx=12,pady=(0,8),sticky="ew")
    mode_box=ttk.Combobox(form,textvariable=mode_var,values=["Car","Bus","Motorcycle"],state="readonly",width=29)
    mode_box.grid(row=3,column=1,padx=12,pady=(0,8),sticky="ew")

    tk.Label(form,text="Distance (km)",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=4,column=0,padx=12,pady=(2,2),sticky="w")
    tk.Label(form,text="CO₂ Emission (kg)",bg=WHITE,fg=TEXT,font=("Arial",9,"bold")).grid(row=4,column=1,padx=12,pady=(2,2),sticky="w")
    tk.Entry(form,textvariable=distance_var,width=32).grid(row=5,column=0,padx=12,pady=(0,8),sticky="ew")
    tk.Entry(form,textvariable=emission_var,state="readonly",width=32).grid(row=5,column=1,padx=12,pady=(0,8),sticky="ew")
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
        return {"Car":3,"Bus":4,"Motorcycle":5}.get(mode_var.get())

    def calculate():
        try:
            d=float(distance_var.get()); factor_id=fid()
            if d<0 or factor_id is None: raise ValueError
            con=get_connection(); cur=con.cursor()
            cur.execute("SELECT factor_value FROM emission_factor WHERE factor_id=:1",(factor_id,))
            factor=cur.fetchone()[0]
            emission_var.set(f"{d*float(factor):.2f}")
            cur.close(); con.close()
        except Exception:
            messagebox.showerror("Invalid Input","Enter a valid distance and transport mode.")

    def clear():
        date_var.set("2026-09-14"); mode_var.set(""); distance_var.set(""); emission_var.set("")
        if dept_box["values"]: dept_box.current(0)

    def load():
        for item in tree.get_children(): tree.delete(item)
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor()
            cur.execute("""
                SELECT transport_id,d.dept_name,TO_CHAR(activity_date,'YYYY-MM-DD'),
                       transport_mode,distance_km,emission_co2
                FROM transport t
                JOIN department d ON d.dept_id=t.dept_id
                ORDER BY transport_id
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
            if not mode_var.get():
                messagebox.showwarning("Missing Information","Please select a transport mode."); return
            if not is_positive_number(distance_var.get()):
                messagebox.showerror("Invalid Distance","Distance must be a number greater than 0."); return

            distance=float(distance_var.get()); factor_id=fid()
            con=get_connection(); cur=con.cursor()
            cur.execute("SELECT NVL(MAX(transport_id),0)+1 FROM transport")
            tid=cur.fetchone()[0]
            cur.execute("""
                INSERT INTO transport
                (transport_id,dept_id,factor_id,activity_date,transport_mode,distance_km)
                VALUES (:1,:2,:3,TO_DATE(:4,'YYYY-MM-DD'),:5,:6)
            """,(tid,dept_map[dept_var.get()],factor_id,date_var.get(),mode_var.get(),distance))
            con.commit()
            cur.execute("SELECT emission_co2 FROM transport WHERE transport_id=:1",(tid,))
            emission=cur.fetchone()[0]
            messagebox.showinfo("Success",f"Transport record added.\nCO₂ Emission: {float(emission):.2f} kg")
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
        if not sel: messagebox.showwarning("Select Record","Please select a transport record."); return
        tid=tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm Delete",f"Delete Transport ID {tid}?"): return
        con=cur=None
        try:
            con=get_connection(); cur=con.cursor(); cur.execute("DELETE FROM transport WHERE transport_id=:1",(tid,))
            con.commit(); load()
        except Exception as e:
            if con: con.rollback()
            messagebox.showerror("Database Error",str(e))
        finally:
            if cur: cur.close()
            if con: con.close()

    buttons=tk.Frame(window,bg=BG); buttons.pack(pady=10)
    for text,cmd,color in [("Calculate CO₂",calculate,ACCENT),("Add Transport",add,"#163A35"),("Delete Selected",delete,DANGER),("Clear",clear,"#6B7280")]:
        tk.Button(buttons,text=text,command=cmd,width=14,height=1,bg=color,fg="white",bd=0,font=("Arial",9,"bold"),cursor="hand2").pack(side="left",padx=4)

    frame,tree=make_scrollable_table(window,("ID","Department","Date","Mode","Distance (km)","CO₂ (kg)"),
        {"ID":55,"Department":190,"Date":100,"Mode":120,"Distance (km)":110,"CO₂ (kg)":100},9)
    frame.pack(fill="both",expand=True,padx=25,pady=(0,18))
    load_institutions(); load()
