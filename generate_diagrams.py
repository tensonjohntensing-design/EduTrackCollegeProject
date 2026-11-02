import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = os.path.join(os.getcwd(), 'report_assets')
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# Figure 1: 3-Tier System Architecture
# -------------------------------------------------------------
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background canvas
    fig.patch.set_facecolor('#ffffff')

    # Title
    ax.text(50, 95, "EduTrack System 3-Tier Web Architecture", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1B365D')

    # Tier 1: Presentation Layer
    p1 = patches.FancyBboxPatch((5, 68), 90, 20, boxstyle="round,pad=1.5", 
                                edgecolor='#2980b9', facecolor='#ebf5fb', linewidth=2)
    ax.add_patch(p1)
    ax.text(8, 84, "PRESENTATION TIER (Client Side - Responsive Web UI)", 
            fontsize=11, fontweight='bold', color='#1f618d')
    
    # Sub-boxes in Tier 1
    boxes_t1 = [
        ("Teacher Portal\n(Roster, Attendance,\nMarks, Grid Timetable)", 10, 70, 24, 11),
        ("Student Portal\n(Personal Stats, Doughnut\nChart, Shortage Alerts)", 38, 70, 24, 11),
        ("UI Technologies\n(HTML5, Modern CSS,\nVanilla JS, SVG Icons, Chart.js)", 66, 70, 26, 11)
    ]
    for text, x, y, w, h in boxes_t1:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", 
                                     edgecolor='#5499cd', facecolor='#ffffff', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8.5, color='#2c3e50')

    # Arrow 1 <-> 2
    ax.annotate('', xy=(50, 60), xytext=(50, 68),
                arrowprops=dict(arrowstyle="<|-|>", color='#34495e', lw=2))
    ax.text(52, 64, "HTTPS / REST JSON API Calls (Session Cookies & Auth Headers)", 
            fontsize=8.5, fontstyle='italic', color='#555555')

    # Tier 2: Application / Business Logic Layer
    p2 = patches.FancyBboxPatch((5, 36), 90, 24, boxstyle="round,pad=1.5", 
                                edgecolor='#27ae60', facecolor='#eafaf1', linewidth=2)
    ax.add_patch(p2)
    ax.text(8, 56, "APPLICATION LOGIC TIER (Python Flask Microservices & Gunicorn WSGI)", 
            fontsize=11, fontweight='bold', color='#1e8449')

    boxes_t2 = [
        ("Authentication Engine\n(PBKDF2 SHA-256 Hashing,\nSession Guards, RBAC)", 8, 39, 21, 13),
        ("Attendance Engine\n(Bulk Roster Marking,\n75% Shortage Classifier)", 30.5, 39, 20.5, 13),
        ("Academic Marks & Timetable\n(Internal Grading, Grid Scheduler,\nBatch Record Update)", 52.5, 39, 22, 13),
        ("Production WSGI / Hosting\n(Gunicorn Process Manager,\nRender Cloud Auto-Scale)", 76, 39, 17, 13)
    ]
    for text, x, y, w, h in boxes_t2:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", 
                                     edgecolor='#52be80', facecolor='#ffffff', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, color='#2c3e50')

    # Arrow 2 <-> 3
    ax.annotate('', xy=(50, 28), xytext=(50, 36),
                arrowprops=dict(arrowstyle="<|-|>", color='#34495e', lw=2))
    ax.text(52, 32, "SQL Queries / Connection Pool (psycopg2 & sqlite3)", 
            fontsize=8.5, fontstyle='italic', color='#555555')

    # Tier 3: Database & Storage Layer
    p3 = patches.FancyBboxPatch((5, 5), 90, 23, boxstyle="round,pad=1.5", 
                                edgecolor='#8e44ad', facecolor='#f4ecf7', linewidth=2)
    ax.add_patch(p3)
    ax.text(8, 24, "DATA PERSISTENCE TIER (Dual Database Engine)", 
            fontsize=11, fontweight='bold', color='#6c3483')

    boxes_t3 = [
        ("Users Table\n(id, username, password,\nrole, roll_no, name)", 8, 8, 20, 13),
        ("Attendance Table\n(id, student_id, date,\nsubject, status, time_slot)", 30, 8, 21, 13),
        ("Marks Table\n(id, student_id, subject,\ninternal_marks, max_marks)", 53, 8, 20, 13),
        ("Timetable Tables\n(grid_timetable, timetable,\nday, slot, subject, room)", 75, 8, 18, 13)
    ]
    for text, x, y, w, h in boxes_t3:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", 
                                     edgecolor='#a569bd', facecolor='#ffffff', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=7.5, color='#2c3e50')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'figure1_architecture.png'), bbox_inches='tight', dpi=300)
    plt.close()
    print("Created figure1_architecture.png")


