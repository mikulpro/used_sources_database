import mysql.connector

cnx = mysql.connector.connect(
  user='user', 
  password='password',
  host='db',   # Use the service name defined in docker-compose
  database='mydatabase'
)

# Don't forget to close the connection when done
cnx.close()