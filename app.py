from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_crossref_url(book, chapter, verse):
    base_url = f"https://www.blueletterbible.org/esv/{book}/{chapter}/{verse}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    anchors = soup.select('a[href*="t_corr_"]')

    for a in anchors:
        href = a.get("href")
        if href and "t_corr_" in href:
            return "https://www.blueletterbible.org" + href

    return None

@app.route("/get-crossref", methods=["GET"])
def get_crossref():
    verse = request.args.get("verse", "")
    try:
        parts = verse.lower().replace(":", "").split()
        if len(parts) != 3:
            return jsonify({"error": "Invalid verse format"}), 400
        book, chapter, verse_num = parts
        book_abbrev = book[:3]
        url = get_crossref_url(book_abbrev, chapter, verse_num)
        if url:
            return jsonify({"crossref_url": url})
        else:
            return jsonify({"error": "Cross-reference not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
