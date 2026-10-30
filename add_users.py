import sqlite3
from werkzeug.security import generate_password_hash

def add_new_user(username, password, role):
    try:
        conn = sqlite3.connect('college.db')
        c = conn.cursor()
        
        # Securely hash the password before storage
        hashed_password = generate_password_hash(password)
        
        # Insert the new unique user
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  (username, hashed_password, role))
        
        conn.commit()
        print(f"Success: Created {role} account for '{username}' (password securely hashed)")
    
    except sqlite3.IntegrityError:
        print(f"Error: The username '{username}' already exists!")
    
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 4:
        add_new_user(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("--- Add New User to EduTrack ---")
        u = input("Enter username: ").strip()
        p = input("Enter password: ").strip()
        r = input("Enter role (student/teacher): ").strip().lower()
        if u and p and r in ['student', 'teacher']:
            add_new_user(u, p, r)
        else:
            print("Invalid input. Role must be 'student' or 'teacher'.")

