import re
import pandas as pd
from datetime import datetime


def edb_to_timestamp(pd_data):
    """Transforms an unconverted string in pandas DataFrame or Series of Ereignisdatenbank (edb) to timestamp"""

    if type(pd_data) == pd.DataFrame:
        for column in pd_data:
            pd_data[column] = pd_data[column].astype(str)
            pd_data[column] = pd_data[column].str.replace('.', ' ')
            pd_data[column] = pd_data[column].apply(lambda x: datetime.strptime(x, '%d %m %Y').strftime("%Y-%m-%d")
                                                    if re.match(r"\d\d\.\d\d\.\d\d\d\d", x) and "-" not in x else x)
        return pd_data
    elif type(pd_data) == pd.Series:
        pd_data = pd_data.astype(str)
        pd_data = pd_data.str.replace('.', ' ')
        pd_data = pd_data.apply(lambda x: datetime.strptime(x, '%d %m %Y').strftime("%Y-%m-%d")
                                if re.match(r"\d\d\.\d\d\.\d\d\d\d", x) and "-" not in x else x)
        return pd_data


def clean_country_names(countries):
    """Takes a list of countries (from Ereginsdatenbank) and returns a set of cleaned country names"""
    card_dir = re.compile(r"(Süd|Nord|West|Ost)\s(\S*)")  # Matches cardinal directions and the string after it
    countries_unique = list(set(countries))  # Optional. Used for better overview and faster calculation

    # Because someone used new lines in entries instead of comma to list countries
    countries_unique = list(map(lambda x: re.sub(r'\n', ', ', x), countries_unique))

    # Because the line above adds one comma to much
    countries_unique = list(map(lambda x: re.sub(r',,', ',', x), countries_unique))
    countries_unique = list(map(lambda x: re.sub(r'\(.*\)', "", x).strip(" "), countries_unique))
    countries_unique = list(map(lambda x: x.replace("&", "und"), countries_unique))
    countries_unique = list(
        map(lambda x: x.split(",") if "," in x else x, countries_unique))  # For entries with more than one country
    countries_unique = list(map(lambda x: x.replace("_", " ") if type(x) != list else x, countries_unique))

    # To transform Süd Sudan to Südsudan
    try:
        countries_unique = list(map(lambda x: card_dir.match(x)[1] + card_dir.match(x)[2].lower()
                                    if type(x) != list and card_dir.match(x) else x, countries_unique))
    except IndexError:
        print(card_dir.match, " has a cardinal direction but is not of the form 'Süd Sudan'")

    # "Recursively" clean lists
    countries_unique = list(map(lambda x: clean_country_names(x) if type(x) == list else x, countries_unique))
    return countries_unique
