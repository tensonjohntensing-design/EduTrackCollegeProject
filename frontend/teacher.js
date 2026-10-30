const API_URL = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' || window.location.protocol === 'file:')
    ? 'http://127.0.0.1:5000'
    : 'https://tenson1234.pythonanywhere.com';

const loggedInUser = localStorage.getItem('loggedInUser');
const userRole = localStorage.getItem('userRole');

// Session protection
if (!loggedInUser || (userRole && userRole !== 'teacher')) {
    localStorage.removeItem('loggedInUser');
    localStorage.removeItem('userRole');
    window.location.href = 'index.html';
}

// Current active session config for attendance
let activeAttendanceConfig = null;

// Chart instance references
let teacherSubjectChartInstance = null;
let teacherStandingChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Display teacher name
    const greetingEl = document.getElementById('teacherGreeting');
    if (greetingEl) {
        greetingEl.innerText = `Logged in as: ${loggedInUser}`;
    }

    // 2. Setup Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // Setup Mobile Navigation Drawer
    setupMobileNav();

    // 3. Set default date to today
    const dateInput = document.getElementById('attendanceDate');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }

    // 4. Load Visual Analytics & Charts
    loadTeacherAnalytics();

    // 5. Populate students dropdown for Marks upload
    loadStudentsForMarks();

    // 6. Setup Attendance forms
    setupAttendanceHandlers();

    // 7. Setup Marks submission
    setupMarksHandler();

    // 8. Setup Register Student form
    setupAddStudentHandler();

    // 9. Setup Change Password form
    setupChangePasswordHandler();

    // 10. Load and render Grid Timetable
    loadGridTimetable();
});

// Mobile Navigation Drawer Toggle Handler
function setupMobileNav() {
    const toggleBtn = document.getElementById('mobileMenuToggle');
    const closeBtn = document.getElementById('sidebarCloseBtn');
    const overlay = document.getElementById('sidebarOverlay');
    const sidebar = document.getElementById('sidebar');
    if (!toggleBtn || !sidebar) return;

    function openMenu() {
        sidebar.classList.add('open');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    toggleBtn.addEventListener('click', openMenu);
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
    if (overlay) overlay.addEventListener('click', closeMenu);

    // Auto-close sidebar on mobile when navigation links are clicked
    sidebar.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            closeMenu();
        });
    });
}

// Logout Helper
function logout() {
    localStorage.removeItem('loggedInUser');
    localStorage.removeItem('userRole');
    window.location.href = 'index.html';
}

// Visual Analytics & Charts
function loadTeacherAnalytics() {
    fetch(`${API_URL}/api/analytics/teacher`)
        .then(res => res.json())
        .then(data => {
            // Update Stat Tiles
            const totalStudentsEl = document.getElementById('teacherTotalStudents');
            const overallRateEl = document.getElementById('teacherOverallRate');
            const goodStandingEl = document.getElementById('teacherGoodStanding');
            const shortageCountEl = document.getElementById('teacherShortageCount');

            if (totalStudentsEl) totalStudentsEl.innerText = data.total_students || 0;
            if (overallRateEl) {
                overallRateEl.innerText = `${data.overall_attendance_rate || 0}%`;
                overallRateEl.style.color = (data.overall_attendance_rate || 0) >= 75 ? '#27ae60' : '#e74c3c';
            }
            if (goodStandingEl) goodStandingEl.innerText = data.good_standing_count || 0;
            if (shortageCountEl) shortageCountEl.innerText = data.shortage_count || 0;

            // Render Charts
            renderSubjectAttendanceChart(data.subject_attendance || []);
            renderStandingChart(data.good_standing_count || 0, data.shortage_count || 0);
        })
        .catch(err => {
            console.error('Error loading teacher analytics:', err);
        });
}

function renderSubjectAttendanceChart(subjectList) {
    const canvas = document.getElementById('teacherSubjectAttendanceChart');
    if (!canvas || typeof Chart === 'undefined') return;

    if (teacherSubjectChartInstance) {
        teacherSubjectChartInstance.destroy();
    }

    const labels = subjectList.length > 0 ? subjectList.map(s => s.subject) : ['No Data'];
    const rates = subjectList.length > 0 ? subjectList.map(s => s.rate) : [0];
    const colors = rates.map(r => r >= 75 ? '#2ecc71' : (r >= 50 ? '#3498db' : '#e74c3c'));

    const ctx = canvas.getContext('2d');
    teacherSubjectChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Attendance Rate (%)',
                data: rates,
                backgroundColor: colors,
                borderRadius: 6,
                maxBarThickness: 45
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { callback: v => `${v}%` },
                    grid: { color: '#f0f3f6' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `Attendance: ${ctx.raw}%`
                    }
                }
            }
        }
    });
}

