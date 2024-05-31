const registerForm = document.getElementById("register-form");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirm-password");
const errorMessage = document.getElementById("error-message");

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault(); // Prevent default form submission

  const username = usernameInput.value.trim();
  const password = passwordInput.value.trim();
  const confirmPassword = confirmPasswordInput.value.trim();

  // Basic validation (optional)
  if (!username || !password || !confirmPassword) {
    errorMessage.textContent = "Please fill in all fields.";
    return;
  }

  if (password !== confirmPassword) {
    errorMessage.textContent = "Passwords do not match.";
    return;
  }

  try {
    // Send registration request to the backend API
    const response = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      errorMessage.textContent = errorData.detail || "Registration failed.";
      return;
    }

    // Handle successful registration (optional)
    console.log("Registration successful!");
    window.location.href = "/login"; // Redirect to login page (optional)
  } catch (error) {
    console.error("Registration error:", error);
    errorMessage.textContent = "An error occurred. Please try again.";
  }
});
