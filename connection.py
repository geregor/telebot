from adds import connect

def register(user_id):
	connection = connect()
	try:
		with connection.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM tbot WHERE user_id={user_id}")
			row = cursor.fetchone()
			if result == 0:
				cursor.execute(f"INSERT INTO tbot(user_id) VALUES({user_id})")
				connection.commit()
			else:
				return row
	finally:
		connection.close()