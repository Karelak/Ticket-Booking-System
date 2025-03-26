import sqlite3
import random
import datetime
from faker import Faker
import os


def create_database_structure(conn):
    """Create the database tables with the correct schema."""
    cursor = conn.cursor()

    # Create customers table with correct schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customers_id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT,
        type TEXT CHECK(type IN ('Child', 'Adult', 'Senior', 'VIP'))
    )
    """)

    # Create shows table with correct schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shows (
        shows_id INTEGER PRIMARY KEY,
        title TEXT,
        date DATETIME,
        venue TEXT
    )
    """)

    # Create bookings table with correct schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        bookings_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        show_id INTEGER,
        booking_date DATETIME,
        total_price DECIMAL(10, 2),
        FOREIGN KEY (customer_id) REFERENCES customers (customers_id),
        FOREIGN KEY (show_id) REFERENCES shows (shows_id)
    )
    """)

    # Create seats table with correct schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seats (
        seats_id INTEGER PRIMARY KEY,
        booking_id INTEGER,
        seat_number TEXT,
        price DECIMAL(10, 2),
        status TEXT CHECK(status IN ('Booked', 'Available', 'Blocked')),
        FOREIGN KEY (booking_id) REFERENCES bookings(bookings_id)
    )
    """)

    conn.commit()


