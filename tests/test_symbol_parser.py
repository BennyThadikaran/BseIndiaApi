import unittest
from context import SymbolParser


class Test_Symbol_Parser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = SymbolParser()

    def test_properties(self):
        self.assertTrue(isinstance(self.parser.fields, tuple))
        self.assertEqual(len(self.parser.fields), 4)
        self.assertEqual(self.parser.index, 0)
        self.assertFalse(self.parser.start, False)
        self.assertEqual(self.parser.result, {})

    def test_anchor_tag_triggers_parsing(self):
        self.parser.handle_starttag(tag="p", attrs=[])
        self.assertFalse(self.parser.start)

        self.parser.handle_starttag(tag="a", attrs=[])
        self.assertTrue(self.parser.start)

    def test_anchor_closing_tag_pauses_parsing(self):
        self.parser.start = True
        self.parser.handle_endtag(tag="p")

        self.assertTrue(self.parser.start)

        self.parser.handle_endtag(tag="a")
        self.assertFalse(self.parser.start)

    def test_ignore_data_if_parsing_paused(self):
        self.assertFalse(self.parser.start)

        self.parser.handle_data("HDFC bank Ltd")
        self.assertEqual(self.parser.result, {})

    def test_data_parsed_when_anchor_tag_is_open(self):
        str_to_test = "HDFC bank Ltd"
        self.parser.start = True

        self.parser.handle_data(str_to_test)
        self.assertEqual(self.parser.result.get("company_name", None), str_to_test)

    def test_index_increments_on_each_data(self):
        str_to_test = "HDFC bank Ltd"
        self.parser.start = True

        self.assertEqual(self.parser.index, 0)
        self.parser.handle_data(str_to_test)
        self.assertEqual(self.parser.index, 1)

    def test_reset(self):
        self.parser.start = True
        company_name = "HDFC bank ltd"

        self.parser.handle_data(company_name)

        self.parser.reset_data()
        self.assertEqual(self.parser.result, {})
        self.assertFalse(self.parser.start, False)
        self.assertEqual(self.parser.index, 0)

    def test_full_sequential_parsing(self):
        self.parser.start = True
        company_name = "HDFC bank ltd"
        symbol_name = "HDFCBANK"
        isin_code = "IN02421234"
        bse_code = "232011"

        self.parser.handle_data(company_name)
        self.parser.handle_data(symbol_name)
        self.parser.handle_data(isin_code)
        self.parser.handle_data(bse_code)

        self.assertTrue("company_name" in self.parser.result)
        self.assertTrue("symbol" in self.parser.result)
        self.assertTrue("isin" in self.parser.result)
        self.assertTrue("bse_code" in self.parser.result)
        self.assertEqual(self.parser.result.get("company_name", None), company_name)
        self.assertEqual(self.parser.result.get("symbol", None), symbol_name)
        self.assertEqual(self.parser.result.get("isin", None), isin_code)
        self.assertEqual(self.parser.result.get("bse_code", None), bse_code)

    def test_parsing_combined_space_separated_fields(self):
        self.parser.start = True

        company_name = "HDFC bank ltd"
        symbol_name = "HDFCBANK"
        isin_code = "IN02421234"

        self.parser.handle_data(company_name)
        self.parser.handle_data(f"{symbol_name}  {isin_code}")

        self.assertEqual(self.parser.result.get("symbol", None), symbol_name)
        self.assertEqual(self.parser.result.get("isin", None), isin_code)


if __name__ == "__main__":
    unittest.main()
