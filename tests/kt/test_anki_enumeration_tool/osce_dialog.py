from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPlainTextEdit, QPushButton,
    QAction
)

from aqt.utils import showInfo

from typing import Optional, List

from aifa import AFAAnki

__all__ = [
    "run_anki_enumeration_tool"
]

class OsceDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self._render_window()
        
    def _render_window(self):
        self.setWindowTitle("Test Enumeration Tool")
        self.box_layout = QVBoxLayout()
        self.label_1 = QLabel("Enter lines below, each line goes into {{c1::line}} in a note")
        self.noteseditor = QPlainTextEdit()
        self.box_layout.addWidget(self.label_1)
        self.box_layout.addWidget(self.noteseditor)
        
        self.label_2 = QLabel("Enter name of deck below")
        self.deck_taker = QLineEdit()
        self.box_layout.addWidget(self.label_2)
        self.box_layout.addWidget(self.deck_taker)
        
        self.label_3 = QLabel("Enter name of note type below")
        self.note_taker = QLineEdit()
        self.box_layout.addWidget(self.label_3)
        self.box_layout.addWidget(self.note_taker)
        
        self.label_4 = QLabel("Press button below to make notes")
        self.button = QPushButton("Create notes")
        self.button.clicked.connect(self._make_note_cards)
        self.box_layout.addWidget(self.label_4)
        self.box_layout.addWidget(self.button)
        self.setLayout(self.box_layout)
        
    def _make_note_cards(self):
        notetype = self.note_taker.text()
        deckname = self.deck_taker.text()
        
        model = mw.col.models.by_name(notetype)
        if model is None:
            showInfo(text="Unable to find the specified note type.")
            return
        
        deck_id = mw.col.decks.id(deckname); mw.col.decks.select(deck_id)
        deck = mw.col.decks.get(deck_id)
        
        contents = self._process_text(self.noteseditor.toPlainText())
        
        model['did'] = deck_id; mw.col.models.save(model)   # save the current active deck into database for later synchronization? i think?
        deck['mid'] = model['id']; mw.col.decks.save(deck)  # normally `deck` doesn't have `mid` field, but this add-on insert this field for defaultly creating new note cards
        
        for content in contents:
            new_note_card = mw.col.newNote()    # use deck['mid'] information above
            new_note_card.fields[0] = content
            mw.col.addNote(new_note_card)
            
        showInfo("Cards created successfully!")
        
    def _process_text(self, text: str) -> List[str]:
        contents = []
        lines = text.split('\n')
        prev_text = ""
        for i, line in enumerate(lines):
            curr_text = f"{prev_text}<br>{i + 1}: {{{{c1::{line}}}}}"
            prev_text = f"{prev_text}<br>{i + 1}: {line}"
            contents.append(curr_text)
        return contents
            
    
def run_anki_enumeration_tool(afa: AFAAnki):
    afa.dialog = OsceDialog()
    
    afa.action = QAction()
    afa.action.setText("Test Enumeration Tool")
    afa.action.triggered.connect(afa.dialog.show)
    mw.form.menuTools.addAction(afa.action)