import sys
import sqlite3
import datetime
from PyQt5 import QtWidgets, QtGui
from ui_files.main_window_ui import Ui_Dialog as MainWindowUI
from ui_files.seat_manager_ui import Ui_Dialog as SeatManagerUI
from ui_files.customer_search_ui import Ui_Dialog as CustomerSearchUI
from ui_files.bookings_ui import Ui_Dialog as BookingsUI


class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        self.show_id = None

        self.ui.gotocustomers.clicked.connect(self.open_customer_search)
        self.ui.gotobookings.clicked.connect(self.open_bookings)
        self.ui.gotoseats.clicked.connect(self.open_seats)

    def open_customer_search(self):
        self.show_id = self.ui.showid.text()
        if not self.show_id:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a Show ID")
            return

        self.customer_search = CustomerSearch(self.show_id)
        self.hide()
        self.customer_search.exec_()
        self.show()

    def open_bookings(self):
        self.show_id = self.ui.showid.text()
        if not self.show_id:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a Show ID")
            return

        self.bookings = Bookings(self.show_id)
        self.hide()
        self.bookings.exec_()
        self.show()

    def open_seats(self):
        self.show_id = self.ui.showid.text()
        if not self.show_id:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a Show ID")
            return

        self.seats = SeatManager(self.show_id)
        self.hide()
        self.seats.exec_()
        self.show()


class CustomerSearch(QtWidgets.QDialog):
    def __init__(self, show_id):
        super(CustomerSearch, self).__init__()
        self.ui = CustomerSearchUI()
        self.ui.setupUi(self)
        self.show_id = show_id

        self.setWindowTitle(f"Customer Search - Show ID: {show_id}")

        self.ui.backtomenu.clicked.connect(self.close)

        self.ui.childonly.clicked.connect(lambda: self.filter_by_type("Child"))
        self.ui.adultonly.clicked.connect(lambda: self.filter_by_type("Adult"))
        self.ui.senioronly.clicked.connect(lambda: self.filter_by_type("Senior"))

        self.setup_table()

    def setup_table(self):
        self.ui.tableofresults.setColumnCount(3)
        self.ui.tableofresults.setHorizontalHeaderLabels(
            ["Customer ID", "Name", "Type"]
        )

    def filter_by_type(self, customer_type):
        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT customers_id, name, type FROM customers WHERE type = ?",
                (customer_type,),
            )

            customers = cursor.fetchall()
            self.ui.tableofresults.setRowCount(len(customers))

            for row, customer in enumerate(customers):
                self.ui.tableofresults.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(str(customer[0]))
                )
                self.ui.tableofresults.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(customer[1])
                )
                self.ui.tableofresults.setItem(
                    row, 2, QtWidgets.QTableWidgetItem(customer[2])
                )

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to filter customers: {str(e)}"
            )


