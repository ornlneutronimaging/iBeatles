from qtpy.QtWidgets import QProgressBar, QVBoxLayout
import pyqtgraph as pg

from src.ibeatles import interact_me_style


class Initialization:
    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.widgets()
        self.pyqtgraph()

    def widgets(self):
        # progress bar
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

        # show what to do next
        self.parent.ui.select_folder_pushButton.setStyleSheet(interact_me_style)

    def pyqtgraph(self):
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.roiBtn.hide()
        self.parent.ui.image_view.ui.menuBtn.hide()

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.widget.setLayout(vertical_layout)
        self.parent.ui.line_view = None
