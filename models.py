# models.py
from abc import ABC, abstractmethod


class User(ABC):
    """Base class for all user roles (Abstraction & Encapsulation)."""

    def __init__(self, user_id, username, role, campus_id=None):
        self._user_id = user_id          # Protected attribute (Encapsulation)
        self._username = username
        self._role = role
        self._campus_id = campus_id

    # Getters using properties (Encapsulation)
    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @property
    def role(self):
        return self._role

    @property
    def campus_id(self):
        return self._campus_id

    @abstractmethod
    def get_dashboard_title(self):
        """Each role must implement its own dashboard title."""
        pass


class Lecturer(User):
    """Represents a lecturer who books resources."""

    def __init__(self, user_id, username, campus_id=None):
        super().__init__(user_id, username, "lecturer", campus_id)

    def get_dashboard_title(self):
        return f"Lecturer Dashboard - {self.username}"


class CampusAdmin(User):
    """Represents an administrator who manages a specific campus."""

    def __init__(self, user_id, username, campus_id):
        super().__init__(user_id, username, "admin", campus_id)

    def get_dashboard_title(self):
        return f"Campus Admin Dashboard - {self.username}"


class SystemOperator(User):
    """Represents institutional management with system-wide access."""

    def __init__(self, user_id, username):
        super().__init__(user_id, username, "operator", None)

    def get_dashboard_title(self):
        return f"System Operator Dashboard - {self.username}"


class Resource:
    """Represents a bookable campus resource (lab, projector, room)."""

    def __init__(self, resource_id, name, type_, campus_id, capacity=0):
        self.resource_id = resource_id
        self.name = name
        self.type = type_
        self.campus_id = campus_id
        self.capacity = capacity

    def __str__(self):
        return f"{self.name} ({self.type}) - Capacity: {self.capacity}"


class Booking:
    """Represents a resource booking."""

    def __init__(self, booking_id, user_id, resource_id, campus_id,
                 booking_date, start_time, duration, status="active"):
        self.booking_id = booking_id
        self.user_id = user_id
        self.resource_id = resource_id
        self.campus_id = campus_id
        self.booking_date = booking_date
        self.start_time = start_time
        self.duration = duration
        self.status = status

    def __str__(self):
        return (f"Booking #{self.booking_id}: Resource {self.resource_id} "
                f"on {self.booking_date} at {self.start_time} "
                f"for {self.duration} hour(s)")