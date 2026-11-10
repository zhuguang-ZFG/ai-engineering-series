import unittest

from parcel import fee_cents


class ParcelTests(unittest.TestCase):
    def test_prices(self):
        for grams, cents in ((1, 600), (1000, 600), (1001, 800),
                             (2000, 800), (2001, 1000), (30000, 6400)):
            with self.subTest(grams=grams):
                self.assertEqual(fee_cents(grams), cents)

    def test_rejects_wrong_type(self):
        for grams in (True, "1000", 1000.0, None):
            with self.subTest(grams=grams), self.assertRaises(TypeError):
                fee_cents(grams)

    def test_rejects_out_of_range(self):
        for grams in (0, -1, 30001):
            with self.subTest(grams=grams), self.assertRaises(ValueError):
                fee_cents(grams)


if __name__ == "__main__":
    unittest.main()
