#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG增强的小红书文案生成器
基于 DeepSeek Agent + Milvus RAG 的智能文案生成系统

Author: AI Learning Assistant
Date: 2025-06-15
Version: 2.0
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
from pymilvus import MilvusClient, model as milvus_model
from tqdm import tqdm

# 加载环境变量
load_dotenv()


class ProductRAG:
    """产品知识库RAG系统"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.embedding_model = milvus_model.DefaultEmbeddingFunction()
        self.milvus_client = MilvusClient(uri="./product_knowledge.db")
        self.collection_name = "product_collection"
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        # 初始化时检查并创建产品知识库
        self._init_product_knowledge()
    
    def _init_product_knowledge(self):
        """初始化产品知识库"""
        # 如果集合已存在，直接返回
        if self.milvus_client.has_collection(self.collection_name):
            print("✅ 产品知识库已存在")
            return
        
        print("🔧 正在初始化产品知识库...")
        
        # 创建示例产品数据
        product_data = self._create_sample_product_data()
        
        # 生成embedding并创建集合
        self._build_knowledge_base(product_data)
        
        print("✅ 产品知识库初始化完成")
    
    def _create_sample_product_data(self) -> List[str]:
        """创建示例产品数据"""
        return [
            """深海蓝藻保湿面膜
            产品类型：面膜
            品牌：海洋之谜
            核心成分：深海蓝藻提取物、透明质酸、甘油、神经酰胺
            功效：深层补水、修护肌肤屏障、舒缓敏感泛红、提升肌肤弹性
            适用肌肤：所有肌肤类型，特别适合干燥、敏感、缺水肌肤
            质地：凝胶状，清爽不粘腻
            规格：25ml×5片装
            使用方法：洁面后取出面膜敷于面部，15-20分钟后撕下，轻拍剩余精华至吸收
            用户反馈：补水效果显著，敷完肌肤水润有光泽，敏感肌使用无刺激
            价格区间：中高端
            热门话题：沙漠干皮救星、熬夜急救面膜、水光肌养成""",
            
            """美白精华液
            产品类型：精华液
            品牌：雪花秀
            核心成分：烟酰胺3%、维生素C衍生物、熊果苷、传明酸
            功效：提亮肤色、淡化痘印、改善暗沉、均匀肤色、预防色斑
            适用肌肤：需要美白提亮的肌肤，特别适合痘印、色斑、暗沉肌肤
            质地：轻薄易吸收的乳液状
            规格：30ml
            使用方法：早晚洁面后使用，滴2-3滴于手心，轻拍至面部吸收，需配合防晒
            用户反馈：28天可见肌肤提亮，痘印明显变淡，质地温和不刺激
            价格区间：中高端
            热门话题：冷白皮养成、痘印救星、熬夜暗沉急救""",
            
            """玻尿酸原液
            产品类型：原液/精华
            品牌：润百颜
            核心成分：多重分子量玻尿酸、小分子透明质酸、大分子透明质酸
            功效：强效补水、锁水保湿、丰盈肌肤、改善细纹
            适用肌肤：所有肌肤类型，特别是缺水、干燥、有细纹的肌肤
            质地：清透水状，快速渗透
            规格：15ml
            使用方法：洁面爽肤后使用，滴3-5滴于面部，轻拍至吸收
            用户反馈：补水效果立竿见影，肌肤饱满有弹性，性价比很高
            价格区间：平价
            热门话题：玻尿酸补水、平价好物、学生党必备""",
            
            """男士控油洁面乳
            产品类型：洁面乳
            品牌：理肤泉
            核心成分：水杨酸、茶树精油、竹炭、薄荷提取物
            功效：深层清洁、控油去黑头、收缩毛孔、清爽洁净
            适用肌肤：油性肌肤、混合性肌肤、毛孔粗大、黑头较多的肌肤
            质地：泡沫丰富的膏状
            规格：150ml
            使用方法：早晚使用，取适量加水搓泡后按摩面部，用清水冲洗干净
            用户反馈：清洁力强，控油效果好，用后肌肤清爽不紧绷
            价格区间：中端
            热门话题：男士护肤、控油清洁、黑头清洁""",
            
            """防晒霜SPF50+
            产品类型：防晒霜
            品牌：安耐晒
            核心成分：氧化锌、二氧化钛、透明质酸、维生素E
            功效：广谱防晒、防水防汗、保湿滋润、预防光老化
            适用肌肤：所有肌肤类型，特别适合户外活动、运动场景
            质地：轻薄乳液状，不泛白
            规格：60ml
            使用方法：出门前20分钟涂抹，需定时补涂，卸妆时需用卸妆产品
            用户反馈：防晒效果强，不搓泥不泛白，适合日常和户外使用
            价格区间：中高端
            热门话题：硬核防晒、户外必备、防晒不泛白"""
        ]
    
    def _build_knowledge_base(self, product_data: List[str]):
        """构建产品知识库"""
        # 生成测试embedding获取维度
        test_embedding = self.embedding_model.encode_queries(["test"])[0]
        embedding_dim = len(test_embedding)
        
        # 创建集合
        self.milvus_client.create_collection(
            collection_name=self.collection_name,
            dimension=embedding_dim,
            metric_type="IP",  # 内积距离
            consistency_level="Strong"
        )
        
        # 生成embeddings并插入数据
        print("🔄 正在生成产品数据embeddings...")
        doc_embeddings = self.embedding_model.encode_documents(product_data)
        
        data = []
        for i, (product_text, embedding) in enumerate(zip(product_data, doc_embeddings)):
            data.append({
                "id": i,
                "vector": embedding,
                "product_info": product_text
            })
        
        self.milvus_client.insert(collection_name=self.collection_name, data=data)
        print(f"✅ 已插入 {len(data)} 个产品数据")
    
    def query_product_database(self, product_name: str) -> str:
        """
        基于RAG的产品数据库查询
        
        Args:
            product_name: 产品名称
            
        Returns:
            产品详细信息
        """
        print(f"🔍 [RAG Tool] 查询产品: {product_name}")
        
        try:
            # 使用embedding搜索相关产品
            search_res = self.milvus_client.search(
                collection_name=self.collection_name,
                data=self.embedding_model.encode_queries([product_name]),
                limit=2,  # 返回最相关的2个结果
                search_params={"metric_type": "IP", "params": {}},
                output_fields=["product_info"]
            )
            
            if not search_res[0]:
                return f"未找到关于'{product_name}'的产品信息"
            
            # 提取检索到的产品信息
            retrieved_products = [
                (res["entity"]["product_info"], res["distance"]) 
                for res in search_res[0]
            ]
            
            # 使用LLM进行信息整合和生成
            context = "\n\n".join([info for info, _ in retrieved_products])
            
            system_prompt = """
            你是一个产品信息专家。请根据提供的产品信息，为用户查询的产品生成详细、准确的介绍。
            重点突出产品的核心卖点、适用人群和使用体验。语言要专业但易懂。
            """
            
            user_prompt = f"""
            基于以下产品信息，为'{product_name}'生成详细介绍：

            {context}

            请生成包含以下要点的产品介绍：
            1. 核心成分和功效
            2. 适用肌肤类型
            3. 使用方法和体验
            4. 用户反馈亮点
            5. 推荐理由
            """
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            print(f"📋 RAG查询结果: {result[:100]}...")
            return result
            
        except Exception as e:
            print(f"❌ RAG查询错误: {e}")
            return f"查询产品'{product_name}'时发生错误，请稍后重试"
    
    def add_product(self, product_info: str):
        """添加新产品到知识库"""
        try:
            # 生成embedding
            embedding = self.embedding_model.encode_documents([product_info])[0]
            
            # 获取当前最大ID
            current_count = self.milvus_client.query(
                collection_name=self.collection_name,
                expr="id >= 0",
                output_fields=["id"]
            )
            
            max_id = max([item["id"] for item in current_count]) if current_count else -1
            new_id = max_id + 1
            
            # 插入新产品
            data = [{
                "id": new_id,
                "vector": embedding,
                "product_info": product_info
            }]
            
            self.milvus_client.insert(collection_name=self.collection_name, data=data)
            print(f"✅ 已添加新产品到知识库，ID: {new_id}")
            
        except Exception as e:
            print(f"❌ 添加产品失败: {e}")


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
    """增强的工具管理类 - 集成RAG产品查询"""
    
    def __init__(self, api_key: str):
        self.product_rag = ProductRAG(api_key)
    
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
    
    def query_product_database(self, product_name: str) -> str:
        """基于RAG的真实产品数据库查询"""
        return self.product_rag.query_product_database(product_name)
    
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
        self.tool_manager = ToolManager(config.api_key)  # 传入API密钥
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
                    "description": "查询RAG增强的产品数据库，获取产品详细信息、卖点、成分等",
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
                    "generated_at": datetime.now().isoformat(),
                    "rag_enhanced": True
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
                    print(f"📤 工具结果: {tool_result[:100] if len(str(tool_result)) > 100 else tool_result}")
                    
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
        
        # 添加RAG标识
        rag_suffix = "_RAG" if metadata.get("rag_enhanced") else ""
        
        return f"{clean_product}_{clean_style}_{timestamp}{rag_suffix}.md"

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
            f"- **RAG增强**: {'是' if metadata.get('rag_enhanced') else '否'}",
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
            "*由 DeepSeek Agent + Milvus RAG 智能生成*"
        ])
        
        return "\n".join(lines)

    def format_rednote_for_markdown(self, json_string: str) -> str:
        """
        将 JSON 格式的小红书文案转换为 Markdown 格式，以便于阅读和发布。
        
        Args:
            json_string (str): 包含小红书文案的 JSON 字符串。
                               预计格式为 {"title": "...", "body": "...", "hashtags": [...], "emojis": [...]}
        
        Returns:
            str: 格式化后的 Markdown 文本。
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            return f"错误：无法解析 JSON 字符串 - {e}\n原始字符串：\n{json_string}"

        title = data.get("title", "无标题")
        body = data.get("body", "")
        hashtags = data.get("hashtags", [])
        
        # 构建 Markdown 文本
        markdown_output = f"## {title}\n\n"
        
        # 正文，保留换行符
        markdown_output += f"{body}\n\n"
        
        # Hashtags
        if hashtags:
            hashtag_string = " ".join(hashtags)
            markdown_output += f"{hashtag_string}\n"
        
        return markdown_output.strip()


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
        print("🔧 RAG产品知识库已就绪")
        
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
            },
            {
                "product_name": "玻尿酸原液",
                "style": "专业科普",
                "target_audience": "护肤爱好者",
                "key_features": ["强效补水", "多重分子量", "性价比高"]
            }
        ]
    
        print(f"\n🎯 开始RAG增强的批量生成测试 ({len(test_cases)} 个案例)")
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*50}")
            print(f"测试案例 {i}/{len(test_cases)}")
            print(f"{'='*50}")
            
            # 生成文案
            result = generator.generate(**case)
            
            if result["success"]:
                # 保存文件
                filepath = file_manager.save_to_markdown(result)
                
                # 格式化输出预览
                formatted_content = file_manager.format_rednote_for_markdown(
                    json.dumps(result["content"], ensure_ascii=False, indent=2)
                )
                
                print(f"\n📝 生成的文案预览:")
                print("=" * 40)
                print(formatted_content)
                print("=" * 40)
                
                print(f"🎉 案例 {i} 完成，文件路径: {filepath}")
            else:
                print(f"❌ 案例 {i} 失败: {result.get('error')}")
        
        print(f"\n🏁 所有测试完成！文件保存在: {config.daily_dir}")
        
        # 演示RAG知识库扩展功能
        print(f"\n🔧 演示RAG知识库扩展...")
        new_product = """
        维生素C精华
        产品类型：精华液
        品牌：修丽可
        核心成分：15%左旋维生素C、维生素E、阿魏酸
        功效：抗氧化、提亮肤色、促进胶原蛋白生成、淡化色斑
        适用肌肤：需要抗氧化和提亮的肌肤，建议有一定护肤基础
        质地：略粘稠的精华液
        规格：30ml
        使用方法：早晨使用，避光保存，需配合防晒
        用户反馈：抗氧化效果显著，长期使用肌肤更有光泽
        价格区间：高端
        热门话题：抗氧化精华、维C护肤、抗老必备
        """
        
        generator.tool_manager.product_rag.add_product(new_product)
        
        # 测试新添加的产品
        print(f"\n🧪 测试新添加的产品...")
        test_result = generator.generate(
            product_name="维生素C精华",
            style="专业推荐",
            target_audience="护肤进阶用户",
            key_features=["抗氧化", "提亮", "抗老"]
        )
        
        if test_result["success"]:
            filepath = file_manager.save_to_markdown(test_result)
            print(f"✅ 新产品文案生成成功: {filepath}")
        
    except Exception as e:
        print(f"❌ 程序执行错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())