import sys
import os
sys.path.append(os.path.dirname(__file__))

from aifa import AFAAnki, AFAServer

anki = AFAServer()
anki.run()