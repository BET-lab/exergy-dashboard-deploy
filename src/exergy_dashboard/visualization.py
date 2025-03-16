"""Exergy 시스템 시각화를 위한 모듈

이 모듈은 Exergy 대시보드의 시각화 기능을 관리합니다. 레지스트리 패턴을 사용하여
새로운 시각화 기능을 쉽게 등록하고 관리할 수 있습니다.

Examples
--------
1. 새로운 시각화 함수 등록하기:
    ```python
    from exergy_dashboard.visualization import viz_registry
    
    @viz_registry.register('Performance', 'COP Distribution')
    def plot_cop_distribution(session_state, selected_systems):
        import altair as alt
        import pandas as pd
        
        # 데이터 준비
        data = []
        for sys_name in selected_systems:
            system = session_state.systems[sys_name]
            if system['type'] == 'ASHP':
                cop = system['variables']['cop_A']
            elif system['type'] == 'GSHP':
                cop = system['variables']['cop_G']
            data.append({'system': sys_name, 'cop': cop})
            
        df = pd.DataFrame(data)
        
        # 차트 생성
        chart = alt.Chart(df).mark_bar().encode(
            x='system',
            y='cop',
            color='system'
        )
        
        return chart
    ```

2. 앱에서 시각화 사용하기:
    ```python
    import streamlit as st
    from exergy_dashboard.visualization import VisualizationManager
    
    viz_manager = VisualizationManager()
    viz_manager.render_tabs(st.session_state, selected_systems)
    ```
"""

from typing import Callable, Dict, List, Any, Optional
import pandas as pd
import altair as alt
import streamlit as st
from .chart import plot_waterfall_multi


class VisualizationRegistry:
    """시각화 함수를 등록하고 관리하는 레지스트리"""
    
    def __init__(self):
        self._visualizers: Dict[str, Dict[str, Callable]] = {}
    
    def register(self, tab: str, name: str) -> Callable:
        """
        데코레이터: 특정 탭과 이름으로 시각화 함수를 등록

        Parameters
        ----------
        tab : str
            시각화가 표시될 탭 이름
        name : str
            시각화의 이름

        Returns
        -------
        Callable
            데코레이터 함수
        """
        def decorator(func: Callable) -> Callable:
            if tab not in self._visualizers:
                self._visualizers[tab] = {}
            self._visualizers[tab][name] = func
            return func
        return decorator
    
    def get_tabs(self) -> List[str]:
        """등록된 모든 탭 이름을 반환"""
        return list(self._visualizers.keys())
    
    def get_visualizers(self, tab: str) -> Dict[str, Callable]:
        """특정 탭의 모든 시각화 함수를 반환"""
        return self._visualizers.get(tab, {})


class VisualizationManager:
    """시각화 관리 및 렌더링을 담당하는 클래스"""
    
    def __init__(self, registry: Optional[VisualizationRegistry] = None):
        self.registry = registry or viz_registry
    
    def render_tabs(self, session_state: Any, selected_systems: List[str]) -> None:
        """
        등록된 모든 시각화를 탭으로 구성하여 렌더링

        Parameters
        ----------
        session_state : Any
            Streamlit session state
        selected_systems : List[str]
            선택된 시스템 이름 목록
        """
        if not selected_systems:
            return
            
        tabs = st.tabs(self.registry.get_tabs())
        
        for tab, tab_name in zip(tabs, self.registry.get_tabs()):
            with tab:
                visualizers = self.registry.get_visualizers(tab_name)
                for name, func in visualizers.items():
                    st.subheader(name)
                    chart = func(session_state, selected_systems)
                    st.altair_chart(chart, use_container_width=True)


# 전역 레지스트리 인스턴스 생성
viz_registry = VisualizationRegistry()


@viz_registry.register('Efficiency', 'Exergy Efficiency')
def plot_exergy_efficiency(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 효율 차트 생성"""
    efficiencies = []
    xins = []
    xouts = []
    
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        if session_state.systems[key]['type'] == 'ASHP':
            eff = sv['Xout_A'] / sv['Xin_A'] * 100
            efficiencies.append(eff)
            xins.append(sv['Xin_A'])
            xouts.append(sv['Xout_A'])
        if session_state.systems[key]['type'] == 'GSHP':
            eff = sv['Xout_G'] / sv['Xin_G'] * 100
            efficiencies.append(eff)
            xins.append(sv['Xin_G'])
            xouts.append(sv['Xout_G'])

    chart_data = pd.DataFrame({
        'efficiency': efficiencies,
        'xins': xins,
        'xouts': xouts,
        'system': selected_systems,
    })

    max_v = chart_data['efficiency'].max()

    c = alt.Chart(chart_data).mark_bar(size=30).encode(
        y=alt.Y('system:N', title='System', sort=None)
           .axis(title=None, labelFontSize=18, labelColor='black'),
        x=alt.X('efficiency:Q', title='Exergy Efficiency [%]')
           .axis(
                labelFontSize=20,
                labelColor='black',
                titleFontSize=22,
                titleColor='black',
            )
            .scale(domain=[0, max_v + 3]),
        color=alt.Color('system:N', sort=None, legend=None),
        tooltip=['system', 'efficiency'],
    ).properties(
        width='container',
        height=len(selected_systems) * 60 + 50,
    )

    text = c.mark_text(
        align='left',
        baseline='middle',
        dx=3,
        fontSize=20,
        fontWeight='normal',
    ).encode(
        text=alt.Text('efficiency:Q', format='.2f')
    )

    return c + text


@viz_registry.register('Process', 'Exergy Consumption Process')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        if session_state.systems[key]['type'] == 'ASHP':
            labels = ['Input', r'X_{c,int}', r'X_{c,ref}', r'X_{c,ext}', r'X_{ext,out}', 'Output']
            amounts = [sv['Xin_A'], -sv['Xc_int_A'], -sv['Xc_r_A'], -sv['Xc_ext_A'], -sv['X_a_ext_out_A'], 0]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)
            
        if session_state.systems[key]['type'] == 'GSHP':
            labels = ['Input', r'X_{c,int}', r'X_{c,ref}', r'X_{c,GHE}', 'Output']
            amounts = [sv['Xin_G'], -sv['Xc_int_G'], -sv['Xc_r_G'], -sv['Xc_GHE'], 0]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)

    source = pd.concat(sources)
    return plot_waterfall_multi(source, 'Input', 'Output') 