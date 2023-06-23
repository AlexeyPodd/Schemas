import datetime
from random import randint, choice

"""
For every data type must be uniq function for data generating.
This function's name must be in two parts.
The first part is 'generate_', and the second part is the name of the data type,
in lowercase, with replaced spaces by '_'.
If data type implements limitations - function must take parameters minimal and maximal. If not - no parameters.
Id data types uses source file for generating - function must take parameters with same name,
as in main dict in json source file.
The function must return string.
"""

first_letter_code = ord('a')
last_letter_code = ord('z')


def generate_word(minimal: int, maximal: int) -> str:
    return ''.join([chr(randint(first_letter_code, last_letter_code)) for _ in range(randint(minimal, maximal))])


def generate_sentence(minimal: int, maximal: int) -> str:
    return ' '.join([generate_word(3, 10) for _ in range(randint(minimal, maximal))]).capitalize() + '.'


def generate_integer(minimal: int, maximal: int) -> str:
    return str(randint(minimal, maximal))


def generate_full_name(first_names: list[str], last_names: list[str]) -> str:
    first_name = choice(first_names)
    last_name = choice(last_names)
    return first_name + ' ' + last_name


def generate_job(jobs: list[str]) -> str:
    return choice(jobs)


def generate_email() -> str:
    email_name = ''.join([chr(randint(first_letter_code, last_letter_code)) for _ in range(randint(5, 12))])
    return email_name + '@gmail.com'


def generate_domain_name() -> str:
    top_level_domains = ['com', 'ua', 'club', 'net', 'org', 'uk', 'jp', 'pl', 'io', 'edu', 'gov', 'info']
    second_level_domain = generate_word(3, 15)
    return second_level_domain + '.' + choice(top_level_domains)


def generate_phone_number() -> str:
    return '+380' + ''.join([generate_integer(0, 9) for _ in range(9)])


def generate_company_name() -> str:
    return ' '.join([generate_word(5, 15).upper() for _ in range(randint(1, 5))])


def generate_text(minimal: int, maximal: int) -> str:
    return ' '.join([generate_sentence(3, 10) for _ in range(randint(minimal, maximal))])


def generate_address() -> str:
    country = generate_word(3, 14).capitalize()
    district = generate_word(5, 14).capitalize()
    city = generate_word(5, 8).capitalize()
    street = choice([
        generate_sentence(1, 3)[:-1].title(),
        generate_integer(1, 100) + ' ' + choice(['street', 'avenue']),
    ])
    building = generate_integer(1, 500)

    return f"{country}, district {district}, city {city}, street {street}, building {building}"


def generate_date() -> str:
    start_date = datetime.date(1000, 1, 1)
    end_date = datetime.date(2100, 12, 31)
    max_days = (end_date - start_date).days
    return str(start_date + datetime.timedelta(days=randint(1, max_days)))