class Bookings(QtWidgets.QDialog):
    def __init__(self, show_id):
        super(Bookings, self).__init__()
        self.ui = BookingsUI()
        self.ui.setupUi(self)
        self.show_id = show_id

        self.setWindowTitle(f"Bookings - Show ID: {show_id}")

        self.ui.backtomenu.clicked.connect(self.close)
        self.ui.reportofselectedresult.clicked.connect(self.generate_report)

        self.setup_table()
        self.load_bookings()

    def setup_table(self):
        self.ui.tableofresults.setColumnCount(6)
        self.ui.tableofresults.setHorizontalHeaderLabels(
            [
                "Booking ID",
                "Customer Name",
                "Booking Date",
                "Total Price",
                "Seats",
                "Status",
            ]
        )

    def load_bookings(self):
        """Load bookings from database for the current show."""
        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            # Query bookings with customer information and count seats
            cursor.execute(
                """
                SELECT b.bookings_id, c.name, c.type, 
                       b.booking_date, b.total_price,
                       COUNT(s.seats_id) as seat_count
                FROM bookings b
                JOIN customers c ON b.customer_id = c.customers_id
                LEFT JOIN seats s ON s.booking_id = b.bookings_id
                WHERE b.show_id = ?
                GROUP BY b.bookings_id
            """,
                (self.show_id,),
            )

            bookings = cursor.fetchall()

            # Populate table with bookings
            self.ui.tableofresults.setRowCount(len(bookings))
            for row, booking in enumerate(bookings):
                booking_id = booking[0]
                customer_name = booking[1]
                customer_type = booking[2]

                # Format date as DMY only
                booking_date = booking[3]
                try:
                    if isinstance(booking_date, str) and "T" in booking_date:
                        # Parse ISO format date
                        parsed_date = datetime.datetime.fromisoformat(
                            booking_date.replace("Z", "+00:00")
                        )
                        formatted_date = parsed_date.strftime("%d/%m/%Y")
                    elif isinstance(booking_date, datetime.datetime):
                        formatted_date = booking_date.strftime("%d/%m/%Y")
                    else:
                        # Try to parse the date if it's in another format
                        parsed_date = datetime.datetime.strptime(
                            str(booking_date), "%Y-%m-%d %H:%M:%S"
                        )
                        formatted_date = parsed_date.strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    formatted_date = str(booking_date).split()[
                        0
                    ]  # Fallback to just using the date part

                total_price = booking[4]
                seat_count = booking[5]

                self.ui.tableofresults.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(str(booking_id))
                )
                self.ui.tableofresults.setItem(
                    row,
                    1,
                    QtWidgets.QTableWidgetItem(f"{customer_name} ({customer_type})"),
                )
                self.ui.tableofresults.setItem(
                    row, 2, QtWidgets.QTableWidgetItem(formatted_date)
                )
                self.ui.tableofresults.setItem(
                    row, 3, QtWidgets.QTableWidgetItem(f"£{total_price:.2f}")
                )
                self.ui.tableofresults.setItem(
                    row, 4, QtWidgets.QTableWidgetItem(f"{seat_count} seats")
                )
                self.ui.tableofresults.setItem(
                    row, 5, QtWidgets.QTableWidgetItem("Confirmed")
                )

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to load bookings: {str(e)}"
            )

    def generate_report(self):
        selected_items = self.ui.tableofresults.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please select a booking to generate a report"
            )
            return

        # Get booking ID from the first column of the selected row
        row = selected_items[0].row()
        booking_id = self.ui.tableofresults.item(row, 0).text()

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            # Query booking details with customer and show information
            cursor.execute(
                """
                SELECT b.bookings_id, c.customers_id, c.name, c.type,
                       b.show_id, s.title, s.venue, s.date, b.booking_date, b.total_price
                FROM bookings b
                JOIN customers c ON b.customer_id = c.customers_id
                JOIN shows s ON b.show_id = s.shows_id
                WHERE b.bookings_id = ?
            """,
                (booking_id,),
            )

            booking = cursor.fetchone()

            # Get seat information
            cursor.execute(
                """
                SELECT seat_number, price 
                FROM seats
                WHERE booking_id = ?
                ORDER BY seat_number
            """,
                (booking_id,),
            )

            seats = cursor.fetchall()
            seat_list = ", ".join([seat[0] for seat in seats])

            if booking:
                # Format dates as DMY only
                booking_date = booking[8]
                show_date = booking[7]

                try:
                    # Format booking date
                    if isinstance(booking_date, str) and "T" in booking_date:
                        parsed_date = datetime.datetime.fromisoformat(
                            booking_date.replace("Z", "+00:00")
                        )
                        formatted_booking_date = parsed_date.strftime("%d/%m/%Y")
                    elif isinstance(booking_date, datetime.datetime):
                        formatted_booking_date = booking_date.strftime("%d/%m/%Y")
                    else:
                        parsed_date = datetime.datetime.strptime(
                            str(booking_date), "%Y-%m-%d %H:%M:%S"
                        )
                        formatted_booking_date = parsed_date.strftime("%d/%m/%Y")

                    # Format show date
                    if isinstance(show_date, str) and "T" in show_date:
                        parsed_date = datetime.datetime.fromisoformat(
                            show_date.replace("Z", "+00:00")
                        )
                        formatted_show_date = parsed_date.strftime("%d/%m/%Y")
                    elif isinstance(show_date, datetime.datetime):
                        formatted_show_date = show_date.strftime("%d/%m/%Y")
                    else:
                        parsed_date = datetime.datetime.strptime(
                            str(show_date), "%Y-%m-%d %H:%M:%S"
                        )
                        formatted_show_date = parsed_date.strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    # Fallback to simpler parsing
                    formatted_booking_date = str(booking_date).split()[0]
                    formatted_show_date = str(show_date).split()[0]

                # Get price explanation based on customer type
                customer_type = booking[3]
                if customer_type == "VIP":
                    price_explanation = "VIP (Free admission)"
                elif customer_type in ["Child", "Senior"]:
                    price_explanation = f"{customer_type} (£5.00 - discounted rate)"
                else:
                    price_explanation = f"{customer_type} (£10.00 - standard rate)"

                # Format report with more details
                report_text = f"""
                BOOKING REPORT
                ------------------------------
                Booking ID: {booking[0]}
                Booking Date: {formatted_booking_date}
                
                CUSTOMER INFORMATION
                ------------------------------
                Name: {booking[2]} (ID: {booking[1]})
                Type: {price_explanation}
                
                SHOW INFORMATION
                ------------------------------
                Title: {booking[5]}
                Venue: {booking[6]}
                Date: {formatted_show_date}
                
                SEAT INFORMATION
                ------------------------------
                Seats: {seat_list}
                Number of Seats: {len(seats)}
                
                PAYMENT INFORMATION
                ------------------------------
                Total Price: £{booking[9]:.2f}
                ------------------------------
                """

                # Display report in a dialog
                report_dialog = QtWidgets.QDialog(self)
                report_dialog.setWindowTitle(f"Booking Report - ID: {booking_id}")
                report_dialog.resize(500, 500)

                layout = QtWidgets.QVBoxLayout()
                text_display = QtWidgets.QTextEdit()
                text_display.setReadOnly(True)
                text_display.setText(report_text)

                print_button = QtWidgets.QPushButton("Print Report")
                print_button.clicked.connect(lambda: self.print_report(report_text))

                close_button = QtWidgets.QPushButton("Close")
                close_button.clicked.connect(report_dialog.close)

                layout.addWidget(text_display)
                layout.addWidget(print_button)
                layout.addWidget(close_button)

                report_dialog.setLayout(layout)
                report_dialog.exec_()
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Warning", f"Booking ID {booking_id} not found."
                )

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to generate report: {str(e)}"
            )

    def print_report(self, report_text):
        """Print the report content."""
        printer = QtWidgets.QPrinter()
        dialog = QtWidgets.QPrintDialog(printer)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            document = QtGui.QTextDocument()
            document.setPlainText(report_text)
            document.print_(printer)
            QtWidgets.QMessageBox.information(
                self, "Print", "Report sent to printer successfully!"
            )


