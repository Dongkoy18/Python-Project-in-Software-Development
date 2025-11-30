import mariadb

# Connect to the MariaDB db
try:
    connection = mariadb.connect(
        host="localhost",
        user="root",
        password="",
        database="opticalclinic_db"
    )

    print("Connected Successfully.")

    # Create cursor object to interact with the db
    cursor = connection.cursor()
    
    # Create
    cursor.execute("""
        CREATE TABLE employees (
            employee_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(50),
            contact_num VARCHAR(12)
        )
    """)

    # Insert
    cursor.execute("""
        INSERT INTO employees (name, email, contact_num)
        VALUES (?, ?, ?)
    """, ("Emman Kristoffer Ame", "e.ame@email.com", "09123456789"))
    connection.commit()
    print("Inserted Successfully.")

    # Read
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    print("All Employees:")
    for row in rows:
        print(row)

    # Update
    cursor.execute("""
        UPDATE employees
        SET contact_num = ?
        WHERE name = ?
    """, ("09876543210", "Emman Kristoffer Ame"))
    connection.commit()
    print("Updated Successfully.")

    # Delete
    cursor.execute("""
        DELETE FROM employees
        WHERE name = ?
    """, ("Emman Kristoffer Ame",))
    connection.commit()
    print("Deleted Successfully.")

    # Close cursor and connection
    cursor.close()
    connection.close()

except mariadb.Error as e:
    print(f"Failed to Connect: {e}")


# Database Class

class Database:
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                host="localhost",
                user="root",
                password="",
                database="opticalclinic_db"
            )
            
            print("Connection to database successful.")
        
        except mariadb.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None


db = Database()
