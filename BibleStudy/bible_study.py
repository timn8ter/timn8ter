import sqlite3
from datetime import datetime

DATABASE = "bible_study.db"

def read_bible():
    import urllib.parse
    import urllib.request

    while True:
        print("\n--- NET Bible ---")
        print("Type 'exit' to return to the main menu.")

        passage = input("Enter Bible passage: ")

        if passage.lower() == "exit":
            break

        params = urllib.parse.urlencode({
            "passage": passage,
            "formatting": "plain",
            "type": "text"
        })

        url = "https://labs.bible.org/api/?" + params

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                text = response.read().decode("utf-8")

            print()
            print("=" * 70)
            print("NET BIBLE")
            print("=" * 70)

            import re

            verses = re.split(r"\s{2,}(?=\d+\s)", text.strip())

            if verses:
                first_verse = verses[0]
                match = re.match(r"(\d+):(\d+)\s+(.*)", first_verse)

                if match:
                    chapter = match.group(1)

                    print(f"{chapter}:{match.group(2)}  {match.group(3)}")

                    for verse in verses[1:]:
                        verse_match = re.match(r"(\d+)\s+(.*)", verse.strip())

                        if verse_match:
                            print(f"{chapter}:{verse_match.group(1)}  {verse_match.group(2)}")
                        else:
                            print(verse.strip())
                else:
                    for verse in verses:
                        print(verse.strip())
            print("=" * 70)

        except Exception as error:
            print("\nUnable to retrieve the Bible passage.")
            print("Error:", error)

def search_bible():
    import urllib.parse
    import urllib.request

    print("\n--- NET Bible Search ---")
    print("Enter a word or phrase to search.")
    print("Type 'exit' to return to the main menu.")

    search_term = input("Search: ")

    if search_term.lower() == "exit":
        return

    params = urllib.parse.urlencode({
        "search": search_term,
        "type": "verse",
        "formatting": "plain"
    })

    url = "https://labs.bible.org/api/?" + params

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            text = response.read().decode("utf-8")

        print()
        print("=" * 70)
        print("NET BIBLE SEARCH RESULTS")
        print("=" * 70)

        if text.strip():
            print(text)
        else:
            print("No results found.")

        print("=" * 70)

    except Exception as error:
        print("\nUnable to search the NET Bible.")
        print("Error:", error)

def bible_study():
    print("\n--- Bible Study Passage ---")
    print("Enter a passage such as John 3:16 or Romans 8.")
    print("Type 'exit' to return to the main menu.")

    while True:
        passage = input("\nPassage: ")

        if passage.lower() == "exit":
            break

        import urllib.parse
        import urllib.request

        params = urllib.parse.urlencode({
            "passage": passage,
            "formatting": "plain",
            "type": "text"
        })

        url = "https://labs.bible.org/api/?" + params

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                text = response.read().decode("utf-8")

            print("\n" + "=" * 70)
            print("NET BIBLE")
            print("=" * 70)
            print(text)
            print("=" * 70)

        except Exception as error:
            print("\nUnable to retrieve that passage.")
            print("Error:", error)
def connect_database():
    return sqlite3.connect(DATABASE)


