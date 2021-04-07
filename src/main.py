from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QHBoxLayout,
                             QVBoxLayout,
                             QGridLayout,
                             QListWidget,
                             QListWidgetItem,
                             QLabel,
                             QLineEdit,
                             QAbstractItemView,
                             QGraphicsDropShadowEffect,
                             QSpacerItem,
                             QSizePolicy,
                             QFrame)
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize
from pypresence import Presence
import os.path


def get_available_presets():
    '''Return a list of tuple of presets [("title", "index", "absolute/image/path"), ...]'''
    presets = []
    preset_file_path = os.path.join(os.path.dirname(__file__), 'presets.txt')
    with open(preset_file_path, 'r') as presets_file:
        content = presets_file.read()
        for preset in content.splitlines()[1:]:
            if " ;" not in preset:
                continue
            image, id, title = preset.split(" ;")
            image_path = os.path.join(os.path.dirname(__file__), "Images", str(image+".png"))
            presets.append((title, id, image_path))
    return presets


class DCP(QWidget):
    def __init__(self):
        super(DCP, self).__init__()
        self.setWindowTitle("Discord custom presence")
        self.pid = None  # Used for the presence application
        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshPresence)
        self.startPresenceTimer()
        self.rpc = {"state": '',
                    "details": '',
                    "start": 0,
                    "end": 0,
                    "large_image": '',
                    "large_text": '',
                    "small_image": '',
                    "small_text": '',
                    "party_size": [],
                    "buttons": []}

        font_db = QFontDatabase()
        font_db.addApplicationFont(os.path.join(os.path.dirname(__file__),
                                   "Fonts", "Oswald", "Oswald-VariableFont_wght.ttf"))

        self.setStyleSheet("font-family: oswald;")
        self.preset_info = get_available_presets()
        self.create_panel()
        self.create_area()
        self.active = None
        self.selected = None
        global_layout = QHBoxLayout()
        global_layout.setSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.addWidget(self.panel)
        global_layout.addWidget(self.area)
        self.setLayout(global_layout)

    def create_panel(self):
        def over():
            print('test')
            for item in self.presets:
                self.preset_list.itemWidget(item).setStyleSheet("""background: #C4C4C4;
                                                                border: 0px;
                                                                border-radius: 16px;""")
            active_item = self.preset_list.selectedItems()[0]
            active_elt = self.preset_list.itemWidget(active_item)
            active_elt.setStyleSheet("""background: #C4C4C4;
                                    border: 4px solid #797979;
                                    border-radius: 16px;""")

        self.panel = QWidget()
        self.panel.setFixedWidth(320)
        self.panel.setStyleSheet("""background-color: #484848;
                                    border: 0px;
                                    border-radius: 0px;""")
        header = QLabel("Discord custom presence")
        header.setFont(QFont('Oswald', 24))
        header.setFixedHeight(60)
        header.setStyleSheet("color: black;background-color: #C25D5D;")
        header.setAlignment(Qt.AlignCenter)

        search = QWidget()

        preset_list = QListWidget()
        preset_list.setMinimumHeight(200)
        preset_list.setIconSize(QSize(55, 55))
        preset_list.setSpacing(4)
        preset_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        preset_list.setStyleSheet("""QListView::item:focus{border:none;}
                                     QListView::item:over{border:none;}
                                     QListView:over{border:none;}
                                     QListView:focus{border:none;}""")
        self.presets = []
        for preset_info in self.preset_info:
            preset_title = QLabel(preset_info[0])
            preset_title.setStyleSheet("""border: inherited;
                                       border-radius: inherited;
                                       color: #000000;""")
            preset_title.setFont(QFont('Oswald', 24))

            drop_shadow_effect = QGraphicsDropShadowEffect()
            drop_shadow_effect.setBlurRadius(20)
            drop_shadow_effect.setXOffset(1)
            drop_shadow_effect.setYOffset(1)
            drop_shadow_effect.setColor(Qt.black)
            preset = QFrame()
            preset.setGraphicsEffect(drop_shadow_effect)
            layout = QHBoxLayout()
            icon = QLabel()
            icon.setPixmap(QPixmap(preset_info[2]))
            icon.setScaledContents(True)
            icon.setFixedSize(40, 40)
            icon.setStyleSheet("border: inherited;")
            layout.setAlignment(Qt.AlignLeft)
            layout.addWidget(icon)
            layout.addWidget(preset_title)
            preset.setLayout(layout)
            item = QListWidgetItem()
            item.setSizeHint(QSize(55, 55))
            preset.info = preset_info
            preset.rpc = self.rpc.copy()
            preset.rpc['large_image'] = preset.info[2].split("/")[-1].split(".")[0]
            self.presets.append(item)
            preset_list.addItem(item)
            preset_list.setItemWidget(item, preset)
        self.preset_list = preset_list
        self.preset_list.setCurrentRow(0)
        self.preset_list.selected = self.preset_list.itemWidget(self.preset_list.selectedItems()[0])
        self.preset_list.active = self.preset_list.itemWidget(self.preset_list.selectedItems()[0])
        self.preset_list.currentItemChanged.connect(self.change_selected)
        self.preset_list.itemDoubleClicked.connect(self.change_active)
        self.refresh_presets()
        panel_layout = QVBoxLayout()
        panel_layout.setSpacing(0)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(header)
        panel_layout.addWidget(search)
        panel_layout.addWidget(self.preset_list)
        self.panel.setLayout(panel_layout)

    def create_area(self):
        self.area = QWidget()
        self.area.setStyleSheet("QWidget{background-color: #625B5B;margin-left: 4px solid black;}")
        self.area.dynamic_widgets = []

        area_layout = QVBoxLayout()

        prop_layout = QGridLayout()
        def push_prop(text, namecode): self.preset_list.selected.rpc[namecode] = text

        def pull_prop(widget): widget.setText(self.preset_list.selected.rpc[widget.namecode])

        def define_line_edit(namecode, placeholder, x_, y_, span_x=1, span_y=1):
            layout = QHBoxLayout()
            label = QLabel(placeholder)
            label.setFont(QFont('Oswald', 13, QFont.Light))
            label.setStyleSheet("color: black")
            label.setFixedWidth(120)
            label.setAlignment(Qt.AlignRight)
            lineedit = QLineEdit()
            lineedit.setFont(QFont('Oswald', 13, QFont.Light))
            lineedit.setStyleSheet("""border: 2px solid black;
                                       border-radius: 10px;
                                       color: black;""")
            lineedit.setPlaceholderText(placeholder)
            lineedit.textChanged.connect(lambda text, x=namecode: push_prop(text, x))
            lineedit.namecode = namecode
            lineedit.pull = pull_prop
            layout.addWidget(label)
            layout.addWidget(lineedit)
            prop_layout.addLayout(layout, x_, y_, span_x, span_y)
            self.area.dynamic_widgets.append(lineedit)

        define_line_edit('state', "State", 1, 0)
        define_line_edit('details', "Details", 1, 1)
        define_line_edit('large_text', "Large image text", 2, 0)
        define_line_edit('large_image', "Large image image", 3, 0)
        define_line_edit('small_text', "Small image text", 2, 1)
        define_line_edit('small_image', "Small image name", 3, 1)

        header = QFrame()
        drop_shadow_effect = QGraphicsDropShadowEffect()
        drop_shadow_effect.setBlurRadius(20)
        drop_shadow_effect.setXOffset(1)
        drop_shadow_effect.setYOffset(1)
        drop_shadow_effect.setColor(Qt.black)
        header.setGraphicsEffect(drop_shadow_effect)
        header.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        header.setStyleSheet("""background: #C4C4C4;
                                border: 4px solid #797979;
                                border-radius: 60px;""")
        header_layout = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QPixmap(self.preset_list.selected.info[2]))
        icon.setScaledContents(True)
        icon.setFixedSize(100, 100)
        icon.setStyleSheet("border: inherited;background: transparent;")
        def pull_image(widget): widget.setPixmap(QPixmap(self.preset_list.selected.info[2]))
        icon.pull = pull_image
        self.area.dynamic_widgets.append(icon)
        header_layout.addWidget(icon)

        title = QLabel(self.preset_list.selected.info[0])
        title.setFont(QFont('Oswald', 32))
        title.setStyleSheet("border: inherited;background: transparent;padding-right: 30px;")
        def pull_text(widget): widget.setText(self.preset_list.selected.info[0])
        title.pull = pull_text
        self.area.dynamic_widgets.append(title)
        header_layout.addWidget(title)
        header.setLayout(header_layout)
        spacer = QSpacerItem(10000, 10000, QSizePolicy.Expanding, QSizePolicy.Expanding)
        area_layout.addWidget(header)
        area_layout.addLayout(prop_layout)
        area_layout.addItem(spacer)

        self.area.setLayout(area_layout)

    def startPresenceTimer(self):
        self.timer.start(15 * 1000)  # Can only update presence every 15 seconds

    def endPresenceTimer(self):
        self.timer.stop()

    def refreshPresence(self):
        if self.pid != self.preset_list.active.info[1]:
            if hasattr(self, "RPC"):
                self.RPC.close()
            self.pid = self.preset_list.active.info[1]
            self.RPC = Presence(self.pid)
            self.RPC.connect()
        real_rpc = {}
        for prop in self.preset_list.active.rpc.keys():
            if self.preset_list.active.rpc[prop] not in [0, "", []]:
                real_rpc[prop] = self.preset_list.active.rpc[prop]
            else:
                real_rpc[prop] = None
        print(real_rpc)
        self.RPC.update(state=real_rpc["state"],
                        details=real_rpc['details'],
                        start=real_rpc["start"],
                        end=real_rpc["end"],
                        large_image=real_rpc["large_image"],
                        large_text=real_rpc["large_text"],
                        small_image=real_rpc["small_image"],
                        small_text=real_rpc["small_text"],
                        party_size=real_rpc["party_size"],
                        buttons=real_rpc["buttons"])

    def change_active(self, item):
        self.preset_list.active = self.preset_list.itemWidget(item)
        self.refresh_presets()

    def change_selected(self, item):
        self.preset_list.selected = self.preset_list.itemWidget(item)
        self.refresh_presets()
        self.refresh_area()

    def refresh_presets(self):
        for item in self.presets:
            self.preset_list.itemWidget(item).setStyleSheet("""background: #C4C4C4;
                                                            border: 4px solid #C4C4C4;
                                                            border-radius: 20px;""")
        self.preset_list.selected.setStyleSheet("""background: #C4C4C4;
                                 border: 4px solid #4962D9;
                                 border-radius: 20px;""")
        self.preset_list.active.setStyleSheet("""background: #C4C4C4;
                                 border: 4px solid #1FEB4C;
                                 border-radius: 20px;""")

    def refresh_area(self):
        for widget in self.area.dynamic_widgets:
            widget.pull(widget)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dcp = DCP()
    dcp.show()
    sys.exit(app.exec_())
