"""
Orchestrator 测试
"""

import unittest
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.orchestrator import Orchestrator


class TestOrchestrator(unittest.TestCase):
    """Orchestrator 测试类"""

    def setUp(self):
        """测试前准备"""
        self.engine = Orchestrator()

    def test_execute_event_analysis(self):
        """测试事件分析工作流"""
        result = self.engine.execute("帮我分析一下 QFII 国债期货事件")
        self.assertEqual(result["status"], "success")
        self.assertIn("output", result)
        self.assertIn("event_analysis", result["skill_chain"])

    def test_execute_position_diagnosis(self):
        """测试持仓诊断工作流"""
        result = self.engine.execute("诊断我的持仓：518880 30%, 510300 25%")
        self.assertEqual(result["status"], "success")
        self.assertIn("output", result)
        self.assertIn("position_diagnosis", result["skill_chain"])

    def test_execute_unknown_input(self):
        """测试未知输入（默认路由到完整投顾）"""
        result = self.engine.execute("未知输入")
        self.assertEqual(result["status"], "success")
        self.assertIn("output", result)
        # 默认路由到完整投顾
        self.assertIn("personality_test", result["skill_chain"])

    def test_execution_log(self):
        """测试执行日志"""
        self.engine.execute("测试 1")
        self.engine.execute("测试 2")
        log = self.engine.get_execution_log(limit=2)
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]["input"], "测试 1")
        self.assertEqual(log[1]["input"], "测试 2")

    def test_reset(self):
        """测试重置"""
        self.engine.execute("测试")
        self.engine.reset()
        log = self.engine.get_execution_log()
        self.assertEqual(len(log), 0)


if __name__ == "__main__":
    unittest.main()
