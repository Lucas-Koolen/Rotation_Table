import sys
import os
from PyQt5.QtWidgets import QApplication

# Ensure the repository root is on the Python path when executing this
# script directly (e.g. ``python main/main.py``).  This allows imports of
# top-level packages such as ``ui`` to succeed regardless of the current
# working directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.dashboard import LiveFeedDashboard

def main():
    app = QApplication(sys.argv)
    dashboard = LiveFeedDashboard()
    dashboard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
