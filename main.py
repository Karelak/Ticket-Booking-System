import sys
import sqlite3
import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from ui_files.main_window_ui import Ui_Dialog as MainWindowUI
from ui_files.seat_manager_ui import Ui_Dialog as SeatManagerUI
from ui_files.customer_search_ui import Ui_Dialog as CustomerSearchUI
from ui_files.bookings_ui import Ui_Dialog as BookingsUI


class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)
        self.ui.gotocustomers.clicked.connect(self.open_customer_search)
        self.ui.gotobookings.clicked.connect(self.open_bookings)
        self.ui.gotoseats.clicked.connect(self.open_seats)

    def open_customer_search(self):
        self.customer_search = CustomerSearch()
        self.hide()
        self.customer_search.exec_()
        self.show()

    def open_bookings(self):
        self.bookings = Bookings()
        self.hide()
        self.bookings.exec_()
        self.show()

    def open_seats(self):
        self.seats = SeatManager()
        self.hide()
        self.seats.exec_()
        self.show()


class CustomerSearch(QtWidgets.QDialog):
    def __init__(self):
        super(CustomerSearch, self).__init__()
        self.ui = CustomerSearchUI()
        self.ui.setupUi(self)

        self.setWindowTitle("Customer Search")

        self.ui.backtomenu.clicked.connect(self.close)

        self.ui.childonly.clicked.connect(lambda: self.filter_by_type("Child"))
        self.ui.adultonly.clicked.connect(lambda: self.filter_by_type("Adult"))
        self.ui.senioronly.clicked.connect(lambda: self.filter_by_type("Senior"))
        self.ui.viponly.clicked.connect(lambda: self.filter_by_type("VIP"))

        self.ui.firstname.textChanged.connect(self.search_customers)
        self.ui.lastname.textChanged.connect(self.search_customers)
        self.ui.customerID.textChanged.connect(self.search_customers)
        self.ui.phonenumber.textChanged.connect(self.search_customers)

        self.setup_table()
        self.load_all_customers()

    def setup_table(self):
        self.ui.tableofresults.setColumnCount(4)
        self.ui.tableofresults.setHorizontalHeaderLabels(
            ["Customer ID", "Name", "Phone", "Type"]
        )

    def load_all_customers(self):
        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            cursor.execute("SELECT customers_id, name, phone, type FROM customers")

            customers = cursor.fetchall()
            self.populate_table(customers)

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to load customers: {str(e)}"
            )

    def search_customers(self):
        first_name = self.ui.firstname.text().strip()
        last_name = self.ui.lastname.text().strip()
        customer_id = self.ui.customerID.text().strip()
        phone = self.ui.phonenumber.text().strip()

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            query = "SELECT customers_id, name, phone, type FROM customers WHERE 1=1"
            params = []

            if customer_id:
                query += " AND customers_id = ?"
                params.append(customer_id)

            if first_name or last_name:
                name_filter = ""
                if first_name and last_name:
                    name_filter = f"{first_name} {last_name}"
                elif first_name:
                    name_filter = first_name
                else:
                    name_filter = last_name

                query += " AND name LIKE ?"
                params.append(f"%{name_filter}%")

            if phone:
                query += " AND phone LIKE ?"
                params.append(f"%{phone}%")

            cursor.execute(query, params)
            customers = cursor.fetchall()
            self.populate_table(customers)

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to search customers: {str(e)}"
            )

    def filter_by_type(self, customer_type):
        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT customers_id, name, phone, type FROM customers WHERE type = ?",
                (customer_type,),
            )

            customers = cursor.fetchall()
            self.populate_table(customers)

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to filter customers: {str(e)}"
            )

    def populate_table(self, customers):
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
            self.ui.tableofresults.setItem(
                row, 3, QtWidgets.QTableWidgetItem(customer[3])
            )


