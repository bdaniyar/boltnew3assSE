"""Availability checks for one fictional campus room; no bookings are changed."""


def can_book(start, end, now, blocked, existing):
    """Return whether [start, end) meets the room's availability rules.

    Times are integer minutes after midnight. ``now`` is assumed valid
    (0–1439), ``blocked`` is a Boolean flag, and ``existing`` contains
    well-formed (start, end) booking pairs. Touching endpoints are allowed.
    This function only reads its arguments and never creates a booking.
    """
    if type(start) is not int or type(end) is not int:
        return False
    if not 0 <= start < end <= 1440:
        return False
    if start <= now:
        return False
    if end - start > 120:
        return False
    if blocked:
        return False
    for booked_start, booked_end in existing:
        if start < booked_end and end > booked_start:
            return False
    return True
