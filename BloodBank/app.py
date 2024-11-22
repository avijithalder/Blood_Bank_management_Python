import sqlite3

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from BloodBank import BloodBank
from database import mydb, cursor
import mysql.connector as sql

app = Flask(__name__)
app.secret_key = "1234"  # Required for flash messages


# Function to execute SQL queries
def db_query(query, params=None):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Database query error: {str(e)}")
        return None


##############################################  update inventory section

def update_inventory_quantity(blood_type, quantity_change):
    try:
        # Query to fetch current quantity of the blood type
        query = "SELECT quantity FROM inventory WHERE blood_type = %s"
        result = db_query(query, (blood_type,))

        if not result:
            # If no record exists, insert a new record for the blood type
            query = "INSERT INTO inventory (blood_type, quantity) VALUES (%s, %s)"
            db_query(query, (blood_type, quantity_change))
            mydb.commit()
        else:
            # If a record exists, update the quantity
            current_quantity = result[0][0]
            updated_quantity = current_quantity + quantity_change
            query = "UPDATE inventory SET quantity = %s WHERE blood_type = %s"
            db_query(query, (updated_quantity, blood_type))
            mydb.commit()

    except Exception as e:
        print(f"Error updating inventory: {str(e)}")


###############################################   update inventory section
# delete section
###############################################################################
##########################&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&   123

def delete_request(request_id):
    try:
        # Check if request exists
        cursor1.execute("SELECT * FROM request WHERE request_id = %s", (request_id,))
        request2 = cursor1.fetchone()

        if request2:
            # Request exists, proceed to delete
            cursor1.execute("DELETE FROM request WHERE request_id = %s", (request_id,))
            mydb1.commit()
            return f"Request with ID {request_id} has been deleted successfully."
        else:
            return f"No request found with ID {request_id}."

    except sql.Error as err:
        return f"Error occurred: {err}"


# Route to delete a request
@app.route('/delete_request/<int:request_id>', methods=['DELETE'])
def delete_request_data(request_id):
    result = delete_request(request_id)
    success = "has been deleted successfully" in result
    return jsonify({"success": success, "message": result})


#############&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&


############################&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
mydb1 = sql.connect(
    host="localhost",
    user="root",
    passwd="1234",
    database="bloodbank"
)
cursor1 = mydb1.cursor()


# Function to delete a donor from the donor table
def delete_donor(donor_id):
    try:
        # Check if donor exists
        cursor1.execute("SELECT * FROM donor WHERE donor_id = %s", (donor_id,))
        donor = cursor1.fetchone()

        if donor:
            # Get the blood type before deleting donor
            blood_type = donor[3]  # Assuming blood_type is the 4th column

            # Donor exists, proceed to delete
            cursor1.execute("DELETE FROM donor WHERE donor_id = %s", (donor_id,))
            mydb1.commit()

            # Update inventory after deleting donor (decrease quantity)
            update_inventory_quantity(blood_type, -1)  # Subtract 1 unit from the inventory

            return f"Donor with ID {donor_id} has been deleted successfully."
        else:
            return f"No donor found with ID {donor_id}."

    except sql.Error as err:
        return f"Error occurred: {err}"


# Route to delete a donor
@app.route('/delete_donor/<int:donor_id>', methods=['DELETE'])
def delete_donor_route(donor_id):
    result = delete_donor(donor_id)
    success = "has been deleted successfully" in result
    return jsonify({"success": success, "message": result})


#########&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

############################################################################
# delete section
######
@app.route('/main')
def home_page():
    return render_template('main.html')  # This will render the 'main.html' template


########################################################################################################################

@app.route('/admin')
def admin():
    return render_template('admin.html')


# Logout route: Clears session and redirects to the admin page
@app.route('/logout')
def logout():
    session.clear()  # Clears the session (you can also delete cookies if using token-based auth)
    return redirect(url_for('admin'))


######################################################################################################################


# Route for the admin login page
@app.route('/')
def home():
    return render_template('admin.html')  # Renders admin.html for login


# Route for handling login form submission
@app.route('/login', methods=['POST'])
def login():
    userid = request.form.get('userid')
    password = request.form.get('password')

    # Query to verify admin credentials
    query = "SELECT * FROM admin WHERE userid = %s AND password = %s"
    cursor.execute(query, (userid, password))
    result = cursor.fetchone()

    if result:
        return redirect(url_for('main'))  # Redirect to the main page upon successful login
    else:
        flash("Invalid User ID or Password. Please try again.", "error")  # Error feedback
        return redirect('/')  # Redirect back to the login page


# Route for the main page after login
@app.route('/main')
def main():
    return render_template('main.html')  # Ensure this template exists in the `templates` folder


############################################################################################################################


# Function to fetch request data from the database
def get_request_data():
    query = """
    SELECT request_id, hospital_name, patient_name, patient_age, 
           patient_blood_type, donor_name, donor_age, donor_blood_type
    FROM request
    """
    return db_query(query)


@app.route('/request_data')
def request_data():
    # Fetch request data using the helper function
    requests = get_request_data()
    # Pass the data to the template
    return render_template('request_data.html', requests=requests)


##########################################################################################


