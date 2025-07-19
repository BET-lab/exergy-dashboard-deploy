from exergy_dashboard.visualization import VisualizationRegistry


def test_register_and_get_visualizer():
    registry = VisualizationRegistry()

    @registry.register('TEST', 'dummy')
    def dummy_visualizer(ss, systems):
        return 'ok'

    func = registry.get_visualizer('dummy', 'TEST')
    assert func is dummy_visualizer
    assert func(None, []) == 'ok'

    assert registry.get_visualizer('unknown', 'TEST') is None