# -------------------------------------------------------------
# Figure 2: DFD Level 0 (Context Diagram)
# -------------------------------------------------------------
def create_dfd_level0():
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    fig.patch.set_facecolor('#ffffff')

    ax.text(50, 94, "EduTrack System - DFD Level 0 (Context Analysis Diagram)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1B365D')

    # Central Process
    circ = patches.Circle((50, 50), 16, edgecolor='#1B365D', facecolor='#ebf5fb', linewidth=2.5)
    ax.add_patch(circ)
    ax.text(50, 52, "0.0\nEduTrack\nCore System", ha='center', va='center', 
            fontsize=11, fontweight='bold', color='#1B365D')

    # Entity: Student
    box_stud = patches.Rectangle((4, 38), 20, 24, edgecolor='#2980b9', facecolor='#ffffff', linewidth=2)
    ax.add_patch(box_stud)
    ax.text(14, 50, "STUDENT\n(External Entity)", ha='center', va='center', 
            fontsize=10, fontweight='bold', color='#2980b9')

    # Entity: Teacher / Faculty
    box_teach = patches.Rectangle((76, 38), 20, 24, edgecolor='#27ae60', facecolor='#ffffff', linewidth=2)
    ax.add_patch(box_teach)
    ax.text(86, 50, "TEACHER /\nFACULTY\n(External Entity)", ha='center', va='center', 
            fontsize=10, fontweight='bold', color='#27ae60')

    # Entity: Administrator
    box_admin = patches.Rectangle((40, 4), 20, 16, edgecolor='#8e44ad', facecolor='#ffffff', linewidth=2)
    ax.add_patch(box_admin)
    ax.text(50, 12, "SYSTEM ADMIN\n(Security Entity)", ha='center', va='center', 
            fontsize=9.5, fontweight='bold', color='#8e44ad')

    # Student Flows
    # Inward
    ax.annotate('', xy=(34, 55), xytext=(24, 55),
                arrowprops=dict(arrowstyle="->", color='#2980b9', lw=1.8))
    ax.text(29, 58, "Login Credentials,\nProfile Request", fontsize=7.5, ha='center', color='#333333')

    # Outward
    ax.annotate('', xy=(24, 45), xytext=(34, 45),
                arrowprops=dict(arrowstyle="->", color='#2980b9', lw=1.8))
    ax.text(29, 39, "Attendance %, Marks,\nTimetable, Warning Alerts", fontsize=7.5, ha='center', color='#333333')

    # Teacher Flows
    # Inward
    ax.annotate('', xy=(66, 55), xytext=(76, 55),
                arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.8))
    ax.text(71, 58, "Attendance Roster,\nInternal Marks, Timetable", fontsize=7.5, ha='center', color='#333333')

    # Outward
    ax.annotate('', xy=(76, 45), xytext=(66, 45),
                arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.8))
    ax.text(71, 39, "Student Analytics,\nShortage Lists, Audit Logs", fontsize=7.5, ha='center', color='#333333')

    # Admin Flows
    ax.annotate('', xy=(47, 34), xytext=(47, 20),
                arrowprops=dict(arrowstyle="->", color='#8e44ad', lw=1.8))
    ax.text(42, 27, "DB Sync / Backups", fontsize=7.5, ha='right', color='#333333')

    ax.annotate('', xy=(53, 20), xytext=(53, 34),
                arrowprops=dict(arrowstyle="->", color='#8e44ad', lw=1.8))
    ax.text(57, 27, "Health & DB Metrics", fontsize=7.5, ha='left', color='#333333')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'figure2_dfd_level0.png'), bbox_inches='tight', dpi=300)
    plt.close()
    print("Created figure2_dfd_level0.png")


