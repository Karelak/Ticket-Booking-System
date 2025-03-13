import sys
from PyQt5 import QtWidgets
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
        self.ui.tableofresults.setColumnCount(5)
        self.ui.tableofresults.setHorizontalHeaderLabels(
            ["Customer ID", "First Name", "Last Name", "Phone Number", "Type"]
        )

    def filter_by_type(self, customer_type):
        QtWidgets.QMessageBox.information(
            self,
            "Filter Applied",
            f"Filtering by {customer_type} - This will be implemented with database",
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

    def generate_report(self):
        selected_items = self.ui.tableofresults.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please select a booking to generate a report"
            )
            return

        QtWidgets.QMessageBox.information(
            self,
            "Report",
            "Report generation will be implemented with database connection",
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

        self.ui.firstname.textChanged.connect(self.filter_seats)
        self.ui.lastname.textChanged.connect(self.filter_seats)
        self.ui.bookingid.textChanged.connect(self.filter_seats)

    def filter_seats(self):
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