def setup_database():
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_topics (
            note_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            PRIMARY KEY (note_id, topic_id),
            FOREIGN KEY (note_id) REFERENCES notes(id),
            FOREIGN KEY (topic_id) REFERENCES topics(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            translation TEXT NOT NULL,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reference TEXT,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sermons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            scripture TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cross_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_reference TEXT NOT NULL,
            related_reference TEXT NOT NULL,
            note TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def add_note():
    print("\n--- Add Study Note ---")

    title = input("Title: ")
    reference = input("Bible reference: ")

    print("Enter your note.")
    print("Press ENTER on an empty line when finished.")

    lines = []

    while True:
        line = input()

        if line == "":
            break

        lines.append(line)

    note = "\n".join(lines)

    topic_name = input("Topic (optional): ")

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notes
        (title, reference, note, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        title,
        reference,
        note,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    note_id = cursor.lastrowid

    if topic_name:
        cursor.execute("""
            SELECT id
            FROM topics
            WHERE name = ?
        """, (topic_name,))

        topic = cursor.fetchone()

        if topic:
            topic_id = topic[0]

            cursor.execute("""
                INSERT OR IGNORE INTO note_topics
                (note_id, topic_id)
                VALUES (?, ?)
            """, (note_id, topic_id))
        else:
            print(f"\nTopic '{topic_name}' was not found.")
            create_topic = input("Create this topic now? (y/n): ")

            if create_topic.lower() == "y":
                description = input("Topic description: ")

                cursor.execute("""
                    INSERT INTO topics
                    (name, description)
                    VALUES (?, ?)
                """, (topic_name, description))

                topic_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO note_topics
                    (note_id, topic_id)
                    VALUES (?, ?)
                """, (note_id, topic_id))

                print(f"\nTopic '{topic_name}' created and note added to it.")
            else:
                print("\nNote was saved without a topic.")

    conn.commit()
    conn.close()

    print("\nNote saved!")

def add_note_to_topic():
    print("\n--- Add Note to Topic ---")

    note_id = input("Note ID: ")
    topic_name = input("Topic name: ")

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM notes
        WHERE id = ?
    """, (note_id,))

    note = cursor.fetchone()

    if not note:
        print("\nNote not found.")
        conn.close()
        return

    cursor.execute("""
        SELECT id
        FROM topics
        WHERE name = ?
    """, (topic_name,))

    topic = cursor.fetchone()

    if not topic:
        print("\nTopic not found.")
        conn.close()
        return

    cursor.execute("""
        INSERT OR IGNORE INTO note_topics
        (note_id, topic_id)
        VALUES (?, ?)
    """, (note_id, topic[0]))

    conn.commit()
    conn.close()

    print(f"\n'{note[1]}' added to topic '{topic_name}'.")

def search_notes():
    print("\n--- Search My Notes ---")

    search = input("Search: ")

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, reference, note, created_at
        FROM notes
        WHERE LOWER(title) LIKE LOWER(?)
        OR LOWER(reference) LIKE LOWER(?)
        OR LOWER(note) LIKE LOWER(?)
        ORDER BY created_at DESC
    """, (
        f"%{search}%",
        f"%{search}%",
        f"%{search}%"
    ))

    results = cursor.fetchall()

    conn.close()

    if not results:
        print("\nNo notes found.")
        return

    print(f"\nFound {len(results)} result(s):\n")

    for note in results:
        print("=" * 60)
        print(f"ID: {note[0]}")
        print(f"Title: {note[1]}")
        print(f"Reference: {note[2]}")
        print(f"Date: {note[4]}")
        print()
        print(note[3])
        print()


def add_topic():
    print("\n--- Add Topic ---")

    name = input("Topic name: ")
    description = input("Description: ")

    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO topics (name, description)
            VALUES (?, ?)
        """, (name, description))

        conn.commit()
        print("\nTopic saved!")

    except sqlite3.IntegrityError:
        print("\nThat topic already exists.")

    conn.close()


def search_topics():
    print("\n--- Search Topics ---")

    search = input("Topic: ")

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, description
        FROM topics
        WHERE name LIKE ?
           OR description LIKE ?
        ORDER BY name
    """, (
        f"%{search}%",
        f"%{search}%"
    ))

    results = cursor.fetchall()

    conn.close()

    if not results:
        print("\nNo topics found.")
        return

    for topic in results:
        print("\n" + "=" * 50)
        print(topic[1])
        print(topic[2])

def study_dashboard():
    print("\n" + "=" * 60)
    print("              BIBLE STUDY DASHBOARD")
    print("=" * 60)

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM notes")
    note_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM topics")
    topic_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cross_references")
    cross_reference_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT topics.name, COUNT(note_topics.note_id)
        FROM topics
        LEFT JOIN note_topics
            ON topics.id = note_topics.topic_id
        GROUP BY topics.id
        ORDER BY topics.name
    """)
    topics = cursor.fetchall()

    cursor.execute("""
        SELECT title, reference, created_at
        FROM notes
        ORDER BY created_at DESC
        LIMIT 5
    """)
    recent_notes = cursor.fetchall()

    conn.close()

    print(f"\nTotal Study Notes: {note_count}")
    print(f"Total Topics: {topic_count}")
    print(f"Total Cross-References: {cross_reference_count}")

    print("\n--- Topics ---")

    if not topics:
        print("No topics yet.")
    else:
        for topic in topics:
            print(f"- {topic[0]} ({topic[1]} note{'s' if topic[1] != 1 else ''})")

    print("\n--- Recent Studies ---")

    if not recent_notes:
        print("No study notes yet.")
        return

    for title, reference, created_at in recent_notes:
        print(f"\n{title}")
        print(f"Reference: {reference}")
        print(f"Date: {created_at}")

    print("\n" + "=" * 60)

