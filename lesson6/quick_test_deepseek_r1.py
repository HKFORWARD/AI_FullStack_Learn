#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek-R1:8B 快速测试脚本
简单快速地测试 deepseek-r1:8b 模型是否正常工作

Usage: python quick_test_deepseek_r1.py
"""

from rednote import Config, RedNoteGenerator, FileManager


def quick_test():
    """快速测试 DeepSeek-R1:8B"""
    print("🚀 DeepSeek-R1:8B 快速测试")
    print("=" * 40)
    
    try:
        # 创建配置，指定使用 deepseek-r1:8b
        print("📝 创建配置...")
        config = Config(provider="ollama", ollama_model="deepseek-r1:8b")
        
        # 创建生成器
        print("🤖 初始化生成器...")
        generator = RedNoteGenerator(config)
        file_manager = FileManager(config)
        
        # 简单测试案例
        print("🎯 开始生成测试...")
        result = generator.generate(
            product_name="蜂蜜柠檬手工皂",
            style="清新自然",
            target_audience="喜欢天然护肤的人群",
            key_features=["天然成分", "温和清洁", "淡淡香味"]
        )
        
        if result["success"]:
            print("✅ 生成成功！")
            
            # 保存文件
            filepath = file_manager.save_to_markdown(result)
            print(f"📄 文件已保存: {filepath}")
            
            # 显示内容
            content = result["content"]
            print(f"\n📝 生成内容预览:")
            print(f"标题: {content['title']}")
            print(f"正文: {content['body'][:150]}...")
            print(f"标签: {' '.join(content['hashtags'])}")
            print(f"表情: {' '.join(content['emojis'])}")
            
            return True
        else:
            print(f"❌ 生成失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print(f"\n🎉 DeepSeek-R1:8B 测试通过！")
        print(f"💡 现在可以运行完整测试: python test_deepseek_r1.py")
    else:
        print(f"\n💭 如果测试失败，请检查:")
        print(f"   1. Ollama 是否正在运行: ollama serve")
        print(f"   2. 模型是否已下载: ollama pull deepseek-r1:8b")
        print(f"   3. 检查可用模型: ollama list") 