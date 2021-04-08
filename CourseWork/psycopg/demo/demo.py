import psycopg2

connection = psycopg2.connect('dbname=example')

cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS table2;')

cursor.execute('''
    CREATE TABLE table2 (
        id INTEGER PRIMARY KEY,
        completed BOOLEAN NOT NULL DEFAULT False
        );
''')

cursor.execute('INSERT INTO table2 (id, completed) VALUES (%s, %s);', (1, True))

cursor.execute('INSERT INTO table2 (id, completed) ' +
               'VALUES (%(id)s, %(completed)s);', {'id':2, 'completed':False})

cursor.execute('INSERT INTO table2 (id, completed) ' +
               'VALUES (%(id)s, %(completed)s);', {'id':3, 'completed':True})

cursor.execute('SELECT * from table2;')

result = cursor.fetchmany(2)
print('fetchmany: ', result)

result2 = cursor.fetchone()
print('fetchone: ', result2)

cursor.execute('SELECT * from table2;')

result3 = cursor.fetchone()
print('fetchone2: ', result3)

connection.commit()

connection.close()
cursor.close()
