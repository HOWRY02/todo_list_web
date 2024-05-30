import mysql.connector


class Database:

    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    # Define functions for specific database operations (CRUD)
    def insert_task(self, user_id, description):
        # Implement logic to insert a new task
        # Replace with your specific SQL query and parameter binding
        sql = "INSERT INTO tasks (user_id, description) VALUES (%s, %s)"
        self.cursor.execute(sql, (user_id, description))
        self.connection.commit()

    # Define similar functions for get_tasks, update_task, delete_task

    # Example function to fetch all tasks for a user
    def get_tasks(self, user_id):
        sql = "SELECT * FROM tasks WHERE user_id = %s"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def update_task(self, user_id, task_id, task_update):
        # Implement logic to update a task based on task_id and task_update data
        # Replace with your specific SQL query and parameter binding
        sql = "UPDATE tasks SET "  # Update clause with specific fields
        update_params = []
        if "description" in task_update:
            sql += "description = %s, "
            update_params.append(task_update["description"])
        if "is_done" in task_update:
            sql += "is_done = %s, "
            update_params.append(task_update["is_done"])
        sql = sql[:-2]  # Remove trailing comma
        sql += " WHERE user_id = %s AND id = %s"  # WHERE clause for filtering
        update_params.extend((user_id, task_id))
        self.cursor.execute(sql, update_params)
        self.connection.commit()
        return self.cursor.rowcount > 0  # Return True if a row was updated

    def delete_task(self, user_id, task_id):
        sql = "DELETE FROM tasks WHERE user_id = %s AND id = %s"
        self.cursor.execute(sql, (user_id, task_id))
        self.connection.commit()
        return self.cursor.rowcount > 0  # Return True if a row was deleted
