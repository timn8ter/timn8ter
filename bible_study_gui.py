import tkinter as tk
from tkinter import ttk
import urllib.request
import json
import re
import sqlite3
import calendar


# Bible Study color theme
BG_COLOR = "#f4f1ea"
HEADER_COLOR = "#3f2f24"
HEADER_TEXT_COLOR = "#f5e6c8"
SECONDARY_COLOR = "#e8d8bd"
TEXT_COLOR = "#3f2f24"


def style_bible_window(window, title, height=15):
    window.configure(bg=BG_COLOR)

    header = tk.Frame(
        window,
        bg=HEADER_COLOR
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text=title,
        font=("TkDefaultFont", 20, "bold"),
        bg=HEADER_COLOR,
        fg=HEADER_TEXT_COLOR
    ).pack(pady=15)

    return header

def read_bible():
    import urllib.parse
    import urllib.request
    import json

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

OPENBIBLE_FILE = "/home/tim/BibleStudy/cross_references.txt"

OPENBIBLE_BOOKS = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev",
    "Numbers": "Num", "Deuteronomy": "Deut", "Joshua": "Josh",
    "Judges": "Judg", "Ruth": "Ruth", "1 Samuel": "1Sam",
    "2 Samuel": "2Sam", "1 Kings": "1Kgs", "2 Kings": "2Kgs",
    "1 Chronicles": "1Chr", "2 Chronicles": "2Chr",
    "Ezra": "Ezra", "Nehemiah": "Neh", "Esther": "Est",
    "Job": "Job", "Psalms": "Ps", "Psalm": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Song of Solomon": "Song",
    "Isaiah": "Isa", "Jeremiah": "Jer", "Lamentations": "Lam",
    "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad",
    "Jonah": "Jonah", "Micah": "Mic", "Nahum": "Nah",
    "Habakkuk": "Hab", "Zephaniah": "Zeph", "Haggai": "Hag",
    "Zechariah": "Zech", "Malachi": "Mal",

    "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke",
    "John": "John", "Acts": "Acts", "Romans": "Rom",
    "1 Corinthians": "1Cor", "2 Corinthians": "2Cor",
    "Galatians": "Gal", "Ephesians": "Eph", "Philippians": "Phil",
    "Colossians": "Col", "1 Thessalonians": "1Thess",
    "2 Thessalonians": "2Thess", "1 Timothy": "1Tim",
    "2 Timothy": "2Tim", "Titus": "Titus", "Philemon": "Phlm",
    "Hebrews": "Heb", "James": "Jas", "1 Peter": "1Pet",
    "2 Peter": "2Pet", "1 John": "1John", "2 John": "2John",
    "3 John": "3John", "Jude": "Jude", "Revelation": "Rev"
}


def openbible_reference_to_readable(reference):
    reverse_books = {}

    for full_name, abbreviation in OPENBIBLE_BOOKS.items():
        reverse_books[abbreviation] = full_name

    def convert_single(ref):
        parts = ref.split(".")

        if len(parts) < 3:
            return ref

        book = reverse_books.get(parts[0], parts[0])
        chapter = parts[1]
        verse = parts[2]

        return f"{book} {chapter}:{verse}"

    if "-" not in reference:
        return convert_single(reference)

    start_ref, end_ref = reference.split("-", 1)

    start_parts = start_ref.split(".")
    end_parts = end_ref.split(".")

    if len(start_parts) >= 3 and len(end_parts) >= 3:
        start_book = reverse_books.get(
            start_parts[0],
            start_parts[0]
        )

        end_book = reverse_books.get(
            end_parts[0],
            end_parts[0]
        )

        start_chapter = start_parts[1]
        start_verse = start_parts[2]

        end_chapter = end_parts[1]
        end_verse = end_parts[2]

        if (
            start_book == end_book
            and start_chapter == end_chapter
        ):
            return (
                f"{start_book} {start_chapter}:"
                f"{start_verse}–{end_verse}"
            )

        if start_book == end_book:
            return (
                f"{start_book} {start_chapter}:{start_verse}"
                f"–{end_chapter}:{end_verse}"
            )

        return (
            f"{start_book} {start_chapter}:{start_verse}"
            f" – {end_book} {end_chapter}:{end_verse}"
        )

    return convert_single(reference)



def get_openbible_cross_references(book, chapter, verse):
    dataset_book = OPENBIBLE_BOOKS.get(book)

    if not dataset_book:
        return []

    search_verse = f"{dataset_book}.{chapter}.{verse}"

    results = []

    try:
        with open(OPENBIBLE_FILE, encoding="utf-8") as f:
            next(f)

            for line in f:
                parts = line.strip().split("\t")

                if len(parts) < 3:
                    continue

                from_verse, to_verse, votes = parts[:3]

                if from_verse == search_verse:
                    try:
                        results.append(
                            (to_verse, int(votes))
                        )
                    except ValueError:
                        pass

    except FileNotFoundError:
        return []

    results.sort(key=lambda item: item[1], reverse=True)

    return results

COMMENTARY_API = "https://bible.helloao.org/api/c"


COMMENTARIES = {
    "Matthew Henry": "matthew-henry",
    "Adam Clarke": "adam-clarke",
    "John Gill": "john-gill",
    "John Calvin": "john-calvin",
    "Jamieson-Fausset-Brown": "jamieson-fausset-brown",
    "Keil & Delitzsch": "keil-delitzsch",
    "Tyndale": "tyndale"
}


COMMENTARY_BOOKS = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV",
    "Numbers": "NUM", "Deuteronomy": "DEU", "Joshua": "JOS",
    "Judges": "JDG", "Ruth": "RUT", "1 Samuel": "1SA",
    "2 Samuel": "2SA", "1 Kings": "1KI", "2 Kings": "2KI",
    "1 Chronicles": "1CH", "2 Chronicles": "2CH",
    "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST",
    "Job": "JOB", "Psalms": "PSA", "Psalm": "PSA",
    "Proverbs": "PRO", "Ecclesiastes": "ECC",
    "Song of Solomon": "SNG", "Isaiah": "ISA",
    "Jeremiah": "JER", "Lamentations": "LAM",
    "Ezekiel": "EZK", "Daniel": "DAN", "Hosea": "HOS",
    "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA",
    "Jonah": "JON", "Micah": "MIC", "Nahum": "NAM",
    "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG",
    "Zechariah": "ZEC", "Malachi": "MAL",
    "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK",
    "John": "JHN", "Acts": "ACT", "Romans": "ROM",
    "1 Corinthians": "1CO", "2 Corinthians": "2CO",
    "Galatians": "GAL", "Ephesians": "EPH",
    "Philippians": "PHP", "Colossians": "COL",
    "1 Thessalonians": "1TH", "2 Thessalonians": "2TH",
    "1 Timothy": "1TI", "2 Timothy": "2TI",
    "Titus": "TIT", "Philemon": "PHM", "Hebrews": "HEB",
    "James": "JAS", "1 Peter": "1PE", "2 Peter": "2PE",
    "1 John": "1JN", "2 John": "2JN", "3 John": "3JN",
    "Jude": "JUD", "Revelation": "REV"
}

