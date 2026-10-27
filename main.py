import psycopg
import questionary
import typer
from rich import print
from rich.table import Table
from rich.console import Console
import os
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()


class Postgre:
    def __init__(self):
        self.conn = psycopg.connect(
            f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}"
        )
        self.cur = self.conn.cursor()

    def createTable(self):
         print("Create Table")
         table_name = input("Enter table name: ").strip()

         if not table_name:
             print("Error: Table name cannot be empty.")
             return

         columns = []
         
         while True:
             column = input(
                "Enter column (name type), or 'done' to finish: "
             ).strip()
 
             if column.lower() == "done":
                 break
 
             if not column:
                 print("Error: Column cannot be empty.")
                 continue
 
             parts = column.split()
 
             if len(parts) != 2:
                 print("Invalid format. Example: name VARCHAR(100)")
                 continue
 
             column_name, data_type = parts
             columns.append(f"{column_name} {data_type}")
 
         if not columns:
             print("Error: At least one column is required.")
             return
 
         print(f"Table: {table_name}")
         print("Columns:")
 
         column_data = ",".join(columns)
         print(column_data)
 
         self.cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_data})")
         self.conn.commit()
 
    def fetchTable(self):
        table_name = self._getTableList()
        print(table_name)
 
    def insertData(self):
        print("Inserting data...")
        # get the list of tables
        table_name = self._getTableList()
 
        # from the retrieved table list choose one table
        chosen_table = questionary.select(
            "Choose the Table for Insertion",
            choices=table_name,
        ).unsafe_ask()
        print(chosen_table)
 
        # For the chosen table get the column metadata
        self.cur.execute(f"""
            SELECT
                column_name,
                data_type,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = '{chosen_table}'
            ORDER BY ordinal_position;
        """)
        column_metadata = []
        column_name = []
        for column in self.cur.fetchall():
            column_metadata.append(column)
            column_name.append(column[0])
        print(column_name)
 
        insertion_data = []
        while True:
            data = input(
                f"Enter data ({", ".join(column_name)}), or 'done' to finish: "
            ).strip()
            if data.lower() == 'done':
                break
            if not data:
                print("Error: Enter valid data")
                continue
 
            data = data.split(",")
            if len(data) != len(column_name):
                print("Error: Enter valid data. Data entry mismatch")
                continue
            print(data)
            insertion_data.append(data)
        print(insertion_data)
        self.cur.executemany(f"""
            INSERT INTO {chosen_table} ({", ".join(column_name)}) VALUES ({", ".join(["%s"] * len(column_name))});
        """, insertion_data)
        self.conn.commit()
        print("Data inserted successfully")
 


    def fetchData(self):
        print("Selecting data...")
        table_name = self._getTableList()
        print(table_name)

        # from the retrieved table list choose one table
        chosen_table = questionary.select(
            "Choose the Table for Fetching",
            choices=table_name,
        ).unsafe_ask()
        print(chosen_table)

        self.cur.execute(f"""
            SELECT * FROM {chosen_table};
        """)

        column_name = [column.name for column in self.cur.description]
        data = self.cur.fetchall()
        table = Table(title=f"Data from {chosen_table}")
        for column in column_name:
            table.add_column(column)
        for row in data:
            table.add_row(*map(str, row))
        console = Console()
        console.print(table)
 
    def updateData(self):
        print("Updating data...")
 
    def deleteData(self):
        print("Deleting data...")

    def _getTableList(self):
        self.cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        table_name = []
        for table in self.cur.fetchall():
            table_name.append(table[0])
        return table_name
 
    def close(self):
        self.cur.close()
        self.conn.close()
 
 
@app.command()
def main():
    postgre = Postgre()
 
    choice_fn = {
        "Create Table": postgre.createTable,
        "Insert Data": postgre.insertData,
        "Fetch Data": postgre.fetchData,
        "Update Data": postgre.updateData,
        "Delete Data": postgre.deleteData,
        "Fetch Table": postgre.fetchTable
    }
 
    try:
        while True:
            choice = questionary.select(
                "Welcome to SQL Testing",
                choices=[
                    "Create Table",
                    "Insert Data",
                    "Fetch Data",
                    "Update Data",
                    "Delete Data",
                    "Fetch Table",
                    "Exit",
                ],
            ).unsafe_ask()
 
            if choice is None or choice == "Exit":
                break
 
            action = choice_fn.get(choice)
 
            if action:
                action()
 
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
 
    except EOFError:
        print("\nInput stream closed.")
 
    except psycopg.Error as e:
        print(f"\nDatabase error: {e}")
 
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    finally:
        postgre.close()
        print("Database connection closed.")
 
 
if __name__ == "__main__":
    app()