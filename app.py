import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Resolve paths relative to this file for reliable deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'college.db')
DATABASE_URL = os.environ.get('DATABASE_URL')

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'frontend'), static_url_path='')
CORS(app)

class DB:
    """Universal Database client that transparently supports PostgreSQL and SQLite."""
    def __init__(self):
        self.is_postgres = False
        self.conn = None
        if DATABASE_URL:
            try:
                import psycopg2
                url = DATABASE_URL
                if url.startswith("postgres://"):
                    url = url.replace("postgres://", "postgresql://", 1)
                self.conn = psycopg2.connect(url)
                self.is_postgres = True
            except Exception as e:
                print(f"[DB] PostgreSQL connection failed, falling back to SQLite: {e}")
                self.conn = sqlite3.connect(DB_PATH)
                self.is_postgres = False
        else:
            self.conn = sqlite3.connect(DB_PATH)
            self.is_postgres = False

        self.cursor = self.conn.cursor()

    def _adapt_query(self, sql):
        if self.is_postgres:
            # PostgreSQL uses %s placeholders instead of ?
            sql = sql.replace('?', '%s')
            # Handle SQLite's INSERT OR REPLACE for grid_timetable
            if "INSERT OR REPLACE INTO grid_timetable" in sql:
                sql = """
                    INSERT INTO grid_timetable (day, time_slot, subject)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (day, time_slot) DO UPDATE SET subject = EXCLUDED.subject
                """
        return sql

    def execute(self, sql, params=None):
        sql = self._adapt_query(sql)
        if params is not None:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self.cursor

    def executemany(self, sql, param_list):
        sql = self._adapt_query(sql)
        self.cursor.executemany(sql, param_list)
        return self.cursor

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
        except Exception:
            pass
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

