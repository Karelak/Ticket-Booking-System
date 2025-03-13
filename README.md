# Ticket Booking System

## Overview
The Ticket Booking System is a PyQt5-based desktop application designed to manage theater ticket bookings. This system allows users to search customers, manage bookings, and track seat allocations for different shows.

## Features
- Show-based ticket management
- Customer search and filtering by type (Child, Adult, Senior)
- Booking management with report generation
- Interactive seat management interface
- User-friendly PyQt5 GUI

## Project Structure
```
ticket-booking-system/
│
├── ui_design_files/      # Qt Designer UI files
│   ├── bookings.ui
│   ├── customer-search.ui
│   ├── main-window.ui
│   └── seat-manager.ui
│
├── ui_files/             # Generated Python UI code
│   ├── bookings_ui.py
│   ├── customer_search_ui.py
│   ├── main_window_ui.py
│   └── seat_manager_ui.py
│
├── main.py               # Main application entry point
└── README.md             # This file
```

## Requirements
- Python 3.6+
- PyQt5
- (Database dependencies to be implemented)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ticket-booking-system.git
   cd ticket-booking-system
   ```

2. Install the required packages:
   ```
   pip install PyQt5
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

1. Start the application and enter a Show ID in the main window.
2. Navigate to different modules:
   - **Customer Search**: Search and filter customers by name, ID, phone number, or type
   - **Bookings**: Manage bookings and generate booking reports
   - **Seat Manager**: View and manage seats, filter by customer details

## UI Components

### Main Window
The central hub that allows navigation to other screens. Requires a Show ID input to proceed.

### Customer Search
Search customers by:
- First Name
- Last Name
- Customer ID
- Phone Number
- Customer Type (Child, Adult, Senior)

### Bookings Manager
Manage bookings with functionality for:
- Searching bookings by customer details
- Filtering by booking date
- Generating detailed booking reports

### Seat Manager
Visualize and manage seats with:
- Seat status display
- Filtering by customer information
- Booking ID lookup

## Future Improvements
- Database integration
- Report generation and export
- Payment processing
- Email confirmations
- Advanced seat selection interface
- Show management interface
- Analytics dashboard

## Development Notes
This project is structured with UI files created in Qt Designer, which are then converted to Python code using PyQt5's pyuic5 tool. The main application logic connects these UI components together.

To modify UI files:
1. Edit .ui files in Qt Designer
2. Convert to Python with:
   ```
   pyuic5 -o ui_files/file_name_ui.py ui_design_files/file_name.ui
   ```