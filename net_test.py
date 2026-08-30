import urllib.parse
import urllib.request

passage = input("Enter a Bible passage: ")

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
    print("=" * 60)
    print("NET BIBLE")
    print("=" * 60)
    print(text)

except Exception as error:
    print()
    print("Unable to retrieve the Bible passage.")
    print("Error:", error)
