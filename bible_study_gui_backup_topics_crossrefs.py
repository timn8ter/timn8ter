import tkinter as tk
from tkinter import ttk

def read_bible():
    import urllib.parse
    import urllib.request

    passage = input("Enter Bible passage (example: John 3:16): ")

    url = "https://labs.bible.org/api/?"
    params = {
        "passage": passage,
        "formatting": "plain",
        "type": "text"
    }

    try:
        full_url = url + urllib.parse.urlencode(params)

        with urllib.request.urlopen(full_url) as response:
            text = response.read().decode("utf-8")

        verses = re.split(r"\s{2,}(?=\d+\s)", text.strip())

        print("\n" + "=" * 50)
        print(passage)
        print("=" * 50)

        for verse in verses:
            print(verse)

        print("=" * 50)

    except Exception as e:
        print("Unable to retrieve passage.")
        print("Error:", e)
def show_bible_reader():
    import urllib.parse
    import urllib.request
    import re

    window = tk.Toplevel()
    window.title("Read NET Bible")
    window.geometry("850x650")

    ttk.Label(
        window,
        text="NET Bible Reader",
        font=("TkDefaultFont", 18, "bold")
    ).pack(pady=15)

    input_frame = ttk.Frame(window)
    input_frame.pack(fill="x", padx=20)

    ttk.Label(
        input_frame,
        text="Bible passage:"
    ).pack(side="left")

    passage_entry = ttk.Entry(input_frame)
    passage_entry.pack(side="left", fill="x", expand=True, padx=10)

    text_frame = ttk.Frame(window)
    text_frame.pack(fill="both", expand=True, padx=20, pady=15)

    text_box = tk.Text(
        text_frame,
        wrap="word",
        font=("TkDefaultFont", 12)
    )
    text_box.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        text_frame,
        orient="vertical",
        command=text_box.yview
    )
    scrollbar.pack(side="right", fill="y")

    text_box.configure(yscrollcommand=scrollbar.set)

    def load_passage():
        passage = passage_entry.get().strip()

        if not passage:
            return

        params = urllib.parse.urlencode({
            "passage": passage,
            "formatting": "plain",
            "type": "text"
        })

        url = "https://labs.bible.org/api/?" + params

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                text = response.read().decode("utf-8")

            verses = re.split(r"\s{2,}(?=\d+\s)", text.strip())

            text_box.delete("1.0", tk.END)

            if verses:
                first_verse = verses[0]
                match = re.match(
                    r"(\d+):(\d+)\s+(.*)",
                    first_verse
                )

                if match:
                    chapter = match.group(1)

                    text_box.insert(
                        tk.END,
                        f"{chapter}:{match.group(2)}  "
                        f"{match.group(3)}\n\n"
                    )

                    for verse in verses[1:]:
                        verse_match = re.match(
                            r"(\d+)\s+(.*)",
                            verse.strip()
                        )

                        if verse_match:
                            text_box.insert(
                                tk.END,
                                f"{chapter}:{verse_match.group(1)}  "
                                f"{verse_match.group(2)}\n\n"
                            )
                        else:
                            text_box.insert(
                                tk.END,
                                verse.strip() + "\n\n"
                            )
                else:
                    text_box.insert(tk.END, text.strip())

        except Exception as error:
            text_box.delete("1.0", tk.END)
            text_box.insert(
                tk.END,
                f"Unable to retrieve the Bible passage.\n\n"
                f"Error: {error}"
            )

    ttk.Button(
        input_frame,
        text="Read",
        command=load_passage
    ).pack(side="left", padx=5)

    ttk.Button(
        input_frame,
        text="Constable's Notes",
        command=lambda: show_constable_notes(passage_entry.get().strip())
    ).pack(side="left", padx=5)

    ttk.Button(
        window,
        text="Close",
        command=window.destroy
    ).pack(pady=(0, 15))

    passage_entry.focus()

