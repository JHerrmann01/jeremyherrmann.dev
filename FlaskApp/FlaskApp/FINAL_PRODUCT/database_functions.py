import sqlite3

DATABASE = "./instagramUsers.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def query_database(query, args=(), dictionary = True):
    con = sqlite3.connect(DATABASE)
    if dictionary:
        con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    con.commit()
    con.close()
    return rv

def post_database(query, args=()):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute(query, args)
    con.commit()
    con.close()

#Actual functions regarding the data inside the database
def get_similar_accounts():
    results = query_database("SELECT * FROM similarAccounts;")
    return(results)

def get_follow_list():
    results = query_database("SELECT * FROM accountsToFollow WHERE HasFollowed = 0")
    return(results)

def get_random_follow_list(LIMIT):
    results = query_database("SELECT * FROM accountsToFollow WHERE HasFollowed = 0 ORDER BY RANDOM() LIMIT ?", (LIMIT,))
    return(results)

def get_captions():
    results = query_database("SELECT * FROM captions")
    return(results)

def insert_into_follow_list(username, user_id, full_name):
    results = post_database("INSERT OR IGNORE INTO accountsToFollow(Username, UserID, Full_Name) VALUES (?, ?, ?)", (username, user_id, full_name,))
    return(results)

def insert_caption(caption):
    results = post_database("INSERT INTO captions(Caption) VALUES (?);", (caption,))
    return(results)

def update_has_followed(user_id):
    results = post_database("UPDATE accountsToFollow SET HasFollowed = 1 WHERE UserID = ?;", (user_id,))
    return(results)

def update_has_unfollowed(user_id):
    results = post_database("UPDATE accountsToFollow SET HasUnfollowed = 1 WHERE UserID = ?;", (user_id,))
    return(results)
