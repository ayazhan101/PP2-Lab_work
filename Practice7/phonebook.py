import csv
from connect import get_connection

conn = get_connection()
cur = conn.cursor()

#1
def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )
    conn.commit()


#2
def insert_from_csv():
    with open("contacts.csv", "r") as file:
        reader = csv.reader(file)

        for row in reader:
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )
    conn.commit()


#3
def update_contact():
    name = input("Enter name to update: ")
    new_name = input("New name (or press Enter to skip): ")
    new_phone = input("New phone (or press Enter to skip): ")

    if new_name:
        cur.execute(
            "UPDATE contacts SET name = %s WHERE name = %s",
            (new_name, name)
        )

    if new_phone:
        cur.execute(
            "UPDATE contacts SET phone = %s WHERE name = %s",
            (new_phone, name)
        )

    conn.commit()


#4
def search():
    print("1. Search by name")
    print("2. Search by phone prefix")

    choice = input("Choose: ")

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("SELECT * FROM contacts WHERE name = %s", (name,))
    else:
        prefix = input("Enter prefix: ")
        cur.execute("SELECT * FROM contacts WHERE phone LIKE %s", (prefix + "%",))

    rows = cur.fetchall()

    for row in rows:
        print(row)


#5
def delete_contact():
    print("1. Delete by name")
    print("2. Delete by phone")

    choice = input("Choose: ")

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
    else:
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM contacts WHERE phone = %s", (phone,))

    conn.commit()


#!!!
def menu():
    while True:
        print("""
1. Insert from console
2. Insert from CSV
3. Update
4. Search
5. Delete
6. Exit
        """)

        choice = input("Choose: ")

        if choice == "1":
            insert_from_console()
        elif choice == "2":
            insert_from_csv()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            search()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            break

menu()

cur.close()
conn.close()