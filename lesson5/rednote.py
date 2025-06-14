#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小红书文案生成器 - 重构版
基于 DeepSeek Agent 的智能文案生成系统

Author: AI Learning Assistant
Date: 2025-06-14
Version: 1.0
"""

import os
import json
import re
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置管理类"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        self.max_iterations = 5
        self.output_dir = Path("output")
        self.default_style = "活泼甜美"
        
        # 验证必要配置
        if not self.api_key:
            raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
        
        # 创建输出目录
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        self.output_dir.mkdir(exist_ok=True)
        
        # 按日期创建子目录
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_dir = self.output_dir / today
        self.daily_dir.mkdir(exist_ok=True)


class ToolManager:
    """工具管理类 - 负责模拟外部API调用"""
    
    @staticmethod
    def search_web(query: str) -> str:
        """模拟网页搜索工具"""
        print(f"🔍 [Tool] 搜索网页: {query}")
        time.sleep(1)  # 模拟网络延迟
        
        # 基于关键词返回相关信息
        if "小红书" in query and "趋势" in query:
            return "近期小红书流行趋势：'多巴胺穿搭'、'早C晚A'护肤、'伪素颜'妆容。热门关键词：#氛围感 #抗老 #屏障修复"
        elif "保湿" in query and "面膜" in query:
            return "保湿面膜用户痛点：卡粉、泛红、紧绷感。热门话题：沙漠干皮救星、熬夜急救面膜、水光肌养成"
        elif "美白" in query and "精华" in query:
            return "美白精华市场趋势：成分党关注烟酰胺和VC，用户关心淡斑效果和温和性。热门标签：#提亮肤色 #痘印救星"
        else:
            return f"关于'{query}'的市场反馈：用户普遍关注产品成分、功效和使用体验"
    
    @staticmethod
    def query_product_database(product_name: str) -> str:
        """模拟产品数据库查询"""
        print(f"📊 [Tool] 查询产品数据库: {product_name}")
        time.sleep(0.5)
        
        # 产品信息模拟数据
        product_info = {
            "深海蓝藻保湿面膜": "核心成分：深海蓝藻提取物，富含多糖和氨基酸。功效：深层补水、修护肌肤屏障、舒缓敏感。质地清爽不粘腻，适合所有肤质，特别适合干燥敏感肌。规格：25ml×5片",
            "美白精华": "核心成分：烟酰胺3%+VC衍生物。功效：提亮肤色、淡化痘印、改善暗沉。质地轻薄易吸收，适合需要均匀肤色的人群。建议晚间使用，需配合防晒",
            "玻尿酸原液": "核心成分：多重分子量玻尿酸。功效：强效补水、锁水保湿、丰盈肌肤。质地清透，快速渗透。适合所有肌肤类型，特别是缺水性肌肤"
        }
        
        return product_info.get(product_name, f"产品'{product_name}'的基本信息：天然成分，温和有效，适合日常护肤使用")
    
    @staticmethod
    def generate_emoji(context: str) -> List[str]:
        """根据上下文生成表情符号"""
        print(f"😊 [Tool] 生成表情符号，上下文: {context}")
        time.sleep(0.2)
        
        emoji_mapping = {
            "补水|保湿|水润": ["💦", "💧", "🌊", "✨", "💎"],
            "美白|提亮|亮白": ["✨", "🌟", "💫", "🤍", "☀️"],
            "惊喜|爱了|哇塞": ["💖", "😍", "🤩", "💯", "🔥"],
            "熬夜|疲惫|急救": ["😭", "😮‍💨", "😴", "💡", "🆘"],
            "推荐|好物|种草": ["✅", "👍", "⭐", "🛍️", "💝"],
            "修复|舒缓|温和": ["🌿", "🍃", "💚", "🤲", "💆‍♀️"]
        }
        
        # 匹配相关表情
        for pattern, emojis in emoji_mapping.items():
            if any(keyword in context for keyword in pattern.split("|")):
                return random.sample(emojis, min(4, len(emojis)))
        
        # 默认表情
        return random.sample(["✨", "🔥", "💖", "💯", "🎉", "👍", "🤩"], 4)


class RedNoteGenerator:
    """小红书文案生成器核心类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = self._init_client()
        self.tool_manager = ToolManager()
        self.system_prompt = self._get_system_prompt()
        self.tools_definition = self._get_tools_definition()
        
        # 工具映射
        self.available_tools = {
            "search_web": self.tool_manager.search_web,
            "query_product_database": self.tool_manager.query_product_database,
            "generate_emoji": self.tool_manager.generate_emoji
        }
    
    def _init_client(self) -> OpenAI:
        """初始化OpenAI客户端"""
        return OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
你是一个资深的小红书爆款文案专家，擅长结合最新潮流和产品卖点，创作引人入胜、高互动、高转化的笔记文案。

