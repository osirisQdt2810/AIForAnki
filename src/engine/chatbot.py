import os
from abc import abstractmethod
from typing import List, Optional

import sys
if not hasattr(sys.stderr, "flush"):
    sys.stderr.flush = lambda: None
    
from PIL import Image

from src.engine.models import model_chat, model_vision

class Assistant(object):
    @abstractmethod
    def answer(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_image(self, prompt: str) -> Image.Image:
        pass
    
    @abstractmethod
    def describe_image(self, image: Image.Image) -> str:
        pass

    @abstractmethod
    def analyse_images_with_prompt(self, images: List[Image.Image], prompt: str) -> List[str]:
        pass

    @abstractmethod
    def describe_video(self, video: str, **kwargs) -> str:
        pass


class AnkiAssistant(Assistant):
    def __init__(
        self, 
        cache_dir: str = "",
        device_ids: List[str] = None,
        chat_model_name: str = "",
        chat_max_token: int = 512,
        vision_model_name: str = "",
        vision_max_token: int = 512,
        enable_vision_model: bool = False,
        distributed: bool = False
    ):
        if distributed:
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(device_ids)

        self.chat_model_device_id, self.vision_model_device_id = self._select_devices(device_ids, 2)
        self.chat_model = model_chat.GwenModel(
            device_id=self.chat_model_device_id,
            cache_dir=cache_dir,
            max_new_token=chat_max_token,
            chat_model=chat_model_name,
            distributed=distributed
        )
        if enable_vision_model:
            self.vision_model = model_vision.GwenVisionModel(
                device_id=self.vision_model_device_id,
                cache_dir=cache_dir,
                model_name=vision_model_name,
                max_token=vision_max_token,
                distributed=distributed
            )

    
    def _select_devices(self, 
        device_ids: List[str], 
        number_models: int,
        distributed: bool = False
    ) -> List[str]:
        if distributed:
            return [None for _ in range(number_models)]
        
        if not device_ids:
            raise ValueError("The list of device_ids cannot be empty.")
        
        if number_models <= 0:
            raise ValueError("The number of models must be greater than zero.")

        # Use round-robin assignment
        return [f"{device_ids[i % len(device_ids)]}" for i in range(number_models)]
    
    def answer(self, prompt: str, **kwargs):
        if not hasattr(self, "chat_model"):
            raise RuntimeError("[WARN] ChatModel haven't initialized yet.")
        return self.chat_model.answer(prompt)

    def describe_image(self, image: Image.Image, **kwargs) -> str:
        return self.analyse_images_with_prompt([image], "Describe this image.", **kwargs)
    
    def analyse_images_with_prompt(self, images: List[Image.Image], prompt: str, **kwargs) -> str:
        if not hasattr(self, "vision_model"):
            raise RuntimeError("[WARN] VisionModel haven't initialized yet.")
        return self.vision_model.analyse_images_with_prompt(images, prompt, **kwargs)
    
    def describe_video(self, video: str, **kwargs) -> str:
        if not hasattr(self, "vision_model"):
            raise RuntimeError("[WARN] VisionModel haven't initialized yet.")
        return self.vision_model.describe_video(video, **kwargs)
              
def run(args):
    assistant = AnkiAssistant(args.devices)
    print(
        f"\n>>>>> AnkiAssistant answer:\n", 
        assistant.answer(
            "tôi đang muốn học từ vựng tiếng anh, hãy giúp tôi tạo một thẻ flashcard."
            "Mặt trước của thẻ là một câu ví dụ tiếng anh chứa từ cần học, tuy nhiên từ này lại bị thay thế bởi cloze (\"[....]\")."
            "Ngoài ra mặt trước còn chứa định nghĩa bằng cả tiếng anh lẫn tiếng việt của từ (bao gồm tiếng việt ngắn và dài)."
            "Mặt sau của thẻ chứa từ cần học, phiên âm, định nghĩa (bằng cả tiếng anh lẫn tiếng việt), câu ví dụ, dịch nghĩa của câu ví dụ. Từ tôi muốn học là \"intrigue\""
        )
    )
    print(
        f"\n>>>>> AnkiAssistant analyse_images_with_prompt:\n", 
        assistant.analyse_images_with_prompt(
            images=[
                Image.open("/home/phucnp/storage/VTX_BGJ/Test/F04_DC104128_00001.png"),
                Image.open("/home/phucnp/storage/VTX_BGJ/Test/F04_DC104128_00002.png")
            ],
            prompt="What are the common points in these two images?"
        )
    )
    print(
        f"\n>>>>> AnkiAssistant describe_video:\n", 
        assistant.describe_video(
            "/home/phucnp/workspace/XFace/data/JunctionX06.2023_Dataset/Data_4Cam/scene_02/cam1_kg.mp4"
        )
    )

def parse_args():
    import argparse
    parser = argparse.ArgumentParser("Anki-AI-Assistant")
    parser.add_argument("--devices", nargs="+", help="List of devices (e.g., '0 1 2')", default=['0'])
    return parser.parse_args()

if __name__ == "__main__":
    run(parse_args())    
        