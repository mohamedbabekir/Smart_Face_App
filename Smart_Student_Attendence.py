import tkinter as tk
from tkinter import messagebox, ttk
import os
import cv2
import numpy as np
import csv
from datetime import datetime, timedelta
from PIL import Image, ImageTk

# ---- CONFIGURATION ----
BASE_DIR = 'images-log'
LOGO_PATH = 'al_neelain_logo.png'
ATTENDANCE_FILE = 'attendance.csv'
HAAR_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
LBPH_THRESHOLD = 50

DEPARTMENTS = [
    'Computer Engineering',
    'Chemical Engineering',
    'Control Engineering',
    'Communication Engineering'
]
SUBJECTS = [
    'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science'
]

# UI Styling
BG = '#f5f5f5'
P1 = '#004d99'  # primary blue
P2 = '#009933'  # primary green
BTN_FONT = ("Arial", 14, "bold")
LBL_FONT = ("Arial", 14)
TITLE_FONT = ("Arial", 22, "bold")
CONTACT_NAME_FONT = ("Arial", 16, "bold")
CONTACT_INFO_FONT = ("Arial", 14)

# Ensure base directories
os.makedirs(BASE_DIR, exist_ok=True)
for dept in DEPARTMENTS:
    os.makedirs(os.path.join(BASE_DIR, dept), exist_ok=True)