function renderStandingChart(goodStanding, shortage) {
    const canvas = document.getElementById('teacherStandingChart');
    if (!canvas || typeof Chart === 'undefined') return;

    if (teacherStandingChartInstance) {
        teacherStandingChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    teacherStandingChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Good Standing (≥75%)', 'Shortage Risk (<75%)'],
            datasets: [{
                data: [goodStanding, shortage],
                backgroundColor: ['#2ecc71', '#e74c3c'],
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 14, font: { family: "'Segoe UI', sans-serif", weight: '600' } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = goodStanding + shortage;
                            const val = context.raw || 0;
                            const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                            return ` ${context.label}: ${val} (${pct}%)`;
                        }
                    }
                }
            },
            cutout: '68%'
        }
    });
}

// Fetch students to populate marks select dropdown
function loadStudentsForMarks() {
    const studentSelect = document.getElementById('marksStudentSelect');
    if (!studentSelect) return;

    fetch(`${API_URL}/api/students`)
        .then(res => res.json())
        .then(students => {
            studentSelect.innerHTML = '<option value="" disabled selected>Select Student</option>';
            if (students.length === 0) {
                studentSelect.innerHTML = '<option value="" disabled>No students found</option>';
                return;
            }
            students.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.username;
                opt.textContent = s.username;
                studentSelect.appendChild(opt);
            });
        })
        .catch(err => {
            console.error('Failed to load students:', err);
            studentSelect.innerHTML = '<option value="" disabled>Error loading students</option>';
        });
}

