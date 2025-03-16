"""Exergy 시스템 시각화를 위한 모듈

이 모듈은 Exergy 대시보드의 시각화 기능을 관리합니다. 레지스트리 패턴을 사용하여
새로운 시각화 기능을 쉽게 등록하고 관리할 수 있습니다.

Examples
--------
1. 새로운 시각화 함수 등록하기:
    ```python
    from exergy_dashboard.visualization import registry
    
    @registry.register('COP Distribution')
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
    from exergy_dashboard.visualization import registry
    
    viz_manager = VisualizationManager(registry)
    viz_manager.render_tabs(st.session_state, selected_systems)
    ```
"""

from typing import Callable, Dict, List, Any
import pandas as pd
import altair as alt
import streamlit as st
from .chart import plot_waterfall_multi
from dataclasses import dataclass


@dataclass
class VisualizationRegistry:
    """시각화 도구 레지스트리
    
    새로운 시각화 도구를 등록하고 관리하는 레지스트리 클래스입니다.
    """
    _visualizers: Dict[str, Dict[str, Callable]] = None
    
    def __post_init__(self):
        self._visualizers = {}
    
    def register(self, mode: str = None, name: str = None) -> Callable:
        """
        데코레이터: 새로운 시각화 도구를 등록

        Parameters
        ----------
        mode : str, optional
            시각화 도구가 사용될 모드, None이면 모든 모드에서 사용 가능
        name : str
            시각화 도구의 이름

        Returns
        -------
        Callable
            데코레이터 함수
        """
        # 호환성을 위해 모드와 이름 파라미터 순서를 바꿔서도 동작하도록 함
        if mode is not None and name is None:
            name = mode
            mode = None
            
        def decorator(func: Callable) -> Callable:
            if mode not in self._visualizers:
                self._visualizers[mode] = {}
            self._visualizers[mode][name] = func
            return func
        return decorator
    
    def get_visualizer(self, name: str, mode: str = None) -> Callable:
        """
        시각화 도구 함수를 반환

        Parameters
        ----------
        name : str
            시각화 도구의 이름
        mode : str, optional
            시각화 도구가 사용될 모드, None이면 모드 무관 시각화 검색

        Returns
        -------
        Callable
            시각화 함수
        """
        # 특정 모드의 시각화가 있으면 반환
        if mode in self._visualizers and name in self._visualizers[mode]:
            return self._visualizers[mode][name]
        
        # 모드 무관 시각화가 있으면 반환
        if None in self._visualizers and name in self._visualizers[None]:
            return self._visualizers[None][name]
            
        return None
    
    def get_available_visualizers(self, mode: str = None) -> Dict[str, Callable]:
        """
        등록된 모든 시각화 도구를 반환
        
        Parameters
        ----------
        mode : str, optional
            특정 모드의 시각화만 반환할 경우 지정
            
        Returns
        -------
        Dict[str, Callable]
            시각화 이름과 함수의 딕셔너리
        """
        result = {}
        
        # 모드 무관 시각화 추가
        if None in self._visualizers:
            result.update(self._visualizers[None])
            
        # 특정 모드 시각화 추가 (모드가 지정된 경우)
        if mode in self._visualizers:
            result.update(self._visualizers[mode])
            
        return result


class VisualizationManager:
    """시각화 관리 및 렌더링을 담당하는 클래스"""
    
    def __init__(self, registry: VisualizationRegistry):
        """
        시각화 관리자 초기화
        
        Parameters
        ----------
        registry : VisualizationRegistry
            사용할 시각화 레지스트리
        """
        self.registry = registry
    
    def render_tabs(self, session_state: Any, selected_systems: List[str], mode: str = None) -> None:
        """
        등록된 모든 시각화를 탭으로 구성하여 렌더링

        Parameters
        ----------
        session_state : Any
            Streamlit session state
        selected_systems : List[str]
            선택된 시스템 이름 목록
        mode : str, optional
            시각화할 특정 모드
        """
        if not selected_systems:
            return
            
        # 현재 모드에 해당하는 시각화 도구 가져오기
        available_visualizers = self.registry.get_available_visualizers(mode)
        
        if not available_visualizers:
            st.write("No visualizations available for this mode.")
            return
            
        tabs = st.tabs(available_visualizers.keys())
        
        for tab, tab_name in zip(tabs, available_visualizers.keys()):
            with tab:
                func = available_visualizers[tab_name]
                st.subheader(tab_name)
                try:
                    # 새로운 시각화 함수 형식 (variables와 params를 직접 받는 형식)
                    if hasattr(func, '_is_new_format') and func._is_new_format:
                        # 새로운 형식용 데이터 준비
                        systems_data = {}
                        for system_name in selected_systems:
                            system = session_state.systems[system_name]
                            if 'variables' in system:
                                variables = system['variables']
                                params = {k: v['value'] for k, v in system['parameters'].items()}
                                systems_data[system_name] = {'variables': variables, 'params': params}
                        
                        # 새로운 형식의 함수 호출
                        func(systems_data, selected_systems)
                    else:
                        # 기존 형식의 함수 호출
                        chart = func(session_state, selected_systems)
                        if chart is not None:  # 차트를 반환하는 경우에만 표시
                            st.altair_chart(chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Error rendering visualization: {str(e)}")
                    # 디버깅을 위한 추가 정보
                    import traceback
                    st.error(f"상세 오류: {traceback.format_exc()}")


# 새로운 형식의 시각화 함수를 위한 데코레이터
def new_viz_format(func):
    """새로운 형식의 시각화 함수임을 표시하는 데코레이터"""
    func._is_new_format = True
    return func


# 전역 레지스트리 인스턴스 생성
registry = VisualizationRegistry()


@registry.register(name='Exergy Efficiency')
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


@registry.register(name='Exergy Consumption Process')
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