# Functions for database operations

import sqlite3
import numpy as np
import io


def adapt_array(facecode):
    out = io.BytesIO()
    np.save(out, facecode)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

def add(name, facecode):
    """ Adds new name and face encoding to database """
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    conn = sqlite3.connect("face.db", detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("INSERT INTO faces (name, facecode) VALUES(?,?)", (name, facecode))
    conn.commit()
    conn.close()

def getfacelist():
    """ Returns list of all face encodings from db sorted by id """
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)
    conn = sqlite3.connect("face.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.execute("SELECT facecode FROM faces")
    l = []
    for row in cur:
        l.append(row[0])
    conn.close()
    return l

def getidlist():
    """ Returns list of all ids from db """
    conn = sqlite3.connect("face.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.execute("SELECT id FROM faces")
    t = cur.fetchall()
    l = []
    for tup in t:
        l.append(tup[0])
    conn.close()
    return l

def getname(id):
    """ Returns the name of id """
    conn = sqlite3.connect("face.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.execute("SELECT name FROM faces WHERE id = ?", (id,))
    name = cur.fetchone()
    conn.close()
    return name[0]

def getidnamelist():
    """ Returns list of ids with names """
    conn = sqlite3.connect("face.db", detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, name FROM faces")
    result = [dict(row) for row in c.fetchall()]
    return result

def remove(id):
    """ Removes id from database """
    conn = sqlite3.connect("face.db", detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("DELETE FROM faces WHERE id = ?", (id,))
    conn.commit()
    conn.close()