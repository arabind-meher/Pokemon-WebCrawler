import scrapy


class PokemonItem(scrapy.Item):
    name = scrapy.Field()
    form = scrapy.Field()
    index = scrapy.Field()
    types = scrapy.Field()
    species = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    abilities = scrapy.Field()
    local_index = scrapy.Field()
    training = scrapy.Field()
    breeding = scrapy.Field()
    base_stats = scrapy.Field()
