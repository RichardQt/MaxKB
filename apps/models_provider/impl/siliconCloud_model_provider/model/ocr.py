# coding=utf-8
"""
    @project: maxkb
    @Author：OCR Model
    @file： ocr.py
    @date：2026/1/13
    @desc: 硅基流动OCR模型实现
"""
import base64
from typing import Dict

from openai import OpenAI

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel


class SiliconCloudOCR(MaxKBBaseModel):
    api_base: str
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__()
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params', {})

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return SiliconCloudOCR(
            model=model_name,
            api_base=model_credential.get('api_base'),
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        """验证API凭证"""
        client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        response_list = client.models.with_raw_response.list()
        return True

    def recognize(self, image_content: bytes, image_type: str = 'image/png') -> str:
        """
        识别图片中的文字
        :param image_content: 图片二进制内容
        :param image_type: 图片MIME类型
        :return: 识别出的文字内容
        """
        try:
            client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            
            # 将图片转换为base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            image_url = f"data:{image_type};base64,{image_base64}"
            
            # 调用视觉模型进行OCR
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别这张图片中的所有文字内容，保持原有的格式和排版。如果图片中没有文字，请返回空字符串。只返回识别到的文字，不要添加任何解释或说明。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                **self.params
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            return ""
            
        except Exception as e:
            maxkb_logger.error(f"OCR recognition error: {e}")
            raise e

    def recognize_file(self, file) -> str:
        """
        识别文件中的文字
        :param file: 文件对象
        :return: 识别出的文字内容
        """
        file_name = file.name.lower()
        
        # 确定图片类型
        if file_name.endswith('.png'):
            image_type = 'image/png'
        elif file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
            image_type = 'image/jpeg'
        elif file_name.endswith('.gif'):
            image_type = 'image/gif'
        elif file_name.endswith('.webp'):
            image_type = 'image/webp'
        elif file_name.endswith('.bmp'):
            image_type = 'image/bmp'
        else:
            image_type = 'image/png'
        
        # 读取文件内容
        file.seek(0)
        image_content = file.read()
        file.seek(0)
        
        return self.recognize(image_content, image_type)
