import torch
from unsloth import FastLanguageModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, GenerationConfig, DataCollatorForSeq2Seq
from datasets import Dataset

# %pip install huggingface_hub



# 定义模型和一些基本参数
max_seq_length = 8192
dtype = None # None 表示自动选择 (Float16 a T4, V100, BFloat16 a Ampere)
load_in_4bit = True # 使用 4bit 量化加载

# 这是您的模型标识符，请替换为您正在使用的模型
# 例如："qwen-1.5b_lora_model"
# model_name = "qwen-1.5b_lora_model" 
# model_name = "unsloth/DeepSeek-R1-Distill-Qwen-1.5B" 
model_name = "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-unsloth-bnb-4bit" 

# 这一步会返回一个经过 Unsloth 优化的模型和一个分词器
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 模型推理的 Prompt 模板
inference_prompt = """以下是一条描述任务的指令，并配有一个提供进一步上下文的输入。
请撰写一份恰当的回复，以完成该请求。
在回答之前，请仔细思考该问题，并构建一个分步的思考过程，以确保回应的逻辑严谨和内容准确。


### Instruction:
你是一位医学专家，在临床推理、诊断学和治疗规划方面拥有深厚的专业知识。
请回答以下医学问题。

### Question:
{}

### Response:
<think>{}
"""

FastLanguageModel.for_inference(model)

question = "男，28岁，程序员，最近一周每天工作到半夜，感觉头晕、脖子疼，有时候还恶心。"

inputs = tokenizer([inference_prompt.format(question, "")], return_tensors="pt").to("cuda")
attention_mask = inputs.input_ids.ne(tokenizer.pad_token_id).long().to("cuda")

outputs = model.generate(
    input_ids=inputs.input_ids,
    attention_mask=inputs.attention_mask,
    max_new_tokens=1200,
    use_cache=True,
)

response = tokenizer.batch_decode(outputs, skip_special_tokens=True)

print(response[0].split("### Response:")[1])

# 模型训练的 Prompt 模板
train_prompt = """以下是一条描述任务的指令，并配有一个提供进一步上下文的输入。
请撰写一份恰当的回复，以完成该请求。
在回答之前，请仔细思考该问题，并构建一个分步的思考过程，以确保回应的逻辑严谨和内容准确。


### Instruction:
你是一位医学专家，在临床推理、诊断学和治疗规划方面拥有深厚的专业知识。
请回答以下医学问题。

### Question:
{}

### Response:
<think>
{}
</think>
{}
"""

EOS_TOKEN = tokenizer.eos_token # 添加 EOS Token

def formatting_prompts_func(examples):
    inputs = examples["Question"]
    cots = examples["Complex_CoT"]
    outputs = examples["Response"]
    texts = []
    for input, cot, output in zip(inputs, cots, outputs):
        # 将 EOS Token 添加到样本最后
        text = train_prompt.format(input, cot, output) + EOS_TOKEN
        texts.append(text)
    return { "text" : texts, }
pass

from datasets import load_dataset
dataset = load_dataset("FreedomIntelligence/medical-o1-reasoning-SFT", "zh", split = "train")
dataset = dataset.map(formatting_prompts_func, batched = True,)

dataset[0]["text"]

from IPython.display import display, Markdown

display(Markdown(dataset[0]["text"]))



# 因为 `model` 对象现在是由 Unsloth 创建的，它包含了所有必需的属性
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
      "q_proj",
      "k_proj",
      "v_proj",
      "o_proj",
      "gate_proj",
      "up_proj",
      "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=1432,
    use_rslora=False,
    loftq_config=None,
)
# 检查模型结构，确认 LoRA 适配器已添加
print(model)

from trl import SFTConfig, SFTTrainer
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    packing = False, # Can make training 5x faster for short sequences.
    args = SFTConfig(
        per_device_train_batch_size = 64,
        gradient_accumulation_steps = 2,
        warmup_steps = 5,
        # num_train_epochs = 1, # Set this for 1 full training run.
        max_steps = 60,
        learning_rate = 2e-4,
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 1432,
        output_dir = "outputs",
        report_to = "none", # Use this for WandB etc
    ),
)

trainer_stats = trainer.train()

# 打印训练统计信息
print(trainer_stats)

model.save_pretrained("qwen-1.5b_lora_model")

tokenizer.save_pretrained("qwen-1.5b_lora_model")

# 模型保存方式二选一（要么使用上面的分开保存，要么使用这里的合并 Lora 保存）
# model.save_pretrained_merged("qwen-1.5b_lora_model", tokenizer, save_method="merged_16bit")

FastLanguageModel.for_inference(model) # Enable native 2x faster inference

question="一个患有急性阑尾炎的病人已经发病5天，腹痛稍有减轻但仍然发热，在体检时发现右下腹有压痛的包块，此时应如何处理？", # Question
inputs = tokenizer([inference_prompt.format(question, "")], return_tensors="pt").to("cuda")

outputs = model.generate(
    input_ids=inputs.input_ids,
    attention_mask=inputs.attention_mask,
    max_new_tokens=1000,
    use_cache=True,
)

output = tokenizer.batch_decode(outputs, skip_special_tokens=True)
print(output[0].split("### Response:")[1])

def generate_response(question: str, model, tokenizer, inference_prompt: str, max_new_tokens: int = 1024) -> str:
    """
    使用指定的模型和分词器为给定的医学问题生成响应。

    Args:
        question (str): 需要模型回答的医学问题。
        model: 已加载的 Unsloth/Hugging Face 模型。
        tokenizer: 对应的分词器。
        inference_prompt (str): 用于格式化输入的 f-string 模板。
        max_new_tokens (int, optional): 生成响应的最大 token 数量。默认为 1024。

    Returns:
        str: 模型生成的响应文本，已去除 prompt 部分。
    """
    # 1. 使用模板格式化输入
    prompt = inference_prompt.format(
        question, # 填充问题
        "",       # 留空，让模型生成 CoT 和 Response
    )

    # 2. 将格式化后的 prompt 进行分词，并转移到 GPU
    inputs = tokenizer([prompt], return_tensors="pt").to(model.device)

    # 3. 使用模型生成输出
    # use_cache=True 用于加速解码过程
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=max_new_tokens,
        use_cache=True,
    )
    
    # 4. 将生成的 token 解码为文本
    # skip_special_tokens=True 会移除像 EOS_TOKEN 这样的特殊标记
    decoded_output = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

    # 5. 切分字符串，只返回 "### Response:" 之后的部分
    # 使用 .split() 分割并获取响应内容，.strip() 用于去除可能存在的前后空白字符
    response_part = decoded_output.split("### Response:")
    if len(response_part) > 1:
        return response_part[1].strip()
    else:
        # 如果模型没有生成 "### Response:" 标记，则返回整个生成内容以供调试
        return decoded_output

my_question = "对于一名60岁男性患者，出现右侧胸疼并在X线检查中显示右侧肋膈角消失，诊断为肺结核伴右侧胸腔积液，请问哪一项实验室检查对了解胸水的性质更有帮助？"

response = generate_response(my_question, model, tokenizer, inference_prompt)
print("==================== 模型回答 ====================")
print(response)

my_question = "对于一名 28 岁的男性患者，工作是程序员，常年熬夜，最近突然感觉头晕目眩，甚至有点恶心。请问有可能是什么疾病？"

response = generate_response(my_question, model, tokenizer, inference_prompt)
print("==================== 模型回答 ====================")
print(response)

