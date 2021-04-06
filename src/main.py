from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QHBoxLayout,
                             QVBoxLayout,
                             QLabel,
                             QLineEdit,
                             QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from presence import get_available_presets
from pypresence import Presence


class DCP(QWidget):
    def __init__(self):
        self.RPC = Presence("829001265307582524")
        self.RPC.connect()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshPresence)
        self.startPresenceTimer()
        self.title = "This is a test"

        super(DCP, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.create_panel()
        self.create_area()

        global_layout = QHBoxLayout()
        global_layout.setSpacing(0)
        global_layout.addWidget(self.panel)
        global_layout.addWidget(self.area)
        self.setLayout(global_layout)

    def create_panel(self):
        self.panel = QWidget()
        self.panel.setStyleSheet("background-color: #484848;")
        self.panel.setMinimumWidth(200)
        self.panel.setMaximumWidth(300)
        header = QLabel("Discord custom presence")
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #C25D5D;")
        header.setAlignment(Qt.AlignCenter)

        search = QWidget()

        preset_list = QVBoxLayout()

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(header)
        panel_layout.addWidget(search)
        panel_layout.addLayout(preset_list)
        self.panel.setLayout(panel_layout)

    def create_area(self):
        self.area = QWidget()
        self.area.setStyleSheet("background-color: #625B5B;")

        title = QLineEdit()
        title.textChanged.connect(self.test)
        
        description = QWidget()

        area_layout = QGridLayout()
        area_layout.setContentsMargins(0, 0, 0, 0)
        area_layout.addWidget(title, 0, 0)
        area_layout.addWidget(description, 1, 1)
        self.area.setLayout(area_layout)

    def startPresenceTimer(self):
        self.timer.start(15000)

    def endPresenceTimer(self):
        self.timer.stop()

    def refreshPresence(self):
        self.RPC.update(details=self.title)

    def test(self, title):
        self.title = title
        print(title)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dcp = DCP()
    dcp.show()
    sys.exit(app.exec_())