def show_constable_notes(passage):
    import urllib.request
    import subprocess
    import tempfile
    import os
    import re
    from tkinter import messagebox

    if not passage:
        messagebox.showwarning(
            "Missing Passage",
            "Please enter a Bible passage first."
        )
        return

    book_map = {
        "genesis": "genesis",
        "exodus": "exodus",
        "leviticus": "leviticus",
        "numbers": "numbers",
        "deuteronomy": "deuteronomy",
        "joshua": "joshua",
        "judges": "judges",
        "ruth": "ruth",
        "1 samuel": "1samuel",
        "2 samuel": "2samuel",
        "1 kings": "1kings",
        "2 kings": "2kings",
        "1 chronicles": "1chronicles",
        "2 chronicles": "2chronicles",
        "ezra": "ezra",
        "nehemiah": "nehemiah",
        "esther": "esther",
        "job": "job",
        "psalms": "psalms",
        "psalm": "psalms",
        "proverbs": "proverbs",
        "ecclesiastes": "ecclesiastes",
        "song of solomon": "songofsolomon",
        "song of songs": "songofsolomon",
        "isaiah": "isaiah",
        "jeremiah": "jeremiah",
        "lamentations": "lamentations",
        "ezekiel": "ezekiel",
        "daniel": "daniel",
        "hosea": "hosea",
        "joel": "joel",
        "amos": "amos",
        "obadiah": "obadiah",
        "jonah": "jonah",
        "micah": "micah",
        "nahum": "nahum",
        "habakkuk": "habakkuk",
        "zephaniah": "zephaniah",
        "haggai": "haggai",
        "zechariah": "zechariah",
        "malachi": "malachi",
        "matthew": "matthew",
        "mark": "mark",
        "luke": "luke",
        "john": "john",
        "acts": "acts",
        "romans": "romans",
        "1 corinthians": "1corinthians",
        "2 corinthians": "2corinthians",
        "galatians": "galatians",
        "ephesians": "ephesians",
        "philippians": "philippians",
        "colossians": "colossians",
        "1 thessalonians": "1thessalonians",
        "2 thessalonians": "2thessalonians",
        "1 timothy": "1timothy",
        "2 timothy": "2timothy",
        "titus": "titus",
        "philemon": "philemon",
        "hebrews": "hebrews",
        "james": "james",
        "1 peter": "1peter",
        "2 peter": "2peter",
        "1 john": "1john",
        "2 john": "2john",
        "3 john": "3john",
        "jude": "jude",
        "revelation": "revelation"
    }

    book_pattern = "|".join(
        re.escape(book) for book in sorted(book_map, key=len, reverse=True)
    )

    match = re.match(
        rf"^\s*({book_pattern})\s+(\d+)(?::(\d+)(?:-(\d+))?)?\s*$",
        passage,
        re.IGNORECASE
    )

    if not match:
        messagebox.showwarning(
            "Invalid Passage",
            "Please enter a Bible passage using a full book name.\n\n"
            "Examples:\n"
            "Romans 8:1-4\n"
            "John 3:16\n"
            "Matthew 5:1-12"
        )
        return

    book_name = match.group(1).lower()
    book = book_map[book_name]
    chapter = int(match.group(2))
    start_verse = int(match.group(3)) if match.group(3) else None
    end_verse = int(match.group(4)) if match.group(4) else start_verse

    pdf_url = f"https://soniclight.com/tcon/notes/pdf/{book}.pdf"

    window = tk.Toplevel()
    window.title("Constable's Notes")
    window.geometry("900x700")

    ttk.Label(
        window,
        text="CONSTABLE'S NOTES",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=15)

    ttk.Label(
        window,
        text=f"Passage: {passage}",
        font=("TkDefaultFont", 12)
    ).pack(pady=(0, 10))

    text_frame = ttk.Frame(window)
    text_frame.pack(fill="both", expand=True, padx=20, pady=10)

    text_box = tk.Text(
        text_frame,
        wrap="word",
        font=("TkDefaultFont", 12)
    )
    text_box.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        text_frame,
        orient="vertical",
        command=text_box.yview
    )
    scrollbar.pack(side="right", fill="y")

    text_box.configure(yscrollcommand=scrollbar.set)

    text_box.insert(
        tk.END,
        "Retrieving Constable's Notes...\n\n"
    )
    window.update_idletasks()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, "romans.pdf")
            txt_path = os.path.join(temp_dir, "romans.txt")

            urllib.request.urlretrieve(pdf_url, pdf_path)

            result = subprocess.run(
                ["pdftotext", "-layout", pdf_path, txt_path],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "The system could not convert the Constable PDF to text."
                )

            with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
                commentary = f.read()

        lines = commentary.splitlines()

        if start_verse is None:
            pattern = re.compile(
                rf"^\s*{chapter}:(\d+)(?:-(\d+))?\s+.*"
            )
            matching = [
                i for i, line in enumerate(lines)
                if pattern.search(line)
            ]
        else:
            matching = []
            for verse in range(start_verse, end_verse + 1):
                patterns = [
                    re.compile(
                        rf"^\s*{chapter}:{verse}(?:-(\d+))?\s+.*",
                        re.IGNORECASE
                    ),
                    re.compile(
                        rf"\b{chapter}:{verse}\s+and\s+\d+\b",
                        re.IGNORECASE
                    ),
                    re.compile(
                        rf"\b{chapter}:{verse}\s+through\s+\d+\b",
                        re.IGNORECASE
                    ),
                    re.compile(
                        rf"\b{chapter}:{verse}-\d+\b",
                        re.IGNORECASE
                    )
                ]

                found = [
                    i for i, line in enumerate(lines)
                    if any(pattern.search(line) for pattern in patterns)
                ]

                if found:
                    matching.append(found[0])

        if not matching:
            raise RuntimeError(
                f"Could not find Constable's Notes for {passage}."
            )

        first_line = min(matching)

        if start_verse is None:
            next_pattern = re.compile(
                rf"^\\s*{chapter + 1}:1(?:-(\\d+))?\\s+"
            )
        else:
            next_verse = end_verse + 1
            next_pattern = re.compile(
                rf"^\\s*{chapter}:{next_verse}(?:-(\\d+))?\\s+"
            )

        end_line = None

        for i in range(first_line + 1, len(lines)):
            if next_pattern.search(lines[i]):
                end_line = i
                break

        if end_line is None:
            end_line = min(first_line + 300, len(lines))

        selected = lines[first_line:end_line]

        while selected and not selected[-1].strip():
            selected.pop()

        text_box.delete("1.0", tk.END)

        text_box.insert(
            tk.END,
            f"Constable's Notes for {passage}\n"
            f"{'=' * 70}\n\n"
        )

        text_box.insert(
            tk.END,
            "\n".join(selected)
        )

        text_box.insert(
            tk.END,
            "\n\n"
            + "=" * 70
            + "\n"
            "Source: Dr. Thomas L. Constable's Expository Notes on Romans.\n"
            "2026 Edition.\n"
        )

    except Exception as error:
        text_box.delete("1.0", tk.END)
        text_box.insert(
            tk.END,
            "Unable to retrieve Constable's Notes.\n\n"
            f"Error: {error}\n\n"
            f"Source: {pdf_url}"
        )

    ttk.Button(
        window,
        text="Close",
        command=window.destroy
    ).pack(pady=(0, 15))


