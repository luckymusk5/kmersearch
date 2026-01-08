import os
import re
import json
import time
import weaviate
from pathlib import Path
from weaviate.classes.config import Configure, Property, DataType


def clean_html(text: str) -> str:
    """Nettoie le HTML et normalise les espaces."""
    if not text or text == "none":
        return "none"
    text = re.sub(r"<[^>]+>", " ", text)   # supprime balises HTML
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else "none"

client = weaviate.connect_to_local(
    port=8080,
    headers={"X-VoyageAI-Api-Key": os.getenv("VOYAGEAI")}
)
client.connect()


def ensure_product_collection():
    """Crée la collection Produit_glotelho si elle n'existe pas déjà."""
    existing_collections = client.collections.list_all()

    if "Produit_glotelho" in existing_collections:
        print("La collection Produit_glotelho existe déjà")
        return

    client.collections.create(
        name="Produit_glotelho",
        properties=[
            Property(name="url", data_type=DataType.TEXT),
            Property(name="title", data_type=DataType.TEXT),
            Property(name="price", data_type=DataType.NUMBER),
            Property(name="description", data_type=DataType.TEXT),
            Property(name="images", data_type=DataType.TEXT_ARRAY),
        ],
        vectorizer_config=Configure.Vectorizer.none()
    )

    print("Collection Produit_glotelho créée (vectorisation gérée par le serveur)")


def safe_price(value):
    """Convertit le prix en float, retourne 0.0 si invalide."""
    if value in (None, "none", ""):
        return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def store_products(raw_products, batch_size=79):
    """
    Ingestion des produits dans Weaviate en lots de 79 produits par minute.
    Si un lot échoue partiellement, les produits rejetés sont réinjectés au prochain tour.
    """
    collection = client.collections.get("Produit_glotelho")

    success_count = 0
    i = 0

    while i < len(raw_products):
        lot = raw_products[i:i+batch_size]

        failed_products = []

        with collection.batch.fixed_size(batch_size=batch_size) as batch:
            for data in lot:
                produit = {
                    "url": data.get("url", "none"),
                    "title": data.get("title", "none"),
                    "price": safe_price(data.get("price")),
                    "description": clean_html(data.get("description")),
                    "images": data.get("images") if isinstance(data.get("images"), list) else [],
                }
                batch.add_object(properties=produit)
                success_count += 1

            if batch.number_errors > 10:
                print("Arrêt de l'import : trop d'erreurs Weaviate.")
                break

        # Vérifier les objets échoués
        if collection.batch.failed_objects:
            print(f"⚠️ {len(collection.batch.failed_objects)} produits rejetés, réinjection au prochain lot...")
            # On récupère les produits originaux qui ont échoué
            for err in collection.batch.failed_objects:
                if hasattr(err, "original_object"):
                    failed_products.append(err.original_object)

            # Réinjecter les produits échoués dans la liste
            raw_products[i:i+batch_size] = failed_products
        else:
            # Si tout est OK, on avance au lot suivant
            i += batch_size

        print(f"✅ Lot traité (total {success_count})")
        print("⏳ Pause 60s pour respecter la limite...")
        time.sleep(62)

    print(f"Nombre d'objets importés avec succès : {success_count}")


if __name__ == "__main__":
    try:
        ensure_product_collection()

        json_path = Path(r"C:\Users\HP ZBOOK 15 G4\glotelhoscrape\products.json")
        with open(json_path, "r", encoding="utf-8") as f:
            raw_products = json.load(f)

        store_products(raw_products, batch_size=79)
        print("Import terminé avec succès.")
    finally:
        client.close()
