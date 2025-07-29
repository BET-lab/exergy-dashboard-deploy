"""Exergy 시스템 시각화를 위한 모듈

이 모듈은 Exergy 대시보드의 시각화 기능을 관리합니다. 레지스트리 패턴을 사용하여
새로운 시각화 기능을 쉽게 등록하고 관리할 수 있습니다.

Examples
--------
1. 새로운 시각화 함수 등록하기:
    ```python
    from exergy_dashboard.visualization import registry
    
    @registry.register('COOLING', 'COP Distribution')
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
import streamlit as st
from dataclasses import dataclass


@dataclass
class VisualizationRegistry:
    """시각화 도구 레지스트리
    
    새로운 시각화 도구를 등록하고 관리하는 레지스트리 클래스입니다.
    """
    _visualizers: Dict[str, Dict[str, Callable]] = None
    
    def __post_init__(self):
        self._visualizers = {}
    
    def register(self, mode: str, name: str) -> Callable:
        """
        데코레이터: 새로운 시각화 도구를 등록

        Parameters
        ----------
        mode : str
            시각화 도구가 사용될 모드 (예: 'COOLING', 'TEST')
        name : str
            시각화 도구의 이름

        Returns
        -------
        Callable
            데코레이터 함수
        """
        def decorator(func: Callable) -> Callable:
            if mode not in self._visualizers:
                self._visualizers[mode] = {}
            self._visualizers[mode][name] = func
            return func
        return decorator
    
    def get_visualizer(self, name: str, mode: str) -> Callable:
        """
        시각화 도구 함수를 반환

        Parameters
        ----------
        name : str
            시각화 도구의 이름
        mode : str
            시각화 도구가 사용될 모드

        Returns
        -------
        Callable
            시각화 함수
        """
        if mode in self._visualizers and name in self._visualizers[mode]:
            return self._visualizers[mode][name]
        return None
    
    def get_available_visualizers(self, mode: str) -> Dict[str, Callable]:
        """
        특정 모드에 등록된 모든 시각화 도구를 반환
        
        Parameters
        ----------
        mode : str
            시각화를 가져올 모드
            
        Returns
        -------
        Dict[str, Callable]
            시각화 이름과 함수의 딕셔너리
        """
        if mode in self._visualizers:
            return self._visualizers[mode].copy()
        return {}


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
    
    def render_tabs(self, session_state: Any, selected_systems: List[str], mode: str) -> None:
        """
        등록된 모든 시각화를 탭으로 구성하여 렌더링

        Parameters
        ----------
        session_state : Any
            Streamlit session state
        selected_systems : List[str]
            선택된 시스템 이름 목록
        mode : str
            시각화할 특정 모드
        """
        if not selected_systems:
            return
            
        # 현재 모드에 해당하는 시각화 도구 가져오기
        available_visualizers = self.registry.get_available_visualizers(mode)
        
        if not available_visualizers:
            st.write(f"No visualizations available for {mode} mode.")
            return
            
        tabs = st.tabs(available_visualizers.keys())
        
        for tab, tab_name in zip(tabs, available_visualizers.keys()):
            with tab:
                func = available_visualizers[tab_name]
                st.subheader(tab_name)
                try:
                    chart = func(session_state, selected_systems)
                    if isinstance(chart, dict):
                        st.vega_lite_chart(chart)
                    elif isinstance(chart, str):
                        st.components.v1.html(chart)
                    elif chart is not None:  # 차트를 반환하는 경우에만 표시
                        st.altair_chart(chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Error rendering visualization: {str(e)}")
                    import traceback
                    st.error(f"상세 오류: {traceback.format_exc()}")


# 전역 레지스트리 인스턴스 생성
registry = VisualizationRegistry()