def show_dashboard():
    import sqlite3

    db_path = "/home/tim/BibleStudy/bible_study.db"

    conn = sqlite3.connect(db_path)
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

    window = tk.Toplevel()
    window.title("Study Dashboard")
    window.geometry("700x600")

    ttk.Label(
        window,
        text="BIBLE STUDY DASHBOARD",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=20)

    ttk.Label(
        window,
        text=f"Study Notes: {note_count}    "
             f"Topics: {topic_count}    "
             f"Cross-References: {cross_reference_count}",
        font=("TkDefaultFont", 12)
    ).pack(pady=10)

    ttk.Label(
        window,
        text="Topics",
        font=("TkDefaultFont", 14, "bold")
    ).pack(pady=(20, 5))

    topic_text = "\n".join(
        f"• {topic[0]} ({topic[1]} note{'s' if topic[1] != 1 else ''})"
        for topic in topics
    )

    if not topic_text:
        topic_text = "No topics yet."

    ttk.Label(
        window,
        text=topic_text,
        justify="left"
    ).pack(anchor="w", padx=40)

    ttk.Label(
        window,
        text="Recent Studies",
        font=("TkDefaultFont", 14, "bold")
    ).pack(pady=(25, 5))

    recent_text = "\n\n".join(
        f"{note[0]}\nReference: {note[1]}\nDate: {note[2]}"
        for note in recent_notes
    )

    if not recent_text:
        recent_text = "No study notes yet."

    ttk.Label(
        window,
        text=recent_text,
        justify="left"
    ).pack(anchor="w", padx=40)

    ttk.Button(
        window,
        text="Close",
        command=window.destroy
    ).pack(pady=25)

def show_topics():
    import sqlite3

    window = tk.Toplevel()
    window.title("Topics")
    window.geometry("600x500")

    ttk.Label(
        window,
        text="BIBLE STUDY TOPICS",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=20)

    conn = sqlite3.connect("/home/tim/BibleStudy/bible_study.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topics.id, topics.name, topics.description,
               COUNT(note_topics.note_id)
        FROM topics
        LEFT JOIN note_topics
            ON topics.id = note_topics.topic_id
        GROUP BY topics.id
        ORDER BY topics.name
    """)

    topics = cursor.fetchall()
    conn.close()

    if topics:
        topic_text = "\n\n".join(
            f"{topic[1]}\n"
            f"Description: {topic[2] or 'No description'}\n"
            f"Study Notes: {topic[3]}"
            for topic in topics
        )
    else:
        topic_text = "No topics have been created yet."

    ttk.Label(
        window,
        text=topic_text,
        justify="left"
    ).pack(anchor="w", padx=40, pady=10)

    ttk.Button(
        window,
        text="Close",
        command=window.destroy
    ).pack(pady=20)
def show_cross_references():
    import sqlite3

    window = tk.Toplevel()
    window.title("Cross References")
    window.geometry("700x500")

    ttk.Label(
        window,
        text="BIBLE CROSS REFERENCES",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=20)

    conn = sqlite3.connect("/home/tim/BibleStudy/bible_study.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT source_reference, related_reference, note
        FROM cross_references
        ORDER BY source_reference, related_reference
    """)
    references = cursor.fetchall()
    conn.close()

    if references:
        reference_text = "\n\n".join(
            f"{ref[0]} → {ref[1]}\n"
            f"{ref[2] or ''}"
            for ref in references
        )
    else:
        reference_text = "No cross references have been created yet."

    ttk.Label(
        window,
        text=reference_text,
        justify="left"
    ).pack(anchor="w", padx=40, pady=10)

    ttk.Button(
        window,
        text="Add Cross Reference",
        command=add_cross_reference
    ).pack(pady=10)

    ttk.Button(
        window,
        text="Close",
        command=window.destroy
    ).pack(pady=20)

def show_sermon_notes():
    import sqlite3
    from datetime import datetime
    from tkinter import messagebox

    window = tk.Toplevel()
    window.title("Sermon Notes")
    window.geometry("750x650")

    ttk.Label(
        window,
        text="SERMON NOTES",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=15)

    form = ttk.Frame(window)
    form.pack(fill="x", padx=30)

    ttk.Label(form,text="Sermon Title:").grid(
        row=0, column=0, sticky="w", pady=5
    )

    title_entry = ttk.Entry(form, width=70)
    title_entry.grid(row=0, column=1, sticky="ew", pady=5)

    ttk.Label(form, text="Primary Scripture:").grid(
        row=1, column=0, sticky="w", pady=5
    )

    scripture_entry = ttk.Entry(form, width=70)
    scripture_entry.grid(row=1, column=1, sticky="ew", pady=5)

    ttk.Label(form, text="Sermon Notes:").grid(
        row=2, column=0, sticky="nw", pady=5
    )

    content_text = tk.Text(form, width=70, height=20, wrap="word")
    content_text.grid(row=2, column=1, sticky="nsew", pady=5)

    form.columnconfigure(1, weight=1)
    form.rowconfigure(2, weight=1)

    def save_sermon():
        title = title_entry.get().strip()
        scripture = scripture_entry.get().strip()
        content = content_text.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning(
                "Missing Title",
                "Please enter a sermon title."
            )
            return

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
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

        messagebox.showinfo(
            "Sermon Saved",
            "Sermon notes saved successfully!"
        )

        title_entry.delete(0, tk.END)
        scripture_entry.delete(0, tk.END)
        content_text.delete("1.0", tk.END)

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=15)

    ttk.Button(
        button_frame,
        text="Save Sermon",
        command=save_sermon
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="View Sermon Notes",
        command=view_sermon_notes
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="Close",
        command=window.destroy
    ).pack(side="left", padx=10)

