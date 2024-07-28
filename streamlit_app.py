import os

import streamlit as st
import mysql.connector
from mysql.connector import Error
import pyodbc

# Initialize session state variables for navigation and storing inputs
if 'page' not in st.session_state:
    st.session_state.page = "Welcome"
if 'customer_email' not in st.session_state:
    st.session_state.customer_email = ""
if 'staff_id' not in st.session_state:
    st.session_state.staff_id = ""
if 'staff_password' not in st.session_state:
    st.session_state.staff_password = ""
if 'customer_info' not in st.session_state:
    st.session_state.customer_info = None
if 'appointments' not in st.session_state:
    st.session_state.appointments = None
if 'staff_info' not in st.session_state:
    st.session_state.staff_info = None
if 'customers' not in st.session_state:
    st.session_state.customers = None

# Function to navigate between pages
def navigate_to(page):
    st.session_state.page = page

# Function to go back to the previous page
def go_back():
    if st.session_state.page == "Customer Home":
        st.session_state.page = "Customer Login"
    elif st.session_state.page == "Customer Info":
        st.session_state.page = "Customer Home"
    elif st.session_state.page == "Staff Home":
        st.session_state.page = "Staff Login"
    elif st.session_state.page == "Staff Options":
        st.session_state.page = "Staff Home"
    elif st.session_state.page == "View Appointments":
        st.session_state.page = "Staff Home"
    elif st.session_state.page == "View Customers":
        st.session_state.page = "Staff Home"
    else:
        st.session_state.page = "Welcome"

# Function to connect to the database
def create_connection():
    connection_string = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER=tcp:warmspeaker.database.windows.net,1433;'
        f'DATABASE=CarWash;'
        f'UID=Wazaah;'
        f'PWD=Warmspeaker.12;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )
    try:
        connection = pyodbc.connect(connection_string)
        return connection
    except pyodbc.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to fetch customer info by email
def fetch_customer_info(email):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT 
            c.CustomerID, 
            c.FirstName, 
            c.LastName, 
            c.Email, 
            c.PhoneNumber,
            v.Make AS CarMake,
            v.Model AS CarModel,
            v.Year AS CarYear,
            a.AppointmentDate,
            a.Status AS AppointmentStatus
        FROM 
            Customers c
        LEFT JOIN 
            Vehicles v ON c.CustomerID = v.CustomerID
        LEFT JOIN 
            Appointments a ON c.CustomerID = a.CustomerID
        WHERE 
            c.Email = ?
        """
        cursor.execute(query, (email,))
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return result
    return None

# Function to authenticate staff
def authenticate_staff(staff_id, password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        # Check if the staff ID exists
        check_id_query = "SELECT * FROM Employees WHERE EmployeeID = ?"
        cursor.execute(check_id_query, (staff_id,))
        staff_record = cursor.fetchone()

        if staff_record:
            staff_record = dict(zip([column[0] for column in cursor.description], staff_record))
            # Staff ID exists, now check the password
            if staff_record['Password'] == password:
                cursor.close()
                connection.close()
                return "authenticated", staff_record
            else:
                cursor.close()
                connection.close()
                return "incorrect_password", None
        else:
            cursor.close()
            connection.close()
            return "id_not_found", None
    return None, None

# Function to fetch all appointments for staff view
def fetch_staff_appointments(staff_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = """
        SELECT 
            a.AppointmentID,
            c.FirstName,
            c.LastName,
            c.Email,
            v.Make AS CarMake,
            v.Model AS CarModel,
            v.Year AS CarYear,
            a.AppointmentDate,
            a.Status AS AppointmentStatus
        FROM 
            Appointments a
        JOIN 
            Customers c ON a.CustomerID = c.CustomerID
        JOIN 
            Vehicles v ON c.CustomerID = v.CustomerID
        JOIN 
            EmployeeAppointments ea ON a.AppointmentID = ea.AppointmentID
        WHERE 
            ea.EmployeeID = ?
        """
        cursor.execute(query, (staff_id,))
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return result
    return None

# Function to fetch all customers for staff view
def fetch_all_customers():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM Customers"
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return result
    return None

# Function to add a new customer
# Function to add a new customer
def add_customer(first_name, last_name, email, phone_number):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        add_query = """
        INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(add_query, (first_name, last_name, email, phone_number))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False


