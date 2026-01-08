import json


class JsonWriterPipeline:

    def open_spider(self, spider):
        self.file = open("products.json", "w", encoding="utf-8")
        self.file.write("[\n")
        self.first_item = True

    def close_spider(self, spider):
        self.file.write("\n]")
        self.file.close()

    def process_item(self, item, spider):
        # Remplacer les None par "none"
        clean_item = {}
        for key, value in item.items():
            if value is None:
                clean_item[key] = "none"
            else:
                clean_item[key] = value

        if not self.first_item:
            self.file.write(",\n")
        else:
            self.first_item = False

        json.dump(clean_item, self.file, ensure_ascii=False)
        self.file.flush()  # Écriture immédiate sur le disque
        return item
