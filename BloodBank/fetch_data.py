import mysql.connector

# Connect to your database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="1234",
    database="bloodbank"
)

cursor = conn.cursor()

# Query to fetch data from the table
cursor.execute("SELECT * FROM your_table_name")  # Replace 'your_table_name' with your actual table name

# Fetch all rows
rows = cursor.fetchall()

# Check if any data was fetched
if rows:
    print("Data from table:")
    for row in rows:
        print(row)  # This will print each row
else:
    print("No data found in the table.")

# Close the connection
cursor.close()
conn.close()
