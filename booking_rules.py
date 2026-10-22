# booking_rules.py


class BookingRule:
    """Base booking rule. Override methods for campus-specific rules."""

    def __init__(self, campus_name):
        self.campus_name = campus_name

    def max_duration(self):
        """Maximum booking duration in hours."""
        return 4

    def allowed_hours(self):
        """Return (start_hour, end_hour) in 24-hour format."""
        return (7, 21)

    def priority_note(self):
        """Description of priority access rules."""
        return "No priority access rules."

    def validate(self, booking_date, start_time, duration):
        """Return (is_valid, message). Checks the rules automatically."""
        if duration > self.max_duration():
            return False, f"Maximum duration at {self.campus_name} is {self.max_duration()} hours."

        if duration <= 0:
            return False, "Duration must be at least 1 hour."

        try:
            start_hour = int(start_time.split(":")[0])
        except (ValueError, IndexError):
            return False, "Invalid start time format. Use HH:MM."

        open_hour, close_hour = self.allowed_hours()
        if start_hour < open_hour or start_hour >= close_hour:
            return False, (f"Bookings at {self.campus_name} are only allowed "
                           f"between {open_hour:02d}:00 and {close_hour:02d}:00.")

        if start_hour + duration > close_hour:
            return False, (f"Booking would end after closing time "
                           f"({close_hour:02d}:00).")

        return True, "Booking is valid."


# --- Campus-Specific Subclasses (Inheritance) ---

class CenturionRule(BookingRule):
    """Centurion: max 3 hours, 08:00–18:00, priority to exams."""

    def __init__(self):
        super().__init__("Centurion Campus")

    def max_duration(self):
        return 3

    def allowed_hours(self):
        return (8, 18)

    def priority_note(self):
        return "Priority access: Exam bookings take precedence."


class PretoriaRule(BookingRule):
    """Pretoria: max 4 hours, 07:00–21:00, priority to lecturers."""

    def __init__(self):
        super().__init__("Pretoria Campus")

    def max_duration(self):
        return 4

    def allowed_hours(self):
        return (7, 21)

    def priority_note(self):
        return "Priority access: Lecturers have first choice before 10:00."


class MusgraveRule(BookingRule):
    """Musgrave: max 5 hours, 06:00–22:00, first-come first-served."""

    def __init__(self):
        super().__init__("Musgrave Campus")

    def max_duration(self):
        return 5

    def allowed_hours(self):
        return (6, 22)

    def priority_note(self):
        return "Priority access: First-come, first-served."


class BryanstonRule(BookingRule):
    """Bryanston: max 2 hours, 09:00–17:00, strict corporate hours."""

    def __init__(self):
        super().__init__("Bryanston Campus")

    def max_duration(self):
        return 2

    def allowed_hours(self):
        return (9, 17)

    def priority_note(self):
        return "Priority access: Executive meetings take precedence."


class CapeTownRule(BookingRule):
    """Cape Town: max 3 hours, 08:00–18:00, assessments first."""

    def __init__(self):
        super().__init__("Cape Town Campus")

    def max_duration(self):
        return 3

    def allowed_hours(self):
        return (8, 18)

    def priority_note(self):
        return "Priority access: Assessments and exams take precedence."


# --- Registry / Factory ---

CAMPUS_RULES = {
    "Centurion Campus": CenturionRule,
    "Pretoria Campus": PretoriaRule,
    "Musgrave Campus": MusgraveRule,
    "Bryanston Campus": BryanstonRule,
    "Cape Town Campus": CapeTownRule,
}


def get_rule_for_campus(campus_name):
    """Factory function to get the rule object for a campus."""
    rule_class = CAMPUS_RULES.get(campus_name, BookingRule)
    return rule_class()