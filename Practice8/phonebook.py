from connect import get_connection


def search_by_pattern():
    pattern = input("Enter pattern: ")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM get_contacts_by_pattern(%s);", (pattern,))
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No contacts found.")
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def show_paginated():
    limit_val = int(input("Enter limit: "))
    offset_val = int(input("Enter offset: "))

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s);",
            (limit_val, offset_val)
        )
        rows = cur.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No contacts found.")
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def upsert_one_contact():
    name = input("Enter name: ")
    surname = input("Enter surname: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL upsert_contact(%s, %s, %s);", (name, surname, phone))
        conn.commit()
        print("Contact inserted/updated successfully.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def delete_one_contact():
    mode = input("Delete by name or phone? (n/p): ").lower()

    conn = get_connection()
    cur = conn.cursor()
    try:
        if mode == "n":
            name = input("Enter name: ")
            cur.execute("CALL delete_contact(%s, %s);", (name, None))
        elif mode == "p":
            phone = input("Enter phone: ")
            cur.execute("CALL delete_contact(%s, %s);", (None, phone))
        else:
            print("Invalid choice.")
            return

        conn.commit()
        print("Contact deleted successfully.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()


def menu():
    while True:
        print("\n--- PRACTICE 8 PHONEBOOK ---")
        print("1. Search by pattern")
        print("2. Insert or update one contact")
        print("3. Show paginated contacts")
        print("4. Delete contact")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            search_by_pattern()
        elif choice == "2":
            upsert_one_contact()
        elif choice == "3":
            show_paginated()
        elif choice == "4":
            delete_one_contact()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()