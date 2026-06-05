#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将图片转换为base64编码，用于OCR识别
"""

import base64
import os
import sys

def image_to_base64(image_path):
    """将图片转换为base64编码"""
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在：{image_path}")
        return None
    
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            file_size = os.path.getsize(image_path)
            print(f"✓ 图片路径：{image_path}")
            print(f"✓ 文件大小：{file_size} bytes ({file_size/1024:.2f} KB)")
            print(f"✓ Base64编码长度：{len(base64_data)} 字符")
            print(f"✓ 图片已准备好，可以进行OCR识别")
            
            # 保存到文件，方便查看
            output_file = image_path + '.base64.txt'
            with open(output_file, 'w') as f:
                f.write(base64_data)
            print(f"✓ Base64编码已保存到：{output_file}")
            
            return base64_data
            
    except Exception as e:
        print(f"❌ 转换失败：{str(e)}")
        return None

if __name__ == '__main__':
    image_path = r'C:\Users\Administrator\Pictures\baosong.jpg'
    print("=" * 60)
    print("图片转Base64编码工具")
    print("=" * 60)
    print()
    
    base64_data = image_to_base64(image_path)
    
    if base64_data:
        print()
        print("下一步：调用OCR工具识别图片")
    else:
        print()
        print("请检查图片路径是否正确")
        sys.exit(1)
