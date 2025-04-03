import sys
from PyQt5 import QtWidgets
from ui_files.main_window_ui import Ui_Dialog as MainWindowUI
from ui_files.customer_search_ui import Ui_Dialog as CustomerSearchUI
from ui_files.bookings_ui import Ui_Dialog as BookingsUI
from ui_files.seat_manager_ui import Ui_Dialog as SeatManagerUI


class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Ticket Booking System")
        self.setup_connections()

    def setup_connections(self):
        # Connect buttons to their respective functions
        self.ui.gotocustomers.clicked.connect(self.open_customer_search)
        self.ui.gotobookings.clicked.connect(self.open_bookings)
        self.ui.gotoseats.clicked.connect(self.open_seat_manager)

    def open_customer_search(self):
        self.customer_search = CustomerSearch(self)
        self.hide()
        self.customer_search.show()

    def open_bookings(self):
        self.bookings = Bookings(self)
        self.hide()
        self.bookings.show()

    def open_seat_manager(self):
        self.seat_manager = SeatManager(self)
        self.hide()
        self.seat_manager.show()


class CustomerSearch(QtWidgets.QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.ui = CustomerSearchUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Customer Search")
        self.main_window = main_window
        self.ui.backtomenu.clicked.connect(self.back_to_menu)

    def back_to_menu(self):
        self.close()
        self.main_window.show()


class Bookings(QtWidgets.QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.ui = BookingsUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Bookings")
        self.main_window = main_window
        self.ui.backtomenu.clicked.connect(self.back_to_menu)

    def back_to_menu(self):
        self.close()
        self.main_window.show()


class SeatManager(QtWidgets.QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.ui = SeatManagerUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Seat Manager")
        self.main_window = main_window
        self.ui.backtomenu.clicked.connect(self.back_to_menu)

    def back_to_menu(self):
        self.close()
        self.main_window.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