# -------------------------------------------------------------
# Figure 3: DFD Level 1 (Detailed Subsystems)
# -------------------------------------------------------------
def create_dfd_level1():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(50, 95, "EduTrack System - DFD Level 1 (Decomposition Diagram)", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1B365D')

    # Entities on left and right
    stud = patches.Rectangle((2, 60), 16, 25, edgecolor='#2980b9', facecolor='#ffffff', linewidth=1.8)
    ax.add_patch(stud)
    ax.text(10, 72.5, "STUDENT\nPORTAL", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#2980b9')

    teach = patches.Rectangle((2, 15), 16, 25, edgecolor='#27ae60', facecolor='#ffffff', linewidth=1.8)
    ax.add_patch(teach)
    ax.text(10, 27.5, "TEACHER\nPORTAL", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#27ae60')

    # Processes in Middle
    procs = [
        ("1.0 Authentication &\nSession Token Guard", 35, 78, 22, 12, '#3498db'),
        ("2.0 Attendance Roster &\nDaily Log Dispatcher", 35, 56, 22, 12, '#2ecc71'),
        ("3.0 Academic Marks &\nAssessment Subsystem", 35, 34, 22, 12, '#e67e22'),
        ("4.0 Timetable Grid &\nScheduling Module", 35, 12, 22, 12, '#9b59b6')
    ]
    for text, x, y, w, h, col in procs:
        p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", 
                                   edgecolor=col, facecolor='#ffffff', linewidth=2)
        ax.add_patch(p)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, fontweight='bold', color='#2c3e50')

    # Data Stores on Right
    stores = [
        ("D1: USERS STORE\n(Credentials, Roles, Roll No)", 72, 78, 24, 11),
        ("D2: ATTENDANCE STORE\n(Date, Subject, Status, Slot)", 72, 56, 24, 11),
        ("D3: MARKS STORE\n(Subject, Marks, Max Score)", 72, 34, 24, 11),
        ("D4: TIMETABLE STORE\n(Days, Slots, Rooms, Teachers)", 72, 12, 24, 11)
    ]
    for text, x, y, w, h in stores:
        # Data store open-ended representation
        line_top = plt.Line2D([x, x+w], [y+h, y+h], color='#34495e', lw=2)
        line_bot = plt.Line2D([x, x+w], [y, y], color='#34495e', lw=2)
        ax.add_line(line_top)
        ax.add_line(line_bot)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, color='#34495e', fontweight='bold')

    # Connecting Arrows
    # Auth <-> Users
    ax.annotate('', xy=(72, 84), xytext=(57, 84), arrowprops=dict(arrowstyle="<->", color='#3498db', lw=1.5))
    # Attendance -> Store
    ax.annotate('', xy=(72, 62), xytext=(57, 62), arrowprops=dict(arrowstyle="<->", color='#2ecc71', lw=1.5))
    # Marks -> Store
    ax.annotate('', xy=(72, 40), xytext=(57, 40), arrowprops=dict(arrowstyle="<->", color='#e67e22', lw=1.5))
    # Timetable -> Store
    ax.annotate('', xy=(72, 18), xytext=(57, 18), arrowprops=dict(arrowstyle="<->", color='#9b59b6', lw=1.5))

    # Teacher to processes
    ax.annotate('', xy=(35, 62), xytext=(18, 35), arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.3))
    ax.annotate('', xy=(35, 40), xytext=(18, 27), arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.3))
    ax.annotate('', xy=(35, 18), xytext=(18, 20), arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.3))

    # Student to processes
    ax.annotate('', xy=(35, 84), xytext=(18, 75), arrowprops=dict(arrowstyle="->", color='#2980b9', lw=1.3))
    ax.annotate('', xy=(18, 68), xytext=(35, 62), arrowprops=dict(arrowstyle="<-", color='#2980b9', lw=1.3))
    ax.annotate('', xy=(18, 65), xytext=(35, 40), arrowprops=dict(arrowstyle="<-", color='#2980b9', lw=1.3))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'figure3_dfd_level1.png'), bbox_inches='tight', dpi=300)
    plt.close()
    print("Created figure3_dfd_level1.png")