def get_commentary_section(commentary_id, book, chapter, verse):
    api_book = COMMENTARY_BOOKS.get(book)

    if not api_book:
        return {
            "status": "book_mapping_missing",
            "text": None
        }

    url = (
        f"{COMMENTARY_API}/{commentary_id}/"
        f"{api_book}/{chapter}.simple.json"
    )

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        sections = data.get("chapter", {}).get("content", [])

        best_section = None

        for section in sections:
            try:
                section_verse = int(section.get("number"))
            except (TypeError, ValueError):
                continue

            if section_verse <= verse:
                if (
                    best_section is None
                    or section_verse > best_section[0]
                ):
                    text = section.get("text", "")

                    if isinstance(text, list):
                        text = " ".join(
                            str(item) for item in text
                        )

                    text = str(text).strip()

                    if text:
                        best_section = (
                            section_verse,
                            text
                        )

        if best_section:
            return {
                "status": "success",
                "text": best_section[1]
            }

        return {
            "status": "no_section",
            "text": None
        }

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                "status": "not_available",
                "text": None
            }

        print("Commentary HTTP error:", e)

        return {
            "status": "error",
            "text": None
        }

    except Exception as e:
        print("Commentary error:", e)

        return {
            "status": "error",
            "text": None
        }

def show_bible_reader():
    import urllib.parse
    import urllib.request
    import re

    window = tk.Toplevel()
    window.title("Read NET Bible")
    window.geometry("700x600")
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="NET BIBLE READER",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)

    input_frame = ttk.Frame(window)
    input_frame.pack(fill="x", padx=20)

    version_frame = ttk.Frame(window)
    version_frame.pack(fill="x", padx=20, pady=(0, 5))

    ttk.Label(
        version_frame,
        text="Bible Version:"
    ).pack(side="left")

    bible_version = ttk.Combobox(
        version_frame,
        values=["NET", "CSB", "ESV"],
        state="readonly",
        width=12
    )
    bible_version.set("NET")
    bible_version.pack(side="left", padx=10)

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
    def copy_selected_text(event=None):
        try:
            selected_text = text_box.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return

        window.clipboard_clear()
        window.clipboard_append(selected_text)
        window.update()

    context_menu = tk.Menu(window, tearoff=0)
    context_menu.add_command(
        label="Copy",
        command=copy_selected_text
    )

    def select_all_text():
        text_box.tag_remove(tk.SEL, "1.0", tk.END)

        cross_ref_start = text_box.search(
            "=" * 60,
            "1.0",
            tk.END
        )

        if cross_ref_start:
            text_box.tag_add(
                tk.SEL,
                "1.0",
                cross_ref_start
            )
        else:
            text_box.tag_add(
                tk.SEL,
                "1.0",
                tk.END
            )

        text_box.mark_set(tk.INSERT, "1.0")
        text_box.see(tk.INSERT)

    context_menu.add_command(
        label="Select All",
        command=select_all_text
    )

    def show_context_menu(event):
        try:
            text_box.selection_get()
            context_menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            pass

    text_box.bind("<Button-3>", show_context_menu)

    def load_passage():
        passage = passage_entry.get().strip()

        if not passage:
            return

        selected_version = bible_version.get()

        if selected_version == "CSB":
            import webbrowser

            passage_match = re.match(
                r"^\s*((?:[1-3]\s)?[A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+)",
                passage
            )

            if passage_match:
                book = passage_match.group(1).strip().lower()
                chapter = passage_match.group(2)

                book = book.replace(" ", "-")

                url = (
                    "https://read.csbible.com/?book="
                    + urllib.parse.quote(book)
                    + "&chapter="
                    + chapter
                )

                webbrowser.open(url)
                return

        if selected_version == "ESV":
            import webbrowser
            url = (
                "https://www.esv.org/"
                + urllib.parse.quote(passage)
                + "/"
            )
            webbrowser.open(url)
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

                    verse_number = match.group(2)

                    text_box.insert(
                        tk.END,
                        f"{chapter}:{verse_number}  "
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

                    passage_match = re.match(
                        r"((?:[1-3]\s)?[A-Za-z ]+)\s+(\d+)",
                        passage
                    )

                    if passage_match:
                        book = passage_match.group(1).strip()

                        text_box.insert(
                            tk.END,
                            "\n" + "=" * 60 + "\n"
                        )

                        text_box.mark_set("bible_end", tk.END)

                        text_box.insert(
                            tk.END,
                            "CROSS REFERENCES\n"
                        )

                        text_box.insert(
                            tk.END,
                            "=" * 60 + "\n\n"
                        )

                        references = get_openbible_cross_references(
                            book,
                            chapter,
                            verse_number
                        )

                        if references:
                            for reference, votes in references[:5]:
                                readable = (
                                    openbible_reference_to_readable(
                                        reference
                                    )
                                )

                                text_box.insert(
                                    tk.END,
                                    f"• {readable}\n"
                                )
                        else:
                            text_box.insert(
                                tk.END,
                                "No cross references found.\n"
                            )

                else:
                    text_box.insert(
                        tk.END,
                        text.strip()
                    )

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

    passage_entry.bind(
        "<Return>",
        lambda event: load_passage()
    )

    ttk.Button(
        input_frame,
        text="Constable's Notes",
        command=lambda: show_constable_notes(passage_entry.get().strip())
    ).pack(side="left", padx=5)

    def open_commentaries():
        commentary_window = tk.Toplevel(window)
        commentary_window.title("Commentaries")
        commentary_window.geometry("700x600")
        commentary_window.attributes("-zoomed", True)
        commentary_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            commentary_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="SELECT A COMMENTARY",
            font=("TkDefaultFont", 20, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
        ).pack(pady=15)

        commentary_options = [
            ("Matthew Henry", "matthew-henry"),
            ("Adam Clarke", "adam-clarke"),
            ("John Gill", "john-gill"),
            ("John Calvin", "john-calvin"),
            ("Jamieson-Fausset-Brown", "jamieson-fausset-brown"),
            ("Keil & Delitzsch", "keil-delitzsch"),
            ("Tyndale", "tyndale")
        ]

        for name, commentary_id in commentary_options:
            ttk.Button(
                commentary_window,
                text=name,
                command=lambda cid=commentary_id: show_commentary(
                    passage_entry.get().strip(),
                    cid
                )
            ).pack(fill="x", padx=100, pady=5)

    ttk.Button(
        input_frame,
        text="Commentaries",
        command=open_commentaries
    ).pack(side="left", padx=5)

    ttk.Button(
        window,
        text="Close",
        command=window.destroy
    ).pack(pady=(0, 15))

    passage_entry.focus()
def show_commentary(passage, commentary_id):
    passage = passage.strip()

    match = re.match(r"^(.*?)\s+(\d+):(\d+)", passage)

    if not match:
        messagebox.showerror(
            "Invalid Passage",
            "Please enter a passage such as Romans 8:1."
        )
        return

    book = match.group(1).strip()
    chapter = int(match.group(2))
    verse = int(match.group(3))

    if book not in COMMENTARY_BOOKS:
        messagebox.showerror(
            "Invalid Bible Book",
            f"The Bible book '{book}' is not recognized."
        )
        return

    commentary_names = {
        "adam-clarke": "Adam Clarke Bible Commentary",
        "matthew-henry": "Matthew Henry Bible Commentary",
        "john-gill": "John Gill Bible Commentary",
        "john-calvin": "John Calvin's Commentaries",
        "jamieson-fausset-brown":
            "Jamieson-Fausset-Brown Bible Commentary",
        "keil-delitzsch":
            "Keil & Delitzsch Old Testament Commentary",
        "tyndale": "Tyndale Open Study Notes"
    }

    commentary_name = commentary_names.get(
        commentary_id,
        commentary_id
    )


    window = tk.Toplevel()
    window.title(commentary_name)
    window.geometry("700x600")
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text=commentary_name,
        font=("TkDefaultFont", 18, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)

    tk.Label(
        window,
        text=f"Passage: {passage}",
        font=("TkDefaultFont", 12),
        bg="#f4f1ea",
        fg="#3f2f24"
    ).pack(pady=(10, 5))

    text_box = tk.Text(
        window,
        wrap="word",
        font=("TkDefaultFont", 11)
    )
    text_box.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    scrollbar = ttk.Scrollbar(
        window,
        orient="vertical",
        command=text_box.yview
    )
    scrollbar.pack(side="right", fill="y")

    text_box.configure(yscrollcommand=scrollbar.set)

    result = get_commentary_section(
        commentary_id,
        book,
        chapter,
        verse
    )

    status = result.get("status")
    text = result.get("text")

    if status == "success":
        text_box.insert(tk.END, text)

    elif status == "not_available":
        text_box.insert(
            tk.END,
            f"{commentary_name} does not contain "
            f"commentary for {book} {chapter}."
        )

    elif status == "book_mapping_missing":
        text_box.insert(
            tk.END,
            f"The Bible book '{book}' is not currently "
            f"mapped in the commentary system."
        )

    elif status == "no_section":
        text_box.insert(
            tk.END,
            "No specific commentary section was found "
            "for this verse."
        )

    else:
        text_box.insert(
            tk.END,
            "Unable to retrieve commentary at this time."
        )

    text_box.configure(state="disabled")

    def save_commentary():
        commentary_text = text_box.get("1.0", tk.END).strip()

        if not commentary_text:
            return

        save_window = tk.Toplevel(window)
        save_window.title("Save Commentary")
        save_window.geometry("650x450")
        save_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            save_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="Save Commentary to Personal Bible Study",
            font=("TkDefaultFont", 14, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
        ).pack(pady=15)

        ttk.Label(
            save_window,
            text="Study Title:"
        ).pack(anchor="w", padx=20)

        title_entry = ttk.Entry(save_window, width=60)
        title_entry.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(
            save_window,
            text="Study Notes:"
        ).pack(anchor="w", padx=20)

        notes_text = tk.Text(
            save_window,
            height=10,
            wrap="word"
        )
        notes_text.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10)
        )

        notes_text.insert(tk.END, commentary_text)

        def save_study():
            title = title_entry.get().strip()
            content = notes_text.get("1.0", tk.END).strip()

            if not title or not content:
                return

            conn = sqlite3.connect("/home/tim/BibleStudy/bible_study.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO personal_studies
                (title, reference, content, created_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (title, passage, content)
            )

            conn.commit()
            conn.close()

            save_window.destroy()

        ttk.Button(
            save_window,
            text="Save Study",
            command=save_study
        ).pack(pady=10)

    ttk.Button(
        window,
        text="Save to Personal Bible Study",
        command=save_commentary
    ).pack(pady=(5, 10))

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
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="CONSTABLE'S NOTES",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)

    tk.Label(
        window,
        text=f"Passage: {passage}",
        font=("TkDefaultFont", 12),
        bg="#f4f1ea",
        fg="#3f2f24"
    ).pack(pady=(10, 5))

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

    conn = sqlite3.connect(
        "/home/tim/BibleStudy/bible_study.db"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM notes")
    note_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM topics")
    topic_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cross_references")
    cross_reference_count = cursor.fetchone()[0]

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sermons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            scripture TEXT,
            content TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM sermons")
    sermon_count = cursor.fetchone()[0]

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personal_studies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reference TEXT,
            content TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM personal_studies")
    personal_study_count = cursor.fetchone()[0]

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
    window.title("Bible Study Dashboard")
    window.geometry("900x700")
    window.attributes("-zoomed", True)
    window.minsize(800, 600)

    # Main background
    window.configure(bg="#f4f1ea")

    # Header
    header = tk.Frame(
        window,
        bg="#3f2f24",
        height=115
    )
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="📖  BIBLE STUDY",
        font=("TkDefaultFont", 26, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=(20, 2))

    tk.Label(
        header,
        text="Study Scripture • Grow in Faith • Keep Learning",
        font=("TkDefaultFont", 11),
        bg="#3f2f24",
        fg="#e8d8bd"
    ).pack()

    # Content area
    content = tk.Frame(
        window,
        bg="#f4f1ea"
    )
    content.pack(fill="both", expand=True, padx=25, pady=20)

    # Dashboard title
    tk.Label(
        content,
        text="Study Dashboard",
        font=("TkDefaultFont", 18, "bold"),
        bg="#f4f1ea",
        fg="#3f2f24"
    ).pack(anchor="w", pady=(0, 15))

    # Statistics cards
    stats_frame = tk.Frame(
        content,
        bg="#f4f1ea"
    )
    stats_frame.pack(fill="x", pady=(0, 20))

    stats = [
        ("Study Notes", note_count, "#e8d8bd"),
        ("Topics", topic_count, "#d9e6d2"),
        ("Cross References", cross_reference_count, "#d7e3ef"),
        ("Personal Studies", personal_study_count, "#ead8e8"),
        ("Sermon Notes", sermon_count, "#f0dfc0")
    ]

    for title, count, card_bg in stats:
        card = tk.Frame(
            stats_frame,
            bg=card_bg,
            bd=1,
            relief="solid"
        )
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        tk.Label(
            card,
            text=str(count),
            font=("TkDefaultFont", 22, "bold"),
            bg=card_bg,
            fg="#3f2f24"
        ).pack(pady=(12, 2))

        tk.Label(
            card,
            text=title,
            font=("TkDefaultFont", 9, "bold"),
            bg=card_bg,
            fg="#5a4a3d",
            wraplength=120
        ).pack(pady=(0, 12))

    # Lower sections
    lower_frame = tk.Frame(
        content,
        bg="#f4f1ea"
    )
    lower_frame.pack(
        fill="both",
        expand=True
    )

    # Topics panel
    topics_panel = tk.Frame(
        lower_frame,
        bg="white",
        bd=1,
        relief="solid"
    )
    topics_panel.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )

    tk.Label(
        topics_panel,
        text="📚  Topics",
        font=("TkDefaultFont", 14, "bold"),
        bg="white",
        fg="#3f2f24"
    ).pack(anchor="w", padx=15, pady=(12, 8))

    topic_text = "\n".join(
        f"• {topic[0]} ({topic[1]} note{'s' if topic[1] != 1 else ''})"
        for topic in topics
    )

    if not topic_text:
        topic_text = "No topics yet."

    topic_box = tk.Text(
        topics_panel,
        wrap="word",
        height=10,
        font=("TkDefaultFont", 10),
        bg="white",
        fg="#3f2f24",
        bd=0,
        highlightthickness=0
    )
    topic_box.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 15)
    )
    topic_box.insert("1.0", topic_text)
    topic_box.configure(state="disabled")

    # Recent studies panel
    recent_panel = tk.Frame(
        lower_frame,
        bg="white",
        bd=1,
        relief="solid"
    )
    recent_panel.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(8, 0)
    )

    tk.Label(
        recent_panel,
        text="📝  Recent Studies",
        font=("TkDefaultFont", 14, "bold"),
        bg="white",
        fg="#3f2f24"
    ).pack(anchor="w", padx=15, pady=(12, 8))

    recent_text = "\n\n".join(
        f"{note[0]}\nReference: {note[1]}\nDate: {note[2]}"
        for note in recent_notes
    )

    if not recent_text:
        recent_text = "No study notes yet."

    recent_box = tk.Text(
        recent_panel,
        wrap="word",
        height=10,
        font=("TkDefaultFont", 10),
        bg="white",
        fg="#3f2f24",
        bd=0,
        highlightthickness=0
    )
    recent_box.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 15)
    )
    recent_box.insert("1.0", recent_text)
    recent_box.configure(state="disabled")

    # Close button
    tk.Button(
        window,
        text="Close Dashboard",
        command=window.destroy,
        font=("TkDefaultFont", 10, "bold"),
        bg="#3f2f24",
        fg="white",
        activebackground="#5a4333",
        activeforeground="white",
        padx=25,
        pady=8,
        relief="flat",
        cursor="hand2"
    ).pack(pady=(0, 20))