def init_db():
    db = DB()
    if db.is_postgres:
        print("[DB] Initializing PostgreSQL database tables...")
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, 
            password TEXT, 
            role TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY, 
            date TEXT, 
            time_slot TEXT,
            subject TEXT,
            student_username TEXT, 
            status TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS marks (
            id SERIAL PRIMARY KEY, 
            student_username TEXT, 
            subject TEXT, 
            score REAL, 
            total REAL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS grid_timetable (
            day TEXT,
            time_slot TEXT,
            subject TEXT,
            PRIMARY KEY (day, time_slot)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS timetable (
            id SERIAL PRIMARY KEY,
            day TEXT,
            time TEXT,
            subject TEXT,
            room TEXT
        )''')
    else:
        print("[DB] Initializing SQLite database tables...")
        db.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            date TEXT, 
            time_slot TEXT,
            subject TEXT,
            student_username TEXT, 
            status TEXT
        )''')
        
        # Auto-migrate attendance if time_slot or subject columns are missing
        db.execute("PRAGMA table_info(attendance)")
        columns = [col[1] for col in db.fetchall()]
        if 'time_slot' not in columns:
            db.execute("ALTER TABLE attendance ADD COLUMN time_slot TEXT")
        if 'subject' not in columns:
            db.execute("ALTER TABLE attendance ADD COLUMN subject TEXT")

        db.execute('''CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            student_username TEXT, 
            subject TEXT, 
            score INTEGER, 
            total INTEGER
        )''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS grid_timetable (
            day TEXT,
            time_slot TEXT,
            subject TEXT,
            PRIMARY KEY (day, time_slot)
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS timetable
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      day TEXT,
                      time TEXT,
                      subject TEXT,
                      room TEXT)''')

    # Create default users if empty (with secure password hashes)
    db.execute("SELECT COUNT(*) FROM users")
    if db.fetchone()[0] == 0:
        db.execute("INSERT INTO users (username, password, role) VALUES ('student1', ?, 'student')", 
                  (generate_password_hash('password123'),))
        db.execute("INSERT INTO users (username, password, role) VALUES ('student2', ?, 'student')", 
                  (generate_password_hash('password123'),))
        db.execute("INSERT INTO users (username, password, role) VALUES ('teacher1', ?, 'teacher')", 
                  (generate_password_hash('admin123'),))

    # Auto-migrate any existing plaintext passwords in database to secure hashes
    db.execute("SELECT username, password FROM users")
    for row in db.fetchall():
        uname, pword = row[0], row[1]
        if not (pword.startswith('scrypt:') or pword.startswith('pbkdf2:') or pword.startswith('argon2:')):
            db.execute("UPDATE users SET password=? WHERE username=?", (generate_password_hash(pword), uname))

    # Seed grid timetable if empty
    db.execute("SELECT COUNT(*) FROM grid_timetable")
    if db.fetchone()[0] == 0:
        default_grid = [
            ('Monday', '9:00-10:00', 'Web Programming'),
            ('Monday', '10:00-11:00', 'Data Analytics'),
            ('Monday', '11:15-12:15', 'Software Engineering'),
            ('Monday', '12:15-1:15', 'Quantitative Techniques'),
            ('Monday', '2:00-3:00', 'Web Programming LAB'),
            ('Monday', '3:00-4:00', 'Web Programming LAB'),
            ('Tuesday', '9:00-10:00', 'Cryptography & Network Security'),
            ('Tuesday', '10:00-11:00', 'Web Programming'),
            ('Tuesday', '11:15-12:15', 'Data Analytics'),
            ('Tuesday', '12:15-1:15', 'Software Engineering'),
            ('Tuesday', '2:00-3:00', 'Data Analytics LAB'),
            ('Tuesday', '3:00-4:00', 'Data Analytics LAB'),
            ('Wednesday', '9:00-10:00', 'Quantitative Techniques'),
            ('Wednesday', '10:00-11:00', 'Software Engineering'),
            ('Wednesday', '11:15-12:15', 'Cryptography & Network Security'),
            ('Wednesday', '12:15-1:15', 'Web Programming'),
            ('Wednesday', '2:00-3:00', 'Project / Counseling'),
            ('Wednesday', '3:00-4:00', 'Library'),
            ('Thursday', '9:00-10:00', 'Data Analytics'),
            ('Thursday', '10:00-11:00', 'Cryptography & Network Security'),
            ('Thursday', '11:15-12:15', 'Quantitative Techniques'),
            ('Thursday', '12:15-1:15', 'Software Engineering'),
            ('Thursday', '2:00-3:00', 'Seminar'),
            ('Thursday', '3:00-4:00', 'Sports'),
            ('Friday', '9:00-10:00', 'Web Programming'),
            ('Friday', '10:00-11:00', 'Quantitative Techniques'),
            ('Friday', '11:15-12:15', 'Data Analytics'),
            ('Friday', '12:15-1:15', 'Cryptography & Network Security'),
            ('Friday', '2:00-3:00', 'Project / Counseling'),
            ('Friday', '3:00-4:00', 'Project / Counseling'),
            ('Saturday', '9:00-10:00', 'Software Engineering'),
            ('Saturday', '10:00-11:00', 'Web Programming'),
            ('Saturday', '11:15-12:15', 'Quantitative Techniques'),
            ('Saturday', '12:15-1:15', 'Remedial Class')
        ]
        db.executemany("INSERT OR REPLACE INTO grid_timetable (day, time_slot, subject) VALUES (?, ?, ?)", default_grid)

    db.commit()
    db.close()

init_db()

# --- EXISTING ROUTES ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    role = (data.get('role') or '').strip()

    db = DB()
    db.execute("SELECT username, password, role FROM users WHERE username=? AND role=?", (username, role))
    user = db.fetchone()
    db.close()

    if user and check_password_hash(user[1], password):
        return jsonify({
            "success": True, 
            "message": "Login successful!", 
            "username": user[0], 
            "role": user[2]
        }), 200
    else: 
        return jsonify({"success": False, "message": "Invalid username, password, or role."}), 401

@app.route('/api/students', methods=['GET'])
def get_students():
    db = DB()
    db.execute("SELECT username FROM users WHERE role='student' ORDER BY username ASC")
    students = [{"username": row[0]} for row in db.fetchall()]
    db.close()
    return jsonify(students), 200

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    if len(password) < 4:
        return jsonify({"success": False, "message": "Password must be at least 4 characters long."}), 400

    db = DB()
    db.execute("SELECT username FROM users WHERE username=?", (username,))
    if db.fetchone():
        db.close()
        return jsonify({"success": False, "message": f"Username '{username}' already exists!"}), 409

    hashed_pw = generate_password_hash(password)
    db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'student')", (username, hashed_pw))
    db.commit()
    db.close()
    return jsonify({"success": True, "message": f"Student '{username}' registered successfully!"}), 201

# --- USER CREDENTIAL MANAGEMENT ---
@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    current_password = data.get('current_password') or ''
    new_password = (data.get('new_password') or '').strip()

    if not username or not current_password or not new_password:
        return jsonify({"success": False, "message": "All password fields are required."}), 400

    if len(new_password) < 4:
        return jsonify({"success": False, "message": "New password must be at least 4 characters long."}), 400

    db = DB()
    db.execute("SELECT password FROM users WHERE username=?", (username,))
    row = db.fetchone()

    if not row or not check_password_hash(row[0], current_password):
        db.close()
        return jsonify({"success": False, "message": "Current password is incorrect."}), 401

    hashed_new_pw = generate_password_hash(new_password)
    db.execute("UPDATE users SET password=? WHERE username=?", (hashed_new_pw, username))
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Password updated successfully!"}), 200

