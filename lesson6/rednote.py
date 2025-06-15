#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小红书文案生成器 - 修复版
基于 DeepSeek Agent 的智能文案生成系统（修复 Ollama 兼容性问题）

Author: AI Learning Assistant
Date: 2025-06-14
Version: 1.1 (Ollama 修复版)
"""

import os
import json
import re
import time
import random
import requests  # 用于验证 Ollama 服务连接
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置管理类"""
    
    def __init__(self, provider: str = None, ollama_model: str = None):
        # 服务提供商选择：deepseek 或 ollama
        self.provider = provider or os.getenv("AI_PROVIDER", "ollama").lower()  # 默认改为 ollama
        
        # DeepSeek 配置
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        self.deepseek_model = "deepseek-chat"
        
        # Ollama 配置 - 修复 URL 格式
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")  # 默认使用 deepseek-r1:8b
        
        # 通用配置
        self.max_iterations = 5 if self.provider == "ollama" and "deepseek-r1" in self.ollama_model else 3  # DeepSeek-R1 支持更多轮对话
        self.output_dir = Path("output")
        self.default_style = "活泼甜美"
        
        # 动态配置当前使用的服务
        self._configure_current_provider()
        
        # 创建输出目录
        self.ensure_output_dir()
    
    def _configure_current_provider(self):
        """根据选择的 provider 配置当前服务参数"""
        if self.provider == "ollama":
            self.api_key = "ollama"  # Ollama 不需要真实 API key
            self.base_url = self.ollama_base_url
            self.model = self.ollama_model
            print(f"🤖 使用 Ollama 本地模型: {self.ollama_model}")
            
            # 验证 Ollama 服务
            self._validate_ollama_service()
            
        elif self.provider == "deepseek":
            if not self.deepseek_api_key:
                raise ValueError("使用 DeepSeek 服务需要设置 DEEPSEEK_API_KEY 环境变量")
            
            self.api_key = self.deepseek_api_key
            self.base_url = self.deepseek_base_url
            self.model = self.deepseek_model
            print(f"🌐 使用 DeepSeek API 服务: {self.deepseek_model}")
            
        else:
            raise ValueError(f"不支持的服务提供商: {self.provider}，请选择 'deepseek' 或 'ollama'")
    
    def _validate_ollama_service(self):
        """验证 Ollama 服务是否可用 - 改进版"""
        try:
            # 修复：使用正确的 Ollama API endpoint
            tags_url = f"{self.ollama_base_url.replace('/v1', '')}/api/tags"
            print(f"🔍 检查 Ollama 服务: {tags_url}")
            
            response = requests.get(tags_url, timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model["name"] for model in models_data.get("models", [])]
                
                if available_models:
                    print(f"✅ 发现 {len(available_models)} 个可用模型: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}")
                    
                    # 检查指定模型是否存在
                    if not any(self.ollama_model in model for model in available_models):
                        print(f"⚠️ 警告: 模型 {self.ollama_model} 未找到")
                        print(f"💡 建议使用以下模型之一: {', '.join(available_models[:3])}")
                        
                        # 特别提示 DeepSeek-R1 模型
                        if "deepseek-r1" in self.ollama_model:
                            print(f"🤖 DeepSeek-R1 模型下载命令: ollama pull {self.ollama_model}")
                        
                        # 自动选择第一个可用模型
                        if available_models:
                            self.ollama_model = available_models[0]
                            self.model = self.ollama_model
                            print(f"🔄 自动切换到: {self.ollama_model}")
                    else:
                        print(f"✅ 模型验证通过: {self.ollama_model}")
                        if "deepseek-r1" in self.ollama_model:
                            print(f"🧠 使用 DeepSeek-R1 推理模型，支持复杂推理任务")
                else:
                    print(f"⚠️ 警告: 未发现任何已安装的模型")
            else:
                print(f"⚠️ 警告: Ollama 服务响应异常 (状态码: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 错误: 无法连接到 Ollama 服务 ({self.ollama_base_url})")
            print(f"💡 请确保 Ollama 正在运行: ollama serve")
        except requests.exceptions.Timeout:
            print(f"⚠️ 警告: Ollama 服务连接超时")
        except Exception as e:
            print(f"⚠️ 警告: Ollama 服务检查失败: {e}")
    
    def switch_to_ollama(self, model_name: str = None):
        """切换到 Ollama 服务并可选择指定模型"""
        self.provider = "ollama"
        if model_name:
            self.ollama_model = model_name
        self._configure_current_provider()
        print(f"🔄 已切换到 Ollama: {self.ollama_model}")
    
    def switch_to_deepseek(self):
        """切换到 DeepSeek 服务"""
        self.provider = "deepseek"
        self._configure_current_provider()
        print(f"🔄 已切换到 DeepSeek: {self.deepseek_model}")
    
    def list_available_ollama_models(self) -> List[str]:
        """获取可用的 Ollama 模型列表"""
        try:
            tags_url = f"{self.ollama_base_url.replace('/v1', '')}/api/tags"
            response = requests.get(tags_url, timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                return [model["name"] for model in models_data.get("models", [])]
        except Exception as e:
            print(f"获取 Ollama 模型列表失败: {e}")
        return []

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
        """初始化OpenAI客户端 - 修复 Ollama 兼容性"""
        try:
            # 修复：为 Ollama 设置更合理的超时时间
            timeout_settings = 60.0 if self.config.provider == "ollama" else 30.0
            
            client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=timeout_settings
            )
            
            # 测试连接
            print(f"🔗 连接到 {self.config.provider.upper()}: {self.config.base_url}")
            
            # 修复：为 Ollama 进行连接测试
            if self.config.provider == "ollama":
                self._test_ollama_connection(client)
                
            return client
            
        except Exception as e:
            print(f"❌ 客户端初始化失败: {e}")
            raise
    
    def _test_ollama_connection(self, client: OpenAI):
        """测试 Ollama 连接"""
        try:
            print(f"🧪 测试 Ollama 连接...")
            # 发送一个简单的测试请求
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "你好，请回复'连接成功'"}],
                max_tokens=50,
                temperature=0.1
            )
            
            if response.choices[0].message.content:
                print(f"✅ Ollama 连接测试成功！")
            else:
                print(f"⚠️ Ollama 连接测试返回空内容")
                
        except Exception as e:
            print(f"❌ Ollama 连接测试失败: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词 - 为 Ollama 优化"""
        if self.config.provider == "ollama":
            # 为 DeepSeek-R1 模型使用增强的系统提示
            if "deepseek-r1" in self.config.model:
                return """你是一个专业的小红书文案专家，具备深度推理能力，擅长创作高质量的笔记文案。

请按照以下步骤分析和生成文案：

1. 首先分析产品特点和目标受众
2. 思考最吸引人的卖点和表达方式
3. 生成完整的小红书笔记内容

最终输出格式：
```json
{
  "title": "吸引人的标题（带表情符号）",
  "body": "真实有趣的正文内容（包含产品体验、效果描述、使用感受）",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["✨", "🔥", "💖", "💧"]
}
```

要求：
- 标题要有吸引力，包含关键卖点
- 正文要真实自然，像真人分享体验
- 标签要精准相关，有助于传播
- 语言风格要活泼、真诚、有感染力""".strip()
            else:
                # 为其他 Ollama 模型使用简洁的系统提示
                return """你是一个小红书文案专家，擅长创作吸引人的笔记文案。

请根据用户提供的产品信息，生成完整的小红书笔记，包含：
1. 吸引人的标题（带表情符号）
2. 真实有趣的正文内容
3. 5个相关标签
4. 4个表情符号

请以JSON格式输出：
```json
{
  "title": "标题内容",
  "body": "正文内容",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["✨", "🔥", "💖", "💧"]
}
```

语言风格要活泼、真诚、有感染力。""".strip()
        else:
            # DeepSeek 使用原版系统提示
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
```
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
        print(f"🤖 使用模型: {self.config.provider} - {self.config.model}")
        
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
                    "generated_at": datetime.now().isoformat(),
                    "provider": self.config.provider,
                    "model": self.config.model
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
        """执行生成循环（ReAct模式）- 修复 Ollama 兼容性"""
        iteration_count = 0
        
        while iteration_count < self.config.max_iterations:
            iteration_count += 1
            print(f"\n--- 第 {iteration_count} 轮推理 ---")
            
            try:
                # 根据 provider 决定是否使用工具
                use_tools = self.config.provider == "deepseek"
                
                # 对于 DeepSeek-R1 模型，即使在 Ollama 中也启用多轮推理
                enable_multi_turn = (self.config.provider == "deepseek" or 
                                    (self.config.provider == "ollama" and "deepseek-r1" in self.config.model))
                
                if use_tools:
                    # DeepSeek 支持工具调用
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=messages,
                        tools=self.tools_definition,
                        tool_choice="auto",
                        temperature=0.7,
                        max_tokens=2000
                    )
                else:
                    # Ollama 不支持工具调用，使用简化的方式
                    simplified_messages = self._simplify_messages_for_ollama(messages)
                    
                    # 修复：为 Ollama 添加更多参数
                    response = self.client.chat.completions.create(
                        model=self.config.model,
                        messages=simplified_messages,
                        temperature=0.7,
                        max_tokens=2000,
                        stream=False  # 确保不使用流式输出
                    )
                
                response_message = response.choices[0].message
                
                # 处理工具调用（仅 DeepSeek）
                if use_tools and response_message.tool_calls:
                    print("🤖 Agent决定调用工具...")
                    messages.append({
                        "role": "assistant",
                        "content": response_message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            } for tool_call in response_message.tool_calls
                        ]
                    })
                    
                    # 执行所有工具调用
                    tool_outputs = self._execute_tool_calls(response_message.tool_calls)
                    messages.extend(tool_outputs)
                
                # 处理最终内容
                elif response_message.content:
                    if use_tools:
                        print(f"💭 Agent生成内容")
                    else:
                        model_info = f"DeepSeek-R1 推理模式" if "deepseek-r1" in self.config.model else "Ollama 直接生成"
                        print(f"🤖 {model_info}")
                    
                    # 尝试解析JSON内容
                    result = self._extract_json_content(response_message.content)
                    if result:
                        return result
                    else:
                        # 解析失败，根据模型能力决定是否继续多轮推理
                        messages.append({
                            "role": "assistant",
                            "content": response_message.content
                        })
                        
                        if enable_multi_turn:
                            # 支持多轮推理的模型，提供更详细的引导
                            if "deepseek-r1" in self.config.model:
                                guidance = """让我重新分析和生成文案。请按照以下步骤：

1. 分析产品的核心卖点和目标用户
2. 构思吸引人的标题和生动的内容描述  
3. 选择合适的标签和表情符号

最终请以标准JSON格式输出：
```json
{
  "title": "标题（包含表情符号）",
  "body": "正文内容（真实体验分享）",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["✨", "🔥", "💖", "💧"]
}
```"""
                            else:
                                guidance = "请重新分析产品特点，生成更高质量的小红书文案，确保以完整的JSON格式输出。"
                        else:
                            # 普通 Ollama 模型，简单重新生成
                            guidance = "请确保以完整的JSON格式输出文案，格式为：```json\n{\"title\": \"...\", \"body\": \"...\", \"hashtags\": [...], \"emojis\": [...]}\n```"
                        
                        messages.append({
                            "role": "user", 
                            "content": guidance
                        })
                        print("⚠️ JSON解析失败，启用多轮推理优化...")
                
                else:
                    print("❓ 未知响应类型")
                    break
                    
            except Exception as e:
                print(f"❌ API调用错误: {e}")
                # 修复：在 Ollama 失败时提供更详细的错误信息
                if self.config.provider == "ollama":
                    print("💡 Ollama 错误排查建议：")
                    print("   1. 检查 Ollama 是否正在运行: ollama serve")
                    print("   2. 检查模型是否已下载: ollama list")
                    print(f"   3. 尝试拉取模型: ollama pull {self.config.model}")
                break
        
        print(f"\n⚠️ 达到最大迭代次数 ({self.config.max_iterations})，生成失败")
        return None

    def _simplify_messages_for_ollama(self, messages: List[Dict]) -> List[Dict]:
        """为 Ollama 简化消息，移除工具相关内容"""
        simplified = []
        
        for message in messages:
            if message["role"] in ["system", "user"]:
                simplified.append(message)
            elif message["role"] == "assistant" and message.get("content"):
                # 保留助手的文本回复，跳过工具调用
                simplified.append({
                    "role": "assistant",
                    "content": message["content"]
                })
        
        return simplified

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
        """从响应中提取JSON内容 - 改进版"""
        # 尝试多种JSON提取方式
        extraction_patterns = [
            # 标准markdown json代码块
            r"```json\s*(\{.*?\})\s*```",
            # 没有语言标识的代码块
            r"```\s*(\{.*?\})\s*```",
            # 直接的JSON对象
            r"(\{[^{}]*\"title\"[^{}]*\"body\"[^{}]*\"hashtags\"[^{}]*\"emojis\"[^{}]*\})",
            # 更宽松的JSON匹配
            r"(\{.*?\"title\".*?\})"
        ]
        
        for pattern in extraction_patterns:
            json_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if json_match:
                json_str = json_match.group(1)
                try:
                    result = json.loads(json_str)
                    # 验证必要字段
                    if all(key in result for key in ["title", "body", "hashtags", "emojis"]):
                        print("✅ JSON解析成功")
                        return result
                except json.JSONDecodeError:
                    continue
        
        # 如果所有正则都失败，尝试修复常见的JSON问题
        cleaned_content = self._clean_json_content(content)
        if cleaned_content:
            try:
                result = json.loads(cleaned_content)
                if all(key in result for key in ["title", "body", "hashtags", "emojis"]):
                    print("✅ JSON修复并解析成功")
                    return result
            except json.JSONDecodeError:
                pass
        
        print(f"❌ JSON解析失败，原始内容: {content[:200]}...")
        return None
    
    def _clean_json_content(self, content: str) -> Optional[str]:
        """尝试清理和修复JSON内容"""
        # 查找可能的JSON开始和结束
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            return None
        
        json_str = content[start_idx:end_idx + 1]
        
        # 基本清理
        json_str = json_str.strip()
        
        # 修复常见问题
        replacements = [
            (r'"\s*:\s*"([^"]*?)"\s*,?\s*\n', r'": "\1",\n'),  # 修复引号问题
            (r',\s*}', r'}'),  # 移除尾随逗号
            (r',\s*]', r']'),  # 移除数组尾随逗号
        ]
        
        for pattern, replacement in replacements:
            json_str = re.sub(pattern, replacement, json_str)
        
        return json_str
    
    def switch_model(self, model_name: str):
        """切换 Ollama 模型（仅在使用 Ollama 时有效）"""
        if self.config.provider == "ollama":
            old_model = self.config.ollama_model
            self.config.ollama_model = model_name
            self.config.model = model_name
            print(f"🔄 Ollama 模型已切换: {old_model} → {model_name}")
            
            # 重新初始化客户端以测试新模型
            try:
                self._test_ollama_connection(self.client)
            except Exception as e:
                print(f"⚠️ 新模型测试失败，回滚到原模型: {e}")
                self.config.ollama_model = old_model
                self.config.model = old_model
        else:
            print("⚠️ 只有在使用 Ollama 时才能切换模型")


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
        provider = metadata.get("provider", "unknown")
        timestamp = datetime.now().strftime("%H%M%S")
        
        # 清理文件名中的特殊字符
        clean_product = re.sub(r'[<>:"/\\|?*]', '_', product_name)
        
        return f"{clean_product}_{provider}_{timestamp}.md"

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
            f"- **生成模型**: {metadata.get('provider', 'unknown')} - {metadata.get('model', 'unknown')}",
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
            "*由 AI 智能生成*"
        ])
        
        return "\n".join(lines)