# -------------------------------------------------------------
# Figure 4: Entity Relationship (ER) Diagram
# -------------------------------------------------------------
def create_er_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(50, 96, "EduTrack Database Entity-Relationship (ER) Schema", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1B365D')

    # Entity 1: USERS (Center-Left)
    u_box = patches.FancyBboxPatch((5, 40), 26, 45, boxstyle="round,pad=1", 
                                   edgecolor='#1B365D', facecolor='#f8f9fa', linewidth=2)
    ax.add_patch(u_box)
    ax.text(18, 81, "USERS (Entity)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1B365D')
    u_attr = (
        "+ id: INT (PK, Auto)\n"
        "+ username: VARCHAR(50) (UQ)\n"
        "+ password: VARCHAR(255)\n"
        "+ role: VARCHAR(20)\n"
        "+ roll_no: VARCHAR(20)\n"
        "+ name: VARCHAR(100)\n"
        "+ created_at: TIMESTAMP\n"
        "+ is_active: BOOLEAN"
    )
    ax.text(7, 60, u_attr, fontsize=8.5, color='#2c3e50', family='monospace')

    # Entity 2: ATTENDANCE (Top-Right)
    att_box = patches.FancyBboxPatch((60, 55), 35, 36, boxstyle="round,pad=1", 
                                     edgecolor='#27ae60', facecolor='#f8f9fa', linewidth=2)
    ax.add_patch(att_box)
    ax.text(77.5, 87, "ATTENDANCE (Entity)", ha='center', va='center', fontsize=11, fontweight='bold', color='#27ae60')
    att_attr = (
        "+ id: INT (PK, Auto)\n"
        "+ student_id: INT (FK -> users.id)\n"
        "+ date: DATE\n"
        "+ subject: VARCHAR(100)\n"
        "+ status: ENUM('Present','Absent')\n"
        "+ time_slot: VARCHAR(50)\n"
        "+ created_at: TIMESTAMP"
    )
    ax.text(62, 69, att_attr, fontsize=8.5, color='#2c3e50', family='monospace')

    # Entity 3: MARKS (Bottom-Right)
    m_box = patches.FancyBboxPatch((60, 10), 35, 36, boxstyle="round,pad=1", 
                                   edgecolor='#e67e22', facecolor='#f8f9fa', linewidth=2)
    ax.add_patch(m_box)
    ax.text(77.5, 42, "MARKS (Entity)", ha='center', va='center', fontsize=11, fontweight='bold', color='#e67e22')
    m_attr = (
        "+ id: INT (PK, Auto)\n"
        "+ student_id: INT (FK -> users.id)\n"
        "+ subject: VARCHAR(100)\n"
        "+ internal_marks: NUMERIC(5,2)\n"
        "+ max_marks: NUMERIC(5,2)\n"
        "+ exam_type: VARCHAR(50)\n"
        "+ updated_at: TIMESTAMP"
    )
    ax.text(62, 24, m_attr, fontsize=8.5, color='#2c3e50', family='monospace')

    # Entity 4: GRID_TIMETABLE (Bottom-Left)
    t_box = patches.FancyBboxPatch((5, 5), 26, 28, boxstyle="round,pad=1", 
                                   edgecolor='#8e44ad', facecolor='#f8f9fa', linewidth=2)
    ax.add_patch(t_box)
    ax.text(18, 29, "GRID_TIMETABLE", ha='center', va='center', fontsize=10, fontweight='bold', color='#8e44ad')
    t_attr = (
        "+ id: INT (PK)\n"
        "+ day: VARCHAR(15)\n"
        "+ slot_name: VARCHAR(30)\n"
        "+ subject: VARCHAR(100)\n"
        "+ room: VARCHAR(20)"
    )
    ax.text(7, 16, t_attr, fontsize=8, color='#2c3e50', family='monospace')

    # Relationship diamond 1: Has / Logs Attendance
    d1 = patches.Polygon([[44, 73], [52, 79], [44, 85], [36, 79]], closed=True, 
                         edgecolor='#2c3e50', facecolor='#d6eaf8', linewidth=1.5)
    ax.add_patch(d1)
    ax.text(44, 79, "Has\nRecords", ha='center', va='center', fontsize=7.5, fontweight='bold')

    # Relationship diamond 2: Obtains Marks
    d2 = patches.Polygon([[44, 30], [52, 36], [44, 42], [36, 36]], closed=True, 
                         edgecolor='#2c3e50', facecolor='#fdebd0', linewidth=1.5)
    ax.add_patch(d2)
    ax.text(44, 36, "Obtains\nScore", ha='center', va='center', fontsize=7.5, fontweight='bold')

    # Connector Lines with Cardinality
    # USERS -> D1 -> ATTENDANCE
    ax.plot([31, 36], [79, 79], color='#2c3e50', lw=1.8)
    ax.text(32, 81, "1", fontsize=10, fontweight='bold', color='#1B365D')
    ax.plot([52, 60], [79, 79], color='#2c3e50', lw=1.8)
    ax.text(58, 81, "N", fontsize=10, fontweight='bold', color='#27ae60')

    # USERS -> D2 -> MARKS
    ax.plot([31, 36], [45, 36], color='#2c3e50', lw=1.8)
    ax.text(32, 43, "1", fontsize=10, fontweight='bold', color='#1B365D')
    ax.plot([52, 60], [36, 30], color='#2c3e50', lw=1.8)
    ax.text(58, 33, "N", fontsize=10, fontweight='bold', color='#e67e22')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'figure4_er_diagram.png'), bbox_inches='tight', dpi=300)
    plt.close()
    print("Created figure4_er_diagram.png")


