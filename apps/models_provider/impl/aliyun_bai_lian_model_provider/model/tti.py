# coding=utf-8
from http import HTTPStatus
from typing import Dict

from django.utils.translation import gettext
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
import logging

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage


class QwenTextToImageModel(MaxKBBaseModel, BaseTextToImage):
    api_key: str
    model_name: str
    params: dict
    api_base: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.model_name = kwargs.get('model_name')
        self.params = kwargs.get('params')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {'size': '1024*1024', 'n': 1}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        chat_tong_yi = QwenTextToImageModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            api_base=model_credential.get('api_base'),
            **optional_params,
        )
        return chat_tong_yi

    def check_auth(self):
        # from openai import OpenAI
        #
        # client = OpenAI(
        #     # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
        #     api_key=self.api_key,
        #     base_url=self.api_base,
        # )
        # client.chat.completions.create(
        #     # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        #     model="qwen-max",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": gettext('Hello')},
        #     ]
        #
        # )
        return True

    def generate_image(self, prompt: str, negative_prompt: str = None):
        if self.model_name.startswith("wan2.6") or self.model_name.startswith("z"):
            try:
                from dashscope.aigc.image_generation import ImageGeneration
                from dashscope.api_entities.dashscope_response import Message
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "DashScope 版本过旧或未安装 ImageGeneration。请升级/安装 dashscope 后重试。"
                ) from exc
            # 以下为北京地域url，各地域的base_url不同
            message = Message(
                role="user",
                content=[
                    {
                        'text': prompt
                    }
                ]
            )
            rsp = ImageGeneration.call(
                model=self.model_name,
                api_key=self.api_key,
                base_url=self.api_base,
                messages=[message],
                negative_prompt=negative_prompt,
                **self.params
            )
            file_urls = []
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.choices:
                    file_urls.append(result.message.content[0].get('image'))
            else:
                maxkb_logger.error('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                   (rsp.status_code, rsp.code, rsp.message))
                raise Exception('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                (rsp.status_code, rsp.code, rsp.message))
            return file_urls
        elif self.model_name.startswith("wan"):
            try:
                from dashscope import ImageSynthesis
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "未安装 dashscope，无法使用图片生成模型。请先安装/升级 dashscope。"
                ) from exc
            rsp = ImageSynthesis.call(api_key=self.api_key,
                                      model=self.model_name,
                                      base_url=self.api_base,
                                      prompt=prompt,
                                      negative_prompt=negative_prompt,
                                      **self.params)
            file_urls = []
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.results:
                    file_urls.append(result.url)
            else:
                maxkb_logger.error('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                   (rsp.status_code, rsp.code, rsp.message))
                raise Exception('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                (rsp.status_code, rsp.code, rsp.message))
            return file_urls
        elif self.model_name.startswith("qwen"):
            try:
                from dashscope import MultiModalConversation
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "未安装 dashscope，无法使用多模态模型。请先安装/升级 dashscope。"
                ) from exc
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            rsp = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model_name,
                messages=messages,
                result_format='message',
                base_url=self.api_base,
                stream=False,
                negative_prompt=negative_prompt,
                **self.params
            )
            file_urls = []
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.choices:
                    file_urls.append(result.message.content[0].get('image'))
            else:
                maxkb_logger.error('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                   (rsp.status_code, rsp.code, rsp.message))
                raise Exception('sync_call Failed, status_code: %s, code: %s, message: %s' %
                                (rsp.status_code, rsp.code, rsp.message))
            return file_urls
