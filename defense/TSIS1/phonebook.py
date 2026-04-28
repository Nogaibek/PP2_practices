import csv
import json
import os
import sys
from datetime import date, datetime

import psycopg2
import psycopg2.extras

from connect import get_connection

#print(os.getcwd())

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _prompt(msg: str, default: str = "") -> str:
    val = input(msg).strip()
    return val if val else default


def _print_contacts(rows):
    """Pretty-print a list of contact dicts."""
    if not rows:
        print("  (no contacts found)")
        return
    sep = "-" * 80
    print(sep)
    for r in rows:
        print(f"  ID      : {r['id']}")
        print(f"  Name    : {r['name']}")
        print(f"  Email   : {r['email'] or '—'}")
        print(f"  Birthday: {r['birthday'] or '—'}")
        print(f"  Group   : {r['grp'] or '—'}")
        print(f"  Phones  : {r['phones'] or '—'}")
        print(sep)


def _serialize(obj):
    """JSON serialiser for date/datetime objects."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


# ─────────────────────────────────────────────────────────────
# DB bootstrap – apply schema changes if not yet applied
# ─────────────────────────────────────────────────────────────

def apply_schema(conn):
    """Run schema.sql to ensure tables and columns exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        print("[WARN] schema.sql not found – skipping auto-apply.")
        return
    with open(schema_path) as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("[OK] Schema applied.")


def apply_procedures(conn):
    """Run procedures.sql to create/replace stored objects."""
    proc_path = os.path.join(os.path.dirname(__file__), "procedures.sql")
    if not os.path.exists(proc_path):
        print("[WARN] procedures.sql not found – skipping auto-apply.")
        return
    with open(proc_path) as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("[OK] Procedures applied.")


# ─────────────────────────────────────────────────────────────
# Extended schema helpers (groups, phones)
# ─────────────────────────────────────────────────────────────

def get_or_create_group(conn, group_name: str) -> int | None:
    if not group_name:
        return None
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
        conn.commit()
        return cur.fetchone()[0]


def list_groups(conn) -> list[dict]:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────
# Add / update contact  (with new fields)
# ─────────────────────────────────────────────────────────────

def add_contact(conn):
    print("\n── Add Contact ──")
    name     = _prompt("Name          : ")
    email    = _prompt("Email         : ")
    birthday = _prompt("Birthday (YYYY-MM-DD, blank to skip): ")
    birthday = birthday if birthday else None

    # Group
    groups = list_groups(conn)
    print("Groups:", ", ".join(g["name"] for g in groups))
    group_name = _prompt("Group (blank to skip): ")
    group_id   = get_or_create_group(conn, group_name) if group_name else None

    # Primary phone (at least one)
    phone = _prompt("Phone number  : ")
    ptype = _prompt("Phone type (home/work/mobile) [mobile]: ", "mobile")

    with conn.cursor() as cur:
        # Upsert contact (name is unique key from Practice 7)
        cur.execute("""
            INSERT INTO contacts (name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE
                SET email    = EXCLUDED.email,
                    birthday = EXCLUDED.birthday,
                    group_id = EXCLUDED.group_id
            RETURNING id
        """, (name, email or None, birthday, group_id))
        contact_id = cur.fetchone()[0]

        # Add phone
        if phone:
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (contact_id, phone, ptype))

    conn.commit()
    print(f"[OK] Contact '{name}' saved (id={contact_id}).")


# ─────────────────────────────────────────────────────────────
# Advanced search / filter / sort
# ─────────────────────────────────────────────────────────────

SORT_MAP = {
    "name"     : "c.name",
    "birthday" : "c.birthday NULLS LAST",
    "date"     : "c.id",   # id proxy for insertion order (Practice 7 used SERIAL)
}


def _fetch_contacts(conn, where_clause="1=1", params=(), sort="name") -> list[dict]:
    order = SORT_MAP.get(sort, "c.name")
    sql = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name AS grp,
            STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')',
                       ', ' ORDER BY p.id) AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE {where_clause}
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY {order}
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def filter_by_group(conn):
    print("\n── Filter by Group ──")
    groups = list_groups(conn)
    if not groups:
        print("No groups defined.")
        return
    for i, g in enumerate(groups, 1):
        print(f"  {i}. {g['name']}")
    choice = _prompt("Select group number (or name): ")

    # Resolve name
    group_name = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(groups):
            group_name = groups[idx]["name"]
    else:
        group_name = choice

    sort = _prompt("Sort by (name/birthday/date) [name]: ", "name")
    rows = _fetch_contacts(conn,
                           where_clause="g.name ILIKE %s",
                           params=(group_name,),
                           sort=sort)
    _print_contacts(rows)


