const API_URL = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' || window.location.protocol === 'file:')
    ? 'http://127.0.0.1:5000'
    : 'https://tenson1234.pythonanywhere.com';

const currentStudent = localStorage.getItem('loggedInUser');
const userRole = localStorage.getItem('userRole');

// Session protection
if (!currentStudent || (userRole && userRole !== 'student')) {
    localStorage.removeItem('loggedInUser');
    localStorage.removeItem('userRole');
    window.location.href = 'index.html';
}

// Chart instance references
let attendanceChartInstance = null;
let marksChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Personalize greeting
    const welcomeEl = document.getElementById('welcomeMessage');
    if (welcomeEl) {
        welcomeEl.innerText = `Welcome, ${currentStudent}!`;
    }

    const greetingEl = document.getElementById('studentGreeting');
    if (greetingEl) {
        greetingEl.innerText = `Logged in as: ${currentStudent}`;
    }

    // 2. Setup Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // 3. Load attendance records and charts
    loadAttendance();

    // 4. Load marks & grades and charts
    loadMarks();

    // 5. Setup Password Change
    setupStudentPasswordChange();

    // 6. Load weekly grid timetable
    loadGridTimetable();
});

// Logout helper
function logout() {
    localStorage.removeItem('loggedInUser');
    localStorage.removeItem('userRole');
    window.location.href = 'index.html';
}

// 1. Fetch and Display Attendance + Chart
function loadAttendance() {
    fetch(`${API_URL}/api/attendance/${encodeURIComponent(currentStudent)}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('attendanceTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';
            
            const overallEl = document.getElementById('overallPercentage');
            const alertEl = document.getElementById('attendanceAlert');
            const statRateEl = document.getElementById('statAttendanceRate');
            const statCountEl = document.getElementById('statAttendedCount');

            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 20px; color: #7f8c8d;">No attendance records found.</td></tr>';
                if (overallEl) {
                    overallEl.innerText = 'Total: 0%';
                    overallEl.style.color = '#7f8c8d';
                }
                if (statRateEl) statRateEl.innerText = '0%';
                if (statCountEl) statCountEl.innerText = '0 / 0';
                if (alertEl) alertEl.style.display = 'none';
                renderAttendanceChart(0, 0);
                return;
            }

            let presentCount = 0;

            data.forEach(record => {
                const isPresent = (record.status || '').toLowerCase() === 'present';
                if (isPresent) presentCount++;

                const badgeBg = isPresent ? '#27ae60' : '#e74c3c';
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.date || '-'}</td>
                    <td>${record.time_slot || '-'}</td>
                    <td><strong>${record.subject || '-'}</strong></td>
                    <td><span style="background-color: ${badgeBg}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;">${record.status}</span></td>
                `;
                tbody.appendChild(row);
            });
            
            const totalCount = data.length;
            const absentCount = totalCount - presentCount;
            const percentage = ((presentCount / totalCount) * 100).toFixed(1);

            // Update stats
            if (overallEl) {
                overallEl.innerText = `Total: ${percentage}%`;
                overallEl.style.color = percentage >= 75 ? '#27ae60' : '#e74c3c';
            }
            if (statRateEl) {
                statRateEl.innerText = `${percentage}%`;
                statRateEl.style.color = percentage >= 75 ? '#27ae60' : '#e74c3c';
            }
            if (statCountEl) {
                statCountEl.innerText = `${presentCount} / ${totalCount}`;
            }

            // Attendance Alert banner
            if (alertEl) {
                alertEl.style.display = 'block';
                if (percentage < 75) {
                    alertEl.style.backgroundColor = '#fde8e8';
                    alertEl.style.color = '#9b1c1c';
                    alertEl.style.borderColor = '#f8b4b4';
                    alertEl.innerHTML = `⚠️ <strong>Attendance Shortage Alert:</strong> Your attendance is currently <strong>${percentage}%</strong>, which is below the mandatory 75% requirement.`;
                } else {
                    alertEl.style.backgroundColor = '#def7ec';
                    alertEl.style.color = '#03543f';
                    alertEl.style.borderColor = '#bcf0da';
                    alertEl.innerHTML = `✅ <strong>Good Standing:</strong> Your attendance is currently <strong>${percentage}%</strong>. Keep up the good work!`;
                }
            }

            // Render Chart
            renderAttendanceChart(presentCount, absentCount);
        })
        .catch(error => {
            console.error('Error fetching attendance:', error);
            const tbody = document.getElementById('attendanceTableBody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 20px; color: #e74c3c;">Failed to load attendance records.</td></tr>';
            }
        });
}

