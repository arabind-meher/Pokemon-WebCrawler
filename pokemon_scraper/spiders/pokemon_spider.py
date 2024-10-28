import warnings
from typing import Any

import scrapy
from scrapy.http import Response
from bs4 import BeautifulSoup

from pokemon_scraper.database.connection import connect_to_mongodb


warnings.filterwarnings("ignore")


class PokemonSpider(scrapy.Spider):
    name = "pokemon"
    allowed_domains = ["pokemondb.net"]
    start_urls = ["https://pokemondb.net/pokedex/bulbasaur"]

    def __init__(self):
        self.client = connect_to_mongodb()
        self.db = self.client["pokemon_db"]
        self.collection = self.db["pokedex"]

    def parse(self, response: Response) -> Any:
        pokemon_data = dict()

        # Name
        pokemon_data["name"] = response.xpath("//h1/text()").get()

        # Forms
        forms = response.xpath("/html/body/main/div[2]/div[1]/a/text()").getall()

        for iterator, form in enumerate(forms, 1):
            XPATH = self.get_xpaths(iterator)

            key_words = ["Mega", "Alolan", "Galarian", "Hisuian"]
            if pokemon_data["name"] == form or any(map(lambda x: x in form, key_words)):
                key = form
            else:
                key = f'{pokemon_data["name"]} ({form})'

            # National Index
            pokemon_data["index"] = int(response.xpath(XPATH["index"]).get().strip())

            # Pokemon Form
            if pokemon_data["name"] == form:
                pokemon_data["form"] = None
            else:
                pokemon_data["form"] = form

            # Pokemon Types
            pokemon_data["types"] = list(
                map(lambda x: x.strip(), response.xpath(XPATH["types"]).getall())
            )

            # Pokemon Species
            pokemon_data["species"] = response.xpath(XPATH["species"]).get().strip()

            # Pokemon Height
            pokemon_data["height"] = response.xpath(XPATH["height"]).get().strip()

            # Pokemon Weight
            pokemon_data["weight"] = response.xpath(XPATH["weight"]).get().strip()

            # Pokemon Abilities
            pokemon_data["abilities"] = list(
                map(lambda x: x.strip(), response.xpath(XPATH["abilities"]).getall())
            )

            # Local Podex Index
            pokemon_data["local_index"] = dict(
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

            # Pokemon Training
            pokemon_data["training"] = dict(
                zip(
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["training_keys"]).getall()
                    ),
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["training_values"]).getall()
                    ),
                )
            )

            # Pokemon Breeding
            pokemon_data["breeding"] = dict(
                zip(
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["breeding_keys"]).getall()
                    ),
                    self.beautiful_soup_parse(
                        response.xpath(XPATH["breeding_values"]).getall()
                    ),
                )
            )

            # Pokemon Stats
            pokemon_data["base_stats"] = dict(
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

            pokemon_data["base_stats"]["Total"] = sum(
                pokemon_data["base_stats"].values()
            )

            if self.upload_to_db({key: pokemon_data}):
                if pokemon_data.get("form"):
                    log_text = f"{'%04d' % pokemon_data['index']}: {'%15s' % pokemon_data['name']} = {pokemon_data['form']}"
                else:
                    log_text = f"{'%04d' % pokemon_data['index']}: {'%15s' % pokemon_data['name']} = {pokemon_data['name']}"

                print(log_text)

                self.log("Successfully uploaded to db..........")

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

    def upload_to_db(self, pokedex_entry: dict) -> bool:
        try:
            self.collection.insert_one(pokedex_entry)
        except Exception as e:
            print(f"Connection Error {e}")
            return False

        return True

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