def show_topics():
    import sqlite3
    from tkinter import messagebox

    window = tk.Toplevel()
    window.title("Topics")
    window.geometry("700x600")
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="BIBLE STUDY TOPICS",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)

    list_frame = ttk.Frame(window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    topic_list = tk.Listbox(
        list_frame,
        width=80,
        height=20,
        yscrollcommand=scrollbar.set
    )
    topic_list.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=topic_list.yview)

    def load_topics():
        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
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

        results = cursor.fetchall()
        conn.close()

        topic_list.delete(0, tk.END)

        for topic in results:
            topic_list.insert(
                tk.END,
                f"{topic[1]} — "
                f"{topic[2] or 'No description'} — "
                f"{topic[3]} note"
                f"{'s' if topic[3] != 1 else ''}"
            )

        return results

    topics = load_topics()

    def add_topic():
        add_window = tk.Toplevel(window)
        add_window.title("Add Topic")
        add_window.geometry("650x450")
        add_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            add_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="ADD TOPIC",
            font=("TkDefaultFont", 18, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
        ).pack(pady=15)

        form = ttk.Frame(add_window)
        form.pack(fill="both", expand=True, padx=30, pady=10)

        ttk.Label(
            form,
            text="Topic Name:"
        ).grid(row=0, column=0, sticky="w", pady=10)

        name_entry = ttk.Entry(form, width=50)
        name_entry.grid(row=0, column=1, sticky="ew", pady=10)

        ttk.Label(
            form,
            text="Description:"
        ).grid(row=1, column=0, sticky="nw", pady=10)

        description_text = tk.Text(
            form,
            width=50,
            height=8
        )
        description_text.grid(
            row=1,
            column=1,
            sticky="nsew",
            pady=10
        )

        form.columnconfigure(1, weight=1)
        form.rowconfigure(1, weight=1)

        def save_new_topic():
            name = name_entry.get().strip()
            description = description_text.get(
                "1.0",
                tk.END
            ).strip()

            if not name:
                messagebox.showwarning(
                    "Missing Topic Name",
                    "Please enter a topic name."
                )
                return

            conn = sqlite3.connect(
                "/home/tim/BibleStudy/bible_study.db"
            )
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO topics (name, description)
                VALUES (?, ?)
                """,
                (name, description)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Topic Added",
                "Topic added successfully."
            )

            add_window.destroy()
            topics[:] = load_topics()

        button_frame = ttk.Frame(add_window)
        button_frame.pack(pady=15)

        ttk.Button(
            button_frame,
            text="Save Topic",
            command=save_new_topic
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=add_window.destroy
        ).pack(side="left", padx=10)

    def edit_topic():
        selection = topic_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Topic",
                "Please select a topic to edit."
            )
            return

        topic = topics[selection[0]]

        edit_window = tk.Toplevel(window)
        edit_window.title("Edit Topic")
        edit_window.geometry("650x450")
        edit_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            edit_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="EDIT TOPIC",
            font=("TkDefaultFont", 18, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
        ).pack(pady=15)

        form = ttk.Frame(edit_window)
        form.pack(fill="both", expand=True, padx=30)

        ttk.Label(
            form,
            text="Topic Name:"
        ).grid(row=0, column=0, sticky="w", pady=10)

        name_entry = ttk.Entry(form, width=50)
        name_entry.grid(row=0, column=1, sticky="ew", pady=10)
        name_entry.insert(0, topic[1])

        ttk.Label(
            form,
            text="Description:"
        ).grid(row=1, column=0, sticky="nw", pady=10)

        description_text = tk.Text(
            form,
            width=50,
            height=8
        )
        description_text.grid(
            row=1,
            column=1,
            sticky="nsew",
            pady=10
        )
        description_text.insert(
            "1.0",
            topic[2] or ""
        )

        form.columnconfigure(1, weight=1)
        form.rowconfigure(1, weight=1)

        def save_topic():
            name = name_entry.get().strip()
            description = description_text.get(
                "1.0",
                tk.END
            ).strip()

            if not name:
                messagebox.showwarning(
                    "Missing Topic Name",
                    "Please enter a topic name."
                )
                return

            conn = sqlite3.connect(
                "/home/tim/BibleStudy/bible_study.db"
            )
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE topics
                SET name = ?, description = ?
                WHERE id = ?
                """,
                (name, description, topic[0])
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Topic Updated",
                "Topic updated successfully."
            )

            edit_window.destroy()

            topics[:] = load_topics()

        ttk.Button(
            edit_window,
            text="Save Changes",
            command=save_topic
        ).pack(side="left", padx=10, pady=15)

        ttk.Button(
            edit_window,
            text="Cancel",
            command=edit_window.destroy
        ).pack(side="left", padx=10, pady=15)

    def delete_topic():
        selection = topic_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Topic",
                "Please select a topic to delete."
            )
            return

        topic = topics[selection[0]]

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT notes.id, notes.title, notes.reference
            FROM notes
            JOIN note_topics
                ON notes.id = note_topics.note_id
            WHERE note_topics.topic_id = ?
            ORDER BY notes.title
        """, (topic[0],))

        attached_notes = cursor.fetchall()
        conn.close()

        if attached_notes:
            study_list = "\n".join(
                f"• {note[1]} ({note[2]})"
                for note in attached_notes
            )

            remove_topics = messagebox.askyesno(
                "Topic Has Study Notes",
                f"The topic '{topic[1]}' is attached to "
                f"the following study note(s):\n\n"
                f"{study_list}\n\n"
                "Would you like to remove this topic from "
                "those study notes so the topic can be deleted?"
            )

            if not remove_topics:
                return

            conn = sqlite3.connect(
                "/home/tim/BibleStudy/bible_study.db"
            )
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM note_topics WHERE topic_id = ?",
                (topic[0],)
            )

            conn.commit()
            conn.close()

            confirm_delete = messagebox.askyesno(
                "Delete Topic",
                f"The topic has been removed from the "
                f"attached study notes.\n\n"
                f"Do you also want to delete the topic "
                f"'{topic[1]}'?"
            )

            if not confirm_delete:
                topics[:] = load_topics()
                return

        else:
            confirm_delete = messagebox.askyesno(
                "Delete Topic",
                f"Are you sure you want to delete the topic "
                f"'{topic[1]}'?"
            )

            if not confirm_delete:
                return

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM topics WHERE id = ?",
            (topic[0],)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Topic Deleted",
            "Topic deleted successfully."
        )

        topics[:] = load_topics()

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    ttk.Button(
        button_frame,
        text="Add Topic",
        command=add_topic
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Edit Topic",
        command=edit_topic
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Delete Topic",
        command=delete_topic
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Close",
        command=window.destroy
    ).pack(side="left", padx=5)

def show_cross_references():
    import sqlite3
    from tkinter import messagebox

    window = tk.Toplevel()
    window.title("Cross References")
    window.geometry("700x600")
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="BIBLE CROSS REFERENCES",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)

    list_frame = ttk.Frame(window)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    reference_list = tk.Listbox(
        list_frame,
        font=("TkDefaultFont", 12),
        height=18
    )
    reference_list.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar = ttk.Scrollbar(
        list_frame,
        orient="vertical",
        command=reference_list.yview
    )
    scrollbar.pack(side="right", fill="y")

    reference_list.configure(
        yscrollcommand=scrollbar.set
    )

    conn = sqlite3.connect(
        "/home/tim/BibleStudy/bible_study.db"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, source_reference, related_reference, note
        FROM cross_references
        ORDER BY source_reference, related_reference
    """)

    references = cursor.fetchall()
    conn.close()

    def refresh_list():
        reference_list.delete(0, tk.END)

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, source_reference, related_reference, note
            FROM cross_references
            ORDER BY source_reference, related_reference
        """)

        references.clear()
        references.extend(cursor.fetchall())
        conn.close()

        for ref in references:
            display = (
                f"{ref[1]} → {ref[2]}"
            )

            if ref[3]:
                display += f" — {ref[3]}"

            reference_list.insert(
                tk.END,
                display
            )

    refresh_list()

    def edit_cross_reference():
        selection = reference_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Cross Reference",
                "Please select a cross reference to edit."
            )
            return

        reference = references[selection[0]]

        edit_window = tk.Toplevel(window)
        edit_window.title("Edit Cross Reference")
        edit_window.geometry("650x450")
        edit_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            edit_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="EDIT CROSS REFERENCE",
            font=("TkDefaultFont", 18, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
        ).pack(pady=15)

        form = ttk.Frame(edit_window)
        form.pack(fill="both", expand=True, padx=30)

        ttk.Label(
            form,
            text="Source Reference:"
        ).grid(row=0, column=0, sticky="w", pady=10)

        source_entry = ttk.Entry(
            form,
            width=50
        )
        source_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=10
        )
        source_entry.insert(
            0,
            reference[1]
        )

        ttk.Label(
            form,
            text="Related Reference:"
        ).grid(row=1, column=0, sticky="w", pady=10)

        related_entry = ttk.Entry(
            form,
            width=50
        )
        related_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=10
        )
        related_entry.insert(
            0,
            reference[2]
        )

        ttk.Label(
            form,
            text="Note:"
        ).grid(
            row=2,
            column=0,
            sticky="nw",
            pady=10
        )

        note_text = tk.Text(
            form,
            width=50,
            height=8
        )
        note_text.grid(
            row=2,
            column=1,
            sticky="nsew",
            pady=10
        )

        note_text.insert(
            "1.0",
            reference[3] or ""
        )

        form.columnconfigure(1, weight=1)
        form.rowconfigure(2, weight=1)

        def save_cross_reference():
            source = source_entry.get().strip()
            related = related_entry.get().strip()
            note = note_text.get(
                "1.0",
                tk.END
            ).strip()

            if not source or not related:
                messagebox.showwarning(
                    "Missing Reference",
                    "Please enter both Bible references."
                )
                return

            conn = sqlite3.connect(
                "/home/tim/BibleStudy/bible_study.db"
            )
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE cross_references
                SET source_reference = ?,
                    related_reference = ?,
                    note = ?
                WHERE id = ?
            """, (
                source,
                related,
                note,
                reference[0]
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Cross Reference Updated",
                "Cross reference updated successfully."
            )

            edit_window.destroy()
            refresh_list()

        ttk.Button(
            edit_window,
            text="Save Changes",
            command=save_cross_reference
        ).pack(
            side="left",
            padx=10,
            pady=15
        )

        ttk.Button(
            edit_window,
            text="Cancel",
            command=edit_window.destroy
        ).pack(
            side="left",
            padx=10,
            pady=15
        )

    def delete_cross_reference():
        selection = reference_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Select Cross Reference",
                "Please select a cross reference to delete."
            )
            return

        reference = references[selection[0]]

        confirm = messagebox.askyesno(
            "Delete Cross Reference",
            f"Are you sure you want to delete this "
            f"cross reference?\n\n"
            f"{reference[1]} → {reference[2]}\n\n"
            f"{reference[3] or ''}"
        )

        if not confirm:
            return

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM cross_references WHERE id = ?",
            (reference[0],)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Cross Reference Deleted",
            "Cross reference deleted successfully."
        )

        refresh_list()

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    ttk.Button(
        button_frame,
        text="Add Cross Reference",
        command=add_cross_reference
    ).pack(
        side="left",
        padx=5
    )

    ttk.Button(
        button_frame,
        text="Edit",
        command=edit_cross_reference
    ).pack(
        side="left",
        padx=5
    )

    ttk.Button(
        button_frame,
        text="Delete",
        command=delete_cross_reference
    ).pack(
        side="left",
        padx=5
    )

    ttk.Button(
        window,
        text="Close",
        command=window.destroy
    ).pack(pady=(5, 20))


