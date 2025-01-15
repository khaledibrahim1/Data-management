import pymysql
import pandas as pd
from tkinter import Tk, filedialog, messagebox, Entry, Button, Label, Listbox
from tkinter.ttk import Treeview, Notebook, Frame
import ttkbootstrap as tb
import os

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from tkinter import Listbox



# وظيفة لتحميل ملف Excel وإدخال البيانات في قاعدة البيانات
def load_file():
    file_path = filedialog.askopenfilename(title="اختر ملف Excel", filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        messagebox.showerror("خطأ", "لم يتم اختيار أي ملف!")
        return

    try:
        df = pd.read_excel(file_path, header=3)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        db_connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="12111",
            database="products_db"
        )
        cursor = db_connection.cursor()

        table_name = os.path.splitext(os.path.basename(file_path))[0]

        columns = df.columns
        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ("
        create_table_query += ", ".join([f"`{column}` VARCHAR(255)" for column in columns]) + ")"
        cursor.execute(create_table_query)

        for _, row in df.iterrows():
            values = [None if pd.isna(value) else value for value in row]
            insert_query = f"INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in columns])}) VALUES ({', '.join(['%s'] * len(values))})"
            cursor.execute(insert_query, values)

        db_connection.commit()
        messagebox.showinfo("نجاح", "تمت إضافة البيانات بنجاح!")
        cursor.close()
        db_connection.close()
        display_data(table_name)
        update_table_list()
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {e}")

# وظيفة لتحديث قائمة الجداول الجانبية
def update_table_list():
    try:
        db_connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="12111",
            database="products_db"
        )
        cursor = db_connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        table_listbox.delete(0, "end")
        for table in tables:
            table_listbox.insert("end", table)

        cursor.close()
        db_connection.close()
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {e}")

# وظيفة لعرض البيانات عند تحديد جدول
def on_table_select(event):
    try:
        selected_table = table_listbox.get(table_listbox.curselection())
        display_data(selected_table)
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {e}")

# وظيفة لعرض البيانات في الواجهة
def display_data(table_name):
    try:
        db_connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="12111",
            database="products_db"
        )
        cursor = db_connection.cursor()
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        tree.delete(*tree.get_children())
        tree['columns'] = columns

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for row in rows:
            tree.insert("", "end", values=row)

        cursor.close()
        db_connection.close()
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {e}")

# وظيفة لعرض نافذة تحديث البيانات
def edit_selected_row():
    try:
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')

        edit_window = tb.Toplevel(root)
        edit_window.title("تحديث البيانات")

        entry_widgets = []
        for i, col in enumerate(tree['columns']):
            Label(edit_window, text=col).grid(row=i, column=0)
            entry = Entry(edit_window)
            entry.insert(0, values[i])
            entry.grid(row=i, column=1)
            entry_widgets.append(entry)

        def save_changes():
            new_values = [entry.get() for entry in entry_widgets]
            selected_table = table_listbox.get(table_listbox.curselection())
            db_connection = pymysql.connect(
                
            )
            cursor = db_connection.cursor()
            set_clause = ", ".join([f"`{col}` = %s" for col in tree['columns']])
            update_query = f"UPDATE `{selected_table}` SET {set_clause} WHERE `{tree['columns'][0]}` = %s"
            cursor.execute(update_query, new_values + [values[0]])
            db_connection.commit()
            cursor.close()
            db_connection.close()
            messagebox.showinfo("نجاح", "تم تحديث البيانات بنجاح!")
            display_data(selected_table)
            edit_window.destroy()

        Button(edit_window, text="حفظ التغييرات", command=save_changes).grid(row=len(tree['columns']), columnspan=2)
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {e}")



def add_new_data():
    try:
        selected_table = table_listbox.get(table_listbox.curselection())
        
        # فتح نافذة جديدة لإدخال البيانات
        add_window = tb.Toplevel(root)
        add_window.title("إضافة بيانات جديدة")
        
        entry_widgets = []
        
        # الحصول على أسماء الأعمدة من الجدول
        db_connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="12111",
            database="products_db"
        )
        cursor = db_connection.cursor()
        cursor.execute(f"DESCRIBE `{selected_table}`")
        columns = [column[0] for column in cursor.fetchall()]
        cursor.close()
        db_connection.close()
        
        # إضافة حقول الإدخال بناءً على الأعمدة
        for i, col in enumerate(columns):
            Label(add_window, text=col).grid(row=i, column=0)
            entry = Entry(add_window)
            entry.grid(row=i, column=1)
            entry_widgets.append(entry)
        
        # دالة لحفظ البيانات المدخلة في قاعدة البيانات
        def save_data():
            new_values = [entry.get() for entry in entry_widgets]
            db_connection = pymysql.connect(
                host="localhost",
                port=3306,
                user="root",
                password="12111",
                database="products_db"
            )
            cursor = db_connection.cursor()
            insert_query = f"INSERT INTO `{selected_table}` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(new_values))})"
            cursor.execute(insert_query, new_values)
            db_connection.commit()
            cursor.close()
            db_connection.close()
            messagebox.showinfo("نجاح", "تم إضافة البيانات بنجاح!")
            display_data(selected_table)
            add_window.destroy()

        # إضافة زر لحفظ البيانات
        Button(add_window, text="إضافة البيانات", command=save_data).grid(row=len(columns), columnspan=2)
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {e}")