# Function to update customer details
# Function to update customer details
def update_customer(customer_id, first_name, last_name, email, phone_number):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        update_query = """
        UPDATE Customers
        SET FirstName = ?, LastName = ?, Email = ?, PhoneNumber = ?
        WHERE CustomerID = ?
        """
        cursor.execute(update_query, (first_name, last_name, email, phone_number, customer_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False


# Function to update appointment status
def update_appointment_status(appointment_id, status):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        update_query = """
        UPDATE Appointments
        SET Status = ?
        WHERE AppointmentID = ?
        """
        cursor.execute(update_query, (status, appointment_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False

# Function to display staff home page
def display_staff_home():
    st.title("Staff Home")
    st.write(f"Welcome, {st.session_state.staff_info['FirstName']} {st.session_state.staff_info['LastName']}")
    if st.button("View And Manage Appointments"):
        st.session_state.page = "View Appointments"
    if st.button("View And Manage Customers"):
        st.session_state.page = "View Customers"
    if st.button("Back"):
        go_back()

# Function to display all appointments for staff
def display_appointments():
    st.title("Manage Appointments")
    appointments = st.session_state.appointments
    if appointments:
        for appointment in appointments:
            st.subheader(f"Appointment Date: {appointment['AppointmentDate']}")
            st.write(f"Customer Name: {appointment['FirstName']} {appointment['LastName']}")
            st.write(f"Email: {appointment['Email']}")
            st.write(f"Car Make: {appointment['CarMake']}")
            st.write(f"Car Model: {appointment['CarModel']}")
            st.write(f"Car Year: {appointment['CarYear']}")
            st.write(f"Appointment Status: {appointment['AppointmentStatus']}")
            new_status = st.selectbox(f"Update Status for Appointment Date: {appointment['AppointmentDate']}", ["Scheduled", "Completed", "Cancelled"], index=["Scheduled", "Completed", "Cancelled"].index(appointment['AppointmentStatus']))
            if st.button(f"Update Status for {appointment['AppointmentDate']}"):
                if update_appointment_status(appointment['AppointmentID'], new_status):
                    st.success(f"Status for Appointment Date: {appointment['AppointmentDate']} updated successfully!")
                    st.session_state.appointments = fetch_staff_appointments(st.session_state.staff_info['EmployeeID'])  # Refresh the appointments
                    st.rerun()  # Reload the page to show updated status
                else:
                    st.error("Failed to update status. Please try again.")
    if st.button("Back"):
        go_back()

# Function to display all customers for staff
def display_customers():
    st.title("Manage Customers")
    customers = st.session_state.customers
    if customers:
        for customer in customers:
            st.subheader(f"Customer ID: {customer['CustomerID']}")
            st.write(f"First Name: {customer['FirstName']}")
            st.write(f"Last Name: {customer['LastName']}")
            st.write(f"Email: {customer['Email']}")
            st.write(f"Phone Number: {customer['PhoneNumber']}")
            if st.button(f"Edit Details for {customer['CustomerID']}"):
                st.session_state.page = f"Edit Customer {customer['CustomerID']}"
    if st.button("Add New Customer"):
        st.session_state.page = "Add Customer"
    if st.button("Back"):
        go_back()

# Function to add a new customer
# Function to add a new customer
def add_customer_page():
    st.title("Add New Customer")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number")
    if st.button("Add Customer"):
        if add_customer(first_name, last_name, email, phone_number):
            st.success("Customer added successfully!")
            st.session_state.customers = fetch_all_customers()  # Refresh the customers list
            st.session_state.page = "View Customers"
            st.rerun()
        else:
            st.error("Failed to add customer. Please try again.")
    if st.button("Back"):
        go_back()


# Function to edit customer details
# Function to edit customer details
def edit_customer_page(customer_id):
    st.title("Edit Customer Details")
    customer = next((cust for cust in st.session_state.customers if cust['CustomerID'] == customer_id), None)
    if customer:
        first_name = st.text_input("First Name", value=customer['FirstName'])
        last_name = st.text_input("Last Name", value=customer['LastName'])
        email = st.text_input("Email", value=customer['Email'])
        phone_number = st.text_input("Phone Number", value=customer['PhoneNumber'])
        if st.button("Update Customer"):
            if update_customer(customer_id, first_name, last_name, email, phone_number):
                st.success("Customer details updated successfully!")
                st.session_state.customers = fetch_all_customers()  # Refresh the customers list
                st.session_state.page = "View Customers"
                st.rerun()
            else:
                st.error("Failed to update customer details. Please try again.")
    else:
        st.error("Customer not found.")
    if st.button("Back"):
        go_back()


# Welcome Screen
if st.session_state.page == "Welcome":
    st.title("I am a:")
    if st.button("CUSTOMER"):
        navigate_to("Customer Login")
    if st.button("STAFF"):
        navigate_to("Staff Login")

# Customer Login Screen
elif st.session_state.page == "Customer Login":
    st.title("Customer Login")
    email = st.text_input("Email")
    if st.button("Login"):
        customer_info = fetch_customer_info(email)
        if customer_info:
            st.session_state.customer_info = customer_info
            st.session_state.page = "Customer Home"
        else:
            st.error("Invalid email or customer not found.")
    if st.button("Back"):
        go_back()

# Customer Home Screen
elif st.session_state.page == "Customer Home":
    st.title("Customer Home")
    customer_info = st.session_state.customer_info
    if customer_info:
        st.write(f"Welcome, {customer_info[0]['FirstName']} {customer_info[0]['LastName']}")
        if st.button("View Info"):
            st.session_state.page = "Customer Info"
    if st.button("Back"):
        go_back()

# Customer Info Screen
elif st.session_state.page == "Customer Info":
    st.title("Customer Information")
    customer_info = st.session_state.customer_info
    if customer_info:
        for info in customer_info:
            st.subheader(f"Appointment Date: {info['AppointmentDate']}")
            st.write(f"First Name: {info['FirstName']}")
            st.write(f"Last Name: {info['LastName']}")
            st.write(f"Email: {info['Email']}")
            st.write(f"Phone Number: {info['PhoneNumber']}")
            st.write(f"Car Make: {info['CarMake']}")
            st.write(f"Car Model: {info['CarModel']}")
            st.write(f"Car Year: {info['CarYear']}")
            st.write(f"Appointment Status: {info['AppointmentStatus']}")
    if st.button("Back"):
        go_back()

# Staff Login Screen
elif st.session_state.page == "Staff Login":
    st.title("Staff Login")
    staff_id = st.text_input("Staff ID")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if staff_id.isnumeric():
            auth_status, staff_info = authenticate_staff(staff_id, password)
            if auth_status == "authenticated":
                st.session_state.staff_info = staff_info
                st.session_state.page = "Staff Home"
            elif auth_status == "incorrect_password":
                st.error("Incorrect password. Please try again.")
            elif auth_status == "id_not_found":
                st.error("Staff ID not found.")
        else:
            st.error("Staff ID must be a number.")
    if st.button("Back"):
        go_back()

# Staff Home Screen
elif st.session_state.page == "Staff Home":
    display_staff_home()

# View and Manage Appointments Screen
elif st.session_state.page == "View Appointments":
    if st.session_state.appointments is None:
        st.session_state.appointments = fetch_staff_appointments(st.session_state.staff_info['EmployeeID'])
    display_appointments()

# View and Manage Customers Screen
elif st.session_state.page == "View Customers":
    if st.session_state.customers is None:
        st.session_state.customers = fetch_all_customers()
    display_customers()

# Add Customer Screen
elif st.session_state.page == "Add Customer":
    add_customer_page()

# Edit Customer Screen
elif "Edit Customer" in st.session_state.page:
    customer_id = int(st.session_state.page.split(" ")[-1])
    edit_customer_page(customer_id)