def view_sermon_notes():
    import sqlite3
    from tkinter import messagebox

    window = tk.Toplevel()
    window.title("Saved Sermon Notes")
    window.geometry("850x650")

    ttk.Label(
        window,
        text="SAVED SERMON NOTES",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=15)

    list_frame = ttk.Frame(window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    sermon_list = tk.Listbox(
        list_frame,
        width=90,
        height=20,
        yscrollcommand=scrollbar.set
    )
    sermon_list.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=sermon_list.yview)

    conn = sqlite3.connect(
        "/home/tim/BibleStudy/bible_study.db"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, scripture, content, created_at
        FROM sermons
        ORDER BY id DESC
    """)

    sermons = cursor.fetchall()
    conn.close()

    for sermon in sermons:
        sermon_list.insert(
            tk.END,
            f"{sermon[1]} — {sermon[2]} — {sermon[4]}"
        )

    def edit_sermon():
        selection = sermon_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Sermon",
                "Please select a sermon to edit."
            )
            return

        sermon = sermons[selection[0]]

        edit_window = tk.Toplevel(window)
        edit_window.title("Edit Sermon")
        edit_window.geometry("750x600")

        ttk.Label(
            edit_window,
            text="EDIT SERMON",
            font=("TkDefaultFont", 20, "bold")
        ).pack(pady=15)

        form = ttk.Frame(edit_window)
        form.pack(fill="both", expand=True, padx=30)

        ttk.Label(
            form,
            text="Sermon Title:"
        ).grid(row=0, column=0, sticky="w", pady=8)

        title_entry = ttk.Entry(form, width=70)
        title_entry.grid(row=0, column=1, sticky="ew", pady=8)
        title_entry.insert(0, sermon[1])

        ttk.Label(
            form,
            text="Primary Scripture:"
        ).grid(row=1, column=0, sticky="w", pady=8)

        scripture_entry = ttk.Entry(form, width=70)
        scripture_entry.grid(row=1, column=1, sticky="ew", pady=8)
        scripture_entry.insert(0, sermon[2])

        ttk.Label(
            form,
            text="Sermon Notes:"
        ).grid(row=2, column=0, sticky="nw", pady=8)

        content_text = tk.Text(
            form,
            width=70,
            height=20,
            wrap="word"
        )
        content_text.grid(row=2, column=1, sticky="nsew", pady=8)
        content_text.insert("1.0", sermon[3])

        form.columnconfigure(1, weight=1)
        form.rowconfigure(2, weight=1)

        def save_changes():
            title = title_entry.get().strip()
            scripture = scripture_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()

            if not title:
                messagebox.showwarning(
                    "Missing Title",
                    "Please enter a sermon title."
                )
                return

            conn = sqlite3.connect(
                "/home/tim/BibleStudy/bible_study.db"
            )
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE sermons
                SET title = ?, scripture = ?, content = ?
                WHERE id = ?
            """, (
                title,
                scripture,
                content,
                sermon[0]
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Sermon Updated",
                "Sermon notes updated successfully!"
            )

            edit_window.destroy()
            window.destroy()
            view_sermon_notes()

        ttk.Button(
            edit_window,
            text="Save Changes",
            command=save_changes
        ).pack(side="left", padx=20, pady=15)

        ttk.Button(
            edit_window,
            text="Cancel",
            command=edit_window.destroy
        ).pack(side="left", padx=20, pady=15)

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=15)

    ttk.Button(
        button_frame,
        text="Edit Sermon",
        command=edit_sermon
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="Close",
        command=window.destroy
    ).pack(side="left", padx=10)

def add_cross_reference():
    import sqlite3
    from tkinter import messagebox

    window = tk.Toplevel()
    window.title("Add Cross Reference")
    window.geometry("700x500")

    ttk.Label(
        window,
        text="ADD CROSS REFERENCE",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=20)

    form = ttk.Frame(window)
    form.pack(fill="x", padx=30)

    ttk.Label(
        form,
        text="Source Reference:"
    ).grid(row=0, column=0, sticky="w", pady=10)

    source_entry = ttk.Entry(form, width=60)
    source_entry.grid(row=0, column=1, sticky="ew", pady=10)

    ttk.Label(
        form,
        text="Related Reference:"
    ).grid(row=1, column=0, sticky="w", pady=10)

    related_entry = ttk.Entry(form, width=60)
    related_entry.grid(row=1, column=1, sticky="ew", pady=10)

    ttk.Label(
        form,
        text="Why are they related?"
    ).grid(row=2, column=0, sticky="nw", pady=10)

    note_text = tk.Text(
        form,
        width=60,
        height=12,
        wrap="word"
    )
    note_text.grid(row=2, column=1, sticky="nsew", pady=10)

    form.columnconfigure(1, weight=1)
    form.rowconfigure(2, weight=1)

    def save_cross_reference():
        source_reference = source_entry.get().strip()
        related_reference = related_entry.get().strip()
        note = note_text.get("1.0", tk.END).strip()

        if not source_reference or not related_reference:
            messagebox.showwarning(
                "Missing Information",
                "Please enter both Bible references."
            )
            return

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
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

        messagebox.showinfo(
            "Cross Reference Saved",
            "Cross reference saved successfully!"
        )

        source_entry.delete(0, tk.END)
        related_entry.delete(0, tk.END)
        note_text.delete("1.0", tk.END)

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=15)

    ttk.Button(
        button_frame,
        text="Save Cross Reference",
        command=save_cross_reference
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="Close",
        command=window.destroy
    ).pack(side="left", padx=10)

