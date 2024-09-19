from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import csv
import sys
import os
from typing import List, Tuple, Optional


class GoogleMapsPlaceScraper:
    def __init__(self, input_excel_path: str, output_csv_path: str):
        """
        Initialize the scraper with input and output file paths.

        :param input_excel_path: Path to the input Excel file with place names.
        :param output_csv_path: Path to the output CSV file where place names and addresses will be saved.
        """
        self.input_excel_path = input_excel_path
        self.output_csv_path = output_csv_path
        self.driver = None
        self.wait = None

    def setup_driver(self) -> None:
        """
        Setup the Selenium WebDriver with Chrome options.
        """
        options = Options()
        options.add_argument("--start-maximized")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def open_place_page(self, place_name: str) -> None:
        """
        Open the Google Maps search page for the given place name.

        :param place_name: Name of the place to search on Google Maps.
        """
        search_url = (
            f"https://www.google.com/maps/search/{place_name.replace(' ', '+')}"
        )
        self.driver.get(search_url)
        time.sleep(10)  # Wait for the page to load

    def extract_place_name_and_address(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract the place name and address from the Google Maps page.

        :return: A tuple containing the place name and address, or (None, None) if not found.
        """
        try:
            place_name = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//h1[contains(@class, "DUwDvf lfPIob")]')
                )
            ).text
            address = self.driver.find_element(
                By.XPATH,
                '//button[contains(@data-item-id, "address")]//div[@class="Io6YTe fontBodyMedium kR99db "]',
            ).text
            return place_name, address
        except Exception:
            return None, None

    def save_place_info_to_csv(self, places_info: List[Tuple[str, str]]) -> None:
        """
        Save the place information to a CSV file.

        :param places_info: List of tuples containing place names and addresses.
        """
        with open(self.output_csv_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Place Name", "Address"])
            writer.writerows(places_info)

    def scrape_place_info(self) -> None:
        """
        Scrape place names and addresses from Google Maps and save to a CSV file.
        """
        # Read place names from the Excel file
        df = pd.read_excel(self.input_excel_path)
        place_names = df["Place Name"].tolist()

        # Normalize place names: remove extra spaces
        place_names = [place_name.strip() for place_name in place_names]

        self.setup_driver()
        places_info = []
        start_time = time.time()

        try:
            for place_name in place_names:
                self.open_place_page(place_name)
                place_name_found, address = self.extract_place_name_and_address()
                if place_name_found and address:
                    places_info.append((place_name_found, address))
                    print(f"Place Name: {place_name_found}, Address: {address}")
                else:
                    print(f"Address not found for place: {place_name}")
                    places_info.append((place_name, "Address not found"))
        finally:
            self.driver.quit()
            self.save_place_info_to_csv(places_info)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total places searched: {len(place_names)}")
        print(f"Time taken: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_excel_path>")
        sys.exit(1)

    input_excel_path = sys.argv[1]
    output_csv_path = os.path.splitext(input_excel_path)[0] + "_output.csv"

    scraper = GoogleMapsPlaceScraper(input_excel_path, output_csv_path)
    scraper.scrape_place_info()
