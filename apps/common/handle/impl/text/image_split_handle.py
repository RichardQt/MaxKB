# coding=utf-8
"""
    @project: maxkb
    @Author：OCR Image Split Handle
    @file： image_split_handle.py
    @date：2026/1/13
    @desc: 图片文件OCR处理器
"""
import re
import traceback
from typing import List

from common.handle.base_split_handle import BaseSplitHandle
from common.utils.logger import maxkb_logger
from common.utils.split_model import SplitModel

# 支持的图片格式
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.ico']

default_pattern_list = [
    re.compile('(?<=^)# .*|(?<=\\n)# .*'),
    re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
    re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
    re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
    re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
    re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*"),
    re.compile("(?<!\n)\n\n+")
]


class ImageSplitHandle(BaseSplitHandle):
    """图片OCR分割处理器"""
    
    def __init__(self, ocr_model=None):
        """
        初始化图片处理器
        :param ocr_model: OCR模型实例，用于识别图片中的文字
        """
        self.ocr_model = ocr_model
    
    def set_ocr_model(self, ocr_model):
        """设置OCR模型"""
        self.ocr_model = ocr_model
    
    def support(self, file, get_buffer):
        """检查是否支持该文件类型"""
        file_name: str = file.name.lower()
        return any(file_name.endswith(ext) for ext in IMAGE_EXTENSIONS)

    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        """
        处理图片文件，使用OCR识别文字并分割
        :param file: 文件对象
        :param pattern_list: 分割模式列表
        :param with_filter: 是否过滤特殊字符
        :param limit: 分段长度限制
        :param get_buffer: 获取文件缓冲区的函数
        :param save_image: 保存图片的函数
        :return: 包含文件名和分割后内容的字典
        """
        try:
            if type(limit) is str:
                limit = int(limit)
            if type(with_filter) is str:
                with_filter = with_filter.lower() == 'true'
            
            # 使用OCR识别图片内容
            content = self.get_content(file, save_image)
            
            if not content or content.strip() == '':
                maxkb_logger.warning(f"No text recognized from image: {file.name}")
                return {'name': file.name, 'content': []}
            
            # 使用分割模型分割识别出的文字
            if pattern_list is not None and len(pattern_list) > 0:
                split_model = SplitModel(pattern_list, with_filter, limit)
            else:
                split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
            
            return {'name': file.name, 'content': split_model.parse(content)}
            
        except Exception as e:
            maxkb_logger.error(f"Error processing image file {file.name}: {e}, {traceback.format_exc()}")
            return {'name': file.name, 'content': []}

    def get_content(self, file, save_image):
        """
        获取图片内容（通过OCR识别）
        :param file: 文件对象
        :param save_image: 保存图片的函数
        :return: 识别出的文字内容
        """
        if self.ocr_model is None:
            maxkb_logger.error("OCR model is not configured")
            return ""
        
        try:
            # 调用OCR模型识别图片
            content = self.ocr_model.recognize_file(file)
            return content if content else ""
        except Exception as e:
            maxkb_logger.error(f"OCR recognition failed for {file.name}: {e}, {traceback.format_exc()}")
            return ""
    
    @staticmethod
    def is_image_file(file_name: str) -> bool:
        """检查文件是否为图片"""
        return any(file_name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