# --- ATTENDANCE ROUTES ---
@app.route('/api/attendance/bulk', methods=['POST'])
def mark_bulk_attendance():
    records = request.get_json() or []
    if not isinstance(records, list) or len(records) == 0:
        return jsonify({"success": False, "message": "No attendance records provided."}), 400

    db = DB()
    count = 0
    for record in records:
        student_username = record.get('student_username')
        status = record.get('status')
        if student_username and status:
            db.execute("INSERT INTO attendance (date, time_slot, subject, student_username, status) VALUES (?, ?, ?, ?, ?)", 
                      (record.get('date'), record.get('time_slot', ''), record.get('subject', ''), student_username, status))
            count += 1
    db.commit()
    db.close()
    return jsonify({"success": True, "message": f"Successfully saved attendance for {count} student(s)!"}), 201

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json() or {}
    db = DB()
    db.execute("INSERT INTO attendance (date, time_slot, subject, student_username, status) VALUES (?, ?, ?, ?, ?)", 
              (data.get('date'), data.get('time_slot', ''), data.get('subject', ''), data.get('student_username'), data.get('status')))
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Attendance saved!"}), 201

@app.route('/api/attendance/<student_username>', methods=['GET'])
def get_student_attendance(student_username):
    db = DB()
    db.execute("SELECT date, time_slot, subject, status FROM attendance WHERE student_username=? ORDER BY date DESC, id DESC", (student_username,))
    records = [{"date": row[0], "time_slot": row[1] or '-', "subject": row[2] or '-', "status": row[3]} for row in db.fetchall()]
    db.close()
    return jsonify(records), 200

# --- MARKS ROUTES ---
@app.route('/api/marks/bulk', methods=['POST'])
def add_bulk_marks():
    records = request.get_json() or []
    if not isinstance(records, list) or len(records) == 0:
        return jsonify({"success": False, "message": "No marks records provided."}), 400

    db = DB()
    count = 0
    for record in records:
        student = record.get('student_username')
        subject = record.get('subject')
        score = record.get('score')
        total = record.get('total', 100)
        if student and subject and score is not None:
            db.execute("INSERT INTO marks (student_username, subject, score, total) VALUES (?, ?, ?, ?)", 
                      (student, subject, score, total))
            count += 1
    db.commit()
    db.close()
    return jsonify({"success": True, "message": f"Bulk marks saved for {count} entry/entries!"}), 201

@app.route('/api/marks', methods=['POST'])
def add_marks():
    data = request.get_json() or {}
    student_username = data.get('student_username')
    subject = data.get('subject')
    score = data.get('score')
    total = data.get('total', 100)

    if not student_username or not subject or score is None:
        return jsonify({"success": False, "message": "Student, subject, and score are required."}), 400

    try:
        score_val = float(score)
        total_val = float(total)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Score and total must be valid numbers."}), 400

    db = DB()
    db.execute("INSERT INTO marks (student_username, subject, score, total) VALUES (?, ?, ?, ?)", 
              (student_username, subject, score_val, total_val))
    db.commit()
    db.close()
    return jsonify({"success": True, "message": f"Marks saved for {student_username}!"}), 201

@app.route('/api/marks/<student_username>', methods=['GET'])
def get_student_marks(student_username):
    db = DB()
    db.execute("SELECT subject, score, total FROM marks WHERE student_username=? ORDER BY id DESC", (student_username,))
    records = [{"subject": row[0], "score": row[1], "total": row[2]} for row in db.fetchall()]
    db.close()
    return jsonify(records), 200

# --- GRID TIMETABLE ROUTES ---
@app.route('/api/grid-timetable', methods=['GET'])
def get_grid_timetable():
    db = DB()
    db.execute("SELECT day, time_slot, subject FROM grid_timetable")
    records = [{"day": row[0], "time_slot": row[1], "subject": row[2]} for row in db.fetchall()]
    db.close()
    return jsonify(records), 200

@app.route('/api/grid-timetable', methods=['POST'])
def update_grid_timetable():
    data = request.get_json() or {}
    day = data.get('day')
    time_slot = data.get('time_slot')
    subject = (data.get('subject') or '').strip()

    if not day or not time_slot:
        return jsonify({"success": False, "message": "Day and time_slot are required."}), 400

    db = DB()
    if subject:
        db.execute("INSERT OR REPLACE INTO grid_timetable (day, time_slot, subject) VALUES (?, ?, ?)", 
                  (day, time_slot, subject))
    else:
        db.execute("DELETE FROM grid_timetable WHERE day=? AND time_slot=?", (day, time_slot))
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Timetable updated successfully!"}), 200