def get_verse_of_day():
    import urllib.parse
    import urllib.request
    from datetime import date

    verses = [
        "Genesis 1:1",
        "Genesis 1:27",
        "Genesis 2:7",
        "Genesis 12:2",
        "Genesis 15:6",
        "Genesis 18:14",
        "Genesis 28:15",
        "Genesis 50:20",
        "Exodus 14:14",
        "Exodus 15:2",
        "Exodus 20:3",
        "Exodus 20:12",
        "Exodus 33:14",
        "Leviticus 19:18",
        "Numbers 6:24-26",
        "Numbers 23:19",
        "Deuteronomy 6:5",
        "Deuteronomy 7:9",
        "Deuteronomy 10:12",
        "Deuteronomy 31:6",
        "Deuteronomy 31:8",
        "Joshua 1:5",
        "Joshua 1:8",
        "Joshua 1:9",
        "Joshua 24:15",
        "Judges 6:12",
        "Ruth 1:16",
        "1 Samuel 2:2",
        "1 Samuel 16:7",
        "2 Samuel 22:2",
        "2 Samuel 22:31",
        "1 Kings 8:61",
        "1 Kings 18:21",
        "2 Kings 6:16",
        "1 Chronicles 16:11",
        "1 Chronicles 16:34",
        "1 Chronicles 28:9",
        "2 Chronicles 7:14",
        "2 Chronicles 16:9",
        "2 Chronicles 20:15",
        "Ezra 7:10",
        "Nehemiah 8:10",
        "Esther 4:14",
        "Job 1:21",
        "Job 19:25",
        "Job 23:10",
        "Psalm 1:1",
        "Psalm 1:2",
        "Psalm 3:3",
        "Psalm 4:8",
        "Psalm 5:11",
        "Psalm 8:3-4",
        "Psalm 9:1",
        "Psalm 16:8",
        "Psalm 18:1",
        "Psalm 18:2",
        "Psalm 19:1",
        "Psalm 19:14",
        "Psalm 23:1",
        "Psalm 23:4",
        "Psalm 23:6",
        "Psalm 24:1",
        "Psalm 25:4-5",
        "Psalm 27:1",
        "Psalm 27:4",
        "Psalm 27:14",
        "Psalm 28:7",
        "Psalm 30:5",
        "Psalm 32:8",
        "Psalm 34:4",
        "Psalm 34:7",
        "Psalm 34:8",
        "Psalm 34:18",
        "Psalm 37:4",
        "Psalm 37:5",
        "Psalm 37:23-24",
        "Psalm 40:1-2",
        "Psalm 42:1",
        "Psalm 46:1",
        "Psalm 46:10",
        "Psalm 51:10",
        "Psalm 55:22",
        "Psalm 56:3",
        "Psalm 57:1",
        "Psalm 61:1-2",
        "Psalm 62:1-2",
        "Psalm 63:1",
        "Psalm 66:18",
        "Psalm 68:19",
        "Psalm 73:25-26",
        "Psalm 84:11",
        "Psalm 86:11",
        "Psalm 90:12",
        "Psalm 91:1-2",
        "Psalm 91:4",
        "Psalm 94:19",
        "Psalm 100:4-5",
        "Psalm 103:1-5",
        "Psalm 103:8",
        "Psalm 107:1",
        "Psalm 111:10",
        "Psalm 118:5-6",
        "Psalm 118:24",
        "Psalm 119:9",
        "Psalm 119:11",
        "Psalm 119:18",
        "Psalm 119:28",
        "Psalm 119:50",
        "Psalm 119:89",
        "Psalm 119:105",
        "Psalm 119:114",
        "Psalm 119:165",
        "Psalm 121:1-2",
        "Psalm 121:7-8",
        "Psalm 127:3",
        "Psalm 130:5",
        "Psalm 133:1",
        "Psalm 139:1-4",
        "Psalm 139:23-24",
        "Psalm 145:8-9",
        "Psalm 147:3",
        "Psalm 150:6",
        "Proverbs 1:7",
        "Proverbs 2:6",
        "Proverbs 3:5-6",
        "Proverbs 3:7-8",
        "Proverbs 3:11-12",
        "Proverbs 4:23",
        "Proverbs 8:17",
        "Proverbs 9:10",
        "Proverbs 10:12",
        "Proverbs 11:25",
        "Proverbs 12:25",
        "Proverbs 13:20",
        "Proverbs 14:12",
        "Proverbs 15:1",
        "Proverbs 15:3",
        "Proverbs 16:3",
        "Proverbs 16:9",
        "Proverbs 16:18",
        "Proverbs 17:17",
        "Proverbs 18:10",
        "Proverbs 18:21",
        "Proverbs 19:21",
        "Proverbs 20:24",
        "Proverbs 21:21",
        "Proverbs 22:6",
        "Proverbs 27:17",
        "Proverbs 28:13",
        "Proverbs 29:25",
        "Proverbs 31:10",
        "Ecclesiastes 3:1",
        "Ecclesiastes 4:9-10",
        "Ecclesiastes 12:13",
        "Isaiah 6:8",
        "Isaiah 9:6",
        "Isaiah 26:3",
        "Isaiah 40:8",
        "Isaiah 40:28-31",
        "Isaiah 41:10",
        "Isaiah 43:1-2",
        "Isaiah 43:18-19",
        "Isaiah 53:5",
        "Isaiah 54:10",
        "Isaiah 55:8-9",
        "Isaiah 55:11",
        "Isaiah 58:11",
        "Isaiah 61:1",
        "Isaiah 64:8",
        "Jeremiah 1:5",
        "Jeremiah 17:7-8",
        "Jeremiah 29:11",
        "Jeremiah 31:3",
        "Jeremiah 32:17",
        "Jeremiah 33:3",
        "Lamentations 3:22-23",
        "Lamentations 3:25",
        "Ezekiel 36:26",
        "Ezekiel 37:14",
        "Daniel 3:17-18",
        "Daniel 6:27",
        "Daniel 12:3",
        "Hosea 6:6",
        "Joel 2:12-13",
        "Joel 2:25",
        "Amos 5:24",
        "Micah 6:8",
        "Nahum 1:7",
        "Habakkuk 2:4",
        "Habakkuk 3:17-18",
        "Zephaniah 3:17",
        "Haggai 1:5",
        "Zechariah 4:6",
        "Malachi 3:10",
        "Matthew 4:4",
        "Matthew 5:3",
        "Matthew 5:14-16",
        "Matthew 5:44",
        "Matthew 6:9-13",
        "Matthew 6:19-21",
        "Matthew 6:25-26",
        "Matthew 6:33-34",
        "Matthew 7:7",
        "Matthew 7:12",
        "Matthew 7:24-25",
        "Matthew 9:36-38",
        "Matthew 11:28-30",
        "Matthew 16:24",
        "Matthew 17:20",
        "Matthew 18:20",
        "Matthew 19:26",
        "Matthew 21:22",
        "Matthew 22:37-39",
        "Matthew 28:18-20",
        "Mark 8:34",
        "Mark 9:23",
        "Mark 10:27",
        "Mark 10:45",
        "Mark 11:24",
        "Mark 12:30-31",
        "Mark 16:15",
        "Luke 1:37",
        "Luke 4:18",
        "Luke 6:31",
        "Luke 6:36",
        "Luke 9:23",
        "Luke 10:27",
        "Luke 11:9-10",
        "Luke 12:6-7",
        "Luke 18:27",
        "Luke 19:10",
        "Luke 23:34",
        "John 1:1",
        "John 1:14",
        "John 3:16",
        "John 3:17",
        "John 3:18",
        "John 4:24",
        "John 6:35",
        "John 8:12",
        "John 10:10",
        "John 10:27-28",
        "John 11:25-26",
        "John 13:34-35",
        "John 14:1",
        "John 14:6",
        "John 14:15",
        "John 14:27",
        "John 15:5",
        "John 15:12-13",
        "John 16:33",
        "John 17:17",
        "John 20:29",
        "Acts 1:8",
        "Acts 2:38",
        "Acts 4:12",
        "Acts 16:31",
        "Acts 20:24",
        "Romans 1:16",
        "Romans 3:23",
        "Romans 5:1",
        "Romans 5:8",
        "Romans 6:23",
        "Romans 8:1",
        "Romans 8:6",
        "Romans 8:18",
        "Romans 8:26",
        "Romans 8:28",
        "Romans 8:31",
        "Romans 8:32",
        "Romans 8:37-39",
        "Romans 10:9-10",
        "Romans 12:1-2",
        "Romans 12:9-10",
        "Romans 12:18",
        "Romans 15:13",
        "1 Corinthians 1:18",
        "1 Corinthians 6:19-20",
        "1 Corinthians 10:13",
        "1 Corinthians 13:4-7",
        "1 Corinthians 15:33",
        "1 Corinthians 15:58",
        "2 Corinthians 3:17",
        "2 Corinthians 4:16-18",
        "2 Corinthians 5:7",
        "2 Corinthians 5:17",
        "2 Corinthians 9:7",
        "2 Corinthians 12:9",
        "Galatians 2:20",
        "Galatians 5:1",
        "Galatians 5:13",
        "Galatians 5:22-23",
        "Galatians 6:9",
        "Ephesians 2:8-9",
        "Ephesians 2:10",
        "Ephesians 3:20-21",
        "Ephesians 4:32",
        "Ephesians 5:2",
        "Ephesians 6:10-11",
        "Philippians 1:6",
        "Philippians 2:3-4",
        "Philippians 3:13-14",
        "Philippians 4:4",
        "Philippians 4:6-7",
        "Philippians 4:8",
        "Philippians 4:13",
        "Philippians 4:19",
        "Colossians 3:1-2",
        "Colossians 3:12-14",
        "Colossians 3:17",
        "1 Thessalonians 5:16-18",
        "1 Thessalonians 5:21-22",
        "2 Thessalonians 3:3",
        "1 Timothy 4:12",
        "1 Timothy 6:6",
        "2 Timothy 1:7",
        "2 Timothy 2:15",
        "2 Timothy 3:16-17",
        "Titus 2:11-12",
        "Philemon 1:4-7",
        "Hebrews 4:12",
        "Hebrews 4:16",
        "Hebrews 10:23",
        "Hebrews 11:1",
        "Hebrews 11:6",
        "Hebrews 12:1-2",
        "Hebrews 13:5-6",
        "James 1:2-4",
        "James 1:5",
        "James 1:19",
        "James 2:17",
        "James 4:7-8",
        "James 5:16",
        "1 Peter 1:3",
        "1 Peter 2:9",
        "1 Peter 5:7",
        "1 Peter 5:8-9",
        "2 Peter 1:3",
        "2 Peter 3:18",
        "1 John 1:9",
        "1 John 3:1",
        "1 John 4:4",
        "1 John 4:7-8",
        "1 John 4:19",
        "1 John 5:14",
        "2 John 1:6",
        "3 John 1:4",
        "Jude 1:24-25",
        "Revelation 1:8",
        "Revelation 3:20",
        "Revelation 21:4",
        "Revelation 21:5",
        "Revelation 22:12",
        "Revelation 22:20",
        "Psalm 138:8",
        "Proverbs 16:20",
        "Isaiah 12:2",
        "Jeremiah 20:11",
        "Matthew 10:31",
        "Luke 12:32",
        "John 16:13",
        "Romans 15:5",
        "Ephesians 3:17",
        "Colossians 2:6",
        "Hebrews 13:8"
    ]

    day_number = date.today().timetuple().tm_yday
    passage = verses[(day_number - 1) % len(verses)]

    params = urllib.parse.urlencode({
        "passage": passage,
        "formatting": "plain",
        "type": "text"
    })

    url = "https://labs.bible.org/api/?" + params

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            text = response.read().decode("utf-8").strip()

        import re

        clean_text = re.sub(
            r"^\d+:\d+\s*",
            "",
            text
        )

        return passage, clean_text

    except Exception:
        return passage, "Unable to load the Verse of the Day."