// Setup attendance roster loading and bulk submission
function setupAttendanceHandlers() {
    const configForm = document.getElementById('attendanceConfigForm');
    const bulkForm = document.getElementById('bulkAttendanceForm');
    const rosterBody = document.getElementById('rosterBody');
    const rosterHeaderInfo = document.getElementById('rosterHeaderInfo');
    const markAllPresentBtn = document.getElementById('markAllPresentBtn');

    if (configForm) {
        configForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const date = document.getElementById('attendanceDate').value;
            const timeSlot = document.getElementById('attendanceTime').value;
            const subject = document.getElementById('attendanceSubject').value;

            if (!date || !timeSlot || !subject) {
                Swal.fire('Incomplete Details', 'Please select Date, Time Slot, and Subject.', 'info');
                return;
            }

            activeAttendanceConfig = { date, timeSlot, subject };

            // Fetch students from backend
            fetch(`${API_URL}/api/students`)
                .then(res => res.json())
                .then(students => {
                    if (!students || students.length === 0) {
                        Swal.fire('No Students', 'No student accounts exist in the database.', 'warning');
                        return;
                    }

                    rosterBody.innerHTML = '';
                    students.forEach((s, idx) => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td style="text-align: left; padding-left: 15px; font-weight: 500;">
                                ${s.username}
                                <input type="hidden" class="student-user-val" value="${s.username}">
                            </td>
                            <td>
                                <input type="radio" name="status_${idx}" class="present-radio" value="Present" checked>
                            </td>
                            <td>
                                <input type="radio" name="status_${idx}" class="absent-radio" value="Absent">
                            </td>
                        `;
                        rosterBody.appendChild(tr);
                    });

                    if (rosterHeaderInfo) {
                        rosterHeaderInfo.innerHTML = `📋 Roster for: <strong>${subject}</strong> &nbsp;|&nbsp; <strong>${timeSlot}</strong> &nbsp;|&nbsp; <strong>${date}</strong>`;
                    }

                    bulkForm.style.display = 'block';
                    bulkForm.scrollIntoView({ behavior: 'smooth' });
                })
                .catch(err => {
                    console.error('Error fetching students:', err);
                    Swal.fire('Error', 'Could not load student list. Verify server is running.', 'error');
                });
        });
    }

    if (markAllPresentBtn) {
        markAllPresentBtn.addEventListener('click', () => {
            const presentRadios = document.querySelectorAll('.present-radio');
            presentRadios.forEach(radio => radio.checked = true);
        });
    }

    if (bulkForm) {
        bulkForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!activeAttendanceConfig) {
                Swal.fire('Error', 'Please load the class roster first.', 'error');
                return;
            }

            const rows = rosterBody.querySelectorAll('tr');
            const attendanceRecords = [];

            rows.forEach((row, idx) => {
                const usernameEl = row.querySelector('.student-user-val');
                const checkedRadio = row.querySelector(`input[name="status_${idx}"]:checked`);
                if (usernameEl && checkedRadio) {
                    attendanceRecords.push({
                        date: activeAttendanceConfig.date,
                        time_slot: activeAttendanceConfig.timeSlot,
                        subject: activeAttendanceConfig.subject,
                        student_username: usernameEl.value,
                        status: checkedRadio.value
                    });
                }
            });

            if (attendanceRecords.length === 0) {
                Swal.fire('Error', 'No attendance rows found to submit.', 'error');
                return;
            }

            fetch(`${API_URL}/api/attendance/bulk`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(attendanceRecords)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Attendance Saved!',
                        text: data.message || `Saved attendance for ${attendanceRecords.length} student(s).`
                    });
                    bulkForm.style.display = 'none';
                    activeAttendanceConfig = null;
                    // Live refresh charts & analytics
                    loadTeacherAnalytics();
                } else {
                    Swal.fire('Save Failed', data.message || 'Could not save attendance.', 'error');
                }
            })
            .catch(err => {
                console.error('Error saving attendance:', err);
                Swal.fire('Connection Error', 'Could not reach server to save attendance.', 'error');
            });
        });
    }
}

// Setup Marks submission
function setupMarksHandler() {
    const marksForm = document.getElementById('marksForm');
    if (!marksForm) return;

    marksForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const student = document.getElementById('marksStudentSelect').value;
        const subject = document.getElementById('subject').value.trim();
        const score = document.getElementById('score').value;
        const total = document.getElementById('total').value;

        if (!student || !subject || score === '') {
            Swal.fire('Missing Fields', 'Please fill in all mark details.', 'warning');
            return;
        }

        fetch(`${API_URL}/api/marks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_username: student,
                subject: subject,
                score: score,
                total: total
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Marks Uploaded!',
                    text: data.message || `Recorded ${score}/${total} for ${student}.`
                });
                marksForm.reset();
                document.getElementById('total').value = '100';
                // Live refresh charts & analytics
                loadTeacherAnalytics();
            } else {
                Swal.fire('Error', data.message || 'Could not save marks.', 'error');
            }
        })
        .catch(err => {
            console.error('Error uploading marks:', err);
            Swal.fire('Connection Error', 'Failed to submit marks to server.', 'error');
        });
    });
}

// Setup Register New Student handler
function setupAddStudentHandler() {
    const form = document.getElementById('addStudentForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('newStudentUsername').value.trim();
        const password = document.getElementById('newStudentPassword').value;

        if (!username || !password) {
            Swal.fire('Missing Information', 'Please provide both username and password.', 'warning');
            return;
        }

        if (password.length < 4) {
            Swal.fire('Password Too Short', 'Password must be at least 4 characters long.', 'warning');
            return;
        }

        fetch(`${API_URL}/api/students`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, password: password })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Student Created!',
                    text: data.message || `Student '${username}' has been successfully registered.`
                });
                form.reset();
                // Refresh student lists across the dashboard
                loadStudentsForMarks();
                loadTeacherAnalytics();
            } else {
                Swal.fire('Registration Failed', data.message || 'Could not register student.', 'error');
            }
        })
        .catch(err => {
            console.error('Error adding student:', err);
            Swal.fire('Connection Error', 'Could not reach server to create student.', 'error');
        });
    });
}

