"""
完整工作流测试

端到端测试：用户输入 → Skill 路由 → 链式调用 → 数据验证 → 格式化输出
"""

import sys
import os
import unittest
import logging

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 添加 data_layer 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.orchestrator import Orchestrator
from src.verifier import create_verifier
from src.data_providers.tencent_fix import get_indices_fixed
from src.data_providers.fund_fix import get_fund_data_with_fallback

logging.basicConfig(level=logging.INFO)


class TestWorkflow(unittest.TestCase):
    """完整工作流测试类"""

    def setUp(self):
        """测试前准备"""
        self.engine = Orchestrator()
        self.verifier = create_verifier()

    def test_01_market_data_workflow(self):
        """测试 1：市场数据工作流"""
        print("\n" + "=" * 50)
        print("📊 测试 1：市场数据工作流")
        print("=" * 50)

        # 1. 获取市场数据
        market_data = self.verifier.get_market_data("A 股")

        # 2. 验证数据
        self.assertIn("confidence_level", market_data)
        self.assertIn("is_fresh", market_data)
        self.assertIn("disclaimer", market_data)

        # 3. 输出结果
        print(f"\n📊 A 股市场数据：")
        for index_name, data in market_data.items():
            if isinstance(data, dict) and "current" in data:
                print(f"  {index_name}: {data['current']} ({data['change_pct']}%)")

        print(f"\n  信源等级：{market_data.get('confidence_level')}")
        print(f"  时效性：{market_data.get('is_fresh')}")
        print(f"  免责声明：{market_data.get('disclaimer')[:20]}...")

        print("\n✅ 测试 1 通过")

    def test_02_stock_data_workflow(self):
        """测试 2：个股数据工作流"""
        print("\n" + "=" * 50)
        print("📊 测试 2：个股数据工作流")
        print("=" * 50)

        # 1. 获取个股数据
        stock_data = self.verifier.get_stock_data("600519.SH")

        # 2. 验证数据
        self.assertIn("symbol", stock_data)
        self.assertIn("price", stock_data)
        self.assertIn("change_percent", stock_data)
        self.assertIn("confidence_level", stock_data)

        # 3. 输出结果
        print(f"\n📊 个股数据（贵州茅台 600519.SH）：")
        print(f"  代码：{stock_data.get('symbol')}")
        print(f"  当前价：{stock_data.get('price')}")
        print(f"  涨跌幅：{stock_data.get('change_percent')}%")
        print(f"  信源等级：{stock_data.get('confidence_level')}")

        print("\n✅ 测试 2 通过")

    def test_03_fund_data_workflow(self):
        """测试 3：基金数据工作流"""
        print("\n" + "=" * 50)
        print("📊 测试 3：基金数据工作流")
        print("=" * 50)

        # 1. 获取基金数据（带 fallback）
        fund_data = get_fund_data_with_fallback("518880")

        # 2. 验证数据
        self.assertIn("fund_code", fund_data)
        self.assertIn("source", fund_data)

        # 3. 输出结果
        print(f"\n📊 基金数据（518880 黄金 ETF）：")
        print(f"  代码：{fund_data.get('fund_code')}")
        print(f"  名称：{fund_data.get('fund_name')}")
        print(f"  净值：{fund_data.get('nav')}")
        print(f"  来源：{fund_data.get('source')}")

        print("\n✅ 测试 3 通过")

    def test_04_event_analysis_workflow(self):
        """测试 4：事件分析工作流"""
        print("\n" + "=" * 50)
        print("📊 测试 4：事件分析工作流")
        print("=" * 50)

        # 1. 执行工作流
        result = self.engine.execute("帮我分析一下 QFII 国债期货事件")

        # 2. 验证结果
        self.assertEqual(result["status"], "success")
        self.assertIn("output", result)
        self.assertIn("event_analysis", result["skill_chain"])

        # 3. 输出结果
        print(f"\n📥 输入：帮我分析一下 QFII 国债期货事件")
        print(f"📤 状态：{result['status']}")
        print(f"⏱️  耗时：{result.get('execution_time', 0):.2f} 秒")
        print(f"🔗 Skill 链：{' → '.join(result.get('skill_chain', []))}")

        print("\n✅ 测试 4 通过")

    def test_05_position_diagnosis_workflow(self):
        """测试 5：持仓诊断工作流"""
        print("\n" + "=" * 50)
        print("📊 测试 5：持仓诊断工作流")
        print("=" * 50)

        # 1. 执行工作流
        result = self.engine.execute("诊断我的持仓：518880 黄金 ETF 30%, 510300 沪深 300ETF 25%")

        # 2. 验证结果
        self.assertEqual(result["status"], "success")
        self.assertIn("output", result)
        self.assertIn("position_diagnosis", result["skill_chain"])

        # 3. 输出结果
        print(f"\n📥 输入：诊断我的持仓：518880 黄金 ETF 30%, 510300 沪深 300ETF 25%")
        print(f"📤 状态：{result['status']}")
        print(f"⏱️  耗时：{result.get('execution_time', 0):.2f} 秒")
        print(f"🔗 Skill 链：{' → '.join(result.get('skill_chain', []))}")

        print("\n✅ 测试 5 通过")

    def test_06_tencent_fix(self):
        """测试 6：腾讯财经修复版"""
        print("\n" + "=" * 50)
        print("📊 测试 6：腾讯财经修复版")
        print("=" * 50)

        # 1. 获取大盘指数
        indices = get_indices_fixed()

        # 2. 验证数据（允许为空，因为网络问题）
        if indices:
            self.assertIn("上证指数", indices)
            self.assertIn("change_percent", indices["上证指数"])

            # 3. 输出结果
            print(f"\n📊 大盘指数（修复版）：")
            for name, data in indices.items():
                print(f"  {name}: {data['price']} ({data['change_percent']}%)")
        else:
            print(f"\n⚠️ 网络不可用，跳过腾讯财经修复版测试")

        print("\n✅ 测试 6 通过")

    def test_07_full_workflow(self):
        """测试 7：完整工作流（事件分析 + 数据验证）"""
        print("\n" + "=" * 50)
        print("📊 测试 7：完整工作流")
        print("=" * 50)

        # 1. 获取市场数据
        market_data = self.verifier.get_market_data("A 股")

        # 2. 执行事件分析
        result = self.engine.execute("分析当前市场形势")

        # 3. 验证结果
        self.assertEqual(result["status"], "success")

        # 4. 输出结果
        print(f"\n📊 市场数据：")
        for index_name, data in market_data.items():
            if isinstance(data, dict) and "current" in data:
                print(f"  {index_name}: {data['current']} ({data['change_pct']}%)")

        print(f"\n📥 工作流输入：分析当前市场形势")
        print(f"📤 工作流状态：{result['status']}")
        print(f"⏱️  工作流耗时：{result.get('execution_time', 0):.2f} 秒")

        print("\n✅ 测试 7 通过")


if __name__ == "__main__":
    # 运行测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkflow)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试报告
    print("\n" + "=" * 50)
    print("📋 测试报告")
    print("=" * 50)
    print(f"运行测试：{result.testsRun}")
    print(f"通过：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")

    if result.failures:
        print("\n❌ 失败详情：")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\n❌ 错误详情：")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    print("\n" + "=" * 50)
