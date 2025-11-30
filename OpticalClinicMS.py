import mariadb
from datetime import datetime
from getpass import getpass

# RECEIPT HANDLER FUNCTION
def save_order_receipt(order_id, product_name, customer_name):
    """Append order info to receipt.txt"""
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open("receipt.txt", "a") as file:
        file.write(f"Order ID: {order_id} | Product: {product_name} | Customer: {customer_name} | Date: {now}\n")

# DATABASE MANAGER
class Database:
    def __init__(self):
        self.connect_db = mariadb.connect(
            host="localhost",
            user="root",
            password="",
            database="opticalclinic_db"
        )
        self.cursor = self.connect_db.cursor()

    def row_to_dict(self, row, columns):
        return {columns[i]: row[i] for i in range(len(columns))}

    def query(self, sql, params=None):
        self.cursor.execute(sql.replace("%s", "?"), params or ())
        rows = self.cursor.fetchall()
        columns = [col[0] for col in self.cursor.description]
        return [self.row_to_dict(row, columns) for row in rows]

    def execute(self, sql, params=None):
        self.cursor.execute(sql.replace("%s", "?"), params or ())
        self.connect_db.commit()

db = Database()

# UTILITY FUNCTIONS
def print_table(rows, title):
    if not rows:
        print(f"\nNo {title.lower()} found.")
        return

    def format_key(key):
        display = key.replace('_', ' ').title()
        display = display.replace(' Id', ' ID').replace('Cnum', 'Number')
        return display

    headers = [format_key(k) for k in rows[0].keys()]
    column_widths = [max(len(str(row[k])) for row in rows) for k in rows[0].keys()]
    column_widths = [max(len(h), w) for h, w in zip(headers, column_widths)]

    print(f"\n{title.upper()}")
    header_row = " | ".join(h.ljust(w) for h, w in zip(headers, column_widths))
    print(header_row)
    print("-" * len(header_row))

    for row in rows:
        row_string = " | ".join(str(row[k]).ljust(w) for k, w in zip(row.keys(), column_widths))
        print(row_string)

def input_not_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("\nInvalid input.")
    return value

# BASE USER CLASS
class User:
    def __init__(self, employee_id, employee_name, employee_role):
        self.id = employee_id
        self.name = employee_name
        self.role = employee_role

# ADMIN CLASS
class Admin:
    PASSWORD = "opticalclinic_admin"

    @staticmethod
    def add_employee():
        try:
            employee_name = input_not_empty("Employee Name: ")
            employee_role = input_not_empty("Role (Optometrist/Sales Associate): ")
            employee_email = input_not_empty("Email: ")
            employee_contact = input_not_empty("Contact Number: ")
            employee_password = getpass("Password: ").strip()

            db.execute("""
                INSERT INTO Employees (employee_name, employee_role, employee_email, employee_cnum, employee_pwd)
                VALUES (%s, %s, %s, %s, %s)
            """, (employee_name, employee_role, employee_email, employee_contact, employee_password))

            last_id = db.query("SELECT LAST_INSERT_ID() AS id")[0]["id"]
            print(f"\nEmployee ID: {last_id} added successfully.")
        except ValueError as error:
            print(error)

    @staticmethod
    def view_employees():
        employees = db.query("SELECT * FROM Employees")
        print_table(employees, "Employees")

    @staticmethod
    def update_employee():
        employee_id = input("Employee ID: ")
        new_name = input("New Name: ")
        new_role = input("New Role: ")
        new_email = input("New Email: ")
        new_contact = input("New Contact Number: ")
        new_password = getpass("New Password: ")

        db.execute("""
            UPDATE Employees 
            SET employee_name=%s, employee_role=%s, employee_email=%s, employee_cnum=%s, employee_pwd=%s
            WHERE employee_id=%s
        """, (new_name, new_role, new_email, new_contact, new_password, employee_id))
        print(f"\nEmployee ID: {employee_id} updated successfully.")

    @staticmethod
    def delete_employee():
        employee_id = input("Employee ID: ")
        db.execute("DELETE FROM Employees WHERE employee_id=%s", (employee_id,))
        print(f"\nEmployee ID: {employee_id} deleted successfully.")

    @staticmethod
    def add_product():
        try:
            product_name = input_not_empty("Product Name: ")
            product_model = input_not_empty("Product Model: ")
            product_color = input_not_empty("Product Color: ")
            stock_status = input_not_empty("Stock Status (Available/Out of Stock): ")

            if stock_status not in ["Available", "Out of Stock"]:
                raise ValueError("\nInvalid stock status.")

            db.execute("""
                INSERT INTO Products (product_name, product_model, product_color, stock_status)
                VALUES (%s, %s, %s, %s)
            """, (product_name, product_model, product_color, stock_status))

            last_id = db.query("SELECT LAST_INSERT_ID() AS id")[0]["id"]
            print(f"\nProduct ID: {last_id} added successfully.")
        except ValueError as error:
            print(error)

    @staticmethod
    def view_products():
        products = db.query("SELECT * FROM Products")
        print_table(products, "Products")

    @staticmethod
    def update_product():
        product_id = input("Product ID: ")
        new_name = input("New Product Name: ")
        new_model = input("New Product Model: ")
        new_color = input("New Product Color: ")
        new_stock_status = input("Update Stock Status (Available/Out of Stock): ")

        db.execute("""
            UPDATE Products 
            SET product_name=%s, product_model=%s, product_color=%s, stock_status=%s
            WHERE product_id=%s
        """, (new_name, new_model, new_color, new_stock_status, product_id))
        print(f"\nProduct ID: {product_id} updated successfully.")

    @staticmethod
    def delete_product():
        product_id = input("Product ID: ")
        db.execute("DELETE FROM Products WHERE product_id=%s", (product_id,))
        print(f"\nProduct ID: {product_id} deleted successfully.")

