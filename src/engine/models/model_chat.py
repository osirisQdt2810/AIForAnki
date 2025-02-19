import os
from abc import abstractmethod
from typing import List, Optional
    
import torch
from transformers import (AutoModelForCausalLM,  AutoTokenizer,)

from transformers.models.qwen2.modeling_qwen2 import Qwen2ForCausalLM
from transformers.models.qwen2.tokenization_qwen2_fast import Qwen2TokenizerFast

class ChatModel(object):
    def __init__(
        self, 
        device_id: Optional[str] = None,
        distributed: bool = False
    ):
        self._distributed = distributed
        if not distributed:
            self.device = torch.device(
                f"cuda:{device_id}" if torch.cuda.is_available() and device_id is not None else "cpu"
            )
        
    @abstractmethod
    def answer(self, prompt: str) -> str:
        raise NotImplementedError

class GwenModel(ChatModel):
    def __init__(
        self,
        device_id: str, 
        cache_dir: str = "./.caches",
        max_new_token: int = 512,
        chat_model: str = "Qwen/Qwen2.5-7B-Instruct",
        distributed: bool = False
    ):
        super(GwenModel, self).__init__(device_id, distributed)
        self._model_name = chat_model
        self._cache_dir = cache_dir
        self._max_token = max_new_token
        self._init_model()
        
    def _init_model(self):
        if self._distributed:
            self.chat_model: Qwen2ForCausalLM = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=self._model_name,
                torch_dtype="auto",
                device_map="auto",
                cache_dir=os.path.join(self._cache_dir, "ChatAssistant")
            )
        else:
            self.chat_model: Qwen2ForCausalLM = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=self._model_name,
                torch_dtype="auto",
                device_map=None,
                cache_dir=os.path.join(self._cache_dir, "ChatAssistant")
            ).to(self.device)
            
        self.chat_tokenizer: Qwen2TokenizerFast = AutoTokenizer.from_pretrained(self._model_name)
            
    def answer(self, question: str) -> str:
        messages = [
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
        
        text = self.chat_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.chat_tokenizer([text], return_tensors="pt").to(self.chat_model.device)
        generated_ids = self.chat_model.generate(
            **model_inputs,
            max_new_tokens=self._max_token
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.chat_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response