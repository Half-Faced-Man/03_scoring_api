import hashlib
import datetime as dt

import functools
import unittest
import sys

sys.path.append('../')
import api


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)

        return wrapper

    return decorator


class TestBaseData(unittest.TestCase):

    @cases(['first_test', 23])
    def test_valid(self, value):
        bd = api.BaseData()
        bd.__set__(bd, value)
        self.assertEqual(value, bd.__get__(bd, api.BaseData()))

    @cases([None])
    def test_nullable(self, value):
        bd = api.BaseData()
        with self.assertRaises(ValueError):
            bd.__set__(bd, value)

        bd_nullable = api.BaseData(nullable=True)
        bd_nullable.__set__(bd_nullable, value)
        self.assertEqual(value, bd_nullable.__get__(bd_nullable, api.BaseData()))


class TestCharField(unittest.TestCase):

    @cases(['test'])
    def test_valid(self, value):
        field = api.CharField()
        field.__set__(field, value)
        self.assertEqual(value, field.__get__(field, api.CharField()))

    @cases([None])
    def test_nullable(self, value):
        field = api.CharField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)

        field_nullable = api.CharField(nullable=True)
        field_nullable.__set__(field_nullable, value)
        self.assertEqual(value, field_nullable.__get__(field_nullable, api.CharField()))

    @cases([23, 0])
    def test_invalid(self, value):
        field = api.CharField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)


class TestArgumentsField(unittest.TestCase):

    @cases([{'test': '234', 'test_2': 45}])
    def test_valid(self, value):
        field = api.ArgumentsField()
        field.__set__(field, value)
        self.assertEqual(value, field.__get__(field, api.ArgumentsField()))

    @cases([None])
    def test_nullable(self, value):
        field = api.ArgumentsField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)

        field_nullable = api.ArgumentsField(nullable=True)
        field_nullable.__set__(field_nullable, value)
        self.assertEqual(value, field_nullable.__get__(field_nullable, api.ArgumentsField()))

    @cases([23, 'test', None, ''])
    def test_invalid(self, value):
        field = api.ArgumentsField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)


class TestEmailField(unittest.TestCase):

    @cases(['test@test'])
    def test_valid(self, value):
        field = api.EmailField()
        field.__set__(field, value)
        self.assertEqual(value, field.__get__(field, api.EmailField()))

    @cases([None])
    def test_nullable(self, value):
        field = api.EmailField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)

        field_nullable = api.EmailField(nullable=True)
        field_nullable.__set__(field_nullable, value)
        self.assertEqual(value, field_nullable.__get__(field_nullable, api.EmailField()))

    @cases([23, '', [], None, {}, 'testtest'])
    def test_invalid(self, value):
        field = api.EmailField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)


class TestPhoneField(unittest.TestCase):

    @cases(['76543210987', 76543210987])
    def test_valid(self, value):
        field = api.PhoneField()
        field.__set__(field, value)
        self.assertEqual(value, field.__get__(field, api.PhoneField()))

    @cases([None])
    def test_nullable(self, value):
        field = api.PhoneField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)

        field_nullable = api.PhoneField(nullable=True)
        field_nullable.__set__(field_nullable, value)
        self.assertEqual(value, field_nullable.__get__(field_nullable, api.PhoneField()))

    @cases([96543210987, '96543210987', 23, '', [], None, {}])
    def test_invalid(self, value):
        field = api.PhoneField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)


class TestDateField(unittest.TestCase):

    @cases(['22.02.2012'])
    def test_valid(self, value):
        field = api.DateField()
        field.__set__(field, value)
        self.assertIsInstance(field.__get__(field, api.DateField()), dt.date)

    @cases([None])
    def test_nullable(self, value):
        field = api.DateField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)

        field_nullable = api.DateField(nullable=True)
        field_nullable.__set__(field_nullable, value)
        self.assertEqual(value, field_nullable.__get__(field_nullable, api.DateField()))

    @cases(['2012.22.02', '2012.02.22'])
    def test_invalid(self, value):
        field = api.DateField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)


class TestBirthDayField(unittest.TestCase):

    @cases(['22.02.2012'])
    def test_valid(self, value):
        field = api.BirthDayField()
        field.__set__(field, value)
        self.assertIsInstance(field.__get__(field, api.BirthDayField()), dt.date)

    @cases([None])
    def test_nullable(self, value):
        field = api.BirthDayField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)

        field_nullable = api.BirthDayField(nullable=True)
        field_nullable.__set__(field_nullable, value)
        self.assertEqual(value, field_nullable.__get__(field_nullable, api.BirthDayField()))

    @cases(['22.02.1902', '2012.22.02', '2012.02.22'])
    def test_invalid(self, value):
        field = api.BirthDayField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)


class TestGenderField(unittest.TestCase):

    @cases([0, 1, 2])
    def test_valid(self, value):
        field = api.GenderField()
        field.__set__(field, value)
        self.assertEqual(value, field.__get__(field, api.GenderField()))

    @cases([None])
    def test_nullable(self, value):
        field = api.GenderField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)

        field_nullable = api.GenderField(nullable=True)
        field_nullable.__set__(field_nullable, value)
        self.assertEqual(value, field_nullable.__get__(field_nullable, api.GenderField()))

    @cases(['23', 6, -1])
    def test_invalid(self, value):
        field = api.GenderField()
        with self.assertRaises(ValueError):
            field.__set__(field, value)


class TestClientIDsField(unittest.TestCase):

    @cases([[0, 1, 2], [3, 4, -1, 9999]])
    def test_valid(self, value):
        field = api.ClientIDsField()
        field.__set__(field, value)
        self.assertEqual(value, field.__get__(field, api.ClientIDsField()))

    @cases([ ['2', 1] , [] ]) # '23', 6, -1, [], ['2'],
    def test_invalid(self, value):
        field = api.ClientIDsField(required=True)
        with self.assertRaises(ValueError):
            field.__set__(field, value)


if __name__ == "__main__":
    unittest.main()
