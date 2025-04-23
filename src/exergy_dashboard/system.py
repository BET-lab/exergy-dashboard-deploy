# 각 시스템의 파라미터를 설정하세요.
from typing import Dict, Any
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class SystemRegistry:
    """시스템 레지스트리
    
    새로운 시스템을 등록하고 관리하는 레지스트리 클래스입니다.
    기본 시스템(ASHP, GSHP)이 미리 등록되어 있으며,
    사용자는 새로운 시스템과 모드를 자유롭게 추가할 수 있습니다.
    """
    _systems: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        self._systems = {}
        # 기본 시스템 등록
        # self._systems['COOLING'] = {
        #     'ASHP': COOLING_ASGP,
        #     'GSHP': COOLING_GSHP,
        # }
    
    def register_system(self, mode: str, system_type: str, system_config: dict) -> None:
        """새로운 시스템을 레지스트리에 등록합니다.
        
        Parameters
        ----------
        mode : str
            시스템 모드 (예: 'COOLING', 'HEATING', 'TEST' 등 임의의 모드)
        system_type : str
            시스템 유형 (예: 'ASHP', 'GSHP')
        system_config : dict
            시스템 설정 정보를 담은 딕셔너리
            
        Examples
        --------
        >>> from exergy_dashboard.system import register_system, get_system_template
        >>> 
        >>> # 템플릿 가져오기
        >>> template = get_system_template()
        >>> 
        >>> # 템플릿을 수정하여 새로운 시스템 설정
        >>> new_system = template.copy()
        >>> new_system['display']['title'] = 'My New System'
        >>> new_system['display']['icon'] = ':star:'
        >>> new_system['parameters']['T_0'] = {
        ...     'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
        ...     'latex': r'$T_0$',
        ...     'default': 32.0,
        ...     'range': [-50, 50],
        ...     'unit': '℃',
        ...     'step': 0.5,
        ...     'category': 'environment',
        ... }
        >>> # ... 더 많은 파라미터 추가 ...
        >>> 
        >>> # 시스템 등록 (임의의 모드 사용 가능)
        >>> register_system('MY_MODE', 'NEW_SYSTEM', new_system)
        """
        mode = mode.upper()
        system_type = system_type.upper()
        
        # 시스템 설정 검증
        self._validate_system_config(system_config)
        
        # 새로운 모드인 경우 딕셔너리 초기화
        if mode not in self._systems:
            self._systems[mode] = {}
        
        # 시스템 등록
        self._systems[mode][system_type] = deepcopy(system_config)
    
    def get_system_template(self) -> dict:
        """새로운 시스템 설정을 위한 템플릿을 반환합니다.
        
        Returns
        -------
        dict
            시스템 설정 템플릿
            
        Notes
        -----
        이 템플릿을 기반으로 새로운 시스템을 구성할 수 있습니다.
        필수 필드와 옵션 필드가 주석으로 표시되어 있습니다.
        """
        return {
            'display': {  # 필수
                'title': 'System Display Name',  # 필수
                'icon': ':emoji_code:',  # 필수
            },
            'parameters': {  # 필수
                'param_name': {  # 파라미터 이름
                    'explanation': {  # 필수
                        'EN': 'Parameter Description in English',
                        'KR': '한글 파라미터 설명',
                    },
                    'latex': r'$latex_expression$',  # 필수
                    'default': 0.0,  # 필수
                    'range': [-100, 100],  # 필수
                    'unit': 'unit',  # 필수
                    'step': 0.1,  # 필수
                    'category': 'category_name',  # 선택, 기본값: 'General'
                },
            }
        }
    
    def _validate_system_config(self, config: dict) -> None:
        """시스템 설정의 유효성을 검사합니다.
        
        Parameters
        ----------
        config : dict
            검사할 시스템 설정
            
        Raises
        ------
        ValueError
            필수 필드가 없거나 형식이 잘못된 경우
        """
        required_fields = {
            'display': {'title', 'icon'},
            'parameters': set(),
        }
        
        if not isinstance(config, dict):
            raise ValueError("System config must be a dictionary")
            
        for field, subfields in required_fields.items():
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
            
            if subfields and not all(sf in config[field] for sf in subfields):
                raise ValueError(f"Missing required subfields in {field}: {subfields}")
                
        for param in config.get('parameters', {}).values():
            required_param_fields = {
                'explanation', 'latex', 'default', 'range', 'unit', 'step'
            }
            if not all(f in param for f in required_param_fields):
                raise ValueError(f"Parameter missing required fields: {required_param_fields}")
    
    def get_systems(self) -> Dict[str, Dict[str, Any]]:
        """등록된 모든 시스템을 반환합니다.
        
        Returns
        -------
        Dict[str, Dict[str, Any]]
            모든 등록된 시스템의 딕셔너리
        """
        return deepcopy(self._systems)


# 전역 시스템 레지스트리 인스턴스 생성
system_registry = SystemRegistry()

# SYSTEM_CASE를 레지스트리의 프로퍼티로 정의
SYSTEM_CASE = system_registry.get_systems()

def register_system(mode: str, system_type: str, system_config: dict) -> None:
    """새로운 시스템을 등록하는 편의 함수
    
    Parameters
    ----------
    mode : str
        시스템 모드 ('COOLING', 'HEATING', 'HOT WATER')
    system_type : str
        시스템 유형 (예: 'ASHP', 'GSHP')
    system_config : dict
        시스템 설정 정보를 담은 딕셔너리
        
    Examples
    --------
    >>> from exergy_dashboard.system import register_system, get_system_template
    >>> 
    >>> # 템플릿 가져오기
    >>> template = get_system_template()
    >>> 
    >>> # 템플릿을 수정하여 새로운 시스템 설정
    >>> new_system = template.copy()
    >>> new_system['display']['title'] = 'My New System'
    >>> new_system['display']['icon'] = ':star:'
    >>> # ... 파라미터 설정 ...
    >>> 
    >>> # 시스템 등록
    >>> register_system('COOLING', 'NEW_SYSTEM', new_system)
    """
    system_registry.register_system(mode, system_type, system_config)
    
    
def get_system_template() -> dict:
    """새로운 시스템 설정을 위한 템플릿을 반환하는 편의 함수"""
    return system_registry.get_system_template()

def get_systems() -> Dict[str, Dict[str, Any]]:
    """전역 레지스트리에 등록된 모든 시스템을 반환합니다."""
    systems = system_registry.get_systems()
    # UI에 표시되는 이름 임시로 바꾸기: 'TEST' → 'HOT WATER'
    if 'TEST' in systems:
        systems['HOT WATER'] = systems.pop('TEST')
    return system_registry.get_systems()