你的任务是根据用户提供的产品和需求，生成包含标题、正文、相关标签和表情符号的完整小红书笔记。

请始终采用'Thought-Action-Observation'模式进行推理和行动。文案风格需活泼、真诚、富有感染力。

当完成任务后，请以JSON格式直接输出最终文案，格式如下：
```json
{
  "title": "小红书标题（包含表情符号，吸引眼球）",
  "body": "小红书正文（真实体验分享，包含细节描述和情感共鸣）",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["✨", "🔥", "💖", "💧"]
}
在生成文案前，请务必先思考并收集足够的信息。
""".strip()
        
    def _get_tools_definition(self) -> List[Dict]:
        """获取工具定义"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "搜索互联网上的实时信息，用于获取最新趋势、用户评价、行业报告等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词，如'小红书美妆趋势'或'保湿面膜用户评价'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_product_database",
                    "description": "查询内部产品数据库，获取产品详细信息、卖点、成分等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {
                                "type": "string",
                                "description": "产品名称"
                            }
                        },
                        "required": ["product_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_emoji",
                    "description": "根据文本内容生成适合的表情符号",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "文案关键内容或情感，如'惊喜效果'、'补水保湿'"
                            }
                        },
                        "required": ["context"]
                    }
                }
            }
        ]

    def generate(self, product_name: str, style: str = None, target_audience: str = None, key_features: List[str] = None) -> Dict[str, Any]:
        """
        生成小红书文案
        
        Args:
            product_name: 产品名称
            style: 文案风格，如'活泼甜美'、'知性温柔'等
            target_audience: 目标受众，如'20-30岁女性'
            key_features: 产品关键特性列表
            
        Returns:
            包含文案内容和元信息的字典
        """
        print(f"\n🚀 开始生成小红书文案...")
        print(f"📦 产品: {product_name}")
        print(f"🎨 风格: {style or self.config.default_style}")
        
        # 构建用户请求
        user_request = self._build_user_request(product_name, style, target_audience, key_features)
        
        # 初始化对话历史
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_request}
        ]
        
        # 执行生成循环
        result = self._generation_loop(messages)
        
        if result:
            print("✅ 文案生成成功！")
            return {
                "success": True,
                "content": result,
                "metadata": {
                    "product_name": product_name,
                    "style": style or self.config.default_style,
                    "target_audience": target_audience,
                    "key_features": key_features,
                    "generated_at": datetime.now().isoformat()
                }
            }
        else:
            print("❌ 文案生成失败")
            return {"success": False, "error": "生成失败"}

    def _build_user_request(self, product_name: str, style: str, target_audience: str, key_features: List[str]) -> str:
        """构建用户请求文本"""
        request_parts = [f"请为产品「{product_name}」生成一篇小红书爆款文案。"]
        
        # 添加风格要求
        if style:
            request_parts.append(f"要求语气风格：{style}")
        
        # 添加目标受众
        if target_audience:
            request_parts.append(f"目标受众：{target_audience}")
        
        # 添加关键特性
        if key_features:
            features_str = "、".join(key_features)
            request_parts.append(f"重点突出特性：{features_str}")
        
        request_parts.append("请包含标题、正文、至少5个相关标签和表情符号。")
        request_parts.append("请以完整的JSON格式输出，并用markdown代码块包裹。")
        
        return " ".join(request_parts)

    def _generation_loop(self, messages: List[Dict]) -> Optional[Dict]:
        """执行生成循环（ReAct模式）"""
        iteration_count = 0
        
        while iteration_count < self.config.max_iterations:
            iteration_count += 1
            print(f"\n--- 第 {iteration_count} 轮推理 ---")
            
            try:
                # 调用DeepSeek API
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    tools=self.tools_definition,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                
                # 处理工具调用
                if response_message.tool_calls:
                    print("🤖 Agent决定调用工具...")
                    messages.append(response_message)
                    
                    # 执行所有工具调用
                    tool_outputs = self._execute_tool_calls(response_message.tool_calls)
                    messages.extend(tool_outputs)
                
                # 处理最终内容
                elif response_message.content:
                    print(f"💭 Agent生成内容")
                    
                    # 尝试解析JSON内容
                    result = self._extract_json_content(response_message.content)
                    if result:
                        return result
                    else:
                        # 解析失败，继续对话
                        messages.append(response_message)
                        print("⚠️ JSON解析失败，继续生成...")
                
                else:
                    print("❓ 未知响应类型")
                    break
                    
            except Exception as e:
                print(f"❌ API调用错误: {e}")
                break
        
        print(f"\n⚠️ 达到最大迭代次数 ({self.config.max_iterations})，生成失败")
        return None

    def _execute_tool_calls(self, tool_calls) -> List[Dict]:
        """执行工具调用"""
        tool_outputs = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
            
            print(f"🔧 调用工具: {function_name}")
            print(f"📝 参数: {function_args}")
            
            # 执行工具函数
            if function_name in self.available_tools:
                try:
                    tool_function = self.available_tools[function_name]
                    tool_result = tool_function(**function_args)
                    print(f"📤 工具结果: {tool_result}")
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": str(tool_result)
                    })
                except Exception as e:
                    error_msg = f"工具执行错误: {e}"
                    print(f"❌ {error_msg}")
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": error_msg
                    })
            else:
                error_msg = f"未知工具: {function_name}"
                print(f"❌ {error_msg}")
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": error_msg
                })
        
        return tool_outputs

    def _extract_json_content(self, content: str) -> Optional[Dict]:
        """从响应中提取JSON内容"""
        # 尝试匹配markdown json代码块
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析整个内容
            json_str = content.strip()
        
        try:
            result = json.loads(json_str)
            print("✅ JSON解析成功")
            return result
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None
    
class FileManager:
    """文件管理类 - 负责保存和管理输出文件"""
    def __init__(self, config: Config):
        self.config = config

    def save_to_markdown(self, content_data: Dict[str, Any]) -> str:
        """
        保存文案到Markdown文件
        
        Args:
            content_data: 包含文案内容和元信息的字典
            
        Returns:
            保存的文件路径
        """
        if not content_data.get("success"):
            raise ValueError("无法保存失败的生成结果")
        
        content = content_data["content"]
        metadata = content_data["metadata"]
        
        # 生成文件名
        filename = self._generate_filename(metadata)
        filepath = self.config.daily_dir / filename
        
        # 生成Markdown内容
        markdown_content = self._format_markdown(content, metadata)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"💾 文件已保存: {filepath}")
        return str(filepath)

    def _generate_filename(self, metadata: Dict) -> str:
        """生成文件名"""
        product_name = metadata["product_name"]
        style = metadata["style"]
        timestamp = datetime.now().strftime("%H%M%S")
        
        # 清理文件名中的特殊字符
        clean_product = re.sub(r'[<>:"/\\|?*]', '_', product_name)
        clean_style = re.sub(r'[<>:"/\\|?*]', '_', style)
        
        return f"{clean_product}_{clean_style}_{timestamp}.md"

    def _format_markdown(self, content: Dict, metadata: Dict) -> str:
        """格式化Markdown内容"""
        title = content.get("title", "无标题")
        body = content.get("body", "")
        hashtags = content.get("hashtags", [])
        emojis = content.get("emojis", [])
        
        # 构建Markdown文档
        lines = [
            f"# {title}",
            "",
            body,
            "",
            # 标签
            " ".join(hashtags) if hashtags else "",
            "",
            "---",
            "",
            "## 生成信息",
            "",
            f"- **产品名称**: {metadata['product_name']}",
            f"- **文案风格**: {metadata['style']}",
            f"- **生成时间**: {metadata['generated_at']}",
        ]
        
        # 添加可选信息
        if metadata.get("target_audience"):
            lines.append(f"- **目标受众**: {metadata['target_audience']}")
        
        if metadata.get("key_features"):
            features = ", ".join(metadata["key_features"])
            lines.append(f"- **关键特性**: {features}")
        
        if emojis:
            lines.extend([
                "",
                f"**使用表情**: {' '.join(emojis)}"
            ])
        
        lines.extend([
            "",
            "---",
            "*由 DeepSeek Agent 智能生成*"
        ])
        
        return "\n".join(lines)

def main():
    """主函数 - 演示程序使用"""
    try:
        # 初始化配置
        config = Config()
        print("✅ 配置初始化完成")

        # 创建生成器和文件管理器
        generator = RedNoteGenerator(config)
        file_manager = FileManager(config)
        print("✅ 组件初始化完成")
        
        # 测试案例
        test_cases = [
            {
                "product_name": "深海蓝藻保湿面膜",
                "style": "活泼甜美",
                "target_audience": "20-30岁女性",
                "key_features": ["深层补水", "修护屏障", "温和不刺激"]
            },
            {
                "product_name": "美白精华",
                "style": "知性温柔",
                "target_audience": "25-35岁职场女性", 
                "key_features": ["提亮肤色", "淡化痘印"]
            }
        ]
    
        print(f"\n🎯 开始批量生成测试 ({len(test_cases)} 个案例)")
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*50}")
            print(f"测试案例 {i}/{len(test_cases)}")
            print(f"{'='*50}")
            
            # 生成文案
            result = generator.generate(**case)
            
            if result["success"]:
                # 保存文件
                filepath = file_manager.save_to_markdown(result)
                print(f"🎉 案例 {i} 完成，文件路径: {filepath}")
            else:
                print(f"❌ 案例 {i} 失败: {result.get('error')}")
        
        print(f"\n🏁 所有测试完成！文件保存在: {config.daily_dir}")
        
    except Exception as e:
        print(f"❌ 程序执行错误: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())