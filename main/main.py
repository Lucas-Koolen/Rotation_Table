from PyQt5.QtWidgets import QApplication
from ui.dashboard import Dashboard
from logic.autonomous_flow import run_cycle
import sys

def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.start_callback = lambda: run_cycle(dashboard.update_dashboard)
    dashboard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
