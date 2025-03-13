"""
Ticket Booking System.

This module implements a theater ticket booking system with interfaces for
managing shows, customers, bookings, and seats. It provides a user interface
to search and manage various aspects of the booking process.
"""

import sys
from PyQt5 import QtWidgets, QtCore
from main_window_ui import Ui_Dialog as MainWindowUI
from seat_manager_ui import Ui_Dialog as SeatManagerUI
from customer_search_ui import Ui_Dialog as CustomerSearchUI
from bookings_ui import Ui_Dialog as BookingsUI


class MainWindow(QtWidgets.QDialog):
    """
    Main window of the ticket booking system.

    This class serves as the entry point of the application and provides
    navigation to other screens like customer search, bookings, and seat manager.

    Attributes:
        ui: The user interface object from the UI file.
        show_id: The ID of the show selected by the user.
    """

    def __init__(self):
        """
        Initialize the main window.

        Sets up the UI and connects button signals to their respective slots.
        """
        super(MainWindow, self).__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)

        # Store the selected show ID
        self.show_id = None

        # Connect buttons to their respective functions
        self.ui.gotocustomers.clicked.connect(self.open_customer_search)
        self.ui.gotobookings.clicked.connect(self.open_bookings)
        self.ui.gotoseats.clicked.connect(self.open_seats)

    def open_customer_search(self):
        """
        Open the customer search window.

        Retrieves the show ID from the UI and opens the customer search screen.
        Validates that a show ID is provided before proceeding.
        """
        # Get the show ID entered by the user
        self.show_id = self.ui.showid.text()
        if not self.show_id:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a Show ID")
            return

        # Open the customer search window
        self.customer_search = CustomerSearch(self.show_id)
        self.hide()
        self.customer_search.exec_()
        self.show()

    def open_bookings(self):
        """
        Open the bookings window.

        Retrieves the show ID from the UI and opens the bookings screen.
        Validates that a show ID is provided before proceeding.
        """
        # Get the show ID entered by the user
        self.show_id = self.ui.showid.text()
        if not self.show_id:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a Show ID")
            return

        # Open the bookings window
        self.bookings = Bookings(self.show_id)
        self.hide()
        self.bookings.exec_()
        self.show()

    def open_seats(self):
        """
        Open the seat manager window.

        Retrieves the show ID from the UI and opens the seat manager screen.
        Validates that a show ID is provided before proceeding.
        """
        # Get the show ID entered by the user
        self.show_id = self.ui.showid.text()
        if not self.show_id:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a Show ID")
            return

        # Open the seats manager window
        self.seats = SeatManager(self.show_id)
        self.hide()
        self.seats.exec_()
        self.show()


class CustomerSearch(QtWidgets.QDialog):
    """
    Customer search screen.

    This class provides functionality to search and filter customers
    based on various criteria related to a specific show.

    Attributes:
        ui: The user interface object from the UI file.
        show_id: The ID of the show the customers are associated with.
    """

    def __init__(self, show_id):
        """
        Initialize the customer search window.

        Args:
            show_id: The ID of the show to search customers for.
        """
        super(CustomerSearch, self).__init__()
        self.ui = CustomerSearchUI()
        self.ui.setupUi(self)
        self.show_id = show_id

        # Set window title to include show ID
        self.setWindowTitle(f"Customer Search - Show ID: {show_id}")

        # Connect the back button
        self.ui.backtomenu.clicked.connect(self.close)

        # Connect filter buttons
        self.ui.childonly.clicked.connect(lambda: self.filter_by_type("Child"))
        self.ui.adultonly.clicked.connect(lambda: self.filter_by_type("Adult"))
        self.ui.senioronly.clicked.connect(lambda: self.filter_by_type("Senior"))

        # Initialize the table
        self.setup_table()

    def setup_table(self):
        """
        Set up the table with proper columns for customer data.

        Initializes the table with appropriate column headers for
        displaying customer information.
        """
        self.ui.tableofresults.setColumnCount(5)
        self.ui.tableofresults.setHorizontalHeaderLabels(
            ["Customer ID", "First Name", "Last Name", "Phone Number", "Type"]
        )

        # TODO: When database is connected, populate table with actual data
        # This would query the database for customers related to the show_id

    def filter_by_type(self, customer_type):
        """
        Filter the customer table by type.

        Args:
            customer_type: The type of customer to filter by (Child, Adult, Senior).
        """
        # TODO: Implement filtering based on customer type
        QtWidgets.QMessageBox.information(
            self,
            "Filter Applied",
            f"Filtering by {customer_type} - This will be implemented with database",
        )