# OPTOMETRIST
class Optometrist(User):
    def view_patients(self):
        customers = db.query("SELECT * FROM Customers")
        print_table(customers, "Patients")

    def add_prescription(self):
        customer_id = input("Customer ID: ")
        notes = input("Prescription Notes: ")
        db.execute("""
            INSERT INTO Prescriptions (employee_id, customer_id, prescription_notes)
            VALUES (%s, %s, %s)
        """, (self.id, customer_id, notes))
        print("\nPrescription added successfully.")

    def view_schedule(self):
        schedule = db.query("""
            SELECT a.appointment_id, c.customer_name, c.customer_email, c.customer_cnum, 
                   a.appointment_date, a.appointment_time, e.employee_name AS optometrist_name
            FROM Appointments a
            JOIN Customers c ON a.customer_id = c.customer_id
            JOIN Employees e ON a.employee_id = e.employee_id
            WHERE a.employee_id=%s
        """, (self.id,))
        print_table(schedule, "Schedule")

# SALES ASSOCIATE
class SalesAssociate(User):
    def add_customer(self):
        try:
            customer_name = input_not_empty("Customer Name: ")
            customer_email = input_not_empty("Customer Email: ")
            customer_contact = input_not_empty("Customer Contact Number: ")
            db.execute("""
                INSERT INTO Customers (customer_name, customer_email, customer_cnum)
                VALUES (%s, %s, %s)
            """, (customer_name, customer_email, customer_contact))
            print(f"\nCustomer {customer_name} added successfully.")
        except ValueError as error:
            print(error)

    def view_customers(self):
        customers = db.query("SELECT * FROM Customers")
        print_table(customers, "Customers")

    def create_appointment(self):
        optometrists = db.query("SELECT * FROM Employees WHERE employee_role='Optometrist'")
        print_table(optometrists, "Optometrists")

        optometrist_id = input("Assign Optometrist ID: ")
        customer_id = input("Customer ID: ")

        while True:
            try:
                date_str = input("\nEnter reservation date (DD-MM-YYYY): ")
                time_str = input("Enter reservation time (HH:MM): ")
                appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")

                if appointment_datetime < datetime.now():
                    print("\nReservation cannot be in the past. Please enter a future date/time.")
                    continue

                db.execute("""
                    INSERT INTO Appointments (customer_id, employee_id, appointment_date, appointment_time)
                    VALUES (%s, %s, %s, %s)
                """, (customer_id, optometrist_id,
                      appointment_datetime.date(), appointment_datetime.time()))
                print("\nAppointment scheduled successfully.")
                break
            except ValueError:
                print("\nInvalid date or time format.")

    def view_appointments(self):
        appointments = db.query("""
            SELECT a.appointment_id, c.customer_name, c.customer_email, c.customer_cnum, 
                   a.appointment_date, a.appointment_time, e.employee_name AS optometrist_name
            FROM Appointments a
            JOIN Customers c ON a.customer_id = c.customer_id
            JOIN Employees e ON a.employee_id = e.employee_id
        """)
        print_table(appointments, "Appointments")

    def track_orders(self):
        print("""
 1) Create Order
 2) Update Order Status
 3) View Orders
""")
        choice = input("Choose: ").strip()
        if choice == "1":
            customer_id = input("Customer ID: ")
            product_id = input("Product ID: ")
            db.execute("INSERT INTO Orders (customer_id, product_id, order_status) VALUES (%s,%s,'Pending')",
                       (customer_id, product_id))
            last_id = db.query("SELECT LAST_INSERT_ID() AS id")[0]["id"]
            print(f"\nOrder ID: {last_id} created successfully.")

            # --- Save receipt ---
            customer_name = db.query("SELECT customer_name FROM Customers WHERE customer_id=%s", (customer_id,))[0]["customer_name"]
            product_name = db.query("SELECT product_name FROM Products WHERE product_id=%s", (product_id,))[0]["product_name"]
            save_order_receipt(last_id, product_name, customer_name)
            print("Order receipt saved to file successfully.")

        elif choice == "2":
            order_id = input("Order ID: ")
            status = input("Update Order Status (Pending/Cancelled/Completed): ")
            db.execute("UPDATE Orders SET order_status=%s WHERE order_id=%s", (status, order_id))
            print(f"\nOrder ID: {order_id} updated successfully.")

        elif choice == "3":
            orders = db.query("SELECT * FROM Orders")
            print_table(orders, "Orders")
        else:
            print("\nInvalid choice.")

    def view_products(self):
        products = db.query("SELECT * FROM Products")
        print_table(products, "Products")

