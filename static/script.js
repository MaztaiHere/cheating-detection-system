
function fetchDetections() {

    fetch('/get_detections?' + new Date().getTime())
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Fetched data:", data); 

            const tableBody = document.getElementById('detectionTableBody');
            if (!tableBody) {
                console.error("Element with id 'detectionTableBody' not found. Check your HTML.");
                return;
            }

            tableBody.innerHTML = '';

            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5">No detections found</td></tr>';
                return;
            }

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

setInterval(fetchDetections, 2000);

document.addEventListener("DOMContentLoaded", fetchDetections);

document.getElementById("login-form")?.addEventListener("submit", function (e) {
    e.preventDefault();  

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const captchaInput = document.getElementById("captcha").value;
    const captchaCode = document.getElementById("captcha-box").innerText;

    if (username === "" || password === "" || captchaInput === "") {
        document.getElementById("error-message").innerText = "All fields are required.";
        return;
    }
    if (captchaInput !== captchaCode) {
        document.getElementById("error-message").innerText = "Incorrect CAPTCHA.";
        return;
    }

    const allowedCredentials = [
        { username: 'admin', password: 'admin123' },
        { username: 'student', password: 'student123' },
        { username: 'teacher', password: 'teacher123' }
    ];

    const userValid = allowedCredentials.some(credentials => 
        credentials.username === username && credentials.password === password
    );

    if (userValid) {
        window.location.href = "dashboard.html"; 
    } else {
        document.getElementById("error-message").innerText = "Invalid username or password.";
    }
});

function generateCaptcha() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let captcha = '';
    for (let i = 0; i < 6; i++) {
        captcha += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    document.getElementById('captcha-box').innerText = captcha;
}


window.onload = generateCaptcha;

document.getElementById("register-form")?.addEventListener("submit", function (e) {
    e.preventDefault();  

    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (username === "" || password === "" || confirmPassword === "") {
        document.getElementById("register-error-message").innerText = "All fields are required.";
        return;
    }

    if (password !== confirmPassword) {
        document.getElementById("register-error-message").innerText = "Passwords do not match.";
        return;
    }

    console.log("New user registered:", username, password);

    window.location.href = "login.html";  
});
