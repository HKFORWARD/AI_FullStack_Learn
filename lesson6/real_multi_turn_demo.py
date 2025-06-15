#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
真正的多轮推理演示脚本
故意创造条件来展示多轮推理的过程

Author: AI Learning Assistant
Date: 2025-01-27
"""

from rednote import Config, RedNoteGenerator, FileManager
from openai import OpenAI
import json
import time


class MultiTurnDemonstrator:
    """多轮推理演示器"""
    
    def __init__(self):
        self.config = Config(provider="ollama", ollama_model="deepseek-r1:8b")
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=60.0
        )
    
    def demonstrate_real_multi_turn(self):
        """真正展示多轮推理过程"""
        print("🎭 真正的多轮推理演示")
        print("=" * 50)
        
        # 构建一个复杂的请求，更容易触发多轮推理
        complex_request = """请为以下复杂的护肤品组合生成小红书文案：

产品：「三重修护精华套装」
- 主要成分：积雪草提取物 + 烟酰胺 + 玻尿酸
- 适用人群：混合性敏感肌，20-35岁都市白领女性
- 使用场景：早C晚A护肤，工作压力大容易长痘
- 特点：韩国进口、医美级别、温和不刺激、快速见效
- 价格定位：中高端（298元/套装）

要求：
1. 标题要体现"三重修护"概念
2. 正文要包含使用体验、效果对比、适用场景
3. 标签要覆盖成分、功效、人群
4. 语调要专业但不失亲和力
5. 必须以标准JSON格式输出

请深入分析产品特点，分步骤构思文案。"""
        
        # 初始化对话
        messages = [
            {"role": "system", "content": self._get_enhanced_system_prompt()},
            {"role": "user", "content": complex_request}
        ]
        
        print("🚀 开始多轮推理演示...")
        print(f"📝 使用复杂请求触发多轮推理")
        
        # 手动执行多轮对话
        turn_count = 0
        max_turns = 5
        
        while turn_count < max_turns:
            turn_count += 1
            print(f"\n--- 第 {turn_count} 轮对话 ---")
            
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                response_content = response.choices[0].message.content
                print(f"🤖 模型回复长度: {len(response_content)} 字符")
                print(f"📝 回复预览: {response_content[:150]}...")
                
                # 尝试解析JSON
                json_result = self._try_extract_json(response_content)
                
                if json_result:
                    print(f"✅ 第 {turn_count} 轮成功解析JSON!")
                    self._display_result(json_result)
                    return json_result
                else:
                    print(f"❌ 第 {turn_count} 轮JSON解析失败")
                    
                    # 添加助手回复到对话历史
                    messages.append({
                        "role": "assistant",
                        "content": response_content
                    })
                    
                    # 添加引导性的用户回复
                    if turn_count == 1:
                        guidance = "请重新分析产品特点，确保生成的文案包含所有要求的元素，并以正确的JSON格式输出。"
                    elif turn_count == 2:
                        guidance = """让我们分步骤来：
1. 首先分析产品的核心价值：三重修护（积雪草+烟酰胺+玻尿酸）
2. 构思目标用户的痛点和需求
3. 设计吸引人的标题和生动的正文
4. 选择精准的标签和表情符号

请以JSON格式输出：
```json
{
  "title": "标题",
  "body": "正文",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["✨", "🔥", "💖", "💧"]
}
```"""
                    else:
                        guidance = "请确保严格按照JSON格式输出，检查语法是否正确。"
                    
                    messages.append({
                        "role": "user",
                        "content": guidance
                    })
                    
                    print(f"💬 用户引导: {guidance[:100]}...")
                    time.sleep(1)  # 模拟思考时间
                    
            except Exception as e:
                print(f"❌ 第 {turn_count} 轮出错: {e}")
                break
        
        print(f"\n⚠️ 经过 {turn_count} 轮对话仍未成功生成")
        return None
    
    def _get_enhanced_system_prompt(self):
        """获取增强的系统提示"""
        return """你是一个专业的小红书文案专家，具备深度分析能力。

