from typing import Optional, List

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPlainTextEdit, QPushButton,
    QAction
)
from aqt.utils import showInfo

from aifa import AFAAnki
from src.anki.core.assistant import Engine, AsyncAPIEngine
from src.settings import settings

__all__ = [
    "run_anki_assistant_tool"
]

class Dialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self._render_window()
        self._build_engine()
    
    def _build_engine(self):
        self.engine = Engine(settings.LAZY_LOADING)
        
    def _render_window(self):
        self.setWindowTitle("Test Enumeration Tool")
        self.box_layout = QVBoxLayout()
        self.label_1 = QLabel("Enter question")
        self.noteseditor = QPlainTextEdit()
        self.box_layout.addWidget(self.label_1)
        self.box_layout.addWidget(self.noteseditor)
        
        self.label_2 = QLabel("Press button below to answer the question")
        self.button = QPushButton("Create notes")
        self.button.clicked.connect(self._generate_answer)
        self.box_layout.addWidget(self.label_2)
        self.box_layout.addWidget(self.button)
        self.setLayout(self.box_layout)
        
    def _generate_answer(self): 
        showInfo(f"{self.engine.answer(self.noteseditor.toPlainText())}")
    
def run_anki_assistant_tool(afa: AFAAnki):
    afa.dialog = Dialog()
    
    afa.action = QAction()
    afa.action.setText("Test Assistant Tool")
    afa.action.triggered.connect(afa.dialog.show)
    mw.form.menuTools.addAction(afa.action)