def personal_bible_study():
    import sqlite3
    from tkinter import messagebox
    from datetime import datetime

    window = tk.Toplevel()
    window.title("Personal Bible Study")
    window.geometry("850x700")

    ttk.Label(
        window,
        text="PERSONAL BIBLE STUDY",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=15)

    form = ttk.Frame(window)
    form.pack(fill="both", expand=True, padx=30)

    ttk.Label(
        form,
        text="Study Title:"
    ).grid(row=0, column=0, sticky="w", pady=8)

    title_entry = ttk.Entry(form, width=70)
    title_entry.grid(row=0, column=1, sticky="ew", pady=8)

    ttk.Label(
        form,
        text="Bible Reference:"
    ).grid(row=1, column=0, sticky="w", pady=8)

    reference_entry = ttk.Entry(form, width=70)
    reference_entry.grid(row=1, column=1, sticky="ew", pady=8)

    ttk.Label(
        form,
        text="Personal Study:"
    ).grid(row=2, column=0, sticky="nw", pady=8)

    study_text = tk.Text(
        form,
        width=70,
        height=25,
        wrap="word"
    )
    study_text.grid(row=2, column=1, sticky="nsew", pady=8)

    form.columnconfigure(1, weight=1)
    form.rowconfigure(2, weight=1)

    def save_study():
        title = title_entry.get().strip()
        reference = reference_entry.get().strip()
        content = study_text.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning(
                "Missing Title",
                "Please enter a study title."
            )
            return

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal_studies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                reference TEXT,
                content TEXT,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            INSERT INTO personal_studies
            (title, reference, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            title,
            reference,
            content,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Study Saved",
            "Personal Bible Study saved successfully!"
        )

        title_entry.delete(0, tk.END)
        reference_entry.delete(0, tk.END)
        study_text.delete("1.0", tk.END)

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=15)

    ttk.Button(
        button_frame,
        text="Save Study",
        command=save_study
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="View Studies",
        command=view_personal_studies
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="Close",
        command=window.destroy
    ).pack(side="left", padx=10)