# وظيفة لإنشاء جدول جديد
def create_new_table():
    def save_table():
        table_name = table_name_entry.get()
        columns = columns_entry.get().split(",")

        if not table_name or not columns:
            messagebox.showerror("خطأ", "يرجى إدخال اسم الجدول والأعمدة!")
            return

        try:
            db_connection = pymysql.connect(
                host="localhost",
                port=3306,
                user="root",
                password="12111",
                database="products_db"
            )
            cursor = db_connection.cursor()
            create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ("
            create_table_query += ", ".join([f"`{col.strip()}` VARCHAR(255)" for col in columns]) + ")"
            cursor.execute(create_table_query)
            db_connection.commit()
            cursor.close()
            db_connection.close()
            messagebox.showinfo("نجاح", "تم إنشاء الجدول بنجاح!")
            update_table_list()
            new_table_window.destroy()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")

    new_table_window = tb.Toplevel(root)
    new_table_window.title("إنشاء جدول جديد")

    Label(new_table_window, text="اسم الجدول:").grid(row=0, column=0, padx=10, pady=10)
    table_name_entry = Entry(new_table_window)
    table_name_entry.grid(row=0, column=1, padx=10, pady=10)

    Label(new_table_window, text="الأعمدة (مفصولة بفاصلة):").grid(row=1, column=0, padx=10, pady=10)
    columns_entry = Entry(new_table_window)
    columns_entry.grid(row=1, column=1, padx=10, pady=10)

    Button(new_table_window, text="حفظ", command=save_table).grid(row=2, columnspan=2, pady=10)










root = tb.Window(themename="superhero")
root.title("إدارة البيانات")
root.geometry("1000x700")

# دالة لتبديل الوضع المظلم
def toggle_dark_mode():
    if root.style.theme_use() == "superhero":
        root.style.theme_use("darkly")  # تغيير إلى الوضع المظلم
    else:
        root.style.theme_use("superhero")  # العودة إلى الوضع العادي

# إنشاء Notebook لعرض التبويبات
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# إنشاء الإطار الرئيسي
main_frame = ttk.Frame(notebook)
notebook.add(main_frame, text="البيانات")

# إضافة زر لتبديل الوضع المظلم
dark_mode_button = tb.Button(main_frame, text="تبديل الوضع المظلم", command=toggle_dark_mode, bootstyle="secondary")
dark_mode_button.grid(row=6, column=0, pady=10, padx=10, sticky="ew")

# إضافة زر لفتح/إغلاق القائمة الجانبية
def toggle_table_listbox():
    if table_listbox.winfo_ismapped():  # تحقق إذا كانت القائمة ظاهرة
        table_listbox.grid_forget()  # إخفاء القائمة
    else:
        table_listbox.grid(row=5, column=0, pady=10, padx=10, sticky="nsew")  # إظهار القائمة

toggle_button = tb.Button(main_frame, text="فتح/إغلاق القائمة", command=toggle_table_listbox, bootstyle="secondary")
toggle_button.grid(row=7, column=0, pady=10, padx=10, sticky="ew")

# إضافة عناصر الواجهة
load_button = tb.Button(main_frame, text="تحميل ملف Excel", command=load_file, bootstyle="success")
load_button.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

create_table_button = tb.Button(main_frame, text="إنشاء جدول جديد", command=create_new_table, bootstyle="primary")
create_table_button.grid(row=1, column=0, pady=10, padx=10, sticky="ew")


# زر إضافة بيانات جديدة
add_data_button = tb.Button(main_frame, text="إضافة بيانات جديدة", command=add_new_data, bootstyle="success")
add_data_button.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

search_label = tb.Label(main_frame, text="بحث:", bootstyle="light")
search_label.grid(row=4, column=0, pady=5, padx=10, sticky="w")

search_entry = tb.Entry(main_frame, bootstyle="light")
search_entry.grid(row=5, column=0, pady=5, padx=10, sticky="ew")

# قائمة الجداول الجانبية
table_listbox = Listbox(main_frame, height=10, bg="#2c3e50", fg="white", selectbackground="#3498db")
# سيتم إخفاء القائمة عند بدء التطبيق، ويمكن فتحها باستخدام الزر
# table_listbox.grid(row=5, column=0, pady=10, padx=10, sticky="nsew") # Uncomment to initially display the listbox
table_listbox.bind("<<ListboxSelect>>", on_table_select)
update_table_list()

# Treeview لعرض البيانات
tree = Treeview(main_frame, show="headings")
tree.grid(row=0, column=1, rowspan=6, pady=10, padx=10, sticky="nsew")
tree.bind("<Double-1>", lambda e: edit_selected_row())

# تحسين توزيع الأعمدة والصفوف
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=4)
main_frame.grid_rowconfigure(5, weight=1)

root.mainloop()