def search_by_email(conn):
    print("\n── Search by Email ──")
    query = _prompt("Email fragment: ")
    sort  = _prompt("Sort by (name/birthday/date) [name]: ", "name")
    rows  = _fetch_contacts(conn,
                            where_clause="c.email ILIKE %s",
                            params=(f"%{query}%",),
                            sort=sort)
    _print_contacts(rows)


def search_all_fields(conn):
    """Calls the search_contacts DB function from procedures.sql."""
    print("\n── Search (name / email / phone) ──")
    query = _prompt("Search query: ")
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = [dict(r) for r in cur.fetchall()]
    _print_contacts(rows)


# ─────────────────────────────────────────────────────────────
# 3.2 – Paginated navigation console loop
# ─────────────────────────────────────────────────────────────

PAGE_SIZE = 5


def _count_contacts(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM contacts")
        return cur.fetchone()[0]


def _fetch_page(conn, page: int, sort: str) -> list[dict]:
    """Uses the paginated DB function from Practice 8 if available,
    otherwise falls back to a direct query."""
    order  = SORT_MAP.get(sort, "c.name")
    offset = page * PAGE_SIZE
    sql = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name AS grp,
            STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')',
                       ', ' ORDER BY p.id) AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY {order}
        LIMIT %s OFFSET %s
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, (PAGE_SIZE, offset))
        return [dict(r) for r in cur.fetchall()]


def paginated_browse(conn):
    print("\n── Browse Contacts (paginated) ──")
    sort  = _prompt("Sort by (name/birthday/date) [name]: ", "name")
    total = _count_contacts(conn)
    if total == 0:
        print("No contacts in the database.")
        return

    max_page = max((total - 1) // PAGE_SIZE, 0)
    page     = 0

    while True:
        rows = _fetch_page(conn, page, sort)
        print(f"\n  Page {page + 1} of {max_page + 1}  ({total} total)")
        _print_contacts(rows)
        nav = _prompt("[n]ext / [p]rev / [q]uit: ").lower()
        if nav == "n":
            page = min(page + 1, max_page)
        elif nav == "p":
            page = max(page - 1, 0)
        elif nav == "q":
            break


# ─────────────────────────────────────────────────────────────
# Export to JSON
# ─────────────────────────────────────────────────────────────

def export_to_json(conn):
    print("\n── Export to JSON ──")
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts_export.json")
    path = _prompt(f"Output file path [{default_path}]: ", default_path)

    # Pull full contact data including all phones
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT
                c.id,
                c.name,
                c.email,
                c.birthday,
                g.name AS group_name,
                COALESCE(
                    JSON_AGG(
                        JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type)
                        ORDER BY p.id
                    ) FILTER (WHERE p.id IS NOT NULL),
                    '[]'::json
                ) AS phones
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """)
        rows = [dict(r) for r in cur.fetchall()]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=_serialize, ensure_ascii=False)

    print(f"[OK] {len(rows)} contacts exported to '{path}'.")


# ─────────────────────────────────────────────────────────────
# Import from JSON  (duplicate → skip or overwrite)
# ─────────────────────────────────────────────────────────────

def import_from_json(conn):
    print("\n── Import from JSON ──")
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts_export.json")
    path = _prompt(f"JSON file path [{default_path}]: ", default_path)
    
    if not os.path.exists(path):
        print(f"[ERROR] File '{path}' not found.")
        return

    with open(path, encoding="utf-8") as f:
        contacts = json.load(f)

    inserted = updated = skipped = 0

    for c in contacts:
        name = c.get("name", "").strip()
        if not name:
            continue

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

        if existing:
            action = _prompt(
                f"  '{name}' already exists. [s]kip / [o]verwrite [s]: ", "s"
            ).lower()
            if action != "o":
                skipped += 1
                continue

            # Overwrite
            group_id = get_or_create_group(conn, c.get("group_name") or "")
            birthday = c.get("birthday")
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE contacts
                    SET email    = %s,
                        birthday = %s,
                        group_id = %s
                    WHERE name = %s
                    RETURNING id
                """, (c.get("email"), birthday, group_id, name))
                contact_id = cur.fetchone()[0]

                # Replace phones
                cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
                for ph in c.get("phones", []):
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, ph.get("phone"), ph.get("type"))
                    )
            conn.commit()
            updated += 1
        else:
            # Fresh insert
            group_id = get_or_create_group(conn, c.get("group_name") or "")
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (name, c.get("email"), c.get("birthday"), group_id))
                contact_id = cur.fetchone()[0]

                for ph in c.get("phones", []):
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, ph.get("phone"), ph.get("type"))
                    )
            conn.commit()
            inserted += 1

    print(f"[OK] JSON import done: {inserted} inserted, {updated} updated, {skipped} skipped.")