# --- LEGACY TIMETABLE ROUTES ---
@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    db = DB()
    db.execute("SELECT day, time, subject, room FROM timetable")
    records = [{"day": row[0], "time": row[1], "subject": row[2], "room": row[3]} for row in db.fetchall()]
    db.close()
    return jsonify(records), 200

@app.route('/api/timetable', methods=['POST'])
def add_timetable_entry():
    data = request.get_json() or {}
    day = data.get('day')
    time = data.get('time')
    subject = data.get('subject')
    room = data.get('room')

    db = DB()
    db.execute("INSERT INTO timetable (day, time, subject, room) VALUES (?, ?, ?, ?)",
              (day, time, subject, room))
    db.commit()
    db.close()

    return jsonify({"success": True, "message": "Class added to timetable successfully!"}), 201

# --- ANALYTICS ROUTES ---
@app.route('/api/analytics/teacher', methods=['GET'])
def get_teacher_analytics():
    db = DB()

    # 1. Total student count
    db.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    total_students = db.fetchone()[0]

    # 2. Total attendance records & overall rate
    db.execute("SELECT COUNT(*), SUM(CASE WHEN LOWER(status)='present' THEN 1 ELSE 0 END) FROM attendance")
    att_row = db.fetchone()
    total_att = att_row[0] or 0
    present_att = att_row[1] or 0
    overall_rate = round((float(present_att) / float(total_att) * 100), 1) if total_att > 0 else 0

    # 3. Subject-wise attendance breakdown
    db.execute("""
        SELECT subject, 
               COUNT(*) as total_classes, 
               SUM(CASE WHEN LOWER(status)='present' THEN 1 ELSE 0 END) as present_count
        FROM attendance
        WHERE subject IS NOT NULL AND TRIM(subject) != '' AND TRIM(subject) != '-'
        GROUP BY subject
        ORDER BY total_classes DESC
    """)
    subject_stats = []
    for row in db.fetchall():
        subj, total_c, present_c = row[0], row[1], row[2] or 0
        rate = round((float(present_c) / float(total_c) * 100), 1) if total_c > 0 else 0
        subject_stats.append({
            "subject": subj,
            "total": total_c,
            "present": present_c,
            "absent": total_c - present_c,
            "rate": rate
        })

    # 4. Student attendance standing (>=75% vs <75%)
    db.execute("""
        SELECT u.username,
               COUNT(a.id) as total,
               SUM(CASE WHEN LOWER(a.status)='present' THEN 1 ELSE 0 END) as present
        FROM users u
        LEFT JOIN attendance a ON u.username = a.student_username
        WHERE u.role = 'student'
        GROUP BY u.username
        ORDER BY u.username ASC
    """)
    good_standing = 0
    shortage = 0
    student_breakdown = []
    for row in db.fetchall():
        uname = row[0]
        tot = row[1] or 0
        prs = row[2] or 0
        pct = round((float(prs) / float(tot) * 100), 1) if tot > 0 else 0.0
        status_label = "Good Standing" if pct >= 75 and tot > 0 else "Shortage Risk"
        if pct >= 75 and tot > 0:
            good_standing += 1
        else:
            shortage += 1
        student_breakdown.append({
            "username": uname,
            "total": tot,
            "present": prs,
            "absent": tot - prs,
            "percentage": pct,
            "status": status_label
        })

    # 5. Total marks records
    db.execute("SELECT COUNT(*) FROM marks")
    total_marks = db.fetchone()[0]

    # 6. Average marks by subject
    db.execute("""
        SELECT subject, AVG(score * 100.0 / total), COUNT(*)
        FROM marks
        GROUP BY subject
        ORDER BY subject ASC
    """)
    marks_by_subject = []
    for row in db.fetchall():
        marks_by_subject.append({
            "subject": row[0],
            "avg_score": round(float(row[1]), 1) if row[1] is not None else 0,
            "entries": row[2]
        })

    db.close()

    return jsonify({
        "total_students": total_students,
        "total_attendance_records": total_att,
        "overall_attendance_rate": overall_rate,
        "good_standing_count": good_standing,
        "shortage_count": shortage,
        "subject_attendance": subject_stats,
        "student_attendance": student_breakdown,
        "total_marks_records": total_marks,
        "marks_by_subject": marks_by_subject
    }), 200

if __name__ == '__main__':
    print("Starting EduTrack Server...")
    app.run(debug=True, port=5000)