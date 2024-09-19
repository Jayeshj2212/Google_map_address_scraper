## Usage

1. **Prepare Input File**: Create an Excel file named `places_list.xlsx` with a column named `Place Name` that contains the names of the places you want to search for.

2. **Run the Script**: Execute the script using the command line. Provide the path to your input Excel file as an argument:

    ```sh
    python google_maps_scraper.py places_list.xlsx
    ```

    - Replace `places_list.xlsx` with the path to your Excel file.
    - The script will generate an output CSV file named `places_list_output.csv` in the same directory.