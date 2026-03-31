import mysql.connector

#BEFORE RUNNING REPLACE "YOUR_MYSQL_PASSWORD" WITH YOUR ACTUAL MYSQL PASSWORD BUT DONT PUSH YOUR PASSWORD HERE LMAO


# This function creates and returns a connection to MySQL.
# Whenever we want to run a query, we will call this function.

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",              # MySQL server address
        user="root",                   # your MySQL username
        password="YOUR_MYSQL_PASSWORD",# replace with your actual MySQL password
        database="hospital_management" # the database we created
    )
    return connection