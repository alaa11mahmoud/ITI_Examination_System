import tkinter as tk
from tkinter import messagebox, filedialog
import pyodbc

# اتصال بقاعدة البيانات
conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-I2AHNV0;'
    'DATABASE=ITI_System;'
    'Trusted_Connection=yes;')
cursor = conn.cursor()

# النافذة الرئيسية
root = tk.Tk()
root.title("Exam System")
root.state('zoomed')  # تكبير النافذة تلقائيًا
root.configure(bg="#E8F0FE")  # لون الخلفية

button_font = ("Arial", 20, "bold")
label_font = ("Arial", 16)

# ============================ الطالب ============================
def open_student_menu():
    clear_window()
    tk.Label(root, text="Welcome Student!", font=button_font, bg="#E8F0FE").pack(pady=40)
    tk.Button(root, text="Login", font=button_font, width=20, command=open_student_login).pack(pady=20)
    tk.Button(root, text="Register", font=button_font, width=20, command=open_student_register).pack(pady=20)

def open_student_register():
    clear_window()
    tk.Label(root, text="Student Registration", font=button_font, bg="#E8F0FE").pack(pady=20)

    labels = ["Name", "Email", "Password", "Faculty", "GPA", "Phone", "City","Gender"]
    entries = []

    for i, lbl in enumerate(labels):
        tk.Label(root, text=lbl + ":", font=label_font, bg="#E8F0FE").pack()
        ent = tk.Entry(root, font=label_font)
        ent.pack()
        entries.append(ent)

    def register():
        values = [e.get() for e in entries]
        cursor.execute("""
            EXEC ins_stu @Student_name =?, @Email =?, @Password =?, @Faculty =?, @GPA=?, @Phone =?, @City=?,@Gender=?
        """, values)
        result = cursor.fetchone()
        conn.commit()
        messagebox.showinfo("Registered", f"Your ID: {result[0]}\nYour Password: {result[1]}")
        open_student_menu()

    tk.Button(root, text="Submit", font=label_font, command=register).pack(pady=20)

def open_student_login():
    clear_window()
    tk.Label(root, text="Student Login", font=button_font, bg="#E8F0FE").pack(pady=20)

    tk.Label(root, text="Student ID:", font=label_font, bg="#E8F0FE").pack()
    id_entry = tk.Entry(root, font=label_font)
    id_entry.pack()

    tk.Label(root, text="Password:", font=label_font, bg="#E8F0FE").pack()
    pass_entry = tk.Entry(root, show="*", font=label_font)
    pass_entry.pack()

    def login():
        cursor.execute("SELECT * FROM Student WHERE Student_ID=? AND Password=?",
                       id_entry.get(), pass_entry.get())
        if cursor.fetchone():
            open_exam_entry_page(int(id_entry.get()))
        else:
            messagebox.showerror("Error", "Invalid credentials")

    tk.Button(root, text="Login", font=label_font, command=login).pack(pady=20)

# ============================ المدرس ============================
def open_instructor_menu():
    clear_window()
    tk.Label(root, text="Welcome Instructor!", font=button_font, bg="#E8F0FE").pack(pady=40)
    tk.Button(root, text="Show Available Questions", font=button_font, width=25, command=show_available_questions).pack(pady=20)
    tk.Button(root, text="Create Random Exam", font=button_font, width=25, command=create_random_exam).pack(pady=20)
    tk.Button(root, text="View Exam Questions", font=button_font, width=25, command=view_exam_questions).pack(pady=20)
    tk.Button(root, text="Export Exam to Text File", font=button_font, width=25, command=export_exam_to_file).pack(pady=20)

def open_instructor_login_register():
    clear_window()
    tk.Label(root, text="Instructor Portal", font=button_font, bg="#E8F0FE").pack(pady=40)
    tk.Button(root, text="Login", font=button_font, width=20, command=open_instructor_login).pack(pady=20)
    tk.Button(root, text="Register", font=button_font, width=20, command=open_instructor_register).pack(pady=20)