# ─────────────────────────────────────────────────────────────
# Extended CSV import (new fields: email, birthday, group, phone type)
# ─────────────────────────────────────────────────────────────

def import_from_csv(conn):
    """
    Extended CSV importer.
    Expected columns: name, phone, type, email, birthday, group
    (type and group are new; all columns except name are optional)
    """
    print("\n── Import from CSV ──")
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.csv")
    path = _prompt(f"CSV file path [{default_path}]: ", default_path)

    if not os.path.exists(path):
        print(f"[ERROR] File '{path}' not found.")
        return

    inserted = skipped = errors = 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                errors += 1
                continue

            phone    = (row.get("phone")    or "").strip() or None
            ptype    = (row.get("type")     or "mobile").strip()
            email    = (row.get("email")    or "").strip() or None
            birthday = (row.get("birthday") or "").strip() or None
            group_nm = (row.get("group")    or "").strip() or None

            # Validate phone type
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"

            group_id = get_or_create_group(conn, group_nm) if group_nm else None

            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO contacts (name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                        RETURNING id
                    """, (name, email, birthday, group_id))
                    result = cur.fetchone()

                if result:
                    contact_id = result[0]
                    if phone:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO phones (contact_id, phone, type)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (contact_id, phone, ptype))
                    conn.commit()
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                conn.rollback()
                print(f"  [WARN] Row skipped ({name}): {e}")
                errors += 1

    print(f"[OK] CSV import done: {inserted} inserted, {skipped} skipped, {errors} errors.")


# ─────────────────────────────────────────────────────────────
# Call stored procedures from console
# ─────────────────────────────────────────────────────────────

def console_add_phone(conn):
    print("\n── Add Phone to Contact ──")
    contact_name = _prompt("Contact name: ")
    phone        = _prompt("Phone number: ")
    ptype        = _prompt("Type (home/work/mobile) [mobile]: ", "mobile")
    try:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, ptype))
        conn.commit()
        print(f"[OK] Phone '{phone}' ({ptype}) added to '{contact_name}'.")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")


def console_move_to_group(conn):
    print("\n── Move Contact to Group ──")
    contact_name = _prompt("Contact name: ")
    group_name   = _prompt("Target group name: ")
    try:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
        conn.commit()
        print(f"[OK] '{contact_name}' moved to group '{group_name}'.")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] {e}")


# ─────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║        PhoneBook Extended                ║
╠══════════════════════════════════════════╣
║  1. Add / update contact                 ║
║  2. Browse (paginated)                   ║
║  3. Filter by group                      ║
║  4. Search by email                      ║
║  5. Search (name / email / phone)        ║
║  6. Add phone to contact                 ║
║  7. Move contact to group                ║
║  8. Export contacts → JSON               ║
║  9. Import contacts ← JSON               ║
║  10. Import contacts ← CSV               ║
║  0. Exit                                 ║
╚══════════════════════════════════════════╝
"""


def main():
    try:
        conn = get_connection()
    except Exception as e:
        sys.exit(f"[FATAL] Cannot connect to database: {e}")

    print("[INFO] Connected to database.")

    # Auto-apply schema and procedures on first run
    apply_schema(conn)
    apply_procedures(conn)

    actions = {
        "1":  add_contact,
        "2":  paginated_browse,
        "3":  filter_by_group,
        "4":  search_by_email,
        "5":  search_all_fields,
        "6":  console_add_phone,
        "7":  console_move_to_group,
        "8":  export_to_json,
        "9":  import_from_json,
        "10": import_from_csv,
    }

    while True:
        print(MENU)
        choice = _prompt("Choice: ")
        if choice == "0":
            print("Bye!")
            break
        fn = actions.get(choice)
        if fn:
            try:
                fn(conn)
            except KeyboardInterrupt:
                print("\n(cancelled)")
            except Exception as e:
                conn.rollback()
                print(f"[ERROR] {e}")
        else:
            print("Unknown option.")

    conn.close()


if __name__ == "__main__":
    main()