def show_sermon_notes():
    import sqlite3
    from datetime import datetime
    from tkinter import messagebox

    window = tk.Toplevel()
    window.title("Sermon Notes")
    window.geometry("700x600")
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="SERMON NOTES",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)

    form = ttk.Frame(window)
    form.pack(fill="both", expand=True, padx=30, pady=5)

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

    content_text = tk.Text(form, width=70, height=24, wrap="word")
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
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="SAVED SERMON NOTES",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)
    window.geometry("850x650")
    window.attributes("-zoomed", True)

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
        edit_window.geometry("650x450")
        edit_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            edit_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="EDIT SERMON",
            font=("TkDefaultFont", 20, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
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
    window.geometry("650x450")
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="ADD CROSS REFERENCE",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)

    form = ttk.Frame(window)
    form.pack(fill="both", expand=True, padx=30, pady=5)

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

def create_calendar_reminders_table():
    conn = sqlite3.connect("/home/tim/BibleStudy/bible_study.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS calendar_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reminder_date TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT
        )
        """
    )

    conn.commit()
    conn.close()


create_calendar_reminders_table()


def show_calendar(parent):
    from datetime import date

    calendar_window = tk.Toplevel(parent)
    calendar_window.title("Bible Study Calendar")
    calendar_window.geometry("650x450")
    calendar_window.minsize(380, 400)
    calendar_window.configure(bg="#f4f1ea")

    current_date = date.today()
    current_month = current_date.month
    current_year = current_date.year

    header = tk.Frame(
        calendar_window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    title_label = tk.Label(
        header,
        text="📅 Bible Study Calendar",
        font=("TkDefaultFont", 18, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    )
    title_label.pack(pady=15)

    month_frame = tk.Frame(
        calendar_window,
        bg="#f4f1ea"
    )
    month_frame.pack(fill="x", padx=20, pady=15)

    calendar_display = tk.Frame(
        calendar_window,
        bg="white",
        bd=1,
        relief="solid"
    )
    calendar_display.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    def show_reminders(selected_date):
        from tkinter import messagebox
        from datetime import datetime

        conn = sqlite3.connect(
            "/home/tim/BibleStudy/bible_study.db"
        )
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, details
            FROM calendar_reminders
            WHERE reminder_date = ?
            ORDER BY id
            """,
            (selected_date,)
        )

        reminders = cursor.fetchall()
        conn.close()

        if not reminders:
            messagebox.showinfo(
                "Calendar",
                "There are no reminders for this date."
            )
            return

        reminder_window = tk.Toplevel(calendar_window)
        reminder_window.title("Calendar Reminders")
        reminder_window.geometry("650x450")
        reminder_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            reminder_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        display_date = datetime.strptime(
            selected_date,
            "%Y-%m-%d"
        ).strftime("%B %d, %Y")

        tk.Label(
            header,
            text=f"🔔 Reminders — {display_date}",
            font=("TkDefaultFont", 18, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
        ).pack(pady=15)

        content = tk.Frame(
            reminder_window,
            bg="#f4f1ea"
        )
        content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        reminder_text = tk.Text(
            content,
            wrap="word",
            font=("TkDefaultFont", 11),
            bg="white",
            fg="#3f2f24",
            relief="solid",
            bd=1
        )
        reminder_text.pack(
            fill="both",
            expand=True
        )

        for index, (reminder_id, title, details) in enumerate(reminders, start=1):
            reminder_text.insert(
                tk.END,
                f"{index}. {title}\n",
                "title"
            )

            if details:
                reminder_text.insert(
                    tk.END,
                    f"{details}\n"
                )

            reminder_text.insert(
                tk.END,
                "\n"
            )

        reminder_text.tag_configure(
            "title",
            font=("TkDefaultFont", 12, "bold"),
            foreground="#3f2f24"
        )

        reminder_text.configure(state="disabled")

        tk.Button(
            reminder_window,
            text="Close",
            command=reminder_window.destroy,
            font=("TkDefaultFont", 10, "bold"),
            bg="#3f2f24",
            fg="white",
            activebackground="#5a4434",
            activeforeground="white",
            width=18,
            height=2,
            relief="flat",
            cursor="hand2"
        ).pack(pady=(0, 20))

    def add_reminder():
        from datetime import date, datetime
        from tkinter import messagebox

        reminder_window = tk.Toplevel(calendar_window)
        reminder_window.title("Add Calendar Reminder")
        reminder_window.geometry("650x450")
        reminder_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            reminder_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="➕ ADD CALENDAR REMINDER",
            font=("TkDefaultFont", 18, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
        ).pack(pady=15)

        form = tk.Frame(
            reminder_window,
            bg="#f4f1ea"
        )
        form.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        tk.Label(
            form,
            text="Date (MM/DD/YYYY):",
            font=("TkDefaultFont", 10, "bold"),
            bg="#f4f1ea",
            fg="#3f2f24"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=10
        )

        date_entry = tk.Entry(
            form,
            width=30,
            font=("TkDefaultFont", 10)
        )
        date_entry.grid(
            row=0,
            column=1,
            sticky="w",
            pady=10
        )
        date_entry.insert(
            0,
            date.today().strftime("%m/%d/%Y")
        )

        tk.Label(
            form,
            text="Reminder Title:",
            font=("TkDefaultFont", 10, "bold"),
            bg="#f4f1ea",
            fg="#3f2f24"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=10
        )

        title_entry = tk.Entry(
            form,
            width=45,
            font=("TkDefaultFont", 10)
        )
        title_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=10
        )

        tk.Label(
            form,
            text="Details:",
            font=("TkDefaultFont", 10, "bold"),
            bg="#f4f1ea",
            fg="#3f2f24"
        ).grid(
            row=2,
            column=0,
            sticky="nw",
            pady=10
        )

        details_text = tk.Text(
            form,
            width=45,
            height=8,
            font=("TkDefaultFont", 10)
        )
        details_text.grid(
            row=2,
            column=1,
            sticky="nsew",
            pady=10
        )

        form.columnconfigure(1, weight=1)
        form.rowconfigure(2, weight=1)

        def save_reminder():
            entered_date = date_entry.get().strip()
            title = title_entry.get().strip()
            details = details_text.get(
                "1.0",
                tk.END
            ).strip()

            try:
                selected_date = datetime.strptime(
                    entered_date,
                    "%m/%d/%Y"
                ).date()
                reminder_date = selected_date.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Please enter the date in MM/DD/YYYY format."
                )
                return

            if not title:
                messagebox.showwarning(
                    "Missing Reminder Title",
                    "Please enter a reminder title."
                )
                return

            conn = sqlite3.connect(
                "/home/tim/BibleStudy/bible_study.db"
            )
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO calendar_reminders
                (reminder_date, title, details)
                VALUES (?, ?, ?)
                """,
                (reminder_date, title, details)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Reminder Saved",
                "Calendar reminder saved successfully."
            )

            reminder_window.destroy()
            draw_calendar()

        button_frame = tk.Frame(
            reminder_window,
            bg="#f4f1ea"
        )
        button_frame.pack(pady=(0, 20))

        tk.Button(
            button_frame,
            text="Save Reminder",
            command=save_reminder,
            font=("TkDefaultFont", 10, "bold"),
            bg="#3f2f24",
            fg="white",
            activebackground="#5a4434",
            activeforeground="white",
            width=18,
            height=2,
            relief="flat",
            cursor="hand2"
        ).pack(
            side="left",
            padx=10
        )

        tk.Button(
            button_frame,
            text="Cancel",
            command=reminder_window.destroy,
            font=("TkDefaultFont", 10, "bold"),
            bg="#e8d8bd",
            fg="#3f2f24",
            activebackground="#c9b89f",
            activeforeground="#3f2f24",
            width=18,
            height=2,
            relief="flat",
            cursor="hand2"
        ).pack(
            side="left",
            padx=10
        )

    def draw_calendar():
        for widget in month_frame.winfo_children():
            widget.destroy()

        for widget in calendar_display.winfo_children():
            widget.destroy()

        month_name = calendar.month_name[current_month]

        tk.Button(
            month_frame,
            text="◀",
            command=previous_month,
            font=("TkDefaultFont", 10, "bold"),
            bg="#e8d8bd",
            fg="#3f2f24",
            relief="flat",
            width=4
        ).pack(side="left")

        tk.Label(
            month_frame,
            text=f"{month_name} {current_year}",
            font=("TkDefaultFont", 14, "bold"),
            bg="#f4f1ea",
            fg="#3f2f24"
        ).pack(side="left", expand=True)

        tk.Button(
            month_frame,
            text="▶",
            command=next_month,
            font=("TkDefaultFont", 10, "bold"),
            bg="#e8d8bd",
            fg="#3f2f24",
            relief="flat",
            width=4
        ).pack(side="right")

        tk.Button(
            calendar_window,
            text="➕ Add Reminder",
            command=add_reminder,
            font=("TkDefaultFont", 9, "bold"),
            bg="#d9e6d2",
            fg="#3f2f24",
            relief="flat",
            cursor="hand2"
        ).pack(pady=(0, 10))

        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for column, day in enumerate(days):
            tk.Label(
                calendar_display,
                text=day,
                font=("TkDefaultFont", 9, "bold"),
                bg="#d9e6d2",
                fg="#3f2f24",
                width=8,
                pady=10
            ).grid(
                row=0,
                column=column,
                sticky="nsew"
            )

        calendar.setfirstweekday(calendar.SUNDAY)

        month_days = calendar.monthcalendar(
            current_year,
            current_month
        )

        for row, week in enumerate(month_days, start=1):
            for column, day in enumerate(week):
                if day == 0:
                    continue

                is_today = (
                    day == current_date.day
                    and current_month == current_date.month
                    and current_year == current_date.year
                )

                if is_today:
                    bg = "#e8d8bd"
                    font = ("TkDefaultFont", 10, "bold")
                else:
                    bg = "white"
                    font = ("TkDefaultFont", 10)

                day_date = f"{current_year:04d}-{current_month:02d}-{day:02d}"

                conn = sqlite3.connect(
                    "/home/tim/BibleStudy/bible_study.db"
                )
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM calendar_reminders
                    WHERE reminder_date = ?
                    """,
                    (day_date,)
                )

                reminder_count = cursor.fetchone()[0]
                conn.close()

                day_text = str(day)

                if reminder_count > 0:
                    day_text += " 🔔"

                tk.Button(
                    calendar_display,
                    text=day_text,
                    font=font,
                    bg=bg,
                    fg="#3f2f24",
                    activebackground="#d9e6d2",
                    activeforeground="#3f2f24",
                    width=8,
                    pady=8,
                    relief="flat",
                    cursor="hand2",
                    command=lambda selected_date=day_date: show_reminders(
                        selected_date
                    )
                ).grid(
                    row=row,
                    column=column,
                    sticky="nsew",
                    padx=1,
                    pady=1
                )

        for column in range(7):
            calendar_display.columnconfigure(
                column,
                weight=1
            )

    def previous_month():
        nonlocal current_month, current_year

        current_month -= 1

        if current_month == 0:
            current_month = 12
            current_year -= 1

        draw_calendar()

    def next_month():
        nonlocal current_month, current_year

        current_month += 1

        if current_month == 13:
            current_month = 1
            current_year += 1

        draw_calendar()

    draw_calendar()


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
    window.geometry("900x700")
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="PERSONAL BIBLE STUDY",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=15)
    window.geometry("700x600")

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
    window.attributes("-zoomed", True)
    window.configure(bg="#f4f1ea")

    header = tk.Frame(
        window,
        bg="#3f2f24"
    )
    header.pack(fill="x")

    tk.Label(
        header,
        text="PERSONAL BIBLE STUDIES",
        font=("TkDefaultFont", 20, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
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
        edit_window.geometry("650x450")
        edit_window.configure(bg="#f4f1ea")

        header = tk.Frame(
            edit_window,
            bg="#3f2f24"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="EDIT PERSONAL BIBLE STUDY",
            font=("TkDefaultFont", 20, "bold"),
            bg="#3f2f24",
            fg="#f5e6c8"
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

def create_prayer_table():
    conn = sqlite3.connect("/home/tim/BibleStudy/bible_study.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS prayers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        prayer TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def main():
    from datetime import date
    create_prayer_table()

    root = tk.Tk()
    root.attributes("-zoomed", True)
    root.title("Bible Study")
    root.geometry("950x700")
    root.minsize(800, 600)
    root.configure(bg="#f4f1ea")

    # Header
    header = tk.Frame(
        root,
        bg="#3f2f24",
        height=125
    )
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="📖  BIBLE STUDY",
        font=("TkDefaultFont", 28, "bold"),
        bg="#3f2f24",
        fg="#f5e6c8"
    ).pack(pady=(22, 2))

    tk.Label(
        header,
        text="Study Scripture • Grow in Faith • Keep Learning",
        font=("TkDefaultFont", 11),
        bg="#3f2f24",
        fg="#e8d8bd"
    ).pack()

    # Main content
    content = tk.Frame(
        root,
        bg="#f4f1ea"
    )
    content.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=20
    )

    tk.Label(
        content,
        text="Welcome to Your Bible Study",
        font=("TkDefaultFont", 19, "bold"),
        bg="#f4f1ea",
        fg="#3f2f24"
    ).pack(pady=(0, 15))

    # Verse of the Day
    verse_reference, verse_text = get_verse_of_day()

    verse_frame = tk.Frame(
        content,
        bg="white",
        bd=1,
        relief="solid"
    )
    verse_frame.pack(
        fill="x",
        pady=(0, 20)
    )

    tk.Label(
        verse_frame,
        text="VERSE OF THE DAY",
        font=("TkDefaultFont", 11, "bold"),
        bg="white",
        fg="#7a5c3e"
    ).pack(pady=(15, 5))

    verse_label = tk.Label(
        verse_frame,
        text=verse_text,
        wraplength=820,
        justify="center",
        font=("TkDefaultFont", 13),
        bg="white",
        fg="#3f2f24"
    )
    verse_label.pack(
        padx=25,
        pady=(5, 8)
    )

    reference_label = tk.Label(
        verse_frame,
        text=verse_reference,
        font=("TkDefaultFont", 11, "bold"),
        bg="white",
        fg="#7a5c3e"
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

    # Lower section
    lower_frame = tk.Frame(
        content,
        bg="#f4f1ea"
    )
    lower_frame.pack(
        fill="x",
        pady=(0, 5)
    )
    lower_frame.configure(height=350)
    lower_frame.pack_propagate(False)

    lower_frame.columnconfigure(0, weight=1)
    lower_frame.columnconfigure(1, weight=1)

    # Prayer
    prayer_frame = tk.Frame(
        lower_frame,
        bg="#e2ddd4",
        bd=1,
        relief="solid",
        width=700,
        height=550
    )
    prayer_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nw")
    prayer_frame.grid_propagate(False)

    tk.Label(
        prayer_frame,
        text="Prayer",
        font=("TkDefaultFont", 15, "bold"),
        bg="#e2ddd4",
        fg="#3f2f24"
    ).pack(pady=(12, 8))

    prayer_button_frame = tk.Frame(
        prayer_frame,
        bg="#e2ddd4"
    )
    prayer_button_frame.pack(pady=(0, 8))

    for text in ("New", "Search", "Delete"):
        tk.Button(
            prayer_button_frame,
            text=text,
            font=("TkDefaultFont", 10, "bold"),
            bg="#f4f1ea",
            fg="#3f2f24",
            width=8
        ).pack(side="left", padx=3)

    prayer_list = tk.Listbox(
        prayer_frame,
        font=("TkDefaultFont", 10),
        bg="white",
        fg="#3f2f24",
        height=10,
        width=32
    )
    prayer_list.pack(fill="both", expand=True, padx=12, pady=(2, 12))

    # Bible Study Tools
    tools_frame = tk.Frame(
        lower_frame,
        bg="#f4f1ea"
    )
    tools_frame.pack(anchor="center")

    tk.Label(
        tools_frame,
        text="Bible Study Tools",
        font=("TkDefaultFont", 15, "bold"),
        bg="#f4f1ea",
        fg="#3f2f24"
    ).pack(pady=(0, 8))

    button_frame = tk.Frame(
        tools_frame,
        bg="#f4f1ea"
    )
    button_frame.pack()

    buttons = [
        ("📖  Read Bible", show_bible_reader, "#d7e3ef"),
        ("📊  Study Dashboard", show_dashboard, "#e8d8bd"),
        ("📚  Topics", show_topics, "#d9e6d2"),
        ("🔗  Cross References", show_cross_references, "#ead8e8"),
        ("📝  Sermon Notes", show_sermon_notes, "#f0dfc0"),
        ("✍  Personal Bible Study", personal_bible_study, "#e2ddd4")
    ]

    for index, (text_label, command, button_bg) in enumerate(buttons):
        row = index // 2
        column = index % 2

        button = tk.Button(
            button_frame,
            text=text_label,
            command=command,
            font=("TkDefaultFont", 11, "bold"),
            bg=button_bg,
            fg="#3f2f24",
            activebackground="#c9b89f",
            activeforeground="#3f2f24",
            width=30,
            height=2,
            relief="solid",
            bd=1,
            cursor="hand2"
        )
        button.grid(
            row=row,
            column=column,
            padx=8,
            pady=6
        )

    # Calendar preview
    calendar_frame = tk.Frame(
        lower_frame,
        bg="white",
        bd=2,
        relief="solid",
        width=350,
        height=300
    )
    calendar_frame.pack_propagate(False)
    calendar_frame.place(
        relx=1.0,
        y=15,
        anchor="ne"
    )

    tk.Label(
        calendar_frame,
        text="📅  Calendar",
        font=("TkDefaultFont", 14, "bold"),
        bg="white",
        fg="#3f2f24"
    ).pack(pady=(12, 5))

    calendar_preview = tk.Frame(
        calendar_frame,
        bg="white"
    )
    calendar_preview.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(0, 10)
    )

    today = date.today()
    month_name = calendar.month_name[today.month]

    tk.Label(
        calendar_preview,
        text=f"{month_name} {today.year}",
        font=("TkDefaultFont", 11, "bold"),
        bg="white",
        fg="#7a5c3e"
    ).pack(pady=(0, 5))

    days = ["S", "M", "T", "W", "T", "F", "S"]

    week_frame = tk.Frame(
        calendar_preview,
        bg="white"
    )
    week_frame.pack()

    for day_name in days:
        tk.Label(
            week_frame,
            text=day_name,
            font=("TkDefaultFont", 8, "bold"),
            bg="#d9e6d2",
            fg="#3f2f24",
            width=5
        ).pack(side="left", padx=2)

    calendar.setfirstweekday(calendar.SUNDAY)

    for week in calendar.monthcalendar(today.year, today.month):
        week_frame = tk.Frame(
            calendar_preview,
            bg="white"
        )
        week_frame.pack()

        for day in week:
            if day == 0:
                text_value = ""
                bg_value = "white"
            elif day == today.day:
                text_value = str(day)
                bg_value = "#e8d8bd"
            else:
                text_value = str(day)
                bg_value = "white"

            tk.Label(
                week_frame,
                text=text_value,
                font=("TkDefaultFont", 8, "bold" if day == today.day else "normal"),
                bg=bg_value,
                fg="#3f2f24",
                width=5
            ).pack(side="left", padx=2, pady=2)

    tk.Button(
        calendar_frame,
        text="Open Calendar",
        command=lambda: show_calendar(root),
        font=("TkDefaultFont", 9, "bold"),
        bg="#e8d8bd",
        fg="#3f2f24",
        relief="flat",
        cursor="hand2"
    ).pack(pady=(0, 12))

    # Bible Hub button
    tk.Button(
        content,
        text="Bible Hub",
        command=lambda: __import__("webbrowser").open("https://biblehub.com/"),
        font=("TkDefaultFont", 10, "bold"),
        bg="#e8d8bd",
        fg="#3f2f24",
        activebackground="#c9b89f",
        activeforeground="#3f2f24",
        width=18,
        height=2,
        relief="flat",
        cursor="hand2"
    ).pack(pady=(15, 0))

    # Exit button
    tk.Button(
        content,
        text="Exit",
        command=root.destroy,
        font=("TkDefaultFont", 10, "bold"),
        bg="#3f2f24",
        fg="white",
        activebackground="#5a4434",
        activeforeground="white",
        width=18,
        height=2,
        relief="flat",
        cursor="hand2"
    ).pack(pady=(15, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