def open_instructor_register():
    clear_window()
    tk.Label(root, text="Instructor Registration", font=button_font, bg="#E8F0FE").pack(pady=20)

    labels = ["Name", "Email",  "Faculty",  "Phone", "City","Gender"]
    entries = []

    for lbl in labels:
        tk.Label(root, text=lbl + ":", font=label_font, bg="#E8F0FE").pack()
        ent = tk.Entry(root, font=label_font)
        ent.pack()
        entries.append(ent)

    def register():
        values = [e.get() for e in entries]
        cursor.execute("""
            EXEC ins_instruc @ins_name =?, @Email =?,  @Faculty =?, @Phone =?, @City =?, @Gender =?
        """, values)
        result = cursor.fetchone()
        conn.commit()
        messagebox.showinfo("Registered", f"Your ID: {result[0]}")
        open_instructor_login_register()

    tk.Button(root, text="Submit", font=label_font, command=register).pack(pady=20)

def open_instructor_login():
    clear_window()
    tk.Label(root, text="Instructor Login", font=button_font, bg="#E8F0FE").pack(pady=20)

    tk.Label(root, text="Instructor ID:", font=label_font, bg="#E8F0FE").pack()
    id_entry = tk.Entry(root, font=label_font)
    id_entry.pack()

    def login():
        global instructor_id
        instructor_id = int(id_entry.get())
        cursor.execute("SELECT * FROM Instructor WHERE Instructor_ID=?", instructor_id)
        if cursor.fetchone():
            open_instructor_menu()
        else:
            messagebox.showerror("Error", "Invalid ID")

    tk.Button(root, text="Login", font=label_font, command=login).pack(pady=20)

# عرض جميع الأسئلة المتاحة مع شريط تمرير
def show_available_questions():
    clear_window()
    tk.Label(root, text="Available Questions", font=button_font, bg="#E8F0FE").pack(pady=20)

    cursor.execute("EXEC ins_show_question ?", instructor_id)
    questions = cursor.fetchall()
    conn.commit()


    # إطار لاحتواء canvas و scrollbar
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame, bg="#E8F0FE")
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#E8F0FE")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for q in questions:
        text = f"ID: {q[0]}\nQ: {q[1]}\nA: {q[2]}  B: {q[3]}  C: {q[4]}  D: {q[5]}\nAnswer: {q[6]}"
        tk.Label(scrollable_frame, text=text, font=label_font, bg="#E8F0FE", anchor="w", justify="left").pack(pady=10, fill="x")

    tk.Button(root, text="Back", font=label_font, command=open_instructor_menu).pack(pady=20)

# زر إنشاء امتحان عشوائي
def create_random_exam():
    clear_window()
    tk.Label(root, text="Create Random Exam", font=button_font, bg="#E8F0FE").pack(pady=20)

    tk.Label(root, text="Number of True/False Questions:", font=label_font, bg="#E8F0FE").pack()
    tf_entry = tk.Entry(root, font=label_font)
    tf_entry.pack()

    tk.Label(root, text="Number of MCQ Questions:", font=label_font, bg="#E8F0FE").pack()
    mcq_entry = tk.Entry(root, font=label_font)
    mcq_entry.pack()

    tk.Label(root, text="Total Exam Grade:", font=label_font, bg="#E8F0FE").pack()
    grade_entry = tk.Entry(root, font=label_font)
    grade_entry.pack()

    def create():
        tf = int(tf_entry.get())
        mcq = int(mcq_entry.get())
        grade = int(grade_entry.get())
        exam_id = None
        try:
            cursor.execute("EXEC sp_CreateExam ?, ?, ?, ? ", instructor_id, tf, mcq, grade)
            exam_id = cursor.fetchone()[0]
            conn.commit()
            messagebox.showinfo("Success", f"Exam created with ID: {exam_id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Create Exam", font=label_font, command=create).pack(pady=20)
    tk.Button(root, text="Back", font=label_font, command=open_instructor_menu).pack(pady=10)

# عرض أسئلة الامتحان الحالي
def view_exam_questions():
    clear_window()
    tk.Label(root, text="View Exam Questions", font=button_font, bg="#E8F0FE").pack(pady=20)

    tk.Label(root, text="Enter Exam ID:", font=label_font, bg="#E8F0FE").pack()
    exam_id_entry = tk.Entry(root, font=label_font)
    exam_id_entry.pack()

    def show():
        exam_id = int(exam_id_entry.get())
        cursor.execute("EXEC show_q ?, ?", instructor_id, exam_id)
        questions = cursor.fetchall()
        conn.commit()


        for q in questions:
            tk.Label(root, text=f"ID: {q[0]}\nQ: {q[1]}\nA: {q[2]}  B: {q[3]}  C: {q[4]}  D: {q[5]}\nAnswer: {q[6]}", font=label_font, bg="#E8F0FE", anchor="w", justify="left").pack(pady=10)

    tk.Button(root, text="Show Questions", font=label_font, command=show).pack(pady=20)
    tk.Button(root, text="Back", font=label_font, command=open_instructor_menu).pack(pady=10)

