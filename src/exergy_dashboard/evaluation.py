"""Exergy 시스템 평가를 위한 모듈

이 모듈은 다양한 시스템 모드(냉방, 난방, 온수)와 시스템 타입(ASHP, GSHP 등)에 대한
Exergy 평가 기능을 제공합니다. 레지스트리 패턴을 사용하여 새로운 평가 함수를 쉽게
등록하고 관리할 수 있습니다.

주요 기능
--------
- 시스템 모드와 타입별 평가 함수 등록 및 관리
- Streamlit session state와 통합된 파라미터 평가
- 확장 가능한 평가 함수 아키텍처

사용 예시
--------
1. 새로운 평가 함수 등록하기:
    ```python
    from typing import Dict
    from exergy_dashboard.evaluation import registry

    @registry.register('HEATING', 'ASHP')
    def evaluate_heating_ashp(params: Dict[str, float]) -> Dict[str, float]:
        # 입력 파라미터 추출
        T_0 = params['T_0']  # 기준 온도
        T_h = params['T_h']  # 난방수 온도
        Q_h = params['Q_h']  # 난방 용량
        
        # 계산 로직
        X_h = Q_h * (1 - T_0 / T_h)  # 난방수 엑서지
        
        # 계산된 모든 변수 반환
        return {k: v for k, v in locals().items() if k not in ('params')}
    ```

2. Streamlit 앱에서 평가 함수 사용하기:
    ```python
    import streamlit as st
    from exergy_dashboard.evaluation import evaluate_parameters
    
    # 시스템 파라미터 평가
    results = evaluate_parameters(st.session_state, 'system1')
    
    # 결과 출력
    st.write("Exergy 분석 결과:", results)
    ```

새로운 평가 함수 추가 방법
-----------------------
1. 필요한 입력 파라미터 정의:
   - 온도 파라미터의 경우 섭씨(°C)로 입력 받음
   - 파라미터 이름은 시스템에서 사용하는 규칙을 따름 (예: T_0, Q_h 등)

2. 평가 함수 구현:
   - @registry.register 데코레이터로 모드와 타입 지정
   - Dict[str, float] 타입의 파라미터를 입력받아 계산 결과를 반환
   - 모든 중간 계산 결과도 함께 반환하여 상세 분석 가능하게 함

3. 계산 결과 처리:
   - 온도 값은 자동으로 켈빈(K)으로 변환되어 계산됨
   - 반환된 결과는 session state에 자동으로 저장됨

참고사항
-------
- 온도 입력은 섭씨(°C)로 받지만 내부 계산은 켈빈(K)으로 수행
- 시스템 이름은 session state에서 '{system_name}:{parameter_name}' 형식으로 저장
- 평가 함수는 순수 함수(pure function)로 구현하여 테스트와 유지보수가 용이하게 함

See Also
--------
- EvaluationRegistry : 평가 함수 등록 및 관리를 위한 클래스
- evaluate_parameters : 통합 평가 인터페이스 함수
"""

from typing import Callable, Dict, Any, Optional


class EvaluationRegistry:
    """시스템 모드와 타입에 따른 평가 함수를 등록하고 관리하는 레지스트리"""
    
    def __init__(self):
        self._evaluators: Dict[str, Dict[str, Callable]] = {}
    
    def register(self, mode: str, system_type: str) -> Callable:
        """
        데코레이터: 특정 모드와 시스템 타입에 대한 평가 함수를 등록

        Parameters
        ----------
        mode : str
            시스템 모드 (e.g., 'COOLING', 'HEATING', 'HOT WATER')
        system_type : str
            시스템 타입 (e.g., 'ASHP', 'GSHP')

        Returns
        -------
        Callable
            데코레이터 함수

        Examples
        --------
        >>> @registry.register('COOLING', 'ASHP')
        >>> def evaluate_cooling_ashp(params: Dict[str, float]) -> Dict[str, float]:
        >>>     # evaluation logic
        >>>     return variables
        """
        def decorator(func: Callable) -> Callable:
            if mode not in self._evaluators:
                self._evaluators[mode] = {}
            self._evaluators[mode][system_type] = func
            return func
        return decorator
    
    def get_evaluator(self, mode: str, system_type: str) -> Optional[Callable]:
        """특정 모드와 시스템 타입에 대한 평가 함수를 반환"""
        return self._evaluators.get(mode, {}).get(system_type)
    
    def evaluate(self, mode: str, system_type: str, params: Dict[str, float]) -> Dict[str, float]:
        """
        주어진 모드와 시스템 타입에 대한 평가를 수행

        Parameters
        ----------
        mode : str
            시스템 모드
        system_type : str
            시스템 타입
        params : Dict[str, float]
            평가에 필요한 파라미터들

        Returns
        -------
        Dict[str, float]
            계산된 변수들

        Raises
        ------
        ValueError
            해당 모드와 시스템 타입에 대한 평가 함수가 등록되지 않은 경우
        """
        evaluator = self.get_evaluator(mode, system_type)
        if evaluator is None:
            raise ValueError(f"No evaluator registered for mode '{mode}' and system type '{system_type}'")
        return evaluator(params)


# 전역 레지스트리 인스턴스 생성
registry = EvaluationRegistry()

def evaluate_parameters(sss: Any, system_name: str) -> Dict[str, float]:
    """
    시스템 파라미터 평가를 위한 통합 인터페이스

    Parameters
    ----------
    sss : Any
        Streamlit session state
    system_name : str
        평가할 시스템의 이름

    Returns
    -------
    Dict[str, float]
        계산된 변수들의 딕셔너리
    """
    # Extract all inputs
    params = {}
    for key, value in sss.items():
        if not key.startswith(system_name + ':'):
            continue
        
        key = key.split(':')[1]
        params[key] = value

    # Get system mode and type
    system = sss.systems[system_name]
    mode = sss.mode.upper()
    system_type = system['type']

    # Evaluate parameters using registered evaluator
    variables = registry.evaluate(mode, system_type, params)
    
    # Store results in session state
    sss.systems[system_name]['variables'] = variables

    return variables

