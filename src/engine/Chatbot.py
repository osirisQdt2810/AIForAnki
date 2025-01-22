import os
from abc import abstractmethod
from typing import List

import torch
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import (AutoModelForCausalLM, AutoProcessor, AutoTokenizer,
                          Qwen2VLForConditionalGeneration)

from transformers.models.qwen2.modeling_qwen2 import Qwen2ForCausalLM
from transformers.models.qwen2.tokenization_qwen2_fast import Qwen2TokenizerFast
from transformers.models.qwen2_vl.processing_qwen2_vl import Qwen2VLProcessor

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
        device_ids: List[str], 
        cache_dir: str = "./.caches",
        max_new_token_chat: int = 512,
        max_new_token_vl: int = 128,
        enable_vision_model: bool = False,
    ):
        self.chat_model_device_id, self.vl_model_device_id = self._select_devices(device_ids, 2)
        self.vl_model_device_id = self.vl_model_device_id if enable_vision_model else None
        
        self.chat_max_new_tokens = max_new_token_chat
        self.chat_model_device = torch.device(f"{self.chat_model_device_id}" if torch.cuda.is_available() is not None else "cpu")
        self.chat_model_name = "Qwen/Qwen2.5-7B-Instruct"
        self.chat_model: Qwen2ForCausalLM = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=self.chat_model_name,
            torch_dtype="auto",
            device_map=None,
            cache_dir=os.path.join(cache_dir, "ChatAssistant")
        ).to(self.chat_model_device)
        self.chat_tokenizer: Qwen2TokenizerFast = AutoTokenizer.from_pretrained(self.chat_model_name)
        
        if self.vl_model_device_id is not None:
            self.VL_FIXED_RESIZED_HEIGHT = 320
            self.vl_max_new_tokens = max_new_token_vl
            self.vl_model_device = torch.device(f"{self.vl_model_device_id}" if torch.cuda.is_available() is not None else "cpu")
            self.vl_model_name = "Qwen/Qwen2-VL-7B-Instruct"
            self.vl_model = Qwen2VLForConditionalGeneration.from_pretrained(
                pretrained_model_name_or_path=self.vl_model_name, 
                torch_dtype="auto", 
                device_map=None, 
                cache_dir=os.path.join(cache_dir, "VisionLanguageAssistant")
            ).to(self.vl_model_device)
            self.vl_processor: Qwen2VLProcessor = AutoProcessor.from_pretrained(self.vl_model_name)                
    
    def _select_devices(self, device_ids: List[str], number_models: int) -> List[str]:
        if not device_ids:
            raise ValueError("The list of device_ids cannot be empty.")
        
        if number_models <= 0:
            raise ValueError("The number of models must be greater than zero.")

        # Use round-robin assignment
        return [f"cuda:{device_ids[i % len(device_ids)]}" for i in range(number_models)]
    
    def answer(self, prompt: str):
        if hasattr(self, "chat_model"):
            messages = [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            
            text = self.chat_tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = self.chat_tokenizer([text], return_tensors="pt").to(self.chat_model.device)
            generated_ids = self.chat_model.generate(
                **model_inputs,
                max_new_tokens=self.chat_max_new_tokens
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = self.chat_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response
        else:
            print(f"[WARN] ChatModel haven't initialized yet.")
            return ""

    def describe_image(self, image: Image.Image) -> str:
        return self.analyse_images_with_prompt([image], "Describe this image.")
    
    def analyse_images_with_prompt(self, images: List[Image.Image], prompt: str) -> str:
        if hasattr(self, "vl_model"):
            messages = [
                {
                    "role": "user",
                    "content": [
                        *[
                            {
                                "type": "image",
                                "image": image,
                                "resized_height": self.VL_FIXED_RESIZED_HEIGHT,
                                "resized_width": self.VL_FIXED_RESIZED_HEIGHT / image.height * image.width
                            }
                            for image in images
                        ],
                        {
                            "type": "text", 
                            "text": prompt
                        },
                    ],
                }
            ]

            text = self.vl_processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.vl_processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to(self.vl_model.device)

            # Inference: Generation of the output
            generated_ids = self.vl_model.generate(**inputs, max_new_tokens=self.vl_max_new_tokens)
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.vl_processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            return output_text
        else:
            print(f"[WARN] VisionLanguageModel haven't initialized yet.")
            return ""
    
    def describe_video(self, video: str, **kwargs) -> str:
        if hasattr(self, "vl_model"):
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video",
                            "video": video,
                            "max_pixels": kwargs.get("resolution", 360 * 420),
                            "video_fps": kwargs.get("fps", 1.0),
                        },
                        {"type": "text", "text": "Describe this video."},
                    ],
                }
            ]

            text = self.vl_processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.vl_processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to(self.vl_model.device)

            # Inference: Generation of the output
            generated_ids = self.vl_model.generate(**inputs, max_new_tokens=self.vl_max_new_tokens)
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.vl_processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            return output_text
        else:
            print(f"[WARN] VisionLanguageModel haven't initialized yet.")
            return ""
              
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
        