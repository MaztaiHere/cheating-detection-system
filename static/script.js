// Function to fetch detection data from the server for the dashboard
function fetchDetections() {
    // Append a timestamp to the request to prevent caching.
    fetch('/get_detections?' + new Date().getTime())
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Fetched data:", data);  // Debug log

            // Get the table body element where data will be displayed.
            const tableBody = document.getElementById('detectionTableBody');
            if (!tableBody) {
                console.error("Element with id 'detectionTableBody' not found. Check your HTML.");
                return;
            }

            // Clear existing table rows before adding new data.
            tableBody.innerHTML = '';

            if (data.length === 0) {
                // If no detections are found, display a message.
                tableBody.innerHTML = '<tr><td colspan="5">No detections found</td></tr>';
                return;
            }

            // Loop through the returned data and create table rows for each detection.
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.id}</td>
                    <td>${row.timestamp}</td>
                    <td>${row.cheating_type}</td>
                    <td>${parseFloat(row.confidence).toFixed(2)}</td>
                    <td>${row.video_name}</td>
                `;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Refresh detections every 2 seconds (2000 milliseconds).
setInterval(fetchDetections, 2000);

// Initial fetch when the page is loaded
document.addEventListener("DOMContentLoaded", fetchDetections);

// Function for handling login submission
document.getElementById("login-form").addEventListener("submit", function (e) {
    e.preventDefault();  // Prevent form submission for validation

    // Get user inputs
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const captchaInput = document.getElementById("captcha").value;
    const captchaCode = document.getElementById("captcha-box").innerText;

    // Simple client-side validation (can be expanded)
    if (username === "" || password === "" || captchaInput === "") {
        document.getElementById("error-message").innerText = "All fields are required.";
        return;
    }

    // Validate CAPTCHA
    if (captchaInput !== captchaCode) {
        document.getElementById("error-message").innerText = "Incorrect CAPTCHA.";
        return;
    }

    // Validate username and password (mock validation)
    const allowedCredentials = [
        { username: 'admin', password: 'admin123' },
        { username: 'student', password: 'student123' },
        { username: 'teacher', password: 'teacher123' }
    ];

    const userValid = allowedCredentials.some(credentials => 
        credentials.username === username && credentials.password === password
    );

    if (userValid) {
        // Redirect to dashboard or another page upon successful login
        window.location.href = "dashboard.html";  // Change to your desired location
    } else {
        document.getElementById("error-message").innerText = "Invalid username or password.";
    }
});

// Function to generate a random CAPTCHA
function generateCaptcha() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let captcha = '';
    for (let i = 0; i < 6; i++) {
        captcha += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    document.getElementById('captcha-box').innerText = captcha;
}

// Call generateCaptcha() to show a new CAPTCHA when the page loads
window.onload = generateCaptcha;

// Function for handling registration submission
document.getElementById("register-form").addEventListener("submit", function (e) {
    e.preventDefault();  // Prevent form submission for validation

    // Get user inputs
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    // Simple client-side validation (can be expanded)
    if (username === "" || password === "" || confirmPassword === "") {
        document.getElementById("register-error-message").innerText = "All fields are required.";
        return;
    }

    // Check if passwords match
    if (password !== confirmPassword) {
        document.getElementById("register-error-message").innerText = "Passwords do not match.";
        return;
    }

    // Save the new user (for now, just log it, you can later connect to a database)
    console.log("New user registered:", username, password);

    // Redirect to the login page after successful registration
    window.location.href = "login.html";  // Change to your desired location
});