#######################################################################################
# Function to fetch donor data from the database
def get_donors():
    query = "SELECT donor_id, donor_name, donor_age, donor_blood_type FROM donor"
    return db_query(query)


# Route to display the donor list
@app.route('/donor_list')
def donor_list():
    # Fetch donor data from the database
    donors = get_donors()
    return render_template('donor_list.html', donors=donors)


########^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Route to display inventory data
@app.route('/inventory')
def inventory():
    # Query to fetch inventory data
    query = "SELECT DISTINCT blood_type, quantity FROM inventory ORDER BY quantity DESC"
    inventory_data = db_query(query)
    # Render inventory page with fetched data
    return render_template('inventory.html', inventory_data=inventory_data)


######*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# Home route
@app.route('/index')
def index():
    return render_template('main.html')


@app.route('/add_donor', methods=['GET'])
def render_add_donor():
    return render_template('add_donor.html')


# Route to add a donor
@app.route('/add_donor', methods=['POST'])
def add_donor():
    if request.method == 'POST':
        donor_name = request.form['donor_name']
        donor_age = request.form['donor_age']
        blood_type = request.form['blood_type']

        try:
            donor_age = int(donor_age)
        except ValueError:
            return "Invalid age format. Please enter a valid integer for age.", 400

        # Save donor details in the database using BloodBank class
        BloodBank.donor_details(donor_name, donor_age, blood_type)

        # Update inventory after adding donor
        update_inventory_quantity(blood_type, 1)  # Add 1 unit of the blood type to the inventory

        # Redirect to home page after adding the donor
        return redirect(url_for("add_donor"))


@app.route('/request_blood', methods=['GET'])
def render_request_blood():
    return render_template('request_blood.html')


# Route to request blood
@app.route('/request_blood', methods=['POST'])
def request_blood():
    if request.method == 'POST':
        hospital_name = request.form['hospital_name']
        patient_name = request.form['patient_name']
        patient_age = request.form['patient_age']
        patient_blood_type = request.form['patient_blood_type']
        donor_name = request.form['donor_name']
        donor_age = request.form['donor_age']
        donor_blood_type = request.form['donor_blood_type']

        try:
            patient_age = int(patient_age)
            donor_age = int(donor_age)
        except ValueError:
            return "Invalid age format. Please enter a valid integer for age.", 400

        ##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # Function to check blood type compatibility
        def check_blood_type_compatibility(patient_blood_type, donor_blood_type):
            # Dictionary of compatible blood types for each blood type
            compatibility = {
                'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
                'O+': ['O+', 'A+', 'B+', 'AB+'],
                'A-': ['A-', 'A+', 'AB-', 'AB+'],
                'A+': ['A+', 'AB+'],
                'B-': ['B-', 'B+', 'AB-', 'AB+'],
                'B+': ['B+', 'AB+'],
                'AB-': ['AB-', 'AB+'],
                'AB+': ['AB+']
            }

            # # Check if the donor's blood type is compatible with the patient's blood type
            # if donor_blood_type in compatibility.get(patient_blood_type, []):
            #     return True
            # return False

            # Check if the donor's blood type is compatible with the patient's blood type
            if patient_blood_type in compatibility.get(donor_blood_type, []):
                return True
            return False

        # Check blood type compatibility before proceeding
        if not check_blood_type_compatibility(patient_blood_type, donor_blood_type):
            flash("Blood types are not compatible! Please choose a compatible donor.", "error")
            return redirect(url_for('request_blood'))

        ##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # Call the BloodBank function to process the blood request
        BloodBank.request_blood(
            hospital_name, patient_name, patient_age, patient_blood_type,
            donor_name, donor_age, donor_blood_type
        )

        # Redirect to the home page after the request
        return redirect(url_for('request_blood'))
    return render_template('request_blood.html')


@app.route('/add_blood', methods=['POST'])
def add_blood():
    try:
        # Get data from the request body
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided."}), 400

        blood_type = data.get('blood_type')
        quantity = data.get('quantity')

        # Ensure blood_type and quantity are provided
        if not blood_type or not quantity:
            return jsonify({"message": "Blood type and quantity are required."}), 400

        try:
            quantity = int(quantity)
        except ValueError:
            return jsonify({"message": "Invalid quantity. Please enter a valid integer."}), 400

        # Query to check if the blood type exists in the database
        query = "SELECT quantity FROM inventory WHERE blood_type = %s"
        result = db_query(query, (blood_type,))

        if not result:
            # If no record exists, insert a new record
            query = "INSERT INTO inventory (blood_type, quantity) VALUES (%s, %s)"
            db_query(query, (blood_type, quantity))
            mydb.commit()
            return jsonify({"message": f"{quantity} units of {blood_type} added to inventory."}), 200
        else:
            # If a record exists, update the quantity
            current_quantity = result[0][0]
            updated_quantity = current_quantity + quantity
            query = "UPDATE inventory SET quantity = %s WHERE blood_type = %s"
            db_query(query, (updated_quantity, blood_type))
            mydb.commit()
            return jsonify({"message": f"Updated {blood_type} inventory to {updated_quantity} units."}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


# Route to serve the inventory management page (update_inventory.html)
@app.route('/update_inventory')
def update_inventory():
    return render_template('update_inventory.html')


if __name__ == '__main__':
    app.run(debug=True)

# 12345679
