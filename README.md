# Smart Campus Resource Booking System

https://github.com/402418437-sketch/Programming-Assignment.git
A Python + Tkinter + SQLite application for managing campus resource bookings
across multiple Richfield campuses.

## How to Run

1. Ensure Python 3.8+ is installed
2. Open a terminal in this folder
3. Run: `python database.py`  (initialises the database)
4. Run: `python main.py`       (starts the GUI)

## Default Accounts

| Username    | Password  | Role            | Campus     |
|-------------|-----------|-----------------|------------|
| operator    | admin123  | System Operator | (all)      |
| admin_bry   | admin123  | Campus Admin    | Bryanston  |
| admin_cen   | admin123  | Campus Admin    | Centurion  |
| admin_pre   | admin123  | Campus Admin    | Pretoria   |
| admin_mus   | admin123  | Campus Admin    | Musgrave   |
| admin_cpt   | admin123  | Campus Admin    | Cape Town  |

## Campuses and Booking Rules

| Campus     | Max Duration | Hours         | Priority                  |
|------------|--------------|---------------|---------------------------|
| Centurion  | 3 hours      | 08:00–18:00   | Exams take precedence     |
| Pretoria   | 4 hours      | 07:00–21:00   | Lecturers before 10:00    |
| Musgrave   | 5 hours      | 06:00–22:00   | First-come, first-served  |
| Bryanston  | 2 hours      | 09:00–17:00   | Executive meetings        |
| Cape Town  | 3 hours      | 08:00–18:00   | Assessments               |

## Features

- Three user roles: Lecturer, Campus Admin, System Operator
- Role-based dashboards built with Tkinter
- SQLite database for persistence
- Campus-specific booking policies (applied automatically)
- Overlap detection and duration limits
- Booking history and cancellation
- Campus-level reports and cross-campus comparison

## Architecture

- `database.py`        — SQLite connection, schema, seed data
- `models.py`          — OOP classes (User, Lecturer, Admin, Operator, Resource, Booking)
- `booking_rules.py`   — Campus-specific booking policies (extensible via CAMPUS_RULES)
- `auth.py`            — Registration and login (SHA-256 password hashing)
- `reports.py`         — Reporting and analytics
- `gui/`               — All Tkinter windows