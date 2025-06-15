#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API 连接测试
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_deepseek_api():
    """测试DeepSeek API连接"""
    print("🔍 测试 DeepSeek API 连接...")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY 环境变量")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        print("📡 正在发送测试请求...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Hello, please reply with 'API connection successful!'"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API 响应: {result}")
        print("🎉 DeepSeek API 连接成功！")
        return True
        
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        return False

if __name__ == "__main__":
    test_deepseek_api() 