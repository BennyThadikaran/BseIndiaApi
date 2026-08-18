import unittest

from context import CATEGORY


class Test_Category_Constants(unittest.TestCase):
    def test_action_category_is_well_formed(self):
        # Was "Corp`.` Action" - the stray backticks meant the value never
        # matched the category text BSE returns, so filtering by it failed.
        self.assertEqual(CATEGORY.ACTION, "Corp. Action")

    def test_no_category_contains_backticks(self):
        for name, value in vars(CATEGORY).items():
            if name.startswith("_") or not isinstance(value, str):
                continue
            self.assertNotIn("`", value, f"CATEGORY.{name} contains a backtick")


if __name__ == "__main__":
    unittest.main()
