import db

def create_tables():
    conn = db.database_connection()
    cur = conn.cursor()

    schemaFile = open('schema.sql')
    cur.execute(schemaFile.read())

    conn.commit()

if __name__ == "__main__":
    create_tables()
