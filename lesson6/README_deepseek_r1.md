# DeepSeek-R1:8B 小红书文案生成器使用指南

## 🚀 概述

本项目现已优化支持 DeepSeek-R1:8B 模型，这是一个强大的推理模型，特别适合生成高质量的小红书文案。

## 📋 系统要求

- Python 3.8+
- Ollama (已安装并运行)
- DeepSeek-R1:8B 模型

## 🛠️ 快速开始

### 1. 安装 Ollama 和模型

```bash
# 1. 确保 Ollama 正在运行
ollama serve

# 2. 下载 DeepSeek-R1:8B 模型
ollama pull deepseek-r1:8b

# 3. 验证模型安装
ollama list
```

### 2. 安装 Python 依赖

```bash
pip install openai python-dotenv requests
```

### 3. 快速测试

```bash
# 运行快速测试
python quick_test_deepseek_r1.py
```

### 4. 完整测试

```bash
# 运行完整的性能测试
python test_deepseek_r1.py
```

## 🎯 使用方法

### 基本使用

```python
from rednote import Config, RedNoteGenerator, FileManager

# 创建配置，指定使用 deepseek-r1:8b
config = Config(provider="ollama", ollama_model="deepseek-r1:8b")

# 创建生成器
generator = RedNoteGenerator(config)
file_manager = FileManager(config)

# 生成文案
result = generator.generate(
    product_name="玻尿酸补水精华",
    style="活泼甜美",
    target_audience="20-30岁女性",
    key_features=["深层补水", "快速吸收", "温和无刺激"]
)

# 保存结果
if result["success"]:
    filepath = file_manager.save_to_markdown(result)
    print(f"文案已保存到: {filepath}")
```

### 环境变量配置

创建 `.env` 文件：

```bash
# 指定使用 Ollama
AI_PROVIDER=ollama

# 指定模型
OLLAMA_MODEL=deepseek-r1:8b

# Ollama 服务地址（可选）
OLLAMA_BASE_URL=http://localhost:11434/v1
```

## 🎨 DeepSeek-R1:8B 特性

### 优势

- ✅ **强大推理能力**: 支持复杂的逻辑推理和创意思考
- ✅ **中文优化**: 对中文内容理解和生成能力出色
- ✅ **多轮对话**: 支持更多轮次的对话生成
- ✅ **高质量输出**: 生成的文案质量更高，更符合小红书风格

### 优化配置

本项目针对 DeepSeek-R1:8B 进行了以下优化：

1. **增强系统提示**: 利用其推理能力，使用分步骤的生成流程
2. **增加迭代次数**: 从 3 轮增加到 5 轮，充分利用其对话能力
3. **模型检测**: 自动识别 DeepSeek-R1 模型并应用相应优化

## 📊 测试结果示例

运行 `python test_deepseek_r1.py` 将生成详细的测试报告，包括：

- 成功率统计
- 平均生成时间
- 各类产品的文案质量
- 详细的生成内容示例

## 🐛 故障排除

### 常见问题

1. **模型未找到**
   ```bash
   ollama pull deepseek-r1:8b
   ```

2. **Ollama 未运行**
   ```bash
   ollama serve
   ```

3. **端口被占用**
   ```bash
   # 检查端口
   lsof -i :11434
   
   # 或修改端口
   export OLLAMA_HOST=0.0.0.0:11435
   ```

4. **生成超时**
   - DeepSeek-R1 需要较长思考时间，请耐心等待
   - 确保系统资源充足（至少 8GB RAM）

### 性能建议

- **内存**: 建议 16GB+ RAM
- **存储**: 模型占用约 5GB 空间
- **CPU**: 多核 CPU 可显著提升生成速度
- **GPU**: 如有 GPU，可显著加速推理

## 📝 输出示例

DeepSeek-R1:8B 生成的文案特点：

- 标题更具吸引力和创意
- 正文逻辑清晰，体验描述生动
- 标签选择更精准
- 整体风格更贴近真实用户分享

## 🔄 切换其他模型

如需切换到其他模型：

```python
# 切换到其他 Ollama 模型
config = Config(provider="ollama", ollama_model="qwen2.5:7b")

# 或使用 DeepSeek API
config = Config(provider="deepseek")
```

## 📈 性能对比

| 模型 | 生成质量 | 推理能力 | 中文理解 | 生成速度 |
|------|----------|----------|----------|----------|
| deepseek-r1:8b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| llama3.2 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| qwen2.5:7b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 📞 支持

如果遇到问题：

1. 查看测试报告中的详细错误信息
2. 确认 Ollama 服务状态和模型安装
3. 检查系统资源是否充足

---

*Happy writing with DeepSeek-R1:8B! 🎉* 