from rednote import Config, RedNoteGenerator, FileManager

# 创建配置和生成器
config = Config()
generator = RedNoteGenerator(config)
file_manager = FileManager(config)

products = [
    # {"product_name": "美白精华", "style": "知性温柔"},
    # {"product_name": "保湿乳液", "style": "活泼甜美"},
    # {"product_name": "防晒霜", "style": "专业科普"},
    {"product_name": "玻尿酸原液", "style": "专业科普"},
    {"product_name": "防晒霜", "style": "搞怪幽默"},
    {"product_name": "男士控油洁面乳", "style": "活泼甜美"},
    {"product_name": "男士须后水", "style": "知性温柔"},
    {"product_name": "男士香水", "style": "霸气自信"},
    {"product_name": "男士护手霜", "style": "温暖治愈"},
    {"product_name": "情侣款香薰蜡烛", "style": "浪漫甜蜜"}
]

for product_info in products:
    result = generator.generate(**product_info)
    if result["success"]:
        file_manager.save_to_markdown(result)