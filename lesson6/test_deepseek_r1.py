#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek-R1:8B 模型测试脚本
专门用来测试 Ollama 上的 deepseek-r1:8b 模型的小红书文案生成能力

Author: AI Learning Assistant
Date: 2025-01-27
Version: 1.0
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# 导入主模块
from rednote import Config, RedNoteGenerator, FileManager


class DeepSeekR1Tester:
    """DeepSeek-R1:8B 模型专用测试器"""
    
    def __init__(self):
        self.model_name = "deepseek-r1:8b"
        self.test_results = []
        
    def check_model_availability(self) -> bool:
        """检查 deepseek-r1:8b 模型是否可用"""
        print(f"🔍 检查 {self.model_name} 模型可用性...")
        
        try:
            config = Config(provider="ollama", ollama_model=self.model_name)
            available_models = config.list_available_ollama_models()
            
            if not available_models:
                print("❌ 无法获取 Ollama 模型列表")
                return False
            
            # 检查是否有 deepseek-r1 相关模型
            deepseek_models = [m for m in available_models if "deepseek-r1" in m.lower()]
            
            if not deepseek_models:
                print(f"❌ 未找到 {self.model_name} 模型")
                print("💡 请先下载模型：ollama pull deepseek-r1:8b")
                return False
            
            print(f"✅ 找到 DeepSeek-R1 模型：{', '.join(deepseek_models)}")
            
            # 如果找到了完全匹配的模型，使用它
            if self.model_name in available_models:
                print(f"✅ 发现完全匹配的模型：{self.model_name}")
                return True
            else:
                # 使用找到的第一个 deepseek-r1 模型
                self.model_name = deepseek_models[0]
                print(f"🔄 使用找到的模型：{self.model_name}")
                return True
                
        except Exception as e:
            print(f"❌ 模型检查失败：{e}")
            return False
    
    def test_basic_connection(self) -> bool:
        """测试基本连接"""
        print(f"\n🧪 测试基本连接...")
        
        try:
            config = Config(provider="ollama", ollama_model=self.model_name)
            generator = RedNoteGenerator(config)
            
            print(f"✅ 成功初始化 {self.model_name} 生成器")
            return True
            
        except Exception as e:
            print(f"❌ 连接测试失败：{e}")
            return False
    
    def run_generation_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个生成测试"""
        print(f"\n🎯 测试案例：{test_case['name']}")
        print(f"📦 产品：{test_case['product_name']}")
        
        start_time = time.time()
        
        try:
            # 创建配置和生成器
            config = Config(provider="ollama", ollama_model=self.model_name)
            generator = RedNoteGenerator(config)
            file_manager = FileManager(config)
            
            # 生成文案
            result = generator.generate(
                product_name=test_case['product_name'],
                style=test_case.get('style'),
                target_audience=test_case.get('target_audience'),
                key_features=test_case.get('key_features')
            )
            
            generation_time = time.time() - start_time
            
            if result["success"]:
                # 保存文件
                filepath = file_manager.save_to_markdown(result)
                
                # 记录测试结果
                test_result = {
                    "test_name": test_case['name'],
                    "success": True,
                    "generation_time": round(generation_time, 2),
                    "filepath": filepath,
                    "content": result["content"],
                    "metadata": result["metadata"]
                }
                
                print(f"✅ 生成成功，耗时：{generation_time:.2f}秒")
                print(f"📄 文件：{filepath}")
                
                return test_result
                
            else:
                print(f"❌ 生成失败：{result.get('error')}")
                return {
                    "test_name": test_case['name'],
                    "success": False,
                    "error": result.get('error'),
                    "generation_time": round(generation_time, 2)
                }
                
        except Exception as e:
            generation_time = time.time() - start_time
            print(f"❌ 测试执行失败：{e}")
            return {
                "test_name": test_case['name'],
                "success": False,
                "error": str(e),
                "generation_time": round(generation_time, 2)
            }
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """运行全面测试"""
        print(f"\n🚀 开始 {self.model_name} 全面测试")
        print("=" * 60)
        
        # 定义测试案例
        test_cases = [
            {
                "name": "基础护肤产品",
                "product_name": "玻尿酸补水精华",
                "style": "活泼甜美",
                "target_audience": "20-30岁女性",
                "key_features": ["深层补水", "快速吸收", "温和无刺激"]
            },
            {
                "name": "美白产品",
                "product_name": "维C美白面膜",
                "style": "知性温柔",
                "target_audience": "25-35岁职场女性",
                "key_features": ["提亮肤色", "淡化痘印", "抗氧化"]
            },
            {
                "name": "抗老产品",
                "product_name": "胶原蛋白抗衰精华",
                "style": "专业可信",
                "target_audience": "30-45岁成熟女性",
                "key_features": ["紧致肌肤", "减少细纹", "提升弹性"]
            },
            {
                "name": "敏感肌产品",
                "product_name": "舒缓修护乳液",
                "style": "温和亲切",
                "target_audience": "敏感肌人群",
                "key_features": ["舒缓敏感", "修护屏障", "无香料"]
            }
        ]
        
        # 运行所有测试
        total_tests = len(test_cases)
        successful_tests = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n进度：{i}/{total_tests}")
            result = self.run_generation_test(test_case)
            self.test_results.append(result)
            
            if result["success"]:
                successful_tests += 1
                
                # 显示生成内容预览
                content = result["content"]
                print(f"📝 内容预览：")
                print(f"   标题：{content['title']}")
                print(f"   正文：{content['body'][:80]}...")
                print(f"   标签：{' '.join(content['hashtags'][:3])}...")
            
            # 短暂休息避免过载
            if i < total_tests:
                time.sleep(2)
        
        # 生成测试报告
        return self.generate_test_report(successful_tests, total_tests)
    
    def generate_test_report(self, successful_tests: int, total_tests: int) -> Dict[str, Any]:
        """生成测试报告"""
        print(f"\n📊 生成测试报告...")
        
        # 计算统计信息
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        successful_results = [r for r in self.test_results if r["success"]]
        avg_generation_time = sum(r["generation_time"] for r in successful_results) / len(successful_results) if successful_results else 0
        
        # 创建报告
        report = {
            "model_name": self.model_name,
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": round(success_rate, 2),
            "avg_generation_time": round(avg_generation_time, 2),
            "test_results": self.test_results
        }
        
        # 保存报告
        self.save_test_report(report)
        
        return report
    
    def save_test_report(self, report: Dict[str, Any]):
        """保存测试报告"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"deepseek_r1_test_report_{timestamp}.md"
        
        # 生成 Markdown 报告
        markdown_content = self.format_test_report_markdown(report)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📄 测试报告已保存：{report_file}")
    
    def format_test_report_markdown(self, report: Dict[str, Any]) -> str:
        """格式化测试报告为 Markdown"""
        lines = [
            f"# DeepSeek-R1:8B 模型测试报告",
            "",
            f"## 测试概况",
            "",
            f"- **测试模型**: {report['model_name']}",
            f"- **测试时间**: {report['test_time']}",
            f"- **总测试数**: {report['total_tests']}",
            f"- **成功测试数**: {report['successful_tests']}",
            f"- **失败测试数**: {report['failed_tests']}",
            f"- **成功率**: {report['success_rate']}%",
            f"- **平均生成时间**: {report['avg_generation_time']}秒",
            "",
            "## 测试结果详情",
            ""
        ]
        
        for i, result in enumerate(report['test_results'], 1):
            lines.extend([
                f"### 测试 {i}: {result['test_name']}",
                ""
            ])
            
            if result["success"]:
                content = result["content"]
                lines.extend([
                    f"- **状态**: ✅ 成功",
                    f"- **生成时间**: {result['generation_time']}秒",
                    f"- **文件路径**: {result['filepath']}",
                    "",
                    f"**生成内容预览**:",
                    f"- 标题: {content['title']}",
                    f"- 正文: {content['body'][:100]}...",
                    f"- 标签: {' '.join(content['hashtags'])}",
                    f"- 表情: {' '.join(content['emojis'])}",
                    ""
                ])
            else:
                lines.extend([
                    f"- **状态**: ❌ 失败",
                    f"- **生成时间**: {result['generation_time']}秒",
                    f"- **错误信息**: {result.get('error', '未知错误')}",
                    ""
                ])
        
        lines.extend([
            "---",
            "",
            "*测试由 DeepSeek-R1:8B 模型测试器自动生成*"
        ])
        
        return "\n".join(lines)


def main():
    """主函数"""
    print("🧪 DeepSeek-R1:8B 模型测试器")
    print("=" * 50)
    
    # 创建测试器
    tester = DeepSeekR1Tester()
    
    # 检查模型可用性
    if not tester.check_model_availability():
        return 1
    
    # 测试基本连接
    if not tester.test_basic_connection():
        return 1
    
    # 运行全面测试
    try:
        report = tester.run_comprehensive_tests()
        
        # 显示总结
        print(f"\n🏁 测试完成！")
        print(f"📊 总体结果：")
        print(f"   - 成功率：{report['success_rate']}%")
        print(f"   - 平均生成时间：{report['avg_generation_time']}秒")
        print(f"   - 成功/总计：{report['successful_tests']}/{report['total_tests']}")
        
        if report['success_rate'] >= 75:
            print(f"✅ 模型表现良好！")
        elif report['success_rate'] >= 50:
            print(f"⚠️ 模型表现一般，建议检查配置")
        else:
            print(f"❌ 模型表现不佳，需要调试")
        
        return 0
        
    except Exception as e:
        print(f"❌ 测试执行失败：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 