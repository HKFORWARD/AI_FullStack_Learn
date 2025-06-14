from rednote import Config, RedNoteGenerator, FileManager

# 创建配置和生成器
config = Config()
generator = RedNoteGenerator(config)
file_manager = FileManager(config)

# 生成文案
result = generator.generate(
    product_name="深海蓝藻保湿面膜",
    style="活泼甜美",
    target_audience="20-30岁女性",
    key_features=["深层补水", "修护屏障"]
)

# 保存到文件
if result["success"]:
    filepath = file_manager.save_to_markdown(result)
    print(f"文件已保存: {filepath}")