// Setup Change Password handler
function setupChangePasswordHandler() {
    const form = document.getElementById('changePasswordForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmNewPassword = document.getElementById('confirmNewPassword').value;

        if (newPassword !== confirmNewPassword) {
            Swal.fire('Password Mismatch', 'New password and confirmation password do not match.', 'warning');
            return;
        }

        if (newPassword.length < 4) {
            Swal.fire('Password Too Short', 'New password must be at least 4 characters long.', 'warning');
            return;
        }

        fetch(`${API_URL}/api/change-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: loggedInUser,
                current_password: currentPassword,
                new_password: newPassword
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Password Updated!',
                    text: 'Your password has been changed successfully.'
                });
                form.reset();
            } else {
                Swal.fire('Update Failed', data.message || 'Could not update password. Verify your current password.', 'error');
            }
        })
        .catch(err => {
            console.error('Error changing password:', err);
            Swal.fire('Connection Error', 'Could not connect to server to update password.', 'error');
        });
    });
}

// BCA V Semester Weekly Timetable Grid
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

function loadGridTimetable() {
    const tbody = document.getElementById('gridTimetableBody');
    if (!tbody) return;

    fetch(`${API_URL}/api/grid-timetable`)
        .then(res => res.json())
        .then(data => {
            const scheduleMap = {};
            data.forEach(item => {
                scheduleMap[`${item.day}_${item.time_slot}`] = item.subject;
            });

            renderGrid(tbody, scheduleMap);
        })
        .catch(err => {
            console.error('Error loading grid timetable:', err);
            tbody.innerHTML = '<tr><td colspan="9">Failed to load timetable from server.</td></tr>';
        });
}

function renderGrid(tbody, scheduleMap) {
    tbody.innerHTML = '';

    DAYS.forEach((day, dayIndex) => {
        const tr = document.createElement('tr');

        // Day label
        const dayTd = document.createElement('td');
        dayTd.innerHTML = `<strong>${day}</strong>`;
        dayTd.style.backgroundColor = '#ecf0f1';
        tr.appendChild(dayTd);

        // Period 1 (9:00-10:00)
        tr.appendChild(createCell(day, '9:00-10:00', scheduleMap[`${day}_9:00-10:00`]));

        // Period 2 (10:00-11:00)
        tr.appendChild(createCell(day, '10:00-11:00', scheduleMap[`${day}_10:00-11:00`]));

        // TEA BREAK column (rowspan on Monday)
        if (dayIndex === 0) {
            const breakTd = document.createElement('td');
            breakTd.className = 'break-col';
            breakTd.rowSpan = 6;
            breakTd.innerText = 'TEA BREAK';
            tr.appendChild(breakTd);
        }

        // Period 3 (11:15-12:15)
        tr.appendChild(createCell(day, '11:15-12:15', scheduleMap[`${day}_11:15-12:15`]));

        // Period 4 (12:15-1:15)
        tr.appendChild(createCell(day, '12:15-1:15', scheduleMap[`${day}_12:15-1:15`]));

        // LUNCH BREAK column (rowspan on Monday)
        if (dayIndex === 0) {
            const lunchTd = document.createElement('td');
            lunchTd.className = 'lunch-col';
            lunchTd.rowSpan = 6;
            lunchTd.innerText = 'LUNCH BREAK';
            tr.appendChild(lunchTd);
        }

        // Period 5 (2:00-3:00)
        tr.appendChild(createCell(day, '2:00-3:00', scheduleMap[`${day}_2:00-3:00`]));

        // Period 6 (3:00-4:00)
        tr.appendChild(createCell(day, '3:00-4:00', scheduleMap[`${day}_3:00-4:00`]));

        tbody.appendChild(tr);
    });
}

function createCell(day, timeSlot, subject) {
    const td = document.createElement('td');
    td.className = 'editable-cell';
    td.innerText = subject || '-';
    td.title = `Click to edit ${day} (${timeSlot})`;

    if (subject) {
        td.style.fontWeight = '600';
        td.style.color = '#2c3e50';
    } else {
        td.style.color = '#bdc3c7';
    }

    td.addEventListener('click', () => {
        handleEditCell(day, timeSlot, subject);
    });

    return td;
}

function handleEditCell(day, timeSlot, currentSubject) {
    Swal.fire({
        title: `Edit ${day}`,
        text: `Time slot: ${timeSlot}`,
        input: 'text',
        inputValue: currentSubject || '',
        inputPlaceholder: 'Enter Subject Name (leave empty to clear)',
        showCancelButton: true,
        confirmButtonText: 'Save',
        confirmButtonColor: '#3498db',
        cancelButtonText: 'Cancel'
    }).then(result => {
        if (result.isConfirmed) {
            const newSubject = (result.value || '').trim();

            fetch(`${API_URL}/api/grid-timetable`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    day: day,
                    time_slot: timeSlot,
                    subject: newSubject
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    loadGridTimetable(); // Re-render grid
                } else {
                    Swal.fire('Error', data.message || 'Could not update timetable.', 'error');
                }
            })
            .catch(err => {
                console.error('Error saving timetable entry:', err);
                Swal.fire('Error', 'Connection failed while updating timetable.', 'error');
            });
        }
    });
}