# LOGIN SYSTEM
def login():
    while True:
        print("""
 ===== LOGIN OPTIONS =====
 1) Admin
 2) Optometrist
 3) Sales Associate
""")
        choice = input("Choose: ").strip()
        if choice == "1":
            password = getpass("\nPassword: ").strip()
            if password == Admin.PASSWORD:
                return "Admin"
            print("\nWrong password.")
        elif choice in ("2", "3"):
            try:
                employee_id = int(input("\nEmployee ID: ").strip())
            except ValueError:
                print("\nEmployee ID must be a number.")
                continue

            password = getpass("Password: ").strip()
            user_data = db.query(
                "SELECT * FROM Employees WHERE employee_id=%s AND employee_pwd=%s",
                (employee_id, password)
            )
            if user_data:
                user = user_data[0]
                if choice == "2" and user["employee_role"] == "Optometrist":
                    return Optometrist(user["employee_id"], user["employee_name"], user["employee_role"])
                if choice == "3" and user["employee_role"] == "Sales Associate":
                    return SalesAssociate(user["employee_id"], user["employee_name"], user["employee_role"])
            print("\nInvalid credentials.")
        else:
            print("\nInvalid choice.")

# MAIN PROGRAM
def main():
    while True:
        user = login()
        if user == "Admin":
            while True:
                print("""
 ===== ADMIN MENU =====
 1) Employees
 2) Products
 3) Logout
""")
                choice = input("Choose: ").strip()
                if choice == "1":
                    while True:
                        print("""
 ===== EMPLOYEE MANAGEMENT =====
 1) Add Employee
 2) View Employees
 3) Update Employee
 4) Delete Employee
 5) Back to Admin Menu
""")
                        employee_choice = input("Choose: ").strip()
                        match employee_choice:
                            case "1": Admin.add_employee()
                            case "2": Admin.view_employees()
                            case "3": Admin.update_employee()
                            case "4": Admin.delete_employee()
                            case "5": break
                            case _: print("\nInvalid choice.")
                elif choice == "2":
                    while True:
                        print("""
 ===== PRODUCT MANAGEMENT =====
 1) Add Product
 2) View Products
 3) Update Product
 4) Delete Product
 5) Back to Admin Menu
""")
                        product_choice = input("Choose: ").strip()
                        match product_choice:
                            case "1": Admin.add_product()
                            case "2": Admin.view_products()
                            case "3": Admin.update_product()
                            case "4": Admin.delete_product()
                            case "5": break
                            case _: print("\nInvalid choice.")
                elif choice == "3":
                    break
                else:
                    print("\nInvalid choice.")

        elif isinstance(user, Optometrist):
            while True:
                print("""
 ===== OPTOMETRIST MENU =====
 1) View Schedule
 2) View Patients
 3) Add Prescription Notes
 4) Logout
""")
                choice = input("Choose: ").strip()
                match choice:
                    case "1": user.view_schedule()
                    case "2": user.view_patients()
                    case "3": user.add_prescription()
                    case "4": break
                    case _: print("\nInvalid choice.")

        elif isinstance(user, SalesAssociate):
            while True:
                print("""
 ===== SALES ASSOCIATE MENU =====
 1) Add Customer
 2) View Customers
 3) Create Appointment
 4) View Appointments
 5) Track Orders
 6) Track Products
 7) Logout
""")
                choice = input("Choose: ").strip()
                match choice:
                    case "1": user.add_customer()
                    case "2": user.view_customers()
                    case "3": user.create_appointment()
                    case "4": user.view_appointments()
                    case "5": user.track_orders()
                    case "6": user.view_products()
                    case "7": break
                    case _: print("\nInvalid choice.")

if __name__ == "__main__":
    main()
