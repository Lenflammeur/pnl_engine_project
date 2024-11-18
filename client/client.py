import sys
import requests
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QWidget, QMenuBar, QAction, QFileDialog, QPushButton
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

API_BASE_URL = "http://127.0.0.1:8000/pnl"  # Backend URL


class PnLClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PnL Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        # Default portfolio name
        self.portfolio_name = "Portfolio1"

        # Initialize variables for graph
        self.time_data = []
        self.total_pnl_values = []
        self.current_time = 0  # Incremental time for x-axis

        # Set up main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Menu bar
        self.setup_menu_bar()

        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Overview Tab
        self.overview_tab = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.overview_tab, "Overview")

        # Graph Tab
        self.graph_tab = QWidget()
        self.setup_graph_tab()
        self.tabs.addTab(self.graph_tab, "PnL Graph")

        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_pnl)
        self.timer.start(2000)  # Fetch every 2 seconds

    def setup_menu_bar(self):
        """
        Set up the menu bar with File and Settings options.
        """
        menu_bar = QMenuBar(self)

        # File menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menu_bar.addMenu("Settings")
        change_portfolio_action = QAction("Change Portfolio", self)
        change_portfolio_action.triggered.connect(self.change_portfolio)
        settings_menu.addAction(change_portfolio_action)

        self.setMenuBar(menu_bar)

    def setup_overview_tab(self):
        """
        Set up the real-time PnL overview tab.
        """
        layout = QVBoxLayout()
        self.overview_tab.setLayout(layout)

        self.incoming_pnl_label = QLabel("Incoming PnL: -")
        self.incoming_pnl_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.incoming_pnl_label)

        self.trading_pnl_label = QLabel("Trading PnL: -")
        self.trading_pnl_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.trading_pnl_label)

        self.trading_realized_label = QLabel("Trading Realized: -")
        self.trading_realized_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.trading_realized_label)

        self.trading_unrealized_label = QLabel("Trading Unrealized: -")
        self.trading_unrealized_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.trading_unrealized_label)

        self.total_pnl_label = QLabel("Total PnL: -")
        self.total_pnl_label.setFont(QFont("Arial", 16))
        self.total_pnl_label.setStyleSheet("color: blue;")
        layout.addWidget(self.total_pnl_label)

    def setup_graph_tab(self):
        """
        Set up the PnL graph tab.
        """
        layout = QVBoxLayout()
        self.graph_tab.setLayout(layout)

        self.graph_widget = pg.PlotWidget(title="Real-Time PnL")
        self.graph_widget.setBackground("w")  # White background
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setLabel("left", "PnL", units="$")
        self.graph_widget.setLabel("bottom", "Time", units="s")
        layout.addWidget(self.graph_widget)

    def fetch_pnl(self):
        """
        Fetch the latest PnL from the server and update the UI.
        """
        try:
            response = requests.get(f"{API_BASE_URL}/{self.portfolio_name}")  # Correct endpoint
            response.raise_for_status()
            pnl_data = response.json()

            # Extract PnL components
            incoming_pnl = pnl_data.get("incoming_pnl", 0.0)
            trading_pnl = pnl_data.get("trading_pnl", 0.0)
            trading_realized = pnl_data.get("trading_realized", 0.0)
            trading_unrealized = pnl_data.get("trading_unrealized", 0.0)
            total_pnl = pnl_data.get("total_pnl", 0.0)

            # Update labels
            self.incoming_pnl_label.setText(f"Incoming PnL: {incoming_pnl:.2f}")
            self.trading_pnl_label.setText(f"Trading PnL: {trading_pnl:.2f}")
            self.trading_realized_label.setText(f"Trading Realized: {trading_realized:.2f}")
            self.trading_unrealized_label.setText(f"Trading Unrealized: {trading_unrealized:.2f}")
            self.total_pnl_label.setText(f"Total PnL: {total_pnl:.2f}")

            # Update graph data
            self.total_pnl_values.append(total_pnl)
            self.time_data.append(self.current_time)
            self.current_time += 2  # Increment time by 2 seconds

            # Update the graph
            self.update_graph()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PnL: {e}")

    def update_graph(self):
        """
        Update the real-time PnL graph.
        """
        self.graph_widget.clear()
        self.graph_widget.plot(
            self.time_data, self.total_pnl_values, pen=pg.mkPen(color="b", width=2)
        )

    def change_portfolio(self):
        """
        Change the portfolio being tracked.
        """
        portfolio_name, _ = QFileDialog.getOpenFileName(
            self, "Select Portfolio File", "", "JSON Files (*.json)"
        )
        if portfolio_name:
            # Extract portfolio name from file (simulate)
            self.portfolio_name = portfolio_name.split("/")[-1].replace(".json", "")
            print(f"Changed portfolio to {self.portfolio_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = PnLClient()
    client.show()

    # Apply custom stylesheet
    with open("styles.qss", "r") as file:
        app.setStyleSheet(file.read())

    sys.exit(app.exec_())