function renderAttendanceChart(present, absent) {
    const canvas = document.getElementById('studentAttendanceChart');
    if (!canvas || typeof Chart === 'undefined') return;

    if (attendanceChartInstance) {
        attendanceChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    attendanceChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Present Sessions', 'Absent Sessions'],
            datasets: [{
                data: [present, absent],
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
                            const total = present + absent;
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

// 2. Fetch and Display Marks + Chart
function loadMarks() {
    fetch(`${API_URL}/api/marks/${encodeURIComponent(currentStudent)}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('marksTableBody');
            const avgStatEl = document.getElementById('statAvgMarks');
            if (!tbody) return;
            tbody.innerHTML = '';
            
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding: 20px; color: #7f8c8d;">No marks uploaded yet.</td></tr>';
                if (avgStatEl) avgStatEl.innerText = '0%';
                renderMarksChart([], []);
                return;
            }

            let totalPercent = 0;
            const subjects = [];
            const scores = [];

            data.forEach(record => {
                const score = Number(record.score) || 0;
                const total = Number(record.total) || 100;
                const pct = total > 0 ? ((score / total) * 100).toFixed(1) : 0;
                totalPercent += Number(pct);

                subjects.push(record.subject);
                scores.push(Number(pct));

                const pctColor = pct >= 40 ? '#27ae60' : '#e74c3c';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${record.subject}</strong></td>
                    <td>${score} / ${total}</td>
                    <td><strong style="color: ${pctColor};">${pct}%</strong></td>
                `;
                tbody.appendChild(row);
            });

            const avgScore = (totalPercent / data.length).toFixed(1);
            if (avgStatEl) {
                avgStatEl.innerText = `${avgScore}%`;
                avgStatEl.style.color = avgScore >= 75 ? '#27ae60' : (avgScore >= 40 ? '#f39c12' : '#e74c3c');
            }

            // Render marks bar chart
            renderMarksChart(subjects, scores);
        })
        .catch(error => {
            console.error('Error fetching marks:', error);
            const tbody = document.getElementById('marksTableBody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding: 20px; color: #e74c3c;">Failed to load marks.</td></tr>';
            }
        });
}

function renderMarksChart(subjects, percentages) {
    const canvas = document.getElementById('studentMarksChart');
    if (!canvas || typeof Chart === 'undefined') return;

    if (marksChartInstance) {
        marksChartInstance.destroy();
    }

    const barColors = percentages.map(p => p >= 75 ? '#2ecc71' : (p >= 40 ? '#3498db' : '#e74c3c'));

    const ctx = canvas.getContext('2d');
    marksChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: subjects.length > 0 ? subjects : ['No Data'],
            datasets: [{
                label: 'Score Percentage (%)',
                data: percentages.length > 0 ? percentages : [0],
                backgroundColor: barColors.length > 0 ? barColors : ['#bdc3c7'],
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
                    ticks: {
                        callback: value => `${value}%`
                    },
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
                        label: ctx => `Score: ${ctx.raw}%`
                    }
                }
            }
        }
    });
}

// 3. Fetch and Display Timetable Grid
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

function loadGridTimetable() {
    const tbody = document.getElementById('gridTimetableBody');
    if (!tbody) return;

    fetch(`${API_URL}/api/grid-timetable`)
        .then(response => response.json())
        .then(data => {
            const scheduleMap = {};
            data.forEach(item => {
                scheduleMap[`${item.day}_${item.time_slot}`] = item.subject;
            });

            tbody.innerHTML = '';

            DAYS.forEach((day, dayIndex) => {
                const tr = document.createElement('tr');

                // Day column
                const dayTd = document.createElement('td');
                dayTd.innerHTML = `<strong>${day}</strong>`;
                dayTd.style.backgroundColor = '#ecf0f1';
                tr.appendChild(dayTd);

                // 9:00-10:00
                tr.appendChild(createReadOnlyCell(scheduleMap[`${day}_9:00-10:00`]));

                // 10:00-11:00
                tr.appendChild(createReadOnlyCell(scheduleMap[`${day}_10:00-11:00`]));

                // TEA BREAK column (rowspan on Monday)
                if (dayIndex === 0) {
                    const breakTd = document.createElement('td');
                    breakTd.className = 'break-col';
                    breakTd.rowSpan = 6;
                    breakTd.innerText = 'TEA BREAK';
                    tr.appendChild(breakTd);
                }

                // 11:15-12:15
                tr.appendChild(createReadOnlyCell(scheduleMap[`${day}_11:15-12:15`]));

                // 12:15-1:15
                tr.appendChild(createReadOnlyCell(scheduleMap[`${day}_12:15-1:15`]));

                // LUNCH BREAK column (rowspan on Monday)
                if (dayIndex === 0) {
                    const lunchTd = document.createElement('td');
                    lunchTd.className = 'lunch-col';
                    lunchTd.rowSpan = 6;
                    lunchTd.innerText = 'LUNCH BREAK';
                    tr.appendChild(lunchTd);
                }

                // 2:00-3:00
                tr.appendChild(createReadOnlyCell(scheduleMap[`${day}_2:00-3:00`]));

                // 3:00-4:00
                tr.appendChild(createReadOnlyCell(scheduleMap[`${day}_3:00-4:00`]));

                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error fetching grid timetable:', error);
            tbody.innerHTML = '<tr><td colspan="9">Failed to load timetable from server.</td></tr>';
        });
}

function createReadOnlyCell(subject) {
    const td = document.createElement('td');
    td.className = 'readonly-cell';
    td.innerText = subject || '-';
    if (subject) {
        td.style.fontWeight = '600';
        td.style.color = '#2c3e50';
    } else {
        td.style.color = '#bdc3c7';
    }
    return td;
}

// 4. Setup Student Password Change Handler
function setupStudentPasswordChange() {
    const form = document.getElementById('studentChangePasswordForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const currentPassword = document.getElementById('studentCurrentPassword').value;
        const newPassword = document.getElementById('studentNewPassword').value;
        const confirmNewPassword = document.getElementById('studentConfirmNewPassword').value;

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
                username: currentStudent,
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
                Swal.fire('Update Failed', data.message || 'Could not update password. Please check your current password.', 'error');
            }
        })
        .catch(err => {
            console.error('Error changing student password:', err);
            Swal.fire('Connection Error', 'Could not reach server to update password.', 'error');
        });
    });
}