def get_table_info(conn, table_name):
    """Get column information for a specific table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [info[1] for info in cursor.fetchall()]  # Return column names


def generate_sample_customers(conn, num_customers, fake):
    """Generate sample customer data with correct schema."""
    cursor = conn.cursor()

    # Check if customers table is empty
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]

    if count == 0:
        print(f"Generating {num_customers} sample customers...")

        # Customer types according to the schema constraint
        customer_types = ["Adult", "Child", "Senior", "VIP"]

        for i in range(num_customers):
            # Generate full name
            name = fake.name()
            phone = fake.phone_number()
            customer_type = random.choice(customer_types)

            cursor.execute(
                "INSERT INTO customers (name, phone, type) VALUES (?, ?, ?)",
                (name, phone, customer_type),
            )

        conn.commit()
        print(f"Generated {num_customers} sample customers.")
    else:
        print(f"Found {count} existing customers in database.")

    return True


def generate_sample_shows(conn, num_shows, fake, start_date, end_date):
    """Generate sample show data with correct schema."""
    cursor = conn.cursor()

    # Check if shows table is empty
    cursor.execute("SELECT COUNT(*) FROM shows")
    count = cursor.fetchone()[0]

    if count == 0:
        print(f"Generating {num_shows} sample shows...")

        venues = [
            "Royal Albert Hall",
            "O2 Arena",
            "Wembley Stadium",
            "Barbican Centre",
            "Royal Opera House",
            "SSE Arena",
            "Theatre Royal",
            "London Palladium",
            "Shakespeare's Globe",
        ]

        show_prefixes = ["The", "A Night of", "Royal", "Classic", "Modern", "Live"]
        show_names = [
            "Concert",
            "Ballet",
            "Opera",
            "Play",
            "Musical",
            "Symphony",
            "Performance",
        ]

        for i in range(num_shows):
            prefix = random.choice(show_prefixes)
            name = random.choice(show_names)
            artist = fake.name()
            title = f"{prefix} {name} with {artist}"

            # Generate random date between start_date and end_date (date only, no time)
            date = fake.date_time_between_dates(
                datetime_start=start_date, datetime_end=end_date
            )
            # Format as YYYY-MM-DD to exclude time
            date = date.strftime("%Y-%m-%d")

            venue = random.choice(venues)

            cursor.execute(
                "INSERT INTO shows (title, date, venue) VALUES (?, ?, ?)",
                (title, date, venue),
            )

        conn.commit()
        print(f"Generated {num_shows} sample shows.")
    else:
        print(f"Found {count} existing shows in database.")

    return True


def generate_bookings(conn, num_bookings, fake, start_date, end_date):
    """Generate sample booking data."""
    cursor = conn.cursor()

    # Get all customer IDs and their types
    cursor.execute("SELECT customers_id, type FROM customers")
    customers = cursor.fetchall()

    if not customers:
        print("No customers found. Please generate customers first.")
        return False

    # Get all show IDs
    cursor.execute("SELECT shows_id FROM shows")
    show_ids = [row[0] for row in cursor.fetchall()]

    if not show_ids:
        print("No shows found. Please generate shows first.")
        return False

    print(f"Generating {num_bookings} bookings...")

    # Track created booking IDs to generate seats later
    booking_ids = []

    for i in range(num_bookings):
        # Select a random customer and their type
        customer = random.choice(customers)
        customer_id = customer[0]
        customer_type = customer[1]

        show_id = random.choice(show_ids)

        # Generate booking date (before the show date)
        cursor.execute("SELECT date FROM shows WHERE shows_id = ?", (show_id,))
        show_date = cursor.fetchone()[0]

        # Handle show date as string
        if isinstance(show_date, str):
            if "T" in show_date:  # ISO format
                show_date = datetime.datetime.fromisoformat(
                    show_date.replace("Z", "+00:00")
                )
            else:  # YYYY-MM-DD format
                show_date = datetime.datetime.strptime(show_date, "%Y-%m-%d")

        # Booking should be between start_date and show_date
        booking_date = fake.date_time_between_dates(
            datetime_start=start_date, datetime_end=min(end_date, show_date)
        )

        # Format booking date as YYYY-MM-DD to exclude time
        booking_date = booking_date.strftime("%Y-%m-%d")

        # Set price based on customer type
        if customer_type == "VIP":
            total_price = 0.00  # VIPs get in free
        elif customer_type in ["Child", "Senior"]:
            total_price = 5.00  # Under 18 and over 65 pay £5
        else:
            total_price = 10.00  # Default price £10

        cursor.execute(
            "INSERT INTO bookings (customer_id, show_id, booking_date, total_price) VALUES (?, ?, ?, ?)",
            (customer_id, show_id, booking_date, total_price),
        )

        # Get the booking ID for seat generation
        booking_id = cursor.lastrowid
        booking_ids.append((booking_id, customer_type))

        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} bookings...")

    conn.commit()
    print(f"Successfully generated {num_bookings} bookings.")

    # Now generate seats for each booking
    generate_seats(conn, booking_ids)

    return True


def generate_seats(conn, booking_ids):
    """Generate sample seat data for bookings."""
    cursor = conn.cursor()

    print(f"Generating seats for {len(booking_ids)} bookings...")

    # Define possible seat rows and numbers
    rows = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"]
    seats_per_row = 20
    seat_count = 0

    for booking_id, customer_type in booking_ids:
        # Determine number of seats per booking (1-4 seats)
        num_seats = random.randint(1, 4)

        # Set price based on customer type
        if customer_type == "VIP":
            base_price = 0.00  # VIPs get in free
        elif customer_type in ["Child", "Senior"]:
            base_price = 5.00  # Under 18 and over 65 pay £5
        else:
            base_price = 10.00  # Default price £10

        # Pick a random section (row) for booking
        row = random.choice(rows)

        # Generate consecutive seats
        start_seat = random.randint(1, seats_per_row - num_seats + 1)

        for seat_num in range(start_seat, start_seat + num_seats):
            seat_number = f"{row}{seat_num}"

            # Slight price variation based on row
            price = base_price + (rows.index(row) * 0.5)

            cursor.execute(
                "INSERT INTO seats (booking_id, seat_number, price, status) VALUES (?, ?, ?, ?)",
                (booking_id, seat_number, price, "Booked"),
            )
            seat_count += 1

    conn.commit()
    print(f"Successfully generated {seat_count} seats.")
    return True


def main():
    # Setup Faker with UK locale
    fake = Faker("en_GB")

    db_path = "../system.db"
    db_exists = os.path.exists(db_path)

    if db_exists:
        confirm = input("Database already exists. Do you want to replace it? (y/n): ")
        if confirm.lower() == "y":
            os.remove(db_path)
            print("Existing database removed.")
        else:
            print("Using existing database.")

    print("UK Theatre Booking System - Sample Data Generator")
    print("=" * 50)
    print("Pricing rules: Adults: £10, Children/Seniors: £5, VIPs: Free")
    print("=" * 50)

    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Create tables if they don't exist
    create_database_structure(conn)

    # Get user input for generation settings
    print("\nPlease enter the following settings for data generation:")

    # Ask if they want to generate customers and shows too
    generate_all = (
        input("Generate customers and shows too? (y/n, default: y): ").lower() != "n"
    )

    if generate_all:
        num_customers = int(
            input("Number of customers to generate (default: 100): ") or 100
        )
        num_shows = int(input("Number of shows to generate (default: 20): ") or 20)

    num_bookings = int(input("Number of bookings to generate (default: 200): ") or 200)

    # Date range for bookings and shows
    print("\nEnter date range (format: DD/MM/YYYY)")
    start_date_str = input("Start date (default: 01/01/2023): ") or "01/01/2023"
    end_date_str = input("End date (default: 31/12/2023): ") or "31/12/2023"

    # Parse dates from DD/MM/YYYY format
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%d/%m/%Y")
        end_date = datetime.datetime.strptime(end_date_str, "%d/%m/%Y")
    except ValueError:
        print("Invalid date format. Using default dates.")
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 12, 31)

    # Generate data
    if generate_all:
        generate_sample_customers(conn, num_customers, fake)
        generate_sample_shows(conn, num_shows, fake, start_date, end_date)

    generate_bookings(conn, num_bookings, fake, start_date, end_date)

    # Show summary
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shows")
    show_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    booking_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM seats")
    seat_count = cursor.fetchone()[0]

    print("\nDatabase Summary:")
    print(f"- Customers: {customer_count}")
    print(f"- Shows: {show_count}")
    print(f"- Bookings: {booking_count}")
    print(f"- Seats: {seat_count}")

    # Close the connection
    conn.close()

    print("\nData generation complete! Database saved to:", db_path)


if __name__ == "__main__":
    main()