# -------------------------------------------------------------
# Figure 5: UML Use Case Diagram
# -------------------------------------------------------------
def create_use_case_diagram():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(50, 95, "EduTrack System - UML Use Case Model", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1B365D')

    # System boundary box
    sys_boundary = patches.Rectangle((28, 5), 44, 84, edgecolor='#7f8c8d', 
                                     facecolor='#fafafa', linewidth=1.5, linestyle='--')
    ax.add_patch(sys_boundary)
    ax.text(50, 86, "EduTrack Web Platform Boundary", ha='center', va='center', 
            fontsize=10, fontweight='bold', color='#7f8c8d')

    # Student Actor on Left
    ax.text(12, 55, "STUDENT\n(Actor)", ha='center', va='center', fontsize=11, fontweight='bold', color='#2980b9')
    # Simple stick-man head
    head_s = patches.Circle((12, 65), 3.5, edgecolor='#2980b9', facecolor='#ffffff', lw=2)
    ax.add_patch(head_s)
    ax.plot([12, 12], [61.5, 52], color='#2980b9', lw=2)
    ax.plot([7, 17], [57, 57], color='#2980b9', lw=2)
    ax.plot([12, 8], [52, 45], color='#2980b9', lw=2)
    ax.plot([12, 16], [52, 45], color='#2980b9', lw=2)

    # Teacher Actor on Right
    ax.text(88, 55, "TEACHER /\nFACULTY\n(Actor)", ha='center', va='center', fontsize=11, fontweight='bold', color='#27ae60')
    head_t = patches.Circle((88, 65), 3.5, edgecolor='#27ae60', facecolor='#ffffff', lw=2)
    ax.add_patch(head_t)
    ax.plot([88, 88], [61.5, 52], color='#27ae60', lw=2)
    ax.plot([83, 93], [57, 57], color='#27ae60', lw=2)
    ax.plot([88, 84], [52, 45], color='#27ae60', lw=2)
    ax.plot([88, 92], [52, 45], color='#27ae60', lw=2)

    # Use Case Ovals in System Boundary
    cases = [
        ("UC1: Authenticate via PBKDF2 Password", 50, 77),
        ("UC2: View Personal Attendance & Percentage", 50, 66),
        ("UC3: Monitor Shortage Alert Banner (<75%)", 50, 55),
        ("UC4: Inspect Internal Marks & Subject Distribution", 50, 44),
        ("UC5: Mark Roster Bulk Attendance by Date", 50, 33),
        ("UC6: Filter Class Students by Standing / Shortage", 50, 22),
        ("UC7: Configure Weekly Class Timetable Grid", 50, 11)
    ]

    for label, cx, cy in cases:
        ellipse = patches.Ellipse((cx, cy), 36, 7.5, edgecolor='#1B365D', facecolor='#ebf5fb', lw=1.4)
        ax.add_patch(ellipse)
        ax.text(cx, cy, label, ha='center', va='center', fontsize=7.8, color='#2c3e50', fontweight='bold')

    # Student Lines
    ax.plot([16, 32], [63, 77], color='#2980b9', lw=1.2)
    ax.plot([16, 32], [58, 66], color='#2980b9', lw=1.2)
    ax.plot([16, 32], [55, 55], color='#2980b9', lw=1.2)
    ax.plot([16, 32], [50, 44], color='#2980b9', lw=1.2)

    # Teacher Lines
    ax.plot([84, 68], [63, 77], color='#27ae60', lw=1.2)
    ax.plot([84, 68], [55, 33], color='#27ae60', lw=1.2)
    ax.plot([84, 68], [50, 22], color='#27ae60', lw=1.2)
    ax.plot([84, 68], [46, 11], color='#27ae60', lw=1.2)
    ax.plot([84, 68], [52, 44], color='#27ae60', lw=1.2)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'figure5_use_case.png'), bbox_inches='tight', dpi=300)
    plt.close()
    print("Created figure5_use_case.png")


