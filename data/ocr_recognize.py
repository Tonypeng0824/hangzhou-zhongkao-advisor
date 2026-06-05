#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用免费OCR API识别图片中的表格数据
支持OCR.Space免费API（无需注册）
"""

import base64
import json
import requests
import sqlite3
from datetime import datetime
import os

def image_to_base64(image_path):
    """将图片转换为base64编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return base64_data

def ocr_space_recognize(image_path, api_key='helloworld'):
    """
    使用OCR.Space免费API识别图片
    API文档：https://ocr.space/ocrsdk
    免费key：helloworld（每天500次）
    """
    print(f"正在识别图片：{image_path}")
    
    # 将图片转换为base64
    base64_image = image_to_base64(image_path)
    
    # OCR.Space API endpoint
    url = "https://api.ocr.space/parse/image"
    
    # 请求参数
    payload = {
        'base64Image': f'data:image/jpeg;base64,{base64_image}',
        'language': 'eng',  # 可以识别中英文混合
        'isOverlayRequired': False,
        'detectOrientation': True,
        'scale': True,
        'OCREngine': 2,  # 使用引擎2（更准确）
    }
    
    headers = {
        'apikey': api_key,
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            print(f"❌ OCR识别失败：{result.get('ErrorMessage')}")
            return None
        else:
            # 提取识别的文本
            text_results = []
            for parsed_result in result.get('ParsedResults', []):
                text = parsed_result.get('ParsedText', '')
                text_results.append(text)
            
            full_text = '\n'.join(text_results)
            print("✓ OCR识别成功")
            return full_text
            
    except Exception as e:
        print(f"❌ OCR请求失败：{str(e)}")
        return None

def parse_table_data(text):
    """
    解析OCR识别的文本，提取表格数据
    这个函数需要根据实际识别结果调整解析逻辑
    """
    print("\n" + "="*60)
    print("OCR识别结果：")
    print("="*60)
    print(text)
    print("="*60 + "\n")
    
    # 这里需要根据实际的表格格式编写解析逻辑
    # 返回解析后的结构化数据
    return text

def save_to_database(data):
    """将解析后的数据保存到数据库"""
    # TODO: 根据实际数据格式实现数据库保存逻辑
    print("数据已保存到数据库")
    pass

if __name__ == '__main__':
    # 图片路径
    image_path = r'C:\Users\Administrator\Pictures\zhongkao_image.jpg'
    
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在：{image_path}")
        print("请先下载图片到指定路径")
        exit(1)
    
    print("="*60)
    print("开始OCR识别")
    print("="*60 + "\n")
    
    # 步骤1：OCR识别
    recognized_text = ocr_space_recognize(image_path)
    
    if recognized_text:
        # 步骤2：解析表格数据
        parsed_data = parse_table_data(recognized_text)
        
        # 步骤3：保存到数据库（待实现）
        # save_to_database(parsed_data)
        
        print("\n" + "="*60)
        print("识别完成！请检查上面的识别结果")
        print("="*60)
        print("\n下一步：")
        print("1. 检查识别结果是否准确")
        print("2. 如果准确，我将帮你解析并保存到数据库")
        print("3. 如果不准确，我们可以尝试其他OCR工具")
    else:
        print("\n❌ OCR识别失败")
        print("\n可能的解决方案：")
        print("1. 图片不清晰，请重新截图")
        print("2. 尝试其他OCR工具（如百度OCR、Google Keep）")
        print("3. 手动录入数据")
