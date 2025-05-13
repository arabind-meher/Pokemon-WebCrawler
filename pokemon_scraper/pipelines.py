from pokemon_scraper.database import MongoDBClient
from itemadapter import ItemAdapter


class MongoPipeline:
    def open_spider(self, spider):
        # Initialize MongoDB connection
        self.mongo = MongoDBClient()
        self.db = self.mongo.connect()
        self.collection = self.mongo.get_collection("pokedex")

    def close_spider(self, spider):
        # Cleanly close MongoDB connection
        self.mongo.close()

    def process_item(self, item, spider):
        # Convert item to dictionary and insert into collection
        adapter = ItemAdapter(item)
        self.collection.insert_one(adapter.asdict())
        spider.logger.info(
            f"✅ Inserted: {adapter.get('index')} - {adapter.get('name')}"
        )
        return item
