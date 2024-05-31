const loginForm = document.getElementById("login-form");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const errorMessage = document.getElementById("error-message");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission behavior

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
        errorMessage.textContent = "Please enter your username and password.";
        return;
    }

    // Send login request to the backend API
    const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username : username, password : password}),
    });

    if (!response.ok) {
        const errorData = await response.json();
        errorMessage.textContent = errorData.detail || "Login failed.";
        return;
    }

    // Handle successful login (redirect, store session token)
    const data = await response.json();
    console.log("Login successful:", data);  // Replace with actual success handling

    // Here, you would typically redirect the user to the main to-do list page 
    // or store the received session token (if applicable) for further API requests.
    window.location.href = "/todo_list";
});
