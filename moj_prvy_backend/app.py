from groq import Groq
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from pathlib import Path

# === NAČÍTANIE .ENV SPRÁVNE ===
BASE_DIR = Path(__file__).parent.absolute()

# Skús najprv .env, potom key.env
if (BASE_DIR / '.env').exists():
    load_dotenv(BASE_DIR / '.env')
elif (BASE_DIR / 'key.env').exists():
    load_dotenv(BASE_DIR / 'key.env')
else:
    print("⚠️  Ani .env ani key.env súbor nebol nájdený!")

app = Flask(__name__)

api_key = os.getenv("GROQ_API_KEY")

print("🔑 GROQ_API_KEY načítaný:", "ÁNO" if api_key else "NIE")
if api_key:
    print("   Prvých 15 znakov:", api_key[:15] + "...")
else:
    print("   Súbor .env/key.env je pravdepodobne prázdny alebo zle formátovaný.")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY nebol nájdený! Skontroluj .env alebo key.env súbor.")

client = Groq(api_key=api_key)

people = [
    {
        "id": 1,
        "name": "Juice Wrld",
        "image": "https://i.scdn.co/image/ab6761610000e5eb23a60030944f7853c21565ef",
        "bio": "1998 - 2019"
    },
    {
        "id": 2,
        "name": "Milan Rastislav Štefánik",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ5qc7XgySx0TuB1pHTc0nCFMXlNqzd7SsLJw&s",
        "bio": "1880 - 1919"
    },
    {
        "id": 3,
        "name": "Ľudovít Štúr",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTclpRulK8Wbr8ubGlXMaljJQoq2gYVmYZCxA&s",
        "bio": "1815 - 1856"
    },
    {
        "id": 4,
        "name": "Mária Terézia",
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Kaiserin_Maria_Theresia_%28HRR%29.jpg",
        "bio": "1717 - 1780"
    },
    {
        "id": 5,
        "name": "Juraj Jánošík",
        "image": "https://slavni.terchova-info.sk/osobnosti/012.jpg",
        "bio": "1688 - 1713"
    },
    {
        "id": 6,
        "name": "Charlie Kirk",
        "image": "https://media.tenor.com/vpxKBtwubp8AAAAe/charlie-kirk.png",
        "bio": "1993 - 2025"
    },
    {
        "id": 7,
        "name": "triple T",
        "image": "https://preview.redd.it/why-is-triple-t-dead-what-happened-can-someone-fill-me-with-v0-epwco3w0k7tg1.jpeg?width=640&crop=smart&auto=webp&s=f7d35b8ddd5f0d4e05574ad172cbec593277cea5",
        "bio": "2025 - 2026"
    },
    {
        "id": 8,
        "name": "Nicolas Tesla",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTgBmXa3vVOvWKVuLY7rY4MWaimI-UYvXXbhg&s",
        "bio": "1856 - 1943"
    },
    {
        "id": 9,
        "name": "King Von",
        "image": "https://i.ytimg.com/vi/8OXlDMNRu_Q/maxresdefault.jpg",
        "bio": "1994 - 2020"
    },
     {
        "id": 10,
        "name": "JežiŠ Kristus",
        "image": "https://a09cb4783e.cbaul-cdnwnd.com/b35f457793cb40f6643cace0c84acb49/200000002-907d99176a/jezis_kristus_-_joshua_2.jpg",
        "bio": "0 - 33 "
    },
     {
        "id": 11,
        "name": "Adolf Hitler",
        "image": "https://edu.ceskatelevize.cz/storage/video/1200/18329-adolf-hitler-prevzeti-moci.jpg",
        "bio": "1889 - 1945 "
    },
      {
        "id": 12,
        "name": "Chuck Norris",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVAA8woXUTaDHekpxmgY9WhjfvbP9DWtycbg&s",
        "bio": "1940 - 2026 "
    },
]


conversations = {}

@app.route("/")
def index():
    return render_template("index.html", people=people)

@app.route("/chat/<int:id>")
def chat(id):
    person = next((p for p in people if p["id"] == id), None)
    if not person:
        return "Osoba nenájdená", 404
    conversations[id] = []  # reset histórie pri otvorení chatu
    return render_template("chat.html", person=person)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "").strip()
        person_id = int(data.get("person_id", 0))

        print(f"🔹 Prichádzajúca správa: '{user_message}' pre person_id={person_id}")

        if not user_message:
            return jsonify({"error": "Správa nemôže byť prázdna"}), 400

        person = next((p for p in people if p["id"] == person_id), None)
        if not person:
            return jsonify({"error": "Osoba s týmto ID neexistuje"}), 404

        name = person["name"]
        bio = person.get("bio", "")

        system_prompt = f"""Si {name} ({bio}). 
Rozprávaj sa v prvej osobe ako skutočný {name}. 
Odpovedaj výhradne v slovenčine. Buď priateľský, prirodzený a historicky presný."""

        if person_id not in conversations:
            conversations[person_id] = []

        conversations[person_id].append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}] + conversations[person_id],
            model="llama-3.3-70b-versatile",
            temperature=0.75,
            max_tokens=900,
        )

        reply = response.choices[0].message.content.strip()

        conversations[person_id].append({"role": "assistant", "content": reply})

        if len(conversations[person_id]) > 16:
            conversations[person_id] = conversations[person_id][-16:]

        print(f"✅ Odpoveď vygenerovaná ({len(reply)} znakov)")
        return jsonify({"reply": reply})

    except Exception as e:
        print("=== CHYBA V /api/chat ===")
        print(f"Typ chyby: {type(e).__name__}")
        print(f"Správa: {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({"error": f"Chyba: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
