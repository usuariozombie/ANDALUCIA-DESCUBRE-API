# -*- coding: utf-8 -*-

import contextlib, hashlib, mysql.connector
from utils.files import JSON

class MySQL():

	def AddItem(Table : str, Columns : list, Values):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		ColumnsSTR = ", ".join(Columns)
		Placeholders = ", ".join(["%s"] * len(Values))
		SQLCursor.execute(f"INSERT INTO {Table} ({ColumnsSTR}) VALUES ({Placeholders})", Values)
		SQLConnection.commit()
		SQLConnection.close()

	def Connect() -> mysql.connector.connection.MySQLConnection:
		Config : dict = JSON.Read("config.json")
		return mysql.connector.connect(database = Config["mysql"]["database"], host = Config["mysql"]["host"], user = Config["mysql"]["user"], password = Config["mysql"]["password"])

	def FetchAll(Query, Params = None):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(Query, Params)
		SQLResults = SQLCursor.fetchall()
		SQLConnection.close()
		return SQLResults
	
	def FetchOne(Query, Params=None):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(Query, Params)
		SQLResult = SQLCursor.fetchone()
		SQLConnection.close()
		return SQLResult

	def GetLastID(Table : str, Row : str) -> int:
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(f"SELECT * FROM {Table} ORDER BY {Row} DESC LIMIT 1;")
		SQLResult = SQLCursor.fetchone()[0]
		SQLConnection.close()
		return SQLResult

	def GetValueFor(Table : str, Get : str, Row : str, Value):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(f"SELECT {Get} FROM {Table} WHERE {Row} = %s", (Value,))
		SQLResult = SQLCursor.fetchone()[0]
		SQLConnection.close()
		return SQLResult

	def LogError(Endpoint : str, UserID, UserIP : str, LogDate : int, Error, Type : str):
		with contextlib.suppress(Exception): # esto evita que haga un raise a cualquier tipo de error, porque literalmente no queremos un error al logear un error, duh.
			SQLConnection = MySQL.Connect()
			SQLCursor = SQLConnection.cursor()
			SQLCursor.execute(f"INSERT INTO AD_USERS (userID, userIP, logDate, description, type) VALUES (%s, %s, %s, %s, %s)", (UserID, UserIP, LogDate, Error, Type))
			SQLConnection.commit()
			SQLConnection.close()

	def Register(UserID: int, UserIP: str, Email: str, Password: str, TownID: int, Dates: str, Role: str = "user"):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(
			"INSERT INTO AD_USERS (userID, userIP, email, password, townID, dates, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
			(UserID, UserIP, Email, Password, TownID, Dates, Role)
		)
		SQLConnection.commit()
		SQLConnection.close()

	def ValueExists(Table : str, Row : str, Value) -> int:
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(f"SELECT {Row} FROM {Table} WHERE {Row} = %s", (Value,))
		SQLResult = SQLCursor.fetchone()
		SQLConnection.close()
		return False if SQLResult == None else True

	def AddTown(TownID: int, TownName: str, TownDesc: str, TownImage: str, TownMap: str, TownProvince: str, TownVisibility: bool):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(
			"INSERT INTO AD_TOWNS (townId, townName, townDescription, townImage, townMap, townProvince, townVisibility) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
			(TownID, TownName, TownDesc, TownImage, TownMap, TownProvince, TownVisibility)
		)
		SQLConnection.commit()
		SQLConnection.close()

	def UpdateItem(Table: str, Columns: list, Values: list, Condition: str, ConditionValues: tuple):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()

		ColumnsSTR = ", ".join([f"{col} = %s" for col in Columns])

		query = f"UPDATE {Table} SET {ColumnsSTR} WHERE {Condition} = %s"
		parameters = Values + list(ConditionValues)

		try:
			SQLCursor.execute(query, parameters)
			SQLConnection.commit()
		except mysql.connector.Error as err:
			print(f"Error: {err}")
		finally:
			SQLCursor.close()
			SQLConnection.close()

	def Delete(Table: str, Row: str, Value):
		SQLConnection = MySQL.Connect()
		SQLCursor = SQLConnection.cursor()
		SQLCursor.execute(f"DELETE FROM {Table} WHERE {Row} = %s", (Value,))
		SQLConnection.commit()
		SQLConnection.close()
