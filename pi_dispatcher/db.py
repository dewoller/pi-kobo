#!/bin/python
import sqlite3
import os.path


sqlite_file = 'doorUnlocker.sqlite'    # name of the sqlite database file
def getCursor():
    # Connecting to the database file
    if not os.path.isfile( sqlite_file):
        createDatabase()
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    return (conn, c)

def closeCursor( conn ):
    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

def createDatabase():
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('CREATE TABLE cards (card varchar(16) PRIMARY KEY)')
    closeCursor(conn)


def hasCard( cardValue ):
    (conn, c ) =getCursor()
    c.execute('SELECT COUNT(*) FROM cards WHERE card = ?', (cardValue,))
    rv = c.fetchall()
    closeCursor(conn)
    return (rv[0][0] == 1)

def addCard( cardValue ):
    if hasCard(cardValue):
        return
    (conn, c) =getCursor()
    c.execute('INSERT into cards (card) VALUES (?)', (cardValue,))
    closeCursor(conn)
    return 


def delCard( cardValue ):
    if not hasCard(cardValue):
        return
    (conn, c) =getCursor()
    c.execute('DELETE from cards where card=?', (cardValue,))
    closeCursor(conn)
    return 


if __name__ == "__main__":
    #createDatabase()
    addCard( 'test')
    print('card is in database  %s' % hasCard('test'))
    delCard('test')