def view_personal_studies():
    import sqlite3
    from tkinter import messagebox
    from datetime import datetime

    window = tk.Toplevel()
    window.title("Personal Bible Studies")
    window.geometry("900x700")

    ttk.Label(
        window,
        text="PERSONAL BIBLE STUDIES",
        font=("TkDefaultFont", 20, "bold")
    ).pack(pady=15)

    search_frame = ttk.LabelFrame(
        window,
        text="Search Personal Bible Studies"
    )
    search_frame.pack(fill="x", padx=20, pady=(0, 10))

    ttk.Label(
        search_frame,
        text="Search:"
    ).pack(side="left", padx=(10, 8), pady=10)

    search_entry = ttk.Entry(
        search_frame,
        width=50
    )
    search_entry.pack(side="left", fill="x", expand=True, padx=8, pady=10)

    list_frame = ttk.Frame(window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    study_list = tk.Listbox(
        list_frame,
        width=90,
        height=20,
        yscrollcommand=scrollbar.set
    )
    study_list.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=study_list.yview)

    conn = sqlite3.connect(
        "/home/tim/BibleStudy/bible_study.db"
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personal_studies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reference TEXT,
            content TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        SELECT id, title, reference, content, created_at
        FROM personal_studies
        ORDER BY id DESC
    """)

    studies = cursor.fetchall()
    conn.close()

    current_studies = studies.copy()

    def display_studies(study_results):
        nonlocal current_studies

        current_studies = study_results

        study_list.delete(0, tk.END)

        for study in study_results:
            study_list.insert(
                tk.END,
                f"{study[1]} — {study[2]} — {study[4]}"
            )

    display_studies(studies)

    def search_studies():
        search_term = search_entry.get().strip().lower()

        if not search_term:
            display_studies(studies)
            return

        filtered_studies = [
            study for study in studies
            if search_term in (study[1] or "").lower()
            or search_term in (study[2] or "").lower()
            or search_term in (study[3] or "").lower()
        ]

        display_studies(filtered_studies)

    def clear_search():
        search_entry.delete(0, tk.END)
        display_studies(studies)

    ttk.Button(
        search_frame,
        text="Search",
        command=search_studies
    ).pack(side="left", padx=4)

    ttk.Button(
        search_frame,
        text="Clear",
        command=clear_search
    ).pack(side="left", padx=4)

    def edit_study():
        selection = study_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Study",
                "Please select a study to edit."
            )
            return

        study = current_studies[selection[0]]

        edit_window = tk.Toplevel(window)
        edit_window.title("Edit Personal Bible Study")
        edit_window.geometry("800x650")

        ttk.Label(
            edit_window,
            text="EDIT PERSONAL BIBLE STUDY",
            font=("TkDefaultFont", 20, "bold")
        ).pack(pady=15)

        form = ttk.Frame(edit_window)
        form.pack(fill="both", expand=True, padx=30)

        ttk.Label(
            form,
            text="Study Title:"
        ).grid(row=0, column=0, sticky="w", pady=8)

        title_entry = ttk.Entry(form, width=70)
        title_entry.grid(row=0, column=1, sticky="ew", pady=8)
        title_entry.insert(0, study[1])

        ttk.Label(
            form,
            text="Bible Reference:"
        ).grid(row=1, column=0, sticky="w", pady=8)

        reference_entry = ttk.Entry(form, width=70)
        reference_entry.grid(row=1, column=1, sticky="ew", pady=8)
        reference_entry.insert(0, study[2])

        ttk.Label(
            form,
            text="Personal Study:"
        ).grid(row=2, column=0, sticky="nw", pady=8)

        content_text = tk.Text(
            form,
            width=70,
            height=25,
            wrap="word"
        )
        content_text.grid(row=2, column=1, sticky="nsew", pady=8)
        content_text.insert("1.0", study[3])

        form.columnconfigure(1, weight=1)
        form.rowconfigure(2, weight=1)

        def save_changes():
            title = title_entry.get().strip()
            reference = reference_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()

            if not title:
                messagebox.showwarning(
                    "Missing Title",
                    "Please enter a study title."
                )
                return

            conn = sqlite3.connect(
                "/home/tim/BibleStudy/bible_study.db"
            )
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE personal_studies
                SET title = ?, reference = ?, content = ?
                WHERE id = ?
            """, (
                title,
                reference,
                content,
                study[0]
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Study Updated",
                "Personal Bible Study updated successfully!"
            )

            edit_window.destroy()
            window.destroy()
            view_personal_studies()

        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=15)

        ttk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=edit_window.destroy
        ).pack(side="left", padx=10)

    def delete_study():
        selection = study_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Study",
                "Please select a study to delete."
            )
            return

        study = current_studies[selection[0]]

        confirm = messagebox.askyesno(
            "Delete Study",
            f"Are you sure you want to delete:\n\n"
            f"{study[1]}\n\n"
            "This cannot be undone."
        )

        if not confirm:
            return

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM personal_studies
            WHERE id = ?
        """, (study[0],))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Study Deleted",
            "Personal Bible Study deleted successfully!"
        )

        window.destroy()
        view_personal_studies()

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=15)

    ttk.Button(
        button_frame,
        text="Edit Study",
        command=edit_study
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="Delete Study",
        command=delete_study
    ).pack(side="left", padx=10)

    ttk.Button(
        button_frame,
        text="Close",
        command=window.destroy
    ).pack(side="left", padx=10)

def main():
    from datetime import date

    root = tk.Tk()
    root.title("Bible Study")
    root.geometry("900x600")
    root.minsize(700, 500)

    title = ttk.Label(
        root,
        text="Bible Study",
        font=("TkDefaultFont", 24, "bold")
    )
    title.pack(pady=(25, 5))

    subtitle = ttk.Label(
        root,
        text="Study Dashboard",
        font=("TkDefaultFont", 12)
    )
    subtitle.pack(pady=(0, 25))

    verse_reference, verse_text = get_verse_of_day()

    verse_frame = ttk.LabelFrame(
        root,
        text="Verse of the Day"
    )
    verse_frame.pack(
        fill="x",
        padx=40,
        pady=(0, 20)
    )

    verse_label = ttk.Label(
        verse_frame,
        text=verse_text,
        wraplength=800,
        justify="center",
        font=("TkDefaultFont", 12)
    )
    verse_label.pack(padx=20, pady=(15, 5))

    reference_label = ttk.Label(
        verse_frame,
        text=verse_reference,
        font=("TkDefaultFont", 11, "bold")
    )
    reference_label.pack(pady=(0, 15))

    current_day = date.today()

    def update_verse_of_day():
        nonlocal current_day

        today = date.today()

        if today != current_day:
            current_day = today

            new_reference, new_text = get_verse_of_day()

            verse_label.config(text=new_text)
            reference_label.config(text=new_reference)

        root.after(60000, update_verse_of_day)

    root.after(60000, update_verse_of_day)

    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)

    ttk.Button(
        button_frame,
        text="Read Bible",
        width=25,
        command=show_bible_reader
    ).grid(row=0, column=1, padx=10, pady=10)

    ttk.Button(
    button_frame,
    text="Study Dashboard",
    width=25,
    command=show_dashboard
    ).grid(row=0, column=0, padx=10, pady=10)

    ttk.Button(
        button_frame,
        text="Topics",
        width=25,
        command=show_topics
    ).grid(row=1, column=0, padx=10, pady=10)

    ttk.Button(
        button_frame,
        text="Cross References",
        width=25,
        command=show_cross_references
    ).grid(row=2, column=0, padx=10, pady=10)

    ttk.Button(
        button_frame,
        text="Sermon Notes",
        width=25,
        command=show_sermon_notes
    ).grid(row=1, column=1, padx=10, pady=10)

    ttk.Button(
        button_frame,
        text="Personal Bible Study",
        width=25,
        command=personal_bible_study
    ).grid(row=2, column=1, padx=10, pady=10)

    ttk.Button(
        root,
        text="Exit",
        command=root.destroy,
        width=20
    ).pack(pady=30)

    root.mainloop()


if __name__ == "__main__":
    main()