# تصدير الامتحان لملف نصي
def show_exam_question(exam_id, student_id, q):
    clear_window()

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg="#E8F0FE")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = tk.Frame(canvas, bg="#E8F0FE")
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    # عرض السؤال داخل scrollable_frame بدل root
    tk.Label(scrollable_frame, text=q.question, font=button_font, bg="#E8F0FE").pack(pady=20)

    answer_var = tk.StringVar()
    options = [q.a, q.b, q.c, q.d]
    labels = ['A', 'B', 'C', 'D']

    for i in range(4):
        tk.Radiobutton(scrollable_frame, text=f"{labels[i]}) {options[i]}", variable=answer_var, value=labels[i], font=label_font, bg="#E8F0FE").pack(anchor="w")

    def next_question():
        answer = answer_var.get()
        cursor.execute("EXEC check_eachQ ?, ?, ?", student_id, exam_id, answer)
        row = cursor.fetchone()
        conn.commit()

        if row and row[0] == 'Finish Exam':
            show_result(student_id, exam_id)
        elif row:
            show_exam_question(exam_id, student_id, row)

    tk.Button(scrollable_frame, text="Next", font=label_font, command=next_question).pack(pady=20)



# ============================ صفحة دخول الامتحان ============================
def open_exam_entry_page(student_id):
    clear_window()
    tk.Label(root, text="Enter Exam ID:", font=label_font, bg="#E8F0FE").pack(pady=20)
    exam_entry = tk.Entry(root, font=label_font)
    exam_entry.pack(pady=10)

    def start_exam():
        exam_id = int(exam_entry.get())
        try:
            cursor.execute("EXEC show_first_question ?, ?", exam_id, student_id)
            row = cursor.fetchone()
            conn.commit()

            if row:
                show_exam_question(exam_id, student_id, row)
            else:
                messagebox.showinfo("Info", "You have already taken this exam or it is empty.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Start Exam", font=label_font, command=start_exam).pack(pady=20)

# ============================ صفحة عرض سؤال الامتحان ============================
def show_exam_question(exam_id, student_id, q):
    clear_window()
    tk.Label(root, text=q.question, font=button_font, bg="#E8F0FE").pack(pady=20)

    answer_var = tk.StringVar()
    options = [q.a, q.b, q.c, q.d]
    labels = ['A', 'B', 'C', 'D']

    for i in range(4):
        tk.Radiobutton(root, text=f"{labels[i]}) {options[i]}", variable=answer_var, value=labels[i], font=label_font, bg="#E8F0FE").pack(anchor="w")

    def next_question():
        answer = answer_var.get()
        cursor.execute("EXEC check_eachQ ?, ?, ?", student_id, exam_id, answer)
        row = cursor.fetchone()
        conn.commit()
        if row and row[0] == 'Finish Exam':
            show_result(student_id, exam_id)
        elif row:
            show_exam_question(exam_id, student_id, row)

    tk.Button(root, text="Next", font=label_font, command=next_question).pack(pady=20)

# ============================ عرض النتيجة ============================
def show_result(student_id, exam_id):
    clear_window()
    cursor.execute("EXEC Correct_Student_Exam @ExamID =?, @StudentID =?", exam_id,student_id)
    correct = cursor.fetchone()[0]
    conn.commit()


    tk.Label(root, text=f"Exam Result : {correct}", font=button_font, bg="#E8F0FE").pack(pady=40)

    tk.Button(root, text="Back to Menu", font=label_font, command=open_student_menu).pack(pady=30)

# ============================ الأدوات المساعدة ============================
def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# ============================ الصفحة الأولى ============================
tk.Label(root, text="Are you a Student or Instructor?", font=button_font, bg="#E8F0FE").pack(pady=80)
tk.Button(root, text="Student", font=button_font, bg="#4CAF50", fg="white", width=15, height=2, command=open_student_menu).pack(pady=20)
tk.Button(root, text="Instructor", font=button_font, bg="#2196F3", fg="white", width=15, height=2, command=open_instructor_login_register).pack(pady=20)

root.mainloop()
