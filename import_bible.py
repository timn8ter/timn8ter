import sqlite3

DATABASE = "bible_study.db"
BIBLE_FILE = "bible.txt"


def import_bible():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM verses")

    with open(BIBLE_FILE, "r", encoding="utf-8") as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            parts = line.split("|", 3)

            if len(parts) != 4:
                continue

            book = parts[0]
            chapter = int(parts[1])
            verse = int(parts[2])
            text = parts[3]

            cursor.execute("""
                INSERT INTO verses
                (book, chapter, verse, text)
                VALUES (?, ?, ?, ?)
            """, (
                book,
                chapter,
                verse,
                text
            ))

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM verses")
    count = cursor.fetchone()[0]

    conn.close()

    print(f"Imported {count} verses.")


if __name__ == "__main__":
    import_bible()
