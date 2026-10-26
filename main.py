import psycopg
import sys
import typer
import rich
import questionary

app = typer.Typer()

@app.command()
def main():
    print("Hello from python-postgre!")
    print("Type 'exit' to quit.")

    while True:
        try:
            print("Welcome to SQL Testing")
            choice = questionary.select(
                "Choose your device:", choices=["Create Table", "Insert Data", "Select Data", "Update Data", "Delete Data", "Exit"]
            ).unsafe_ask()
            print(f"You chose: {choice}")
            if choice == "Exit":
                break
            command = input("> ").strip()
        except EOFError:
            break

        if command.lower() == "exit":
            break

        print("Hello, world!")


if __name__ == "__main__":
    main()
