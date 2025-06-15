#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版小红书文案生成器测试
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def simple_generate_rednote(product_name: str, style: str = "活泼甜美"):
    """简化版文案生成"""
    print(f"🚀 开始生成小红书文案...")
    print(f"📦 产品: {product_name}")
    print(f"🎨 风格: {style}")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {"success": False, "error": "API密钥未设置"}
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )
    
    # 构建提示词
    system_prompt = """
你是一个资深的小红书爆款文案专家，擅长创作引人入胜、高互动、高转化的笔记文案。

请根据用户提供的产品信息，生成包含标题、正文和标签的完整小红书笔记。

请以JSON格式输出，格式如下：
{
  "title": "小红书标题（包含表情符号，吸引眼球）",
  "body": "小红书正文（真实体验分享，包含细节描述和情感共鸣）",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"]
}
"""
    
    user_prompt = f"请为产品「{product_name}」生成一篇{style}风格的小红书爆款文案。"
    
    try:
        print("📡 正在调用API...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        print("✅ API调用成功")
        
        # 尝试解析JSON
        try:
            # 提取JSON内容
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                content = json.loads(json_str)
                return {"success": True, "content": content, "raw_response": result}
            else:
                return {"success": True, "content": None, "raw_response": result}
        except json.JSONDecodeError:
            return {"success": True, "content": None, "raw_response": result}
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return {"success": False, "error": str(e)}

def main():
    """测试主函数"""
    test_products = [
        "深海蓝藻保湿面膜",
        "美白精华液", 
        "玻尿酸原液"
    ]
    
    for product in test_products:
        print(f"\n{'='*50}")
        print(f"测试产品: {product}")
        print(f"{'='*50}")
        
        result = simple_generate_rednote(product)
        
        if result["success"]:
            if result["content"]:
                print("📝 生成的文案:")
                print(f"标题: {result['content'].get('title', '')}")
                print(f"正文: {result['content'].get('body', '')}")
                print(f"标签: {', '.join(result['content'].get('hashtags', []))}")
            else:
                print("📝 原始响应:")
                print(result["raw_response"])
            print("✅ 生成成功")
        else:
            print(f"❌ 生成失败: {result['error']}")
        
        print("\n" + "-"*30)

if __name__ == "__main__":
    main() 