请按照以下思路分析和创作：
1. 深入分析产品特点和目标用户
2. 识别用户痛点和产品价值匹配
3. 构思具有吸引力的标题
4. 创作真实自然的正文内容
5. 选择精准的标签和表情符号

注意：必须以标准JSON格式输出，确保语法正确。"""
    
    def _try_extract_json(self, content):
        """尝试提取JSON内容"""
        import re
        
        # 多种JSON提取方式
        patterns = [
            r"```json\s*(\{.*?\})\s*```",
            r"```\s*(\{.*?\})\s*```",
            r"(\{[^{}]*\"title\"[^{}]*\"body\"[^{}]*\"hashtags\"[^{}]*\"emojis\"[^{}]*\})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(1))
                    if all(key in result for key in ["title", "body", "hashtags", "emojis"]):
                        return result
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _display_result(self, result):
        """显示生成结果"""
        print(f"\n📝 生成结果:")
        print("=" * 40)
        print(f"📌 标题: {result['title']}")
        print(f"\n📖 正文:")
        print(result['body'])
        print(f"\n🏷️ 标签: {' '.join(result['hashtags'])}")
        print(f"😊 表情: {' '.join(result['emojis'])}")
    
    def demonstrate_forced_multi_turn(self):
        """强制展示多轮推理（故意让第一次失败）"""
        print(f"\n🎬 强制多轮推理演示")
        print("=" * 50)
        
        # 构建一个故意让JSON解析失败的请求
        confusing_request = """请为"神奇面膜"生成小红书文案，要求：
- 标题要有emoji但是不要用常见的
- 正文要超级长超级详细
- 标签要很多很多个
- 输出格式要特别特别标准

请深入思考再回答。"""
        
        messages = [
            {"role": "system", "content": "你是小红书文案专家，但经常忘记使用JSON格式。"},
            {"role": "user", "content": confusing_request}
        ]
        
        print("🎯 使用故意模糊的请求来触发多轮推理...")
        
        turn_count = 0
        while turn_count < 3:
            turn_count += 1
            print(f"\n--- 第 {turn_count} 轮 ---")
            
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=0.8,  # 增加随机性
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content
                print(f"🤖 模型回复: {content[:200]}...")
                
                # 检查是否包含JSON
                if "```json" in content or '{"title"' in content:
                    json_result = self._try_extract_json(content)
                    if json_result:
                        print(f"✅ 第 {turn_count} 轮成功!")
                        self._display_result(json_result)
                        return json_result
                
                # 添加到对话历史
                messages.append({"role": "assistant", "content": content})
                
                # 添加更明确的要求
                if turn_count == 1:
                    guidance = "请必须以JSON格式输出，格式为：```json\n{...}\n```"
                elif turn_count == 2:
                    guidance = "请严格按照JSON格式输出，包含title、body、hashtags、emojis四个字段。"
                else:
                    guidance = "请确保JSON格式正确，可以被程序解析。"
                
                messages.append({"role": "user", "content": guidance})
                print(f"💬 用户要求: {guidance}")
                
            except Exception as e:
                print(f"❌ 错误: {e}")
                break
        
        print(f"⚠️ 多轮演示结束")
        return None


def main():
    """主函数"""
    print("🎯 真正的多轮推理演示")
    print("展示 DeepSeek-R1:8B 的实际推理过程")
    print()
    
    demonstrator = MultiTurnDemonstrator()
    
    print("🔍 说明:")
    print("- 这次演示会展示真实的多轮对话过程")
    print("- 使用复杂请求和故意模糊的指令")
    print("- 观察模型如何在引导下逐步优化输出")
    print()
    
    try:
        # 演示1：复杂请求的多轮推理
        result1 = demonstrator.demonstrate_real_multi_turn()
        
        # 演示2：强制多轮推理
        result2 = demonstrator.demonstrate_forced_multi_turn()
        
        print(f"\n🎉 多轮推理演示完成!")
        print(f"💡 这次展示了真实的多轮对话过程，不是自娱自乐了！")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        print(f"💡 请确保 Ollama 和 deepseek-r1:8b 模型可用")


if __name__ == "__main__":
    main() 