# ---- IMAGE CAPTURE ----
def capture_student_images(sid, dept, num_images=10):
    student_dir = os.path.join(BASE_DIR, dept, sid)
    os.makedirs(student_dir, exist_ok=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open webcam.")
        return False
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    count = 0
    window = f"Register {sid} - look at camera"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, 800, 600)
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100,100))
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_img = gray[y:y+h, x:x+w]
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            cv2.imwrite(os.path.join(student_dir, f"{sid}_{count}_{ts}.jpg"), face_img)
            count += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(frame, f"Captured {count}/{num_images}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.imshow(window, frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    if count < num_images:
        messagebox.showwarning("Incomplete", f"Only captured {count} images.")
    else:
        messagebox.showinfo("Done", f"Captured {count} images for {sid}.")
    return count == num_images

# ---- FACE VALIDATION ----
def validate_face(sid, name, dept):
    student_dir = os.path.join(BASE_DIR, dept, sid)
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    faces, labels = [], []
    for fn in os.listdir(student_dir):
        if fn.lower().endswith('.jpg'):
            img = cv2.imread(os.path.join(student_dir, fn), cv2.IMREAD_GRAYSCALE)
            if img is None: continue
            rects = face_cascade.detectMultiScale(img, 1.1, 5, minSize=(100,100))
            for (x, y, w, h) in rects:
                faces.append(img[y:y+h, x:x+w])
                labels.append(1)
    if not faces:
        messagebox.showerror("Error", "No training faces. Please re-register.")
        return False
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open webcam.")
        return False
    window = f"Verify {name}"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, 800, 600)
    verified = False
    final_frame = None
    end_time = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100,100))
        for (x, y, w, h) in rects:
            roi = gray[y:y+h, x:x+w]
            label, conf = recognizer.predict(roi)
            if label == 1 and conf < LBPH_THRESHOLD:
                if not verified:
                    verified = True
                    final_frame = frame.copy()
                    end_time = datetime.now() + timedelta(seconds=3)
                color, text = (0,255,0), name
            else:
                color, text = (0,0,255), 'Unknown'
            cv2.rectangle(frame, (x,y),(x+w,y+h), color, 2)
            cv2.putText(frame, text, (x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.imshow(window, frame)
        if verified and datetime.now() >= end_time:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return verified

# ---- APPLICATION ----
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Al Neelain University - Smart Attendance")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.current_name = self.current_id = self.current_dept = ''
        # Preload logo image
        self.logo = None
        if os.path.exists(LOGO_PATH):
            self.logo = tk.PhotoImage(file=LOGO_PATH)
        # Menu Bar
        menubar = tk.Menu(self)
        menubar.add_command(label="Home", command=lambda: self.show(Home))
        menubar.add_command(label="Contact", command=lambda: self.show(Contact))
        menubar.add_command(label="About", command=lambda: self.show(About))
        menubar.add_command(label="Admin", command=lambda: self.show(AdminLogin))
        menubar.add_command(label="Exit", command=self.destroy)
        self.config(menu=menubar)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        # Container for pages
        container = tk.Frame(self, bg=BG)
        container.pack(fill='both', expand=True)
        self.frames = {}
        for Page in (Home, Login, SignUp, Mark, Contact, About, AdminLogin, Admin):
            frame = Page(container, self)
            self.frames[Page] = frame
            frame.place(relwidth=1, relheight=1)
        self.show(Home)

    def show(self, cls):
        frame = self.frames[cls]
        if hasattr(frame, 'update_info'):
            frame.update_info()
        if hasattr(frame, 'load_data'):
            frame.load_data()
        frame.tkraise()

# ---- PAGES ----
class Home(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        if app.logo:
            tk.Label(self, image=app.logo, bg=BG).pack(pady=10)
        tk.Label(self, text="Al Neelain University", font=TITLE_FONT, bg=BG).pack(pady=20)
        tk.Button(self, text="Login", bg=P1, fg="white", font=BTN_FONT,
                  width=20, height=2, command=lambda: app.show(Login)).pack(pady=10)
        tk.Button(self, text="Sign Up", bg=P2, fg="white", font=BTN_FONT,
                  width=20, height=2, command=lambda: app.show(SignUp)).pack()

class Login(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        if app.logo:
            tk.Label(self, image=app.logo, bg=BG).pack(pady=10)
        tk.Label(self, text="Login & Verify", font=TITLE_FONT, bg=BG).pack(pady=10)
        tk.Label(self, text="Name:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.name_entry = tk.Entry(self, font=LBL_FONT); self.name_entry.pack(pady=5)
        tk.Label(self, text="ID:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.sid_entry = tk.Entry(self, font=LBL_FONT); self.sid_entry.pack(pady=5)
        tk.Label(self, text="Department:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.dept_combo = ttk.Combobox(self, values=DEPARTMENTS, state='readonly', font=LBL_FONT)
        self.dept_combo.pack(pady=5); self.dept_combo.current(0)
        tk.Button(self, text="Go", bg=P1, fg="white", font=BTN_FONT,
                  width=20, height=2, command=self.login).pack(pady=10)
        tk.Button(self, text="Back", bg=P2, fg="white", font=BTN_FONT,
                  width=20, height=2, command=lambda: app.show(Home)).pack()

    def login(self):
        name = self.name_entry.get().strip()
        sid = self.sid_entry.get().strip()
        dept = self.dept_combo.get()
        folder = os.path.join(BASE_DIR, dept, sid)
        if not os.path.isdir(folder) or not os.listdir(folder):
            return messagebox.showerror("Error", "Not registered or no images.")
        if validate_face(sid, name, dept):
            messagebox.showinfo("Success", f"Welcome {name}!")
            app = self.master.master
            app.current_name, app.current_id, app.current_dept = name, sid, dept
            app.show(Mark)
        else:
            messagebox.showerror("Error", "Face not recognized.")

class SignUp(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        if app.logo:
            tk.Label(self, image=app.logo, bg=BG).pack(pady=10)
        tk.Label(self, text="Sign Up", font=TITLE_FONT, bg=BG).pack(pady=10)
        tk.Label(self, text="Name:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.name_entry = tk.Entry(self, font=LBL_FONT); self.name_entry.pack(pady=5)
        tk.Label(self, text="ID:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.sid_entry = tk.Entry(self, font=LBL_FONT); self.sid_entry.pack(pady=5)
        tk.Label(self, text="Department:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.dept_combo = ttk.Combobox(self, values=DEPARTMENTS, state='readonly', font=LBL_FONT)
        self.dept_combo.pack(pady=5); self.dept_combo.current(0)
        tk.Button(self, text="Register Face", bg=P2, fg="white", font=BTN_FONT,
                  width=20, height=2, command=self.register).pack(pady=10)
        tk.Button(self, text="Back", bg=P1, fg="white", font=BTN_FONT,
                  width=20, height=2, command=lambda: app.show(Home)).pack()

    def register(self):
        name = self.name_entry.get().strip()
        sid = self.sid_entry.get().strip()
        dept = self.dept_combo.get()
        if not name or not sid:
            return messagebox.showerror("Error", "Fill all fields.")
        if capture_student_images(sid, dept):
            messagebox.showinfo("Success", f"Registered {name}!")
            app = self.master.master
            app.show(Home)

class Mark(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        if app.logo:
            tk.Label(self, image=app.logo, bg=BG).pack(pady=10)
        self.app = app
        tk.Label(self, text="Mark Attendance", font=TITLE_FONT, bg=BG).pack(pady=10)
        self.info_lbl = tk.Label(self, text="", font=LBL_FONT, bg=BG)
        self.info_lbl.pack(pady=5)
        tk.Label(self, text="Subject:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.subj_combo = ttk.Combobox(self, values=SUBJECTS, state='readonly', font=LBL_FONT)
        self.subj_combo.pack(pady=5); self.subj_combo.current(0)
        tk.Button(self, text="Submit", bg=P1, fg="white", font=BTN_FONT,
                  width=20, height=2, command=self.mark_att).pack(pady=10)
        tk.Button(self, text="Logout", bg=P2, fg="white", font=BTN_FONT,
                  width=20, height=2, command=lambda: app.show(Home)).pack()

    def update_info(self):
        n,i,d = self.app.current_name, self.app.current_id, self.app.current_dept
        self.info_lbl.config(text=f"{n} ({i}) - {d}")

    def mark_att(self):
        i,n,d = self.app.current_id, self.app.current_name, self.app.current_dept
        subj = self.subj_combo.get()
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new = not os.path.isfile(ATTENDANCE_FILE)
        with open(ATTENDANCE_FILE,'a',newline='') as f:
            w = csv.writer(f)
            if new: w.writerow(['ID','Name','Dept','Subject','Timestamp'])
            w.writerow([i,n,d,subj,ts])
        messagebox.showinfo("Recorded", "Attendance saved.")

class Contact(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        if app.logo:
            tk.Label(self, image=app.logo, bg=BG).pack(pady=10)
        tk.Label(self, text="Contact Us", font=TITLE_FONT, fg=P1, bg=BG).pack(pady=10)
        contacts = [
            ("Mohamed Babiker Osman", "971 58 840 2006", "wadbabiker59@gmail.com"),
            ("Mohamed Hassanin",    "249 914015230", "moh@hassanin.com"),
            ("Mohamed Ammar",       "971 56 653 48750", "amar@gmail.com")
        ]
        for name, phone, email in contacts:
            tk.Label(self, text=name,  font=CONTACT_NAME_FONT, fg=P1, bg=BG).pack(pady=2)
            tk.Label(self, text=f"Phone: {phone}", font=CONTACT_INFO_FONT, fg=P2, bg=BG).pack()
            tk.Label(self, text=f"Email: {email}", font=CONTACT_INFO_FONT, fg="#800080", bg=BG).pack(pady=(0,10))

class About(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        if app.logo:
            tk.Label(self, image=app.logo, bg=BG).pack(pady=10)
        tk.Label(self, text="About Us", font=TITLE_FONT, bg=BG).pack(pady=10)
        txt = "Smart Attendance System\nGraduation Project\nEngineering Faculty"
        tk.Label(self, text=txt, font=LBL_FONT, bg=BG, justify='center').pack(pady=20)
        quote = "\"Education is the passport to the future, for tomorrow belongs to those who prepare for it today.\""
        tk.Label(self, text=quote, font=("Arial",12,"italic"), fg="#555555", bg=BG, justify='center').pack(pady=10)
        credit_text = "Designed by: Mohamed Babiker Osman, Mohamed Hassanin, Mohamed Ammar"
        tk.Label(self, text=credit_text, font=LBL_FONT, fg=P1, bg=BG, justify='center').pack(pady=5)
        sup_text = "Supervisor: Dr. Eman Elrayah"
        tk.Label(self, text=sup_text, font=LBL_FONT, fg=P2, bg=BG, justify='center').pack(pady=5)

class AdminLogin(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        tk.Label(self, text="Admin Login", font=TITLE_FONT, bg=BG).pack(pady=10)
        tk.Label(self, text="User:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.user = tk.Entry(self, font=LBL_FONT); self.user.pack(pady=5)
        tk.Label(self, text="Pass:", font=LBL_FONT, bg=BG).pack(pady=5)
        self.pwd = tk.Entry(self, show='*', font=LBL_FONT); self.pwd.pack(pady=5)
        tk.Button(self, text="Login", bg=P1, fg="white", font=BTN_FONT,
                  width=20, height=2, command=self.login).pack(pady=10)
        tk.Button(self, text="Back", bg=P2, fg="white", font=BTN_FONT,
                  width=20, height=2, command=lambda: app.show(Home)).pack()

    def login(self):
        if self.user.get()=="admin" and self.pwd.get()=="123":
            self.app.show(Admin)
        else:
            messagebox.showerror("Error","Invalid credentials.")

class Admin(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        if app.logo:
            tk.Label(self, image=app.logo, bg=BG).pack(pady=10)
        tk.Label(self, text="Attendance Logs", font=TITLE_FONT, bg=BG).pack(pady=10)
        cols=('ID','Name','Dept','Subject','Timestamp')
        self.tree=ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        tk.Button(self, text="Refresh", bg=P2, fg="white", font=BTN_FONT,
                  width=20, height=2, command=self.load_data).pack(pady=5)
        tk.Button(self, text="Logout", bg=P1, fg="white", font=BTN_FONT,
                  width=20, height=2, command=lambda: app.show(Home)).pack(pady=5)
        self.load_data()

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        if not os.path.isfile(ATTENDANCE_FILE):
            return
        with open(ATTENDANCE_FILE, newline='') as f:
            reader=csv.reader(f); next(reader,None)
            for rec in reader:
                self.tree.insert('', 'end', values=rec)

if __name__ == '__main__':
    App().mainloop()
