import db


def init_db():
    conn = db.database_connection()
    cur = conn.cursor()

    schemaFile = open('schema.sql')
    cur.execute(schemaFile.read())

    schemaFile.close()

    conn.commit()


def drop_db():
    conn = db.database_connection()
    cur = conn.cursor()

    table_names = ['game', 'player', 'score']

    for table_name in table_names:
        # Here we can't use parameters, but there's no risk of SQL
        # injection as long as the table_names array is not
        # user defined
        cur.execute("DROP TABLE IF EXISTS " + table_name + " CASCADE")

    conn.commit()


if __name__ == "__main__":
    init_db()
