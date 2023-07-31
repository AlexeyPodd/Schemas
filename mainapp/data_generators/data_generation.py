import datetime
from random import randint, choice

from schemas.settings import DATA_GENERATION_SETTINGS

"""
For every data type must be uniq function for data generating.
This function's name must be in two parts.
The first part is 'generate_', and the second part is the name of the data type,
in lowercase, with replaced spaces by '_'.
If data type implements limitations - function must take parameters minimal and maximal.
Id data types uses source file for generating - function must take parameters with same name,
as in main dict in json source file.
The function must return string.
"""

first_letter_code = ord('a')
last_letter_code = ord('z')


def generate_word(minimal: int, maximal: int) -> str:
    return ''.join([chr(randint(first_letter_code, last_letter_code)) for _ in range(randint(minimal, maximal))])


def generate_sentence(minimal: int, maximal: int) -> str:
    min_word_length = DATA_GENERATION_SETTINGS["TXT"]["MIN_WORD_LENGTH"]
    max_word_length = DATA_GENERATION_SETTINGS["TXT"]["MIN_WORD_LENGTH"]
    return ' '.join([generate_word(min_word_length, max_word_length)
                     for _ in range(randint(minimal, maximal))]).capitalize() + '.'


def generate_integer(minimal: int, maximal: int) -> str:
    return str(randint(minimal, maximal))


def generate_full_name(first_names: list[str], last_names: list[str]) -> str:
    first_name = choice(first_names)
    last_name = choice(last_names)
    return first_name + ' ' + last_name


def generate_job(jobs: list[str]) -> str:
    return choice(jobs)


def generate_email() -> str:
    min_email_name_length = DATA_GENERATION_SETTINGS["EML"]["MIN_EMAIL_NAME_LENGTH"]
    max_email_name_length = DATA_GENERATION_SETTINGS["EML"]["MAX_EMAIL_NAME_LENGTH"]

    email_name = ''.join([chr(randint(first_letter_code, last_letter_code))
                          for _ in range(randint(min_email_name_length, max_email_name_length))])
    email_domain = choice(DATA_GENERATION_SETTINGS["EML"]["EMAIL_DOMAINS"])

    return email_name + '@' + email_domain


def generate_domain_name() -> str:
    top_level_domains = DATA_GENERATION_SETTINGS["DMN"]["TOP_LEVEL_DOMAINS"]
    min_domain_name_length = DATA_GENERATION_SETTINGS["DMN"]["MIN_DOMAIN_NAME_LENGTH"]
    max_domain_name_length = DATA_GENERATION_SETTINGS["DMN"]["MAX_DOMAIN_NAME_LENGTH"]

    second_level_domain = generate_word(min_domain_name_length, max_domain_name_length)
    return second_level_domain + '.' + choice(top_level_domains)


def generate_phone_number() -> str:
    country_code = choice(DATA_GENERATION_SETTINGS["PHN"]["COUNTRY_CODES"])
    return country_code + ''.join([generate_integer(0, 9)
                                   for _ in range(DATA_GENERATION_SETTINGS["PHN"]["DIGITS_TOTAL"]-len(country_code)+1)])


def generate_company_name() -> str:
    min_word_length = DATA_GENERATION_SETTINGS["CNM"]["MIN_WORD_LENGTH"]
    max_word_length = DATA_GENERATION_SETTINGS["CNM"]["MAX_WORD_LENGTH"]
    min_words_amount = DATA_GENERATION_SETTINGS["CNM"]["MIN_WORDS_AMOUNT"]
    max_words_amount = DATA_GENERATION_SETTINGS["CNM"]["MAX_WORDS_AMOUNT"]
    return ' '.join([generate_word(min_word_length, max_word_length).upper()
                     for _ in range(randint(min_words_amount, max_words_amount))])


def generate_text(minimal: int, maximal: int) -> str:
    min_sentence_length = DATA_GENERATION_SETTINGS["TXT"]["MIN_SENTENCE_LENGTH"]
    max_sentence_length = DATA_GENERATION_SETTINGS["TXT"]["MAX_SENTENCE_LENGTH"]
    return ' '.join([generate_sentence(min_sentence_length, max_sentence_length)
                     for _ in range(randint(minimal, maximal))])


def generate_address() -> str:
    settings = DATA_GENERATION_SETTINGS["ADR"]

    country = generate_word(settings["MIN_COUNTRY_NAME_LENGTH"], settings["MAX_COUNTRY_NAME_LENGTH"]).capitalize()
    district = generate_word(settings["MIN_DISTRICT_NAME_LENGTH"], settings["MAX_DISTRICT_NAME_LENGTH"]).capitalize()
    city = generate_word(settings["MIN_CITY_NAME_LENGTH"], settings["MAX_CITY_NAME_LENGTH"]).capitalize()
    street = choice([
        generate_sentence(settings["MIN_STREET_WORDS_AMOUNT"], settings["MAX_STREET_WORDS_AMOUNT"])[:-1].title(),
        generate_integer(settings["MIN_STREET_NUMBER"], settings["MAX_STREET_NUMBER"]) +
        ' ' + choice(['street', 'avenue']),
    ])
    building = generate_integer(settings["MIN_BUILDING_NUMBER"], settings["MAX_BUILDING_NUMBER"])

    return f"{country}, district {district}, city {city}, street {street}, building {building}"


def generate_date() -> str:
    start_date = DATA_GENERATION_SETTINGS["DTE"]["START_DATE"]
    end_date = DATA_GENERATION_SETTINGS["DTE"]["END_DATE"]
    max_days = (end_date - start_date).days
    return str(start_date + datetime.timedelta(days=randint(1, max_days)))
