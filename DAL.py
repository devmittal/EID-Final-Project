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
    """To Insert Data into the Object Table"""
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
    """To Insert Data into the Command Table"""
    try:
        connection = OpenConnection()

        query = "INSERT into command (received, state) VALUES (%s, %s)"
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

def GetCommandData():
    """Fetch the count of valid and invalid commands from the command table"""
    try:
        connection = OpenConnection()

        query = "select state, count(*) from command group by state order by state asc"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

    except Error as e:
        print("Error while fetching Voice Command Data from Command Table", e)
        result = None

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()

        return result

def GetObjectData():
    """Fetch the count of valid and invalid objects detected from the object table"""
    try:
        connection = OpenConnection()

        query = "select state, count(*) from object group by state order by state asc"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

    except Error as e:
        print("Error while fetching Object Detection Data from Object Table", e)
        result = None

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()

        return result

def FetchObjectTableData(count=10):
    """Fetch label and state data from object table"""
    try:
        connection = OpenConnection()

        query = "select label,state from object order by entrytimestamp desc limit " + str(count)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

    except Error as e:
        print("Error while fetching data from Object Table", e)
        result = None

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()

        return result
        
def FetchCommandTableData(count=10):
    """Fetch command and state data from command table"""
    try:
        connection = OpenConnection()

        query = "select received,state from command order by entrytimestamp desc limit " + str(count)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

    except Error as e:
        print("Error while fetching data from Command Table", e)
        result = None

    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()

        return result

def GetObjectTable(count=10):
    """Convert Object Data from Table into string from tuple"""
    result = FetchObjectTableData()
    cat = ""
    for i in range(count):
        if i < 9:
            cat += str(result[i][0]) + "-" + str(result[i][1]) + ","
        else:
            cat += str(result[i][0]) + "-" + str(result[i][1])
    return cat

def GetCommandTable(count=10):
    """Convert Command Data from Table into string from tuple"""
    result = FetchCommandTableData()
    cat = ""
    for i in range(count):
        if i < 9:
            cat += str(result[i][0]) + "-" + str(result[i][1]) + ","
        else:
            cat += str(result[i][0]) + "-" + str(result[i][1])
    return cat
