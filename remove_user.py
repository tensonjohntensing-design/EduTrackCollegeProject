import sqlite3

def delete_user(username):
    conn = sqlite3.connect('college.db')
    c = conn.cursor()
    
    # Delete the user with the matching username
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    
    # Check if a user was actually found and deleted
    if c.rowcount > 0:
        print(f"Success: User '{username}' has been completely removed.")
    else:
        print(f"Error: User '{username}' was not found in the database.")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        delete_user(sys.argv[1])
    else:
        print("--- Remove User from EduTrack ---")
        u = input("Enter username to remove: ").strip()
        if u:
            delete_user(u)
        else:
            print("No username entered.")