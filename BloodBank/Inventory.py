from database import db_query, mydb  # Ensure the database connection setup is correct

class Inventory:

    @staticmethod
    def add_blood(blood_type, quantity=1):
        try:
            # Query to check the current quantity of the specified blood type
            query = f"""SELECT quantity FROM inventory WHERE blood_type = "{blood_type}";"""
            result = db_query(query)

            # If no record exists, insert a new record for that blood type
            if not result:
                print(f"No record found for blood type {blood_type}. Adding new record.")
                query = f"""INSERT INTO inventory (blood_type, quantity) VALUES ("{blood_type}", {quantity});"""
                db_query(query)
                mydb.commit()
                print(f"Added {quantity} units of {blood_type}.")
            else:
                # If a record exists, update the quantity
                current_quantity = result[0][0]
                print(f"Current quantity of {blood_type}: {current_quantity}")
                updated_quantity = current_quantity + quantity
                query = f"""UPDATE inventory SET quantity = {updated_quantity} WHERE blood_type = "{blood_type}";"""
                db_query(query)
                mydb.commit()
                print(f"Updated quantity of {blood_type} to {updated_quantity}.")

        except Exception as e:
            print(f"An error occurred while adding blood: {e}")

    @staticmethod
    def deduct_blood(blood_type, quantity=1):
        try:
            # Query to check the current quantity of the specified blood type
            query = f"""SELECT quantity FROM inventory WHERE blood_type = "{blood_type}";"""
            result = db_query(query)

            # If no record exists, print a message and return
            if not result:
                print(f"No record found for blood type {blood_type}. Cannot deduct blood.")
                return

            current_quantity = result[0][0]
            print(f"Current quantity of {blood_type}: {current_quantity}")

            if current_quantity < quantity:
                print(f"Sorry, not sufficient blood available for {blood_type}.")
            else:
                # If sufficient blood is available, deduct the quantity
                updated_quantity = current_quantity - quantity
                query = f"""UPDATE inventory SET quantity = {updated_quantity} WHERE blood_type = "{blood_type}";"""
                db_query(query)
                mydb.commit()
                print(f"Deducted {quantity} units of {blood_type}. Updated quantity is {updated_quantity}.")

        except Exception as e:
            print(f"An error occurred while deducting blood: {e}")

#123456789