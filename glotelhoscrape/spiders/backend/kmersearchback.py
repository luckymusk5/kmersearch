from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import weaviate
import os
import redis
import json
import requests

app = Flask(__name__)
# Autoriser le frontend via Traefik
CORS(app, origins=["https://test.kmersearch.com"])

# Connexion à Weaviate via Docker network
client = weaviate.connect_to_custom(
    http_host="weaviate",
    http_port=8080,
    http_secure=False,
    grpc_host="weaviate",
    grpc_port="50051",
    grpc_secure=False,
    headers={"X-VoyageAI-Api-Key": os.getenv("VOYAGEAI")}
)

# Connexion à Redis (ou Memurai si Windows)
cache = redis.Redis(
    host=os.getenv("REDIS_HOST","redis"),  # nom du service Redis dans Docker, si tu en as un
    port=int(os.getenv("REDIS_PORT","6379")),
    db=0,
    decode_responses=True
)

# Fonction de recherche vectorielle
def vector_search(query: str):
    collection = client.collections.get("Produtglotelho")
    response = collection.query.near_text(
        query=query,
        return_properties=["title", "description", "price", "images", "url"]
    )
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

    results = vector_search(query)
    cache.setex(query, 3600, json.dumps(results))
    return jsonify({"results": results, "cached": False})

@app.route("/image")
def get_image():
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
    # Écouter sur 0.0.0.0 pour Docker
    app.run(host="0.0.0.0", port=5000, debug=True)