def quick_test_ollama():
    """快速测试 Ollama 连接的函数"""
    print("🧪 快速测试 Ollama 连接...")
    
    try:
        config = Config(provider="ollama")
        available_models = config.list_available_ollama_models()
        
        if not available_models:
            print("❌ 未发现任何 Ollama 模型")
            print("💡 请先下载模型，例如: ollama pull llama3.2")
            return False
        
        print(f"✅ 发现 {len(available_models)} 个模型: {', '.join(available_models)}")
        
        # 尝试创建生成器
        generator = RedNoteGenerator(config)
        print("✅ Ollama 配置成功！")
        return True
        
    except Exception as e:
        print(f"❌ Ollama 测试失败: {e}")
        return False


def main():
    """主函数 - 修复版本"""
    try:
        print("🚀 小红书文案生成器 - 修复版")
        print("=" * 50)
        
        # 首先测试 Ollama 连接
        if not quick_test_ollama():
            print("\n💡 Ollama 故障排除建议:")
            print("1. 启动 Ollama 服务: ollama serve")
            print("2. 下载模型: ollama pull llama3.2")
            print("3. 检查模型列表: ollama list")
            print("4. 检查端口: 确保 11434 端口未被占用")
            return 1
        
        # ======== 使用 Ollama 本地模型 ========
        print(f"\n🤖 使用 Ollama 本地模型")
        print("-" * 30)
        
        ollama_config = Config(provider="ollama")
        ollama_generator = RedNoteGenerator(ollama_config)
        ollama_file_manager = FileManager(ollama_config)
        
        # ======== 测试案例 ========
        test_case = {
            "product_name": "深海蓝藻保湿面膜",
            "style": "活泼甜美",
            "target_audience": "20-30岁女性",
            "key_features": ["深层补水", "修护屏障", "温和不刺激"]
        }
        
        print(f"\n🎯 开始测试文案生成")
        print(f"📦 测试产品: {test_case['product_name']}")
        
        # ======== 测试 Ollama ========
        result_ollama = ollama_generator.generate(**test_case)
        
        if result_ollama["success"]:
            filepath_ollama = ollama_file_manager.save_to_markdown(result_ollama)
            print(f"✅ Ollama 生成成功，文件: {filepath_ollama}")
            
            # 显示生成的内容
            content = result_ollama["content"]
            print(f"\n📝 生成的文案预览:")
            print(f"标题: {content['title']}")
            print(f"正文: {content['body'][:100]}...")
            print(f"标签: {' '.join(content['hashtags'])}")
            
        else:
            print(f"❌ Ollama 生成失败: {result_ollama.get('error')}")
            return 1
        
        # ======== 测试 DeepSeek（如果可用） ========
        try:
            print(f"\n🌐 测试 DeepSeek API")
            print("-" * 30)
            
            deepseek_config = Config(provider="deepseek")
            deepseek_generator = RedNoteGenerator(deepseek_config)
            deepseek_file_manager = FileManager(deepseek_config)
            
            result_deepseek = deepseek_generator.generate(**test_case)
            
            if result_deepseek["success"]:
                filepath_deepseek = deepseek_file_manager.save_to_markdown(result_deepseek)
                print(f"✅ DeepSeek 生成成功，文件: {filepath_deepseek}")
            else:
                print(f"❌ DeepSeek 生成失败: {result_deepseek.get('error')}")
                
        except ValueError as e:
            print(f"⚠️ DeepSeek API 不可用: {e}")
        
        print(f"\n🏁 测试完成！输出文件保存在: output/")
        return 0
        
    except Exception as e:
        print(f"❌ 程序执行错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


# ======== 使用示例函数 ========
def demo_usage():
    """使用示例演示"""
    print("📚 修复版使用指南:")
    print("=" * 50)
    
    print("\n🔧 修复的主要问题:")
    print("1. ✅ 改进了 Ollama 连接验证逻辑")
    print("2. ✅ 优化了错误处理和超时设置")
    print("3. ✅ 增强了 JSON 解析的容错性")
    print("4. ✅ 添加了自动模型选择功能")
    print("5. ✅ 改进了系统提示词的兼容性")
    
    print("\n🚀 使用步骤:")
    print("1. 确保 Ollama 正在运行: ollama serve")
    print("2. 下载所需模型: ollama pull llama3.2")
    print("3. 运行程序: python xiaohongshu_generator.py")
    
    print("\n🎯 推荐的 Ollama 模型:")
    print("- llama3.2 (通用，推荐)")
    print("- qwen2.5 (中文优化)")
    print("- deepseek-r1 (如果可用)")
    
    print("\n🔧 环境变量配置:")
    print("export AI_PROVIDER=ollama")
    print("export OLLAMA_MODEL=llama3.2")
    print("export OLLAMA_BASE_URL=http://localhost:11434/v1")


if __name__ == "__main__":
    # 显示使用示例
    demo_usage()
    print("\n")
    
    # 运行主程序
    exit(main())