# -------------------------------------------------------------
# Figure 6: Attendance Analytics Visual
# -------------------------------------------------------------
def create_analytics_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)
    fig.patch.set_facecolor('#ffffff')

    # Doughnut Chart: Overall Standing
    labels = ['Good Standing (>=75%)', 'Shortage Risk (<75%)']
    sizes = [84.2, 15.8]
    colors = ['#2ecc71', '#e74c3c']
    explode = (0, 0.08)

    wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                                       startangle=140, colors=colors, textprops=dict(color='#2c3e50', fontweight='bold'))
    centre_circle = plt.Circle((0,0), 0.65, fc='white')
    ax1.add_artist(centre_circle)
    ax1.set_title("Student Standing Distribution\n(75% Minimum Threshold)", fontsize=11, fontweight='bold', color='#1B365D')

    # Bar Chart: Attendance by Subject
    subjects = ['Python/Flask', 'DBMS / SQL', 'Computer Networks', 'Software Eng.', 'Web Tech']
    attendance = [88.5, 78.0, 92.4, 71.5, 84.0]
    bar_colors = ['#2ecc71' if v >= 75 else '#e74c3c' for v in attendance]

    bars = ax2.bar(subjects, attendance, color=bar_colors, width=0.55, edgecolor='#2c3e50', linewidth=1)
    ax2.axhline(75, color='#e74c3c', linestyle='--', linewidth=1.5, label='75% Cutoff')
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Attendance Percentage (%)", fontweight='bold', color='#1B365D')
    ax2.set_title("Subject-Wise Attendance Evaluation", fontsize=11, fontweight='bold', color='#1B365D')
    ax2.tick_params(axis='x', rotation=25)
    ax2.legend(loc='lower right')

    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f'{h:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'figure6_attendance_distribution.png'), bbox_inches='tight', dpi=300)
    plt.close()
    print("Created figure6_attendance_distribution.png")

if __name__ == '__main__':
    create_architecture_diagram()
    create_dfd_level0()
    create_dfd_level1()
    create_er_diagram()
    create_use_case_diagram()
    create_analytics_chart()
    print("All diagrams generated successfully.")
