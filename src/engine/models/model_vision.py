import os
from abc import abstractmethod
from typing import List, Optional

import sys   
import torch
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import (AutoProcessor,
                          Qwen2VLForConditionalGeneration)

from transformers.models.qwen2_vl.processing_qwen2_vl import Qwen2VLProcessor

class VisionModel(object):
    def __init__(self, 
        device_id: Optional[str] = None,
        distributed: bool = False
    ):
        self._distributed = distributed
        if not distributed:
            self.device = torch.device(
                f"cuda:{device_id}" if torch.cuda.is_available() and device_id is not None else "cpu"
            )
                
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

class GwenVisionModel(VisionModel):
    FIXED_RESIZED_HEIGHT = 320
    
    def __init__(
        self,
        device_id: Optional[str] = None,
        cache_dir: str = "",
        model_name: str = "Qwen/Qwen2-VL-7B-Instruct",
        max_token: int = 128,
        distributed: bool = False        
    ):
        super(GwenVisionModel, self).__init__(device_id, distributed)
        self._cache_dir = cache_dir
        self._model_name = model_name
        self._max_token = max_token
        self._init_model()
        
    def _init_model(self):
        if self._distributed:
            self.vision_model = Qwen2VLForConditionalGeneration.from_pretrained(
                pretrained_model_name_or_path=self._model_name, 
                torch_dtype="auto", 
                device_map="auto", 
                cache_dir=os.path.join(self._cache_dir, "VisionLanguageAssistant")
            )
        else:
            self.vision_model = Qwen2VLForConditionalGeneration.from_pretrained(
                pretrained_model_name_or_path=self._model_name, 
                torch_dtype="auto", 
                device_map=None, 
                cache_dir=os.path.join(self._cache_dir, "VisionLanguageAssistant")
            ).to(self.device)
        
        self.processor: Qwen2VLProcessor = AutoProcessor.from_pretrained(self._model_name)
        
    def generate_image(self, prompt: str) -> Image.Image:
        pass
    
    def describe_image(self, image: Image.Image) -> str:
        return self.analyse_images_with_prompt([image], "Describe this image.")

    def analyse_images_with_prompt(self, images: List[Image.Image], prompt: str) -> List[str]:
        messages = [
            {
                "role": "user",
                "content": [
                    *[
                        {
                            "type": "image",
                            "image": image,
                            "resized_height": self.FIXED_RESIZED_HEIGHT,
                            "resized_width": self.FIXED_RESIZED_HEIGHT / image.height * image.width
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

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.vision_model.device)

        # Inference: Generation of the output
        generated_ids = self.vision_model.generate(**inputs, max_new_tokens=self._max_token)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        return output_text

    def describe_video(self, video: str, **kwargs) -> str:
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

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.vision_model.device)

        # Inference: Generation of the output
        generated_ids = self.vision_model.generate(**inputs, max_new_tokens=self._max_token)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        return output_text        