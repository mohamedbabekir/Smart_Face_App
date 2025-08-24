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

**How to use (simple)**

1. **Open the app** (`python app.py`).
2. **Sign Up / Register Face**

   * Enter **Name** and **Student ID**, choose **Department**.
   * Click **Register Face** and look at the camera to save 10–20 photos.
3. **Login**

   * Enter **Name** and **Student ID**, choose **Department**.
   * Click **Go**. If your face matches, you’ll proceed.
4. **Take Attendance**

   * Pick the **Subject** and click **Take Attendance**.
   * Wait for the face check to finish; you’ll get a success message.
5. **Admin (optional)**

   * Open **Admin** to see the attendance table (test login: `admin / 123`).
6. **Where it saves**

   * Face photos: `images-log/`
   * Attendance file: `attendance.csv`

Created By:
**Mohamed Babiker Osman**
**Wadbabiker59@gmail.com**

