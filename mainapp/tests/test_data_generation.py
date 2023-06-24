import datetime
import re

from django.test import SimpleTestCase

from ..data_generators.data_generation import generate_word, generate_sentence, generate_integer, generate_full_name, \
    generate_job, generate_email, generate_domain_name, generate_phone_number, generate_company_name, generate_text, \
    generate_address, generate_date


class TestDummyDataGeneration(SimpleTestCase):
    minimal = 3
    maximal = 10

    def test_generate_word(self):
        regex = re.compile(r'[a-z]{3,10}')
        for _ in range(100):
            word = generate_word(self.minimal, self.maximal)

            self.assertTrue(re.fullmatch(regex, word))

    def test_generate_sentence(self):
        regex = re.compile(r'[A-Z][a-z]{2,9}(?: [a-z]{3,10}){2,9}\.')
        for _ in range(100):
            sentence = generate_sentence(self.minimal, self.maximal)

            self.assertTrue(re.fullmatch(regex, sentence))

    def test_integer(self):
        for _ in range(100):
            integer = generate_integer(self.minimal, self.maximal)

            self.assertTrue(self.minimal <= int(integer) <= self.maximal)

    def test_generate_full_name(self):
        first_names = ['Hanna', 'Alice', 'Bone']
        last_names = ['Smith', 'Anderson', 'Johnson']
        regex = re.compile(r'[A-Z][a-z]+ [A-Z][a-z]+')
        for _ in range(100):
            full_name = generate_full_name(first_names, last_names)

            self.assertTrue(re.fullmatch(regex, full_name))
            self.assertIn(full_name.split()[0], first_names)
            self.assertIn(full_name.split()[1], last_names)

    def test_generate_job(self):
        jobs = ['plumber', 'tractor driver', 'farmer', 'python developer']

        for _ in range(100):
            job = generate_job(jobs)

            self.assertIn(job, jobs)

    def test_generate_email(self):
        regex = re.compile(r'[a-z]{5,12}@gmail\.com')
        for _ in range(100):
            email = generate_email()

            self.assertTrue(re.fullmatch(regex, email))

    def test_generate_domain_name(self):
        regex = re.compile(r'[a-z]{3,15}\.[a-z]{2,4}')
        for _ in range(100):
            domain_name = generate_domain_name()

            self.assertTrue(re.fullmatch(regex, domain_name))

    def test_generate_phone_number(self):
        regex = re.compile(r'\+380\d{9}')
        for _ in range(100):
            phone_number = generate_phone_number()

            self.assertTrue(re.fullmatch(regex, phone_number))

    def test_generate_company_name(self):
        regex = re.compile(r'[A-Z]{5,15}(?: [A-Z]{5,15}){0,4}')
        for _ in range(100):
            company_name = generate_company_name()

            self.assertTrue(re.fullmatch(regex, company_name))

    def test_generate_text(self):
        regex = re.compile(r'[A-Z][a-z]{2,9}(?: [a-z]{3,10}){2,9}\.(?: [A-Z][a-z]{2,9}(?: [a-z]{3,10}){2,9}\.){2,9}')
        for _ in range(100):
            text = generate_text(self.minimal, self.maximal)

            self.assertTrue(re.fullmatch(regex, text))

    def test_generate_address(self):
        regex = re.compile(r'[A-Z][a-z]{2,13}, district [A-Z][a-z]{4,13}, city [A-Z][a-z]{4,7}, street (?:[A-Z][a-z]'
                           r'{2,9}(?: [A-Z][a-z]{2,9}){0,2}|(?:[1-9]|[1-9][0-9]|100) (?:street|avenue)), building '
                           r'(?:[1-9]|[1-9][0-9]|[1-4][0-9]{2}|500)')
        for _ in range(100):
            address = generate_address()

            self.assertTrue(re.fullmatch(regex, address))

    def test_generate_date(self):
        regex = re.compile(r'[12]\d{3}-\d{2}-\d{2}')
        for _ in range(100):
            date = generate_date()

            self.assertTrue(re.fullmatch(regex, date))
            try:
                datetime.date(*map(int, date.split('-')))
            except ValueError:
                self.fail("Date is not valid")
