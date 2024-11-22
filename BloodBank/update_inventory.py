import tkinter as tk
from tkinter import messagebox
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


# Tkinter UI for adding blood quantity
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management")

        # Labels
        self.blood_type_label = tk.Label(root, text="Blood Type")
        self.blood_type_label.grid(row=0, column=0, padx=10, pady=10)

        self.quantity_label = tk.Label(root, text="Quantity")
        self.quantity_label.grid(row=1, column=0, padx=10, pady=10)

        # Entry fields
        self.blood_type_entry = tk.Entry(root)
        self.blood_type_entry.grid(row=0, column=1, padx=10, pady=10)

        self.quantity_entry = tk.Entry(root)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        # Submit button
        self.submit_button = tk.Button(root, text="Add Blood", command=self.add_blood_quantity)
        self.submit_button.grid(row=2, column=0, columnspan=2, pady=20)

    def add_blood_quantity(self):
        blood_type = self.blood_type_entry.get()
        quantity = self.quantity_entry.get()

        if not blood_type or not quantity:
            messagebox.showerror("Error", "Please fill in both fields")
            return

        try:
            quantity = int(quantity)
            Inventory.add_blood(blood_type, quantity)
            messagebox.showinfo("Success", f"{quantity} units of {blood_type} have been added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number!")


# Create the Tkinter root window and start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
