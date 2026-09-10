"""不调用外部模型，验证任务循环和工具。"""
import contextlib
import io
import unittest
from types import SimpleNamespace
from pydantic import ValidationError
from main import Plan, Review, run, calculate_hours


class FakeAgent:
    def __init__(self, *results):
        self.results = iter(results)
        self.calls = []

    def invoke(self, payload, config=None):
        self.calls.append(payload)
        result = next(self.results)
        if isinstance(result, Exception):
            raise result
        return result


def execution(text):
    return {'messages': [SimpleNamespace(type='ai', content=text)]}


class FlowTest(unittest.TestCase):
    def execute(self, *agents, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return run('教学规划', *agents, **kwargs)

    def test_replan_and_finish(self):
        planner = FakeAgent({'structured_response': Plan(steps=['读取资料'])})
        executor = FakeAgent(execution('4周'), execution('16课时并附验收标准'))
        reviewer = FakeAgent(
            {'structured_response': Review(action='continue', reason='缺课时和验收', steps=['补课时与验收'])},
            {'structured_response': Review(action='finish', reason='齐全', answer='完成安排')})
        result = self.execute(planner, executor, reviewer)
        self.assertEqual(result['status'], 'finished')
        self.assertEqual(result['history'][1]['step'], '补课时与验收')
        self.assertIn('4周', executor.calls[1]['messages'][0]['content'])

    def test_limit_and_failure(self):
        planner = FakeAgent({'structured_response': Plan(steps=['读取资料'])})
        executor = FakeAgent(RuntimeError('simulated failure'))
        reviewer = FakeAgent({'structured_response': Review(action='continue', reason='失败需要重试', steps=['重试读取'])})
        result = self.execute(planner, executor, reviewer, max_steps=1)
        self.assertEqual(result['status'], 'max_steps_reached')
        self.assertEqual(result['history'][0]['status'], 'error')
        self.assertEqual(result['remaining_steps'], ['重试读取'])

    def test_review_constraints(self):
        with self.assertRaises(ValidationError):
            Review(action='continue', reason='缺步骤')
        with self.assertRaises(ValidationError):
            Review(action='finish', reason='缺答案')

    def test_real_tool(self):
        self.assertIn('16课时', calculate_hours.invoke({'weeks': 4, 'hours_per_week': 4}))
        self.assertIn('参数错误', calculate_hours.invoke({'weeks': -1, 'hours_per_week': 4}))


if __name__ == '__main__':
    unittest.main()
