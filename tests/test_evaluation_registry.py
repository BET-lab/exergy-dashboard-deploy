import pytest
from exergy_dashboard.evaluation import EvaluationRegistry


def test_register_and_evaluate_dummy():
    registry = EvaluationRegistry()

    @registry.register('TEST', 'DUMMY')
    def dummy(params):
        return {'value': params['a'] + params['b']}

    evaluator = registry.get_evaluator('TEST', 'DUMMY')
    assert evaluator is dummy

    result = registry.evaluate('TEST', 'DUMMY', {'a': 1, 'b': 2})
    assert result == {'value': 3}