class Bookings(QtWidgets.QDialog):
    """
    Bookings management screen.

    This class provides functionality to search and manage bookings
    associated with a specific show, and generate reports.

    Attributes:
        ui: The user interface object from the UI file.
        show_id: The ID of the show the bookings are associated with.
    """

    def __init__(self, show_id):
        """
        Initialize the bookings window.

        Args:
            show_id: The ID of the show to search bookings for.
        """
        super(Bookings, self).__init__()
        self.ui = BookingsUI()
        self.ui.setupUi(self)
        self.show_id = show_id

        # Set window title to include show ID
        self.setWindowTitle(f"Bookings - Show ID: {show_id}")

        # Connect buttons
        self.ui.backtomenu.clicked.connect(self.close)
        self.ui.reportofselectedresult.clicked.connect(self.generate_report)

        # Initialize the table
        self.setup_table()

    def setup_table(self):
        """
        Set up the table with proper columns for booking data.

        Initializes the table with appropriate column headers for
        displaying booking information.
        """
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

        # TODO: When database is connected, populate table with actual booking data
        # This would query the database for bookings related to the show_id

    def generate_report(self):
        """
        Generate a report for the selected booking.

        Creates a detailed report of the selected booking entry,
        including customer and seat information.

        Raises:
            Warning: If no booking is selected.
        """
        # Get the selected row index
        selected_items = self.ui.tableofresults.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please select a booking to generate a report"
            )
            return

        # TODO: Implement report generation functionality
        QtWidgets.QMessageBox.information(
            self,
            "Report",
            "Report generation will be implemented with database connection",
        )


class SeatManager(QtWidgets.QDialog):
    """
    Seat management screen.

    This class provides functionality to view and manage seats
    associated with a specific show, including filtering by customer details.

    Attributes:
        ui: The user interface object from the UI file.
        show_id: The ID of the show the seats are associated with.
    """

    def __init__(self, show_id):
        """
        Initialize the seat manager window.

        Args:
            show_id: The ID of the show to manage seats for.
        """
        super(SeatManager, self).__init__()
        self.ui = SeatManagerUI()
        self.ui.setupUi(self)
        self.show_id = show_id

        # Set window title and show name label to include show ID
        self.setWindowTitle(f"Seat Manager - Show ID: {show_id}")
        self.ui.label.setText(f"Seat Management for Show ID: {show_id}")

        # Connect buttons
        self.ui.backtomenu.clicked.connect(self.close)

        # Initialize the table
        self.setup_table()

    def setup_table(self):
        """
        Set up the table with proper columns for seat data.

        Initializes the table with appropriate column headers for
        displaying seat information and sets up event connections
        for filtering functionality.
        """
        self.ui.tablewithallseats.setColumnCount(4)
        self.ui.tablewithallseats.setHorizontalHeaderLabels(
            ["Seat ID", "Seat Number", "Price", "Status"]
        )

        # TODO: When database is connected, populate table with actual seat data
        # This would query the database for seats related to the show_id

        # Add functionality to search/filter seats based on input fields
        self.ui.firstname.textChanged.connect(self.filter_seats)
        self.ui.lastname.textChanged.connect(self.filter_seats)
        self.ui.bookingid.textChanged.connect(self.filter_seats)

    def filter_seats(self):
        """
        Filter seat data based on the input fields.

        Filters the seats table based on first name, last name,
        and booking ID inputs. Intended to be implemented when
        connected to a database.
        """
        # TODO: Implement seat filtering based on first name, last name, booking ID
        # This would be implemented when connected to database
        pass


def main():
    """
    Main entry point of the application.

    Initializes the application, creates and shows the main window,
    and starts the event loop.

    Returns:
        The exit code of the application.
    """
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
