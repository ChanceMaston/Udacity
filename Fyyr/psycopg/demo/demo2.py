import psycopg2

conn = psycopg2.connect('dbname=example')

cursor = conn.cursor()

# Open a cursor to perform database operations
cur = conn.cursor()

# Drop any existing todos table
cur.execute("DROP TABLE IF EXISTS todos;")

# (Re)create the todos table
# Note: Triple quotes allow multiline text in python
cur.execute('''
    CREATE TABLE todos (
        id serial PRIMARY KEY, 
        description VARCHAR NOT NULL
        );
''')

# Commit, so it does the executions on the db and persists in the db.
conn.commit()

cur.close()
conn.close()
