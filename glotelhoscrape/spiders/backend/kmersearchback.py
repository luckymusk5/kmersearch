from flask import Flask, request, jsonify, Response
from flask_cors import CORS   # ✅ gestion du CORS
import weaviate
import os
import redis
import json
import requests   

app = Flask(__name__)
# Autorise uniquement ton frontend React (http://localhost:5173)
CORS(app, origins=["http://localhost:5173"])

# Connexion à Weaviate (local ou cloud)
client = weaviate.connect_to_local(
    port=8080,
    headers={"X-VoyageAI-Api-Key": os.getenv("VOYAGEAI")}
)

# Connexion à Memurai (équivalent Redis sur Windows)
cache = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True   # pour avoir des strings lisibles
)

# Fonction de recherche vectorielle
def vector_search(query: str):
    # Récupère la collection "Produit_glotelho"
    collection = client.collections.get("Produit_glotelho")

    # Recherche vectorielle avec near_text
    response = collection.query.near_text(
        query=query,
        return_properties=["title", "description", "price", "images", "url"]
    )

    # On retourne uniquement les propriétés des objets
    results = [obj.properties for obj in response.objects]
    return results


@app.route("/search")
def search():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Aucune requête fournie"}), 400

    cached = cache.get(query)
    if cached:
        return jsonify({"results": json.loads(cached), "cached": True})

    # Sinon, fait la recherche vectorielle
    results = vector_search(query)
    
    cache.setex(query, 3600, json.dumps(results))

    return jsonify({"results": results, "cached": False})


@app.route("/image")
def get_image():
    """Endpoint pour récupérer une image depuis son URL"""
    image_url = request.args.get("url")
    if not image_url:
        return jsonify({"error": "Aucune URL fournie"}), 400

    try:
        resp = requests.get(image_url, stream=True)
        resp.raise_for_status()
        return Response(resp.content, mimetype=resp.headers.get("Content-Type", "image/jpeg"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
