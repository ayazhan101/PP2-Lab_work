import csv
import json
from connect import get_connection


def create_group_if_not_exists(group_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO groups(name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
        """,
        (group_name,)
    )

    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    group_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return group_id


def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday YYYY-MM-DD: ")
    group_name = input("Group Family/Work/Friend/Other: ")

    group_id = create_group_if_not_exists(group_name)

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, email, birthday, group_id)
        )

        contact_id = cur.fetchone()[0]

        while True:
            phone = input("Phone number: ")
            phone_type = input("Type home/work/mobile: ")

            cur.execute(
                """
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                """,
                (contact_id, phone, phone_type)
            )

            more = input("Add another phone? yes/no: ")
            if more.lower() != "yes":
                break

        conn.commit()
        print("Contact added successfully.")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    cur.close()
    conn.close()


def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            c.name,
            c.email,
            c.birthday,
            g.name,
            STRING_AGG(p.phone || ' (' || p.type || ')', ', ')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
        ORDER BY c.name
        """
    )

    rows = cur.fetchall()

    for row in rows:
        print("-" * 60)
        print("Name:", row[0])
        print("Email:", row[1])
        print("Birthday:", row[2])
        print("Group:", row[3])
        print("Phones:", row[4])

    cur.close()
    conn.close()


def filter_by_group():
    group_name = input("Enter group name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name ILIKE %s
        ORDER BY c.name
        """,
        (group_name,)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def search_by_email():
    query = input("Enter email part: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT name, email, birthday
        FROM contacts
        WHERE email ILIKE %s
        ORDER BY name
        """,
        (f"%{query}%",)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def advanced_search():
    query = input("Search name/email/phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def sort_contacts():
    print("1. Sort by name")
    print("2. Sort by birthday")
    print("3. Sort by date added")

    choice = input("Choose: ")

    if choice == "1":
        order_by = "c.name"
    elif choice == "2":
        order_by = "c.birthday"
    elif choice == "3":
        order_by = "c.created_at"
    else:
        print("Wrong choice.")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        f"""
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order_by}
        """
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def paginated_contacts():
    page = 0
    limit = 5

    while True:
        offset = page * limit

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT c.name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            ORDER BY c.name
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

        rows = cur.fetchall()

        print("\nPage:", page + 1)

        if not rows:
            print("No contacts on this page.")
        else:
            for row in rows:
                print(row)

        cur.close()
        conn.close()

        command = input("next / prev / quit: ").lower()

        if command == "next":
            page += 1
        elif command == "prev":
            if page > 0:
                page -= 1
        elif command == "quit":
            break


def add_phone_to_contact():
    name = input("Contact name: ")
    phone = input("New phone: ")
    phone_type = input("Type home/work/mobile: ")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()
        print("Phone added.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)

    cur.close()
    conn.close()


def move_contact_to_group():
    name = input("Contact name: ")
    group_name = input("New group: ")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()
        print("Contact moved.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)

    cur.close()
    conn.close()


def export_to_json():
    filename = input("JSON filename, example contacts.json: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.name
        """
    )

    contacts = []

    for contact_id, name, email, birthday, group_name in cur.fetchall():
        cur.execute(
            """
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s
            """,
            (contact_id,)
        )

        phones = []
        for phone, phone_type in cur.fetchall():
            phones.append({
                "phone": phone,
                "type": phone_type
            })

        contacts.append({
            "name": name,
            "email": email,
            "birthday": str(birthday) if birthday else None,
            "group": group_name,
            "phones": phones
        })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4, ensure_ascii=False)

    cur.close()
    conn.close()

    print("Export completed.")


def import_from_json():
    filename = input("JSON filename: ")

    with open(filename, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    conn = get_connection()
    cur = conn.cursor()

    for item in contacts:
        name = item["name"]
        email = item.get("email")
        birthday = item.get("birthday")
        group_name = item.get("group", "Other")
        phones = item.get("phones", [])

        group_id = create_group_if_not_exists(group_name)

        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            action = input(f"{name} already exists. skip/overwrite: ")

            if action.lower() == "skip":
                continue

            contact_id = existing[0]

            cur.execute(
                """
                UPDATE contacts
                SET email = %s, birthday = %s, group_id = %s
                WHERE id = %s
                """,
                (email, birthday, group_id, contact_id)
            )

            cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))

        else:
            cur.execute(
                """
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (name, email, birthday, group_id)
            )

            contact_id = cur.fetchone()[0]

        for phone_item in phones:
            cur.execute(
                """
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                """,
                (
                    contact_id,
                    phone_item["phone"],
                    phone_item["type"]
                )
            )

    conn.commit()
    cur.close()
    conn.close()

    print("Import from JSON completed.")


def import_from_csv():
    filename = input("CSV filename: ")

    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            name = row["name"]
            email = row["email"]
            birthday = row["birthday"]
            group_name = row["group"]
            phone = row["phone"]
            phone_type = row["type"]

            group_id = create_group_if_not_exists(group_name)

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                contact_id = existing[0]

                cur.execute(
                    """
                    UPDATE contacts
                    SET email = %s, birthday = %s, group_id = %s
                    WHERE id = %s
                    """,
                    (email, birthday, group_id, contact_id)
                )

            else:
                cur.execute(
                    """
                    INSERT INTO contacts(name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (name, email, birthday, group_id)
                )

                contact_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
                """,
                (contact_id, phone, phone_type)
            )

    conn.commit()
    cur.close()
    conn.close()

    print("CSV import completed.")


def delete_contact():
    name = input("Contact name to delete: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
    conn.commit()

    cur.close()
    conn.close()

    print("Contact deleted.")


def main():
    while True:
        print("\n===== PHONEBOOK MENU =====")
        print("1. Add contact")
        print("2. Show all contacts")
        print("3. Filter by group")
        print("4. Search by email")
        print("5. Advanced search name/email/phone")
        print("6. Sort contacts")
        print("7. Paginated contacts")
        print("8. Add phone to contact")
        print("9. Move contact to group")
        print("10. Export to JSON")
        print("11. Import from JSON")
        print("12. Import from CSV")
        print("13. Delete contact")
        print("0. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            show_all_contacts()
        elif choice == "3":
            filter_by_group()
        elif choice == "4":
            search_by_email()
        elif choice == "5":
            advanced_search()
        elif choice == "6":
            sort_contacts()
        elif choice == "7":
            paginated_contacts()
        elif choice == "8":
            add_phone_to_contact()
        elif choice == "9":
            move_contact_to_group()
        elif choice == "10":
            export_to_json()
        elif choice == "11":
            import_from_json()
        elif choice == "12":
            import_from_csv()
        elif choice == "13":
            delete_contact()
        elif choice == "0":
            break
        else:
            print("Wrong option.")


if __name__ == "__main__":
    main()