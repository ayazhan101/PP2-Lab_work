CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name VARCHAR,
    p_surname VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM contacts
        WHERE name = p_name AND surname = p_surname
    ) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name AND surname = p_surname;
    ELSE
        INSERT INTO contacts(name, surname, phone)
        VALUES (p_name, p_surname, p_phone);
    END IF;
END;
$$;


DROP TYPE IF EXISTS contact_input CASCADE;

CREATE TYPE contact_input AS (
    name VARCHAR(100),
    surname VARCHAR(100),
    phone VARCHAR(20)
);


CREATE OR REPLACE PROCEDURE insert_many_contacts(p_contacts contact_input[])
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_name VARCHAR(100);
    v_surname VARCHAR(100);
    v_phone VARCHAR(20);
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS invalid_contacts (
        name VARCHAR(100),
        surname VARCHAR(100),
        phone VARCHAR(20),
        reason TEXT
    ) ON COMMIT PRESERVE ROWS;

    DELETE FROM invalid_contacts;

    FOR i IN 1 .. array_length(p_contacts, 1)
    LOOP
        v_name := p_contacts[i].name;
        v_surname := p_contacts[i].surname;
        v_phone := p_contacts[i].phone;

        IF v_phone !~ '^[0-9]{11,15}$' THEN
            INSERT INTO invalid_contacts(name, surname, phone, reason)
            VALUES (v_name, v_surname, v_phone, 'Invalid phone format');
        ELSE
            IF EXISTS (
                SELECT 1
                FROM contacts
                WHERE name = v_name AND surname = v_surname
            ) THEN
                UPDATE contacts
                SET phone = v_phone
                WHERE name = v_name AND surname = v_surname;
            ELSE
                INSERT INTO contacts(name, surname, phone)
                VALUES (v_name, v_surname, v_phone);
            END IF;
        END IF;
    END LOOP;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(
    p_name VARCHAR DEFAULT NULL,
    p_phone VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM contacts
        WHERE name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM contacts
        WHERE phone = p_phone;
    ELSE
        RAISE EXCEPTION 'Provide either name or phone';
    END IF;
END;
$$;