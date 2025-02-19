from typing import Optional, List

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPlainTextEdit, QPushButton,
    QAction, QTextEdit
)
from aqt.utils import showInfo

from aifa import AFAAnki
from src.anki.core.assistant import Engine, AsyncAPIEngine
from src.settings import settings

__all__ = [
    "run_anki_assistant_tool"
]

class SimpleDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self._render_window()
        self._build_engine()
    
    def _build_engine(self):
        self.engine = AsyncAPIEngine()
        
    def _render_window(self):
        self.setWindowTitle("Test Anki Assistant Tool")
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
        
        # Read-only box for displaying answer
        self.label_3 = QLabel("Generated Answer:")
        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True)  # Set the QTextEdit to read-only
        self.box_layout.addWidget(self.label_3)
        self.box_layout.addWidget(self.answer_display)
                
        self.setLayout(self.box_layout)
        
    def _generate_answer(self):
        question = self.noteseditor.toPlainText()
        if not question.strip():
            showInfo("Please enter a question before generating an answer.")
            return
        
        answer = self.engine.answer(question)
        self.answer_display.setText(answer)  # Display the answer in the read-only box
    
def run_anki_assistant_tool(afa: AFAAnki):
    afa.dialog = SimpleDialog()
    
    afa.action = QAction()
    afa.action.setText("Test Assistant Tool")
    afa.action.triggered.connect(afa.dialog.show)
    mw.form.menuTools.addAction(afa.action)