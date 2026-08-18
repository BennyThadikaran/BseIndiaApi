import unittest
from datetime import date

from context import BSE


class Test_Split_Date_Range(unittest.TestCase):
    def test_splits_into_inclusive_chunks(self):
        chunks = BSE.split_date_range(
            date(2026, 1, 1), date(2026, 1, 10), max_chunk_size=5
        )

        self.assertEqual(
            chunks,
            [
                (date(2026, 1, 1), date(2026, 1, 5)),
                (date(2026, 1, 6), date(2026, 1, 10)),
            ],
        )

    def test_final_chunk_is_clamped_to_to_date(self):
        chunks = BSE.split_date_range(
            date(2026, 1, 1), date(2026, 1, 7), max_chunk_size=5
        )

        self.assertEqual(chunks[-1], (date(2026, 1, 6), date(2026, 1, 7)))

    def test_single_day_range(self):
        chunks = BSE.split_date_range(date(2026, 1, 1), date(2026, 1, 1))

        self.assertEqual(chunks, [(date(2026, 1, 1), date(2026, 1, 1))])

    def test_chunks_are_contiguous_and_non_overlapping(self):
        chunks = BSE.split_date_range(
            date(2026, 1, 1), date(2026, 3, 31), max_chunk_size=30
        )

        for (_, prev_end), (next_start, _) in zip(chunks, chunks[1:]):
            self.assertEqual((next_start - prev_end).days, 1)

    def test_zero_chunk_size_raises_instead_of_looping_forever(self):
        # current_end = current_start - 1 day, so current_start is
        # reassigned to itself and the loop never advances.
        with self.assertRaises(ValueError):
            BSE.split_date_range(
                date(2026, 1, 1), date(2026, 1, 10), max_chunk_size=0
            )

    def test_negative_chunk_size_raises(self):
        # Walks the range backwards until the date underflows.
        with self.assertRaises(ValueError):
            BSE.split_date_range(
                date(2026, 1, 1), date(2026, 1, 10), max_chunk_size=-5
            )

    def test_from_date_after_to_date_raises_as_documented(self):
        with self.assertRaises(ValueError):
            BSE.split_date_range(date(2026, 3, 1), date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
