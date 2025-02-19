from abc import abstractmethod

import argparse

class AIForAnki(object):
    @abstractmethod
    def run(self):
        raise NotImplementedError

class AFAServer(AIForAnki):
    def _run_app_main(self):
        import uvicorn
        from src.settings import settings
        
        uvicorn.run(
            "src.app.runner:main_app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            workers=settings.WORKERS,
            log_level="info"
        )
        
    def run(self):
        import multiprocessing as mp
        
        main_process = mp.Process(target=self._run_app_main)
        main_process.start()
        main_process.join()
        
class AFAAnki(AIForAnki):
    def _test_anki_enumeration_tool(self):
        from tests.kt.test_anki_enumeration_tool import osce_dialog
        osce_dialog.run_anki_enumeration_tool(self)
    
    def _run_anki_assistant_tool(self):
        from tests.kt.test_anki_assistant_tool import dialog
        dialog.run_anki_assistant_tool(self)
    
    def run(self):
        self._run_anki_assistant_tool()
    
def parse_args():
    parser = argparse.ArgumentParser("AI For Anki")
    parser.add_argument('-m', "--mode", type=str, default="app", choices=["app", "anki"])
    return parser.parse_args()
        
if __name__ == "__main__":
    args = parse_args()
    if args.mode == "app":
        server = AFAServer()
        server.run()
        
    elif args.mode == "anki":
        anki = AFAAnki()
        anki.run()