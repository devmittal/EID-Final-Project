"""
	__file__ = DAL.py
	__description = Database access layer for inserting and retrieving data pertaining to AWS Label & Commands
	__author__ = Souvik De, Devansh Mittal
	__reference__ = https://pynative.com/python-mysql-select-query-to-fetch-data/
"""

import mysql.connector as mariadb
from mysql.connector import Error

def OpenConnection():
    """Returns connection string for the DB"""
    return mariadb.connect(host='localhost',
                           database='project1db',
                           user='demit',
                           password='vickmit')

def InsertToObject(label, state):
    try:
        connection = OpenConnection()

        query = "INSERT into object (label, state) VALUES (%s, %s)"
        values = (label, state)

        cursor = connection.cursor()
        result = cursor.execute(query, values)
        connection.commit()
        print("Successfully inserted data to Object Table")

    except Error as e:
        print("Error while inseting data to Object Table", e)

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()

def InsertToCommand(received_command, state):
    try:
        connection = OpenConnection()

        query = "INSERT into object (received, state) VALUES (%s, %s)"
        values = (received_command, state)

        cursor = connection.cursor()
        result = cursor.execute(query, values)
        connection.commit()
        print("Successfully inserted data to Command Table")

    except Error as e:
        print("Error while inseting data to Command Table", e)

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()