from flask import Flask, request, jsonify
from flask_cors import CORS   # ✅ gestion du CORS
import weaviate
import os

app = Flask(__name__)
# Autorise uniquement ton frontend React (http://localhost:5173)
CORS(app, origins=["http://localhost:5173"])

# Connexion à Weaviate
client = weaviate.connect_to_local(
    port=8080,
    headers={"X-VoyageAI-Api-Key": os.getenv("VOYAGEAI")}
)

@app.route("/search")
def search():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"results": []})

    # Récupérer la collection
    products = client.collections.get("Produit_glotelho")

    try:
        # Recherche sémantique
        response = products.query.near_text(
            query=query,
            return_properties=["url", "title", "price", "description", "images"]
        )

        results = []
        for item in response.objects:
            results.append({
                "title": item.properties.get("title"),
                "text": item.properties.get("description"),
                "image": item.properties.get("images")[0] if item.properties.get("images") else None,
                "price": item.properties.get("price"),
                "url": item.properties.get("url")
            })

        return jsonify({"results": results})

    except Exception as e:
        # ✅ gestion d'erreur pour éviter un 500 brut
        return jsonify({"error": str(e), "results": []}), 500

if __name__ == "__main__":
    app.run(debug=True)
