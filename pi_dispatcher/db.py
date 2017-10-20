#!/bin/python
import sqlite3
import os.path
import datetime

import logging
logger = logging.getLogger(__name__)
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
    cursor = c.fetchall()
    if (cursor[0][0] == 0 ):
        closeCursor(conn)
        return (False)

    c.execute('SELECT nused FROM cards WHERE card = ?', (cardValue,))
    cursor = c.fetchall()
    c.execute('UPDATE cards SET nused = ?, lastUsed=? where card=?', (
        int(cursor[0][0])+1, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cardValue )
        )
    closeCursor(conn)
    return True

def addCard( cardValue ):
    if hasCard(cardValue):
        return
    (conn, c) =getCursor()
    c.execute('INSERT into cards (card, whenadded, nused) VALUES (?, ?,0)', 
            (cardValue, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
            )
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
    if (hasCard('test')):
        delCard('test')
    addCard( 'test')
    print('card is in database  %s' % hasCard('test'))


