import warnings
from typing import Any

import scrapy
from scrapy.http import Response
from bs4 import BeautifulSoup

from pokemon_scraper.items import PokemonItem

warnings.filterwarnings("ignore")


class PokemonSpider(scrapy.Spider):
    name = "pokemon"
    allowed_domains = ["pokemondb.net"]
    start_urls = ["https://pokemondb.net/pokedex/bulbasaur"]

    def parse(self, response: Response) -> Any:
        # Extract base Pokémon name
        pokemon_data = dict()
        pokemon_data["name"] = response.xpath("//h1/text()").get()

        # Extract all available forms for the Pokémon
        forms = response.xpath("/html/body/main/div[2]/div[1]/a/text()").getall()

        for iterator, form in enumerate(forms, 1):
            # Initialize item for storing structured Pokémon data
            pokemon_item = PokemonItem()
            XPATH = self.get_xpaths(iterator)

            # Generate label for each form (e.g., "Bulbasaur (Mega)", "Bulbasaur")
            key_words = ["Mega", "Alolan", "Galarian", "Hisuian"]
            if pokemon_data["name"] == form or any(map(lambda x: x in form, key_words)):
                key = form
            else:
                key = f'{pokemon_data["name"]} ({form})'

            # Assign basic details
            pokemon_item["name"] = pokemon_data["name"]
            pokemon_item["form"] = None if pokemon_data["name"] == form else form
            pokemon_item["index"] = int(response.xpath(XPATH["index"]).get().strip())
            pokemon_item["types"] = list(
                map(lambda x: x.strip(), response.xpath(XPATH["types"]).getall())
            )
            pokemon_item["species"] = response.xpath(XPATH["species"]).get().strip()
            pokemon_item["height"] = response.xpath(XPATH["height"]).get().strip()
            pokemon_item["weight"] = response.xpath(XPATH["weight"]).get().strip()
            pokemon_item["abilities"] = list(
                map(lambda x: x.strip(), response.xpath(XPATH["abilities"]).getall())
            )

            # Extract localized Pokédex numbers for different regions
            pokemon_item["local_index"] = dict(
                zip(
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["regions"]).getall()
                    ),
                    map(
                        int,
                        self.beautiful_soup_parse(
                            response.xpath(XPATH["local_index"]).getall()
                        ),
                    ),
                )
            )

            # Extract training data (EV yield, base EXP, etc.)
            pokemon_item["training"] = dict(
                zip(
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["training_keys"]).getall()
                    ),
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["training_values"]).getall()
                    ),
                )
            )

            # Extract breeding data (gender ratio, egg group, cycles)
            pokemon_item["breeding"] = dict(
                zip(
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["breeding_keys"]).getall()
                    ),
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["breeding_values"]).getall()
                    ),
                )
            )

            # Extract base stats (HP, Attack, etc.)
            pokemon_item["base_stats"] = dict(
                zip(
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["base_stats_keys"]).getall()
                    ),
                    map(
                        int,
                        self.beautiful_soup_parse(
                            response.xpath(XPATH["base_stats_values"]).getall()
                        ),
                    ),
                )
            )
            # Compute total base stats
            pokemon_item["base_stats"]["Total"] = sum(
                pokemon_item["base_stats"].values()
            )

            # Yield the populated item to pipelines
            self.log(f"✅ Yielding item: {key}")
            yield pokemon_item

        # Follow pagination to next Pokémon entry if available
        next_page = response.xpath(
            '//a[contains(@class, "entity-nav-next")]/@href'
        ).get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def beautiful_soup_parse(self, element: list) -> map:
        return map(
            lambda x: BeautifulSoup(x, "html.parser").get_text().strip(), element
        )

    @staticmethod
    def get_xpaths(itr: int) -> dict:
        xpaths = dict()

        xpaths["index"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[1]/td/strong/text()"
        )
        xpaths["types"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[2]/td/a/text()"
        )
        xpaths["species"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[3]/td/text()"
        )
        xpaths["height"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[4]/td/text()"
        )
        xpaths["weight"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[5]/td/text()"
        )
        xpaths["abilities"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[6]/td//a/text()"
        )
        xpaths["local_index"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[7]/td/text()"
        )
        xpaths["regions"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[2]/table/tbody/tr[7]/td/small/text()"
        )
        xpaths["training_keys"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[3]/div/div[1]/table/tbody/tr/th"
        )
        xpaths["training_values"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[3]/div/div[1]/table/tbody/tr/td"
        )
        xpaths["breeding_keys"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[3]/div/div[2]/table/tbody/tr/th"
        )
        xpaths["breeding_values"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[1]/div[3]/div/div[2]/table/tbody/tr/td"
        )
        xpaths["base_stats_keys"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[2]/div[1]/div[2]/table/tbody/tr/th"
        )
        xpaths["base_stats_values"] = (
            f"/html/body/main/div[2]/div[2]/div[{itr}]/div[2]/div[1]/div[2]/table/tbody/tr/td[1]"
        )

        return xpaths
