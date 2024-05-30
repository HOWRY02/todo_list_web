const taskList = document.getElementById("task-list");
const newTaskInput = document.getElementById("new-task");
const pieChartContainer = document.getElementById("pie-chart");

// Function to fetch the task list from the backend
async function getTasks() {
    const response = await fetch("/api/tasks");
    const tasks = await response.json();
    displayTasks(tasks);
}

// Function to display the task list with checkboxes and delete buttons
function displayTasks(tasks) {
    taskList.innerHTML = ""; // Clear existing tasks
    tasks.forEach((task) => {
        const listItem = document.createElement("li");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = task.is_done;
        checkbox.addEventListener("change", () => updateTask(task.id, checkbox.checked));

        const taskText = document.createTextNode(task.description);
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => deleteTask(task.id));

        listItem.appendChild(checkbox);
        listItem.appendChild(taskText);
        listItem.appendChild(deleteButton);
        taskList.appendChild(listItem);
    });
}

// Function to add a new task using AJAX request
async function addTask() {
    const newTaskDescription = newTaskInput.value;
    if (!newTaskDescription) {
        alert("Please enter a task description!");
        return;
    }

    const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: newTaskDescription }),
    });

    if (!response.ok) {
        alert("Error adding task!");
    } else {
        newTaskInput.value = ""; // Clear input field
        getTasks(); // Refresh task list
    }
}

// Function to update task completion status using AJAX request
async function updateTask(taskId, isDone) {
    const response = await fetch(`/api/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_done: isDone }),
    });

    if (!response.ok) {
        alert("Error updating task!");
    } else {
        getTasks(); // Refresh task list
    }
}

// Function to delete a task using AJAX request
async function deleteTask(taskId) {
    const response = await fetch(`/api/tasks/${taskId}`, {
        method: "DELETE",
    });

    if (!response.ok) {
        alert("Error deleting task!");
    } else {
        getTasks(); // Refresh task list
    }
}

getTasks(); // Fetch tasks on page load

// Call your JavaScript library (e.g., Chart.js) to fetch completion data and generate the pie chart
// This part would depend on the specific library you choose.