class SeatManager(QtWidgets.QDialog):
    def __init__(self, show_id):
        super(SeatManager, self).__init__()
        self.ui = SeatManagerUI()
        self.ui.setupUi(self)
        self.show_id = show_id

        self.setWindowTitle(f"Seat Manager - Show ID: {show_id}")
        self.ui.label.setText(f"Seat Management for Show ID: {show_id}")

        self.ui.backtomenu.clicked.connect(self.close)

        self.setup_table()

    def setup_table(self):
        self.ui.tablewithallseats.setColumnCount(4)
        self.ui.tablewithallseats.setHorizontalHeaderLabels(
            ["Seat ID", "Seat Number", "Price", "Status"]
        )

        # Load seats for this show
        self.load_seats()

    def load_seats(self):
        """Load seats for the selected show."""
        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            # Get all seats associated with this show
            cursor.execute(
                """
                SELECT s.seats_id, s.seat_number, s.price, s.status
                FROM seats s
                JOIN bookings b ON s.booking_id = b.bookings_id
                WHERE b.show_id = ?
                ORDER BY s.seat_number
                """,
                (self.show_id,),
            )

            seats = cursor.fetchall()

            self.ui.tablewithallseats.setRowCount(len(seats))
            for row, seat in enumerate(seats):
                seat_id = seat[0]
                seat_number = seat[1]
                price = seat[2]
                status = seat[3]

                self.ui.tablewithallseats.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(str(seat_id))
                )
                self.ui.tablewithallseats.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(seat_number)
                )
                self.ui.tablewithallseats.setItem(
                    row, 2, QtWidgets.QTableWidgetItem(f"£{price:.2f}")
                )
                self.ui.tablewithallseats.setItem(
                    row, 3, QtWidgets.QTableWidgetItem(status)
                )

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to load seats: {str(e)}"
            )

    def filter_seats(self):
        """Filter seats based on customer name or booking ID."""
        first_name = self.ui.firstname.text().strip()
        last_name = self.ui.lastname.text().strip()
        booking_id = self.ui.bookingid.text().strip()

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            query = """
                SELECT s.seats_id, s.seat_number, s.price, s.status
                FROM seats s
                JOIN bookings b ON s.booking_id = b.bookings_id
                JOIN customers c ON b.customer_id = c.customers_id
                WHERE b.show_id = ?
            """

            params = [self.show_id]

            # Build query based on filters
            if booking_id:
                query += " AND b.bookings_id = ?"
                params.append(booking_id)

            name_filter = ""
            if first_name or last_name:
                name_filter = first_name + " " + last_name
                name_filter = name_filter.strip()
                if name_filter:
                    query += " AND c.name LIKE ?"
                    params.append(f"%{name_filter}%")

            query += " ORDER BY s.seat_number"

            cursor.execute(query, params)
            seats = cursor.fetchall()

            self.ui.tablewithallseats.setRowCount(len(seats))
            for row, seat in enumerate(seats):
                seat_id = seat[0]
                seat_number = seat[1]
                price = seat[2]
                status = seat[3]

                self.ui.tablewithallseats.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(str(seat_id))
                )
                self.ui.tablewithallseats.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(seat_number)
                )
                self.ui.tablewithallseats.setItem(
                    row, 2, QtWidgets.QTableWidgetItem(f"£{price:.2f}")
                )
                self.ui.tablewithallseats.setItem(
                    row, 3, QtWidgets.QTableWidgetItem(status)
                )

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to filter seats: {str(e)}"
            )


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
