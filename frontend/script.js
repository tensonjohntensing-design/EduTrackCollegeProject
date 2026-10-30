const API_URL = (window.location.protocol === 'file:')
    ? 'http://127.0.0.1:5000'
    : window.location.origin;

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const role = document.querySelector('input[name="role"]:checked').value;

    fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, password: password, role: role })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            localStorage.setItem('loggedInUser', data.username || username);
            localStorage.setItem('userRole', data.role || role);
            
            Swal.fire({
                icon: 'success',
                title: 'Welcome!',
                text: 'Redirecting to your dashboard...',
                timer: 1000,
                showConfirmButton: false
            }).then(() => {
                if (role === 'student') {
                    window.location.href = 'student-dashboard.html';
                } else {
                    window.location.href = 'teacher-dashboard.html';
                }
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Login Failed',
                text: data.message || 'Invalid credentials.'
            });
        }
    })
    .catch(error => {
        console.error('Error logging in:', error);
        Swal.fire({
            icon: 'warning',
            title: 'Connection Error',
            text: 'Could not connect to the backend server. Make sure app.py is running on port 5000!'
        });
    });
});