class Bookings(QtWidgets.QDialog):
    def __init__(self):
        super(Bookings, self).__init__()
        self.ui = BookingsUI()
        self.ui.setupUi(self)

        self.setWindowTitle("Bookings Search")

        self.ui.backtomenu.clicked.connect(self.close)
        self.ui.reportofselectedresult.clicked.connect(self.generate_report)

        self.setup_show_selection()

        self.ui.firstname.textChanged.connect(self.search_bookings)
        self.ui.lastname.textChanged.connect(self.search_bookings)
        self.ui.bookingid.textChanged.connect(self.search_bookings)
        self.ui.bookingdate.dateChanged.connect(self.search_bookings)

        self.setup_table()
        self.load_all_bookings()

    def setup_show_selection(self):
        self.show_label = QtWidgets.QLabel("Show:")
        self.show_combo = QtWidgets.QComboBox()
        self.show_combo.setMinimumHeight(25)

        self.show_combo.addItem("All Shows", -1)

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT shows_id, title, date FROM shows ORDER BY date DESC")
            shows = cursor.fetchall()

            for show in shows:
                show_id = show[0]
                title = show[1]
                date = show[2]
                try:
                    if isinstance(date, str):
                        date_part = date.split()[0]
                    else:
                        date_part = str(date).split()[0]
                    self.show_combo.addItem(f"{title} ({date_part})", show_id)
                except:
                    self.show_combo.addItem(f"{title}", show_id)

            conn.close()
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to load shows: {str(e)}"
            )

        self.show_layout = QtWidgets.QHBoxLayout()
        self.show_layout.addWidget(self.show_label)
        self.show_layout.addWidget(self.show_combo)

        self.ui.verticalLayout.insertLayout(0, self.show_layout)

        self.show_combo.currentIndexChanged.connect(self.search_bookings)

    def setup_table(self):
        self.ui.tableofresults.setColumnCount(6)
        self.ui.tableofresults.setHorizontalHeaderLabels(
            [
                "Booking ID",
                "Customer Name",
                "Show Title",
                "Booking Date",
                "Total Price",
                "Seats",
            ]
        )
        self.ui.tableofresults.setColumnWidth(0, 80)
        self.ui.tableofresults.setColumnWidth(1, 150)
        self.ui.tableofresults.setColumnWidth(2, 150)
        self.ui.tableofresults.setColumnWidth(3, 100)
        self.ui.tableofresults.setColumnWidth(4, 100)
        self.ui.tableofresults.setColumnWidth(5, 100)

    def load_all_bookings(self):
        try:
            conn = sqlite3.connect("system.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
            SELECT 
                b.bookings_id, 
                c.name, 
                c.type, 
                s.title, 
                b.booking_date, 
                b.total_price,
                b.show_id
            FROM 
                bookings b
            JOIN 
                customers c ON b.customer_id = c.customers_id
            JOIN 
                shows s ON b.show_id = s.shows_id
            ORDER BY 
                b.booking_date DESC
            """

            cursor.execute(query)
            bookings = cursor.fetchall()

            result_data = []

            for booking in bookings:
                booking_id = booking["bookings_id"]
                cursor.execute(
                    "SELECT COUNT(*) FROM seats WHERE booking_id = ?", (booking_id,)
                )
                seat_count = cursor.fetchone()[0]

                result_data.append(
                    (
                        booking["bookings_id"],
                        booking["name"],
                        booking["type"],
                        booking["title"],
                        booking["booking_date"],
                        booking["total_price"],
                        seat_count,
                    )
                )

            if result_data:
                self.populate_table(result_data)
            else:
                self.show_no_results()

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to load bookings: {str(e)}"
            )
            print(f"Database error in load_all_bookings: {str(e)}")

    def search_bookings(self):
        first_name = self.ui.firstname.text().strip()
        last_name = self.ui.lastname.text().strip()
        booking_id = self.ui.bookingid.text().strip()

        use_date_filter = (
            self.ui.bookingdate.date() != self.ui.bookingdate.minimumDate()
        )
        if use_date_filter:
            booking_date = self.ui.bookingdate.date().toString("dd-MM-yyyy")
        else:
            booking_date = None

        selected_show = self.show_combo.currentData()

        try:
            conn = sqlite3.connect("system.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
            SELECT 
                b.bookings_id, 
                c.name, 
                c.type, 
                s.title, 
                b.booking_date, 
                b.total_price,
                b.show_id
            FROM 
                bookings b
            JOIN 
                customers c ON b.customer_id = c.customers_id
            JOIN 
                shows s ON b.show_id = s.shows_id
            WHERE 1=1
            """

            params = []

            if booking_id:
                query += " AND b.bookings_id = ?"
                params.append(booking_id)

            if first_name or last_name:
                name_filter = ""
                if first_name and last_name:
                    name_filter = f"{first_name} {last_name}"
                elif first_name:
                    name_filter = first_name
                else:
                    name_filter = last_name

                query += " AND c.name LIKE ?"
                params.append(f"%{name_filter}%")

            if use_date_filter:
                query += " AND date(b.booking_date) = date(?)"
                params.append(booking_date)

            if selected_show is not None and selected_show != -1:
                query += " AND b.show_id = ?"
                params.append(selected_show)

            query += " ORDER BY b.booking_date DESC"

            cursor.execute(query, params)
            bookings = cursor.fetchall()

            result_data = []

            for booking in bookings:
                booking_id = booking["bookings_id"]
                cursor.execute(
                    "SELECT COUNT(*) FROM seats WHERE booking_id = ?", (booking_id,)
                )
                seat_count = cursor.fetchone()[0]

                result_data.append(
                    (
                        booking["bookings_id"],
                        booking["name"],
                        booking["type"],
                        booking["title"],
                        booking["booking_date"],
                        booking["total_price"],
                        seat_count,
                    )
                )

            if result_data:
                self.populate_table(result_data)
            else:
                self.show_no_results()

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to search bookings: {str(e)}"
            )
            print(f"Database error in search_bookings: {str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"An unexpected error occurred: {str(e)}"
            )
            print(f"Unexpected error in search_bookings: {str(e)}")

    def show_no_results(self):
        self.ui.tableofresults.setRowCount(1)
        no_results_item = QtWidgets.QTableWidgetItem(
            "No bookings found for the selected criteria"
        )
        no_results_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui.tableofresults.setSpan(0, 0, 1, 6)
        self.ui.tableofresults.setItem(0, 0, no_results_item)

        self.ui.tableofresults.item(0, 0).setTextAlignment(QtCore.Qt.AlignCenter)

    def populate_table(self, bookings):
        self.ui.tableofresults.clearSpans()

        self.ui.tableofresults.setRowCount(len(bookings))
        for row, booking in enumerate(bookings):
            booking_id = booking[0]
            customer_name = booking[1]
            customer_type = booking[2]
            show_title = booking[3]

            booking_date = booking[4]
            try:
                if isinstance(booking_date, str) and "T" in booking_date:
                    parsed_date = datetime.datetime.fromisoformat(
                        booking_date.replace("Z", "+00:00")
                    )
                    formatted_date = parsed_date.strftime("%d/%m/%Y")
                elif isinstance(booking_date, datetime.datetime):
                    formatted_date = booking_date.strftime("%d/%m/%Y")
                else:
                    parsed_date = datetime.datetime.strptime(
                        str(booking_date), "%Y-%m-%d %H:%M:%S"
                    )
                    formatted_date = parsed_date.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                formatted_date = str(booking_date).split()[0]

            total_price = booking[5]
            seat_count = booking[6]

            self.ui.tableofresults.setItem(
                row, 0, QtWidgets.QTableWidgetItem(str(booking_id))
            )
            self.ui.tableofresults.setItem(
                row, 1, QtWidgets.QTableWidgetItem(f"{customer_name} ({customer_type})")
            )
            self.ui.tableofresults.setItem(
                row, 2, QtWidgets.QTableWidgetItem(show_title)
            )
            self.ui.tableofresults.setItem(
                row, 3, QtWidgets.QTableWidgetItem(formatted_date)
            )
            self.ui.tableofresults.setItem(
                row, 4, QtWidgets.QTableWidgetItem(f"£{total_price:.2f}")
            )
            self.ui.tableofresults.setItem(
                row, 5, QtWidgets.QTableWidgetItem(f"{seat_count} seats")
            )

    def generate_report(self):
        selected_items = self.ui.tableofresults.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please select a booking to generate a report"
            )
            return

        row = selected_items[0].row()
        booking_id = self.ui.tableofresults.item(row, 0).text()

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

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
                booking_date = booking[8]
                show_date = booking[7]

                try:
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
                    formatted_booking_date = str(booking_date).split()[0]
                    formatted_show_date = str(show_date).split()[0]

                customer_type = booking[3]
                if customer_type == "VIP":
                    price_explanation = "VIP (Free admission)"
                elif customer_type in ["Child", "Senior"]:
                    price_explanation = f"{customer_type} (£5.00 - discounted rate)"
                else:
                    price_explanation = f"{customer_type} (£10.00 - standard rate)"

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
    def __init__(self):
        super(SeatManager, self).__init__()
        self.ui = SeatManagerUI()
        self.ui.setupUi(self)

        self.setWindowTitle("Seat Manager")
        self.ui.label.setText("Seat Management")

        self.ui.backtomenu.clicked.connect(self.close)

        self.setup_show_selection()

        self.ui.firstname.textChanged.connect(self.filter_seats)
        self.ui.lastname.textChanged.connect(self.filter_seats)
        self.ui.bookingid.textChanged.connect(self.filter_seats)

        self.setup_table()

    def setup_show_selection(self):
        self.show_label = QtWidgets.QLabel("Select Show:")
        self.show_label.setFont(QtGui.QFont("", 12))
        self.show_combo = QtWidgets.QComboBox()
        self.show_combo.setMinimumHeight(30)

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT shows_id, title, date, venue FROM shows ORDER BY date DESC"
            )
            shows = cursor.fetchall()

            for show in shows:
                show_id = show[0]
                title = show[1]
                date = show[2]
                venue = show[3]
                try:
                    if isinstance(date, str):
                        date_part = date.split()[0]
                    else:
                        date_part = str(date).split()[0]
                    self.show_combo.addItem(
                        f"{title} at {venue} ({date_part})", show_id
                    )
                except:
                    self.show_combo.addItem(f"{title} at {venue}", show_id)

            conn.close()
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to load shows: {str(e)}"
            )

        self.show_layout = QtWidgets.QHBoxLayout()
        self.show_layout.addWidget(self.show_label)
        self.show_layout.addWidget(self.show_combo)

        self.ui.verticalLayout_2.insertLayout(0, self.show_layout)

        self.show_combo.currentIndexChanged.connect(self.load_seats_for_show)

    def setup_table(self):
        self.ui.tablewithallseats.setColumnCount(5)
        self.ui.tablewithallseats.setHorizontalHeaderLabels(
            ["Seat ID", "Seat Number", "Price", "Status", "Customer"]
        )

        if self.show_combo.count() > 0:
            self.load_seats_for_show()
        else:
            self.ui.tablewithallseats.setRowCount(1)
            self.ui.tablewithallseats.setItem(
                0, 0, QtWidgets.QTableWidgetItem("No shows available")
            )

    def load_seats_for_show(self):
        selected_show = self.show_combo.currentData()
        if selected_show is None:
            return

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT s.seats_id, s.seat_number, s.price, s.status, c.name
                FROM seats s
                JOIN bookings b ON s.booking_id = b.bookings_id
                JOIN customers c ON b.customer_id = c.customers_id
                WHERE b.show_id = ?
                ORDER BY s.seat_number
                """,
                (selected_show,),
            )

            seats = cursor.fetchall()

            self.ui.tablewithallseats.setRowCount(len(seats))
            for row, seat in enumerate(seats):
                seat_id = seat[0]
                seat_number = seat[1]
                price = seat[2]
                status = seat[3]
                customer = seat[4]

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
                self.ui.tablewithallseats.setItem(
                    row, 4, QtWidgets.QTableWidgetItem(customer)
                )

            show_text = self.show_combo.currentText()
            self.ui.label.setText(f"Seat Management for {show_text}")

            conn.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", f"Failed to load seats: {str(e)}"
            )

    def filter_seats(self):
        selected_show = self.show_combo.currentData()
        if selected_show is None:
            return

        first_name = self.ui.firstname.text().strip()
        last_name = self.ui.lastname.text().strip()
        booking_id = self.ui.bookingid.text().strip()

        try:
            conn = sqlite3.connect("system.db")
            cursor = conn.cursor()

            query = """
                SELECT s.seats_id, s.seat_number, s.price, s.status, c.name
                FROM seats s
                JOIN bookings b ON s.booking_id = b.bookings_id
                JOIN customers c ON b.customer_id = c.customers_id
                WHERE b.show_id = ?
            """

            params = [selected_show]

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
                customer = seat[4]

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
                self.ui.tablewithallseats.setItem(
                    row, 4, QtWidgets.QTableWidgetItem(customer)
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
