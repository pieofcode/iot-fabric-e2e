from datetime import datetime
import os
import time
import sys
import os
import json
import pyodbc


class SQLManager:

    def __init__(self, server, pwd, db="master") -> None:
        driver = "{ODBC Driver 17 for SQL Server}"
        connection_str = f"Driver={driver};Server={server};Database={db};UID=sa;PWD={pwd}"
        self.db_connection = pyodbc.connect(connection_str, autocommit=True)
        self.db_connection.setencoding(encoding='utf-8')

        # Create a cursor from the connection
        self.cursor = self.db_connection.cursor()

    def create_db_table(self, db="EdgeInspect"):
        db_exists = True
        self.cursor.execute(
            f'''
                SELECT * FROM sys.databases where name = '{db}';
            '''
        )
        row = self.cursor.fetchone()
        if not row:
            db_exists = False
            self.cursor.execute(
                f'''
                    CREATE DATABASE {db}; USE {db};
                '''
            )
            print('Database created:', db)

        else:
            print('Database already exists:', row.name)

        # Create ImageCaptureLogs Table
        self.cursor.execute(
            f'''
                USE {db};
                IF OBJECT_ID(N'dbo.ImageCaptureLogs', N'U') IS NULL 
                BEGIN
                CREATE TABLE ImageCaptureLogs (
                    Id int IDENTITY(1,1) PRIMARY KEY,
                    ImageId varchar(255) NOT NULL,
                    Orientation varchar(255) NOT NULL,
                    FilePath varchar(255) NOT NULL,
                    Tag varchar(255) NOT NULL,
                    classification VARCHAR(1000),
                    CreatedOn DATETIME2
                )
                END
            '''
        )

        self.db_connection.commit()
        pass

    def insert_log(self, params):
        print(f"Insert Log: [{params}]")
        self.cursor.execute(
            f'''
                INSERT INTO ImageCaptureLogs (ImageId, Orientation, FilePath, Tag, Classification, CreatedOn) VALUES (?, ?, ?, ?, ?, ?)
            ''',
            params
        )
        self.db_connection.commit()

    def query(self, query, params):
        pass


if __name__ == "__main__":
    print("SQLManager Test")
    sql_manager = SQLManager("localhost", "Test1234")

    # Create a database
    sql_manager.create_db_table()

    params = ["a", "b", "c", "d", "e", datetime.utcnow()]
    # Insert the test data
    sql_manager.insert_log(params)