def notes_by_topic():
    print("\n--- Notes by Topic ---")

    topic_name = input("Topic: ")

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT notes.title,
               notes.reference,
               notes.note,
               notes.created_at
        FROM notes
        JOIN note_topics
            ON notes.id = note_topics.note_id
        JOIN topics
            ON topics.id = note_topics.topic_id
        WHERE topics.name = ?
        ORDER BY notes.created_at DESC
    """, (topic_name,))

    results = cursor.fetchall()

    conn.close()

    if not results:
        print("\nNo notes found for that topic.")
        return

    print(f"\nNotes for: {topic_name}")

    for note in results:
        print("\n" + "=" * 60)
        print(f"Title: {note[0]}")
        print(f"Reference: {note[1]}")
        print(f"Date: {note[3]}")
        print()
        print(note[2])

def add_cross_reference():
    print("\n--- Add Cross Reference ---")

    source_reference = input("Main reference: ")
    related_reference = input("Related reference: ")
    note = input("Why are these passages related? ")

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cross_references
        (source_reference, related_reference, note)
        VALUES (?, ?, ?)
    """, (
        source_reference,
        related_reference,
        note
    ))

    conn.commit()
    conn.close()

    print("\nCross-reference saved!")
def view_cross_references():
    print("\n--- Cross References ---")

    source_reference = input("Reference: ")

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            CASE
               WHEN source_reference = ? THEN related_reference
               ELSE source_reference
            END AS related_reference,
            note
        FROM cross_references
        WHERE source_reference = ?
           OR related_reference = ?
        ORDER BY related_reference
    """, (source_reference, source_reference, source_reference ))

    results = cursor.fetchall()

    conn.close()

    if not results:
        print("\nNo cross-references found.")
        return

    print(f"\nCross-references for {source_reference}:")

    for related_reference, note in results:
        print("\n" + "=" * 60)
        print(f"Related passage: {related_reference}")
        print(f"Why: {note}")
def add_sermon():
    print("\n--- Sermon Notes ---")

    title = input("Sermon title: ")
    scripture = input("Primary Scripture: ")

    print("\nEnter sermon notes.")
    print("Press ENTER on an empty line when finished.")

    lines = []

    while True:
        line = input()

        if line == "":
            break

        lines.append(line)

    content = "\n".join(lines)

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sermons
        (title, scripture, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        title,
        scripture,
        content,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()

    print("\nSermon saved!")


def recent_studies():
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, reference, created_at
        FROM notes
        ORDER BY id DESC
        LIMIT 10
    """)

    results = cursor.fetchall()

    conn.close()

    print("\n--- Recent Studies ---")

    if not results:
        print("No studies yet.")
        return

    for result in results:
        print(
            f"{result[2]} | "
            f"{result[0]} | "
            f"{result[1]}"
        )


def main_menu():
    while True:
        print("\n")
        print("=" * 40)
        print("          BIBLE STUDY TOOL")
        print("=" * 40)

        print("1. Study Dashboard")
        print("2. Read Net Bible")
        print("3. Search My Notes")
        print("4. Read a Passage")
        print("5. Add Study Note")
        print("6. Add Topic")
        print("7. Search Topics")
        print("8. Notes By Topic")
        print("9. Add Cross Reference")
        print("10. Sermon Notes")
        print("11. View Recent Studies")
        print("12. View Cross References")
        print("13. Backup Database")
        print("14. Add Note to Topic")
        print("0. Exit")
        choice = input("\nSelect: ")

        if choice == "1":
            study_dashboard()

        elif choice == "2":
            read_bible()

        elif choice == "3":
            search_notes()

        elif choice == "4":
            bible_study()

        elif choice == "5":
            add_note()

        elif choice == "6":
            add_topic()

        elif choice == "7":
            search_topics()

        elif choice == "8":
            notes_by_topic()

        elif choice == "9":
            add_cross_reference()

        elif choice == "10":
            add_sermon()

        elif choice == "11":
            recent_studies()

        elif choice == "12":
            view_cross_references()

        elif choice == "13":
            print("\nBackup Database will be added next.")

        elif choice == "14":
            add_note_to_topic()

        elif choice == "0":
            print("\nGod bless!")
            break

        else:
            print("\nInvalid selection.")


setup_database()
main_menu()
