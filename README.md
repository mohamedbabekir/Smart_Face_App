Face Recognizer (Python + OpenCV + Tkinter)
Simple desktop app to register faces, recognize in real time, and log attendance.

Requirements:
- Python 3.8+
- A webcam
Packages: opencv-contrib-python, numpy, Pillow

**Simple install & run**

1. Install Python 3.8+ from python.org.
2. Download the project ZIP and extract it.
3. Open a terminal in the project folder.
4. Install needed packages: `pip install opencv-contrib-python numpy Pillow`

   * If Tkinter is missing (Linux): `sudo apt-get install python3-tk`
5. Run the app: `python app.py` (use `python3` on macOS/Linux if needed).
6. First time, go to **Sign Up / Register Face** and capture \~10–20 photos.
7. Then use **Login** → select **Department** and **Subject** → **Take Attendance**.
8. Results: face images in `images-log/`, attendance in `attendance.csv`.


