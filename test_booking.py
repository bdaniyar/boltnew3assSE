"""Run with: python3 -m unittest -v test_booking

Only Python's standard library is used. Each test result is also checked to
be a built-in Boolean. Existing bookings use half-open [start, end) intervals.
"""

import copy
import unittest

from booking import can_book


class CanBookTests(unittest.TestCase):
    def setUp(self):
        self.existing = [(600, 660)]

    def check(self, expected, start, end, *, now=540, blocked=False, existing=None):
        bookings = self.existing if existing is None else existing
        actual = can_book(start, end, now, blocked, bookings)
        self.assertIs(type(actual), bool)
        self.assertIs(actual, expected)

    # The six exact fixtures required on assignment page 14.
    def test_mandatory_1_touching_after_booking(self):
        self.check(True, 660, 720)

    def test_mandatory_2_overlap(self):
        self.check(False, 630, 690)

    def test_mandatory_3_blocked(self):
        self.check(False, 660, 720, blocked=True)

    def test_mandatory_4_exactly_120_minutes(self):
        self.check(True, 720, 840)

    def test_mandatory_5_duration_121_minutes(self):
        self.check(False, 720, 841)

    def test_mandatory_6_starts_now(self):
        self.check(False, 540, 570)

    def test_reversed_times(self):
        self.check(False, 720, 660)

    def test_equal_start_and_end(self):
        self.check(False, 720, 720)

    def test_negative_start(self):
        self.check(False, -1, 60, now=0, existing=[])

    def test_negative_end(self):
        self.check(False, -60, -1, now=0, existing=[])

    def test_end_beyond_day(self):
        self.check(False, 1380, 1441, existing=[])

    def test_start_beyond_day(self):
        self.check(False, 1441, 1442, existing=[])

    def test_start_at_1440(self):
        self.check(False, 1440, 1440, existing=[])

    def test_midnight_start_is_not_future(self):
        self.check(False, 0, 1, now=0, existing=[])

    def test_one_minute_after_midnight(self):
        self.check(True, 1, 2, now=0, existing=[])

    def test_start_in_past(self):
        self.check(False, 539, 570)

    def test_start_one_minute_in_future(self):
        self.check(True, 541, 542)

    def test_end_at_1440_with_120_minutes(self):
        self.check(True, 1320, 1440, existing=[])

    def test_last_minute_of_day(self):
        self.check(True, 1439, 1440, now=1438, existing=[])

    def test_last_valid_now_has_no_future_start(self):
        self.check(False, 1439, 1440, now=1439, existing=[])

    def test_one_minute_duration(self):
        self.check(True, 720, 721)

    def test_119_minute_duration(self):
        self.check(True, 720, 839)

    def test_late_day_121_minute_duration(self):
        self.check(False, 1319, 1440, existing=[])

    def test_start_noninteger_types(self):
        for value in (660.0, 660.5, "660", None, [], {}, complex(660, 0)):
            with self.subTest(start=value):
                self.check(False, value, 720)

    def test_end_noninteger_types(self):
        for value in (720.0, 720.5, "720", None, [], {}, complex(720, 0)):
            with self.subTest(end=value):
                self.check(False, 660, value)

    def test_boolean_start_is_not_integer_time(self):
        for value in (True, False):
            with self.subTest(start=value):
                self.check(False, value, 2, now=0, existing=[])

    def test_boolean_end_is_not_integer_time(self):
        for value in (True, False):
            with self.subTest(end=value):
                self.check(False, 1, value, now=0, existing=[])

    def test_strict_integer_type_excludes_subclass(self):
        class Minute(int):
            pass

        self.check(False, Minute(660), 720)
        self.check(False, 660, Minute(720))

    def test_touching_before_booking(self):
        self.check(True, 570, 600)

    def test_touching_two_bookings(self):
        self.check(True, 660, 720, existing=[(600, 660), (720, 780)])

    def test_one_minute_overlap_at_booking_start(self):
        self.check(False, 599, 601)

    def test_one_minute_overlap_at_booking_end(self):
        self.check(False, 659, 661)

    def test_identical_interval(self):
        self.check(False, 600, 660)

    def test_request_inside_existing(self):
        self.check(False, 610, 650)

    def test_request_contains_existing(self):
        self.check(False, 570, 690)

    def test_separated_before_existing(self):
        self.check(True, 550, 590)

    def test_separated_after_existing(self):
        self.check(True, 700, 760)

    def test_empty_existing(self):
        self.check(True, 600, 660, existing=[])

    def test_overlap_with_second_booking(self):
        self.check(False, 720, 780, existing=[(600, 660), (750, 810)])

    def test_overlap_with_last_of_several_bookings(self):
        self.check(False, 1020, 1080, existing=[(600, 660), (720, 780), (1050, 1110)])

    def test_multiple_nonoverlapping_bookings(self):
        self.check(True, 780, 840, existing=[(600, 660), (720, 780), (840, 900)])

    def test_unsorted_existing_bookings(self):
        self.check(False, 720, 780, existing=[(900, 960), (750, 810), (600, 660)])

    def test_tuple_existing_bookings(self):
        self.check(True, 660, 720, existing=((600, 660), (720, 780)))

    def test_blocked_without_existing_bookings(self):
        self.check(False, 720, 840, blocked=True, existing=[])

    def test_inputs_unchanged_after_available_result(self):
        existing = [[600, 660], [720, 780]]
        before = copy.deepcopy(existing)
        first_interval = existing[0]
        start, end, now, blocked = 660, 720, 540, False
        actual = can_book(start, end, now, blocked, existing)
        self.assertIs(actual, True)
        self.assertEqual(existing, before)
        self.assertIs(existing[0], first_interval)
        self.assertEqual((start, end, now, blocked), (660, 720, 540, False))

    def test_inputs_unchanged_after_all_rejection_paths(self):
        existing = [[600, 660], [720, 780]]
        before = copy.deepcopy(existing)
        interval_ids = [id(interval) for interval in existing]
        requests = [
            ("660", 720, 540, False),
            (-1, 60, 0, False),
            (540, 570, 540, False),
            (780, 901, 540, False),
            (660, 720, 540, True),
            (630, 690, 540, False),
        ]
        requests_before = copy.deepcopy(requests)
        for start, end, now, blocked in requests:
            with self.subTest(start=start, end=end, blocked=blocked):
                actual = can_book(start, end, now, blocked, existing)
                self.assertIs(actual, False)
                self.assertEqual(existing, before)
                self.assertEqual([id(interval) for interval in existing], interval_ids)
        self.assertEqual(requests, requests_before)

    def test_repeated_checks_do_not_create_bookings(self):
        before = copy.deepcopy(self.existing)
        for _ in range(3):
            self.check(True, 660, 720)
        self.assertEqual(self.existing, before)


if __name__ == "__main__":
    unittest.main()
