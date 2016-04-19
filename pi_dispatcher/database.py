#!/bin/python

import sqlite3
import sys


sqlite_file = 'doorUnlocker.sqlite'    # name of the sqlite database file
def getCursor():
    # Connecting to the database file
    try:
        conn = sqlite3.connect(sqlite_file)
    except: 
        createDatabase()
        conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    return (conn, c)

def closeCursor( conn ):
    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

def createDatabase():
    table_name1 = 'cards'  # name of the table to be created
    new_field = 'card' # name of the column
    field_type = 'varchar(16)'  # column data type
    (conn, c ) =getCursor()
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
                    .format(tn=table_name1, nf=new_field, ft=field_type))
    closeCursor(conn)


    def hasCard( cardValue ):
        (conn, c ) =getCursor()
        c.execute('SELECT COUNT(*) FROM cards WHERE card = {cv}'\
                        .format(cv=cardValue))
        rv = c.fetchall()
        closeCursor(conn)
        return (rv[0][0] == 1)

    def addCard( cardValue ):
        if hasCard(cardValue):
            return
        (conn, c) =getCursor()
        c.execute('INSERT into cards (card) VALUE ( {cv})'\
                        .format(cv=cardValue))
        closeCursor(conn)
        return 


if __
