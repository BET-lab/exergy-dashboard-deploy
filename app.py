import math
import copy
import functools
import streamlit as st
import importlib
import os
import glob

def parse_range_value(val, sys_name, sss):
    # 숫자면 바로 float 변환
    if isinstance(val, (int, float)):
        return float(val)
    # 문자열 수식이면 파싱
    if isinstance(val, str):
        try:
            # 변수명 추출 (예: 'T_w_sup+1.0' → 'T_w_sup')
            for param in sss.systems[sys_name]['parameters']:
                if param in val:
                    param_val = sss.get(f"{sys_name}:{param}", sss.systems[sys_name]['parameters'][param]['default'])
                    expr = val.replace(param, str(param_val))
                    return float(eval(expr))
            # 그냥 숫자 문자열이면
            return float(val)
        except Exception:
            return None  # 혹은 적절한 기본값
    return None

# systems 폴더의 *_system.py 파일을 모두 동적으로 임포트
systems_dir = os.path.join(os.path.dirname(__file__), 'systems')
system_files = glob.glob(os.path.join(systems_dir, '*_system.py'))
for file_path in system_files:
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    importlib.import_module(f'systems.{module_name}')

# 시스템 관련 모듈을 나중에 import
from exergy_dashboard.system import get_systems
from exergy_dashboard.evaluation import evaluate_parameters
from exergy_dashboard.visualization import VisualizationManager, registry

# 시스템 상태 확인
systems = get_systems()
print("Available modes:", list(systems.keys()))
if 'TEST' in systems:
    print("Available systems in TEST mode:", list(systems['TEST'].keys()))

LANG = 'EN'

# SYSTEM_CASE 내용 디버깅을 위한 로그
print("Available modes in SYSTEM_CASE:", list(systems.keys()))

st.set_page_config(
    page_title='Exergy Analysis',
    page_icon=':fire:',
    layout='wide',
    initial_sidebar_state='expanded'
)

# 사이드바 너비 조절을 위한 CSS 추가
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 400px;
        max-width: 400px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit의 session_state를 더 짧은 변수명으로 할당
# session_state는 앱의 상태를 저장하는 객체로, 페이지 새로고침 간에 데이터를 유지함
# 사용자 상호작용, 시스템 상태, 계산 결과 등을 저장하는 데 사용됨
# 이 변수를 통해 모드, 시스템 구성, 카운터 등의 상태를 관리
sss = st.session_state

# 사용 가능한 모드 목록 가져오기
systems = get_systems()  # 최신 상태 가져오기
available_modes = list(systems.keys())
default_mode = available_modes[0] if available_modes else 'COOLING'

if 'mode' not in sss:
    sss.mode = default_mode

def reset_systems():
    """시스템 상태를 초기화합니다."""
    sss.systems = {}
    systems = get_systems()  # 최신 상태 가져오기
    sss.system_count = {
        k: 0 for k in systems[sss.mode.upper()].keys()
    }

if 'systems' not in sss:
    sss.systems = {}

if 'system_count' not in sss:
    systems = get_systems()  # 최신 상태 가져오기
    sss.system_count = {
        k: 0 for k in systems[sss.mode.upper()].keys()
    }

def update_system_count():
    """현재 모드에 맞게 system_count를 업데이트합니다."""
    systems = get_systems()
    current_counts = sss.system_count if 'system_count' in sss else {}
    sss.system_count = {
        k: current_counts.get(k, 0) for k in systems[sss.mode.upper()].keys()
    }

def create_system(mode, system_name):
    """시스템 생성 함수
    
    주어진 모드와 시스템 이름에 따라 새로운 시스템을 생성합니다.
    시스템 카운터를 증가시키고 시스템 케이스에서 기본 설정을 복사하여 새 시스템을 구성합니다.
    
    Parameters
    ----------
    mode : str
        시스템 모드 ('COOLING', 'HEATING', 'HOT WATER')
    system_name : str
        시스템 유형 ('ASHP', 'GSHP' 등)
        
    Returns
    -------
    dict
        생성된 시스템 정보를 담은 딕셔너리
    """
    mode = mode.upper()
    # system_name = system_name.upper()

    # system_count가 현재 모드의 시스템들을 포함하도록 업데이트
    if system_name not in sss.system_count:
        update_system_count()

    sss.system_count[system_name] += 1

    systems = get_systems()  # 최신 상태 가져오기
    system = copy.deepcopy(systems[mode][system_name])
    system['name'] = f"{system_name} {sss.system_count[system_name]}"
    system['type'] = system_name

    return system


def add_system(type_):
    data = create_system(mode=sss.mode, system_name=type_)
    sss.systems[data['name']] = data
    # 모든 파라미터의 기본값을 session state에 미리 할당
    for k, v in data['parameters'].items():
        sss[f"{data['name']}:{k}"] = v['default']


with st.sidebar:
    st.title('Exergy Analyzer')
    st.divider()
    st.header('시스템 모드')
    systems = get_systems()  # 최신 상태 가져오기
    available_modes = list(systems.keys())
    if not available_modes:
        st.write('No modes available.')
        st.stop()
    previous_mode = sss.mode if 'mode' in sss else None

    for mode in available_modes:
        button_label = f"{mode}" if sss.mode == mode.capitalize() else mode.capitalize()
        if st.button(button_label, use_container_width=True, key=f"mode_button_{mode}"):
            sss.mode = mode

    if previous_mode != sss.mode:
        reset_systems()
        if 'selected_options' in sss:
            sss.selected_options = []
        st.rerun()

    st.header('시스템 추가')
    systems = get_systems()  # 최신 상태 가져오기
    if len(systems[sss.mode.upper()]) == 0:
        st.write('No system available for the selected mode.')
        st.stop()
    else:
        selected = st.selectbox(
            'System type', systems[sss.mode.upper()].keys()
        )
        st.button(
            'Add system',
            use_container_width=True,
            on_click=functools.partial(add_system, type_=selected),
        )

    # 시스템별 변수 카테고리 선택 버튼
    st.header('입력 변수 카테고리')
    if 'selected_category' not in sss:
        sss.selected_category = {}

    systems = get_systems()
    mode_upper = sss.mode.upper()
    for sys_name, system in sss.systems.items():
        sys_type = system['type']
        if sys_type not in systems[mode_upper]:
            continue
        st.subheader(sys_name)
        categories = set(v.get('category', 'General') for v in system['parameters'].values())
        for category in sorted(categories):
            if st.button(category.capitalize(), key=f"{sys_name}_{category}", use_container_width=True):
                sss.selected_category[sys_name] = category

ml, mr = 0.0001, 0.0001
pad = 0.4
col_border = False
_, title_col, title_right_col = st.columns([ml, 4 + pad + 5, mr], border=col_border)
_, title_col1, _, title_col2, _ = st.columns([ml, 2.5, pad, 7.5, mr], border=col_border)
_, col1, _, col2, _ = st.columns([ml, 2.5, pad, 7.5, mr], border=col_border)

def remove_system(name):
    sss.systems.pop(name)
    to_be_removed = []
    for k, v in sss.items():
        if k.startswith(name):
            to_be_removed.append(k)
    for k in to_be_removed:
        sss.pop(k)

    if 'selected_options' in sss:
        sss.selected_options = [
            option for option in sss.selected_options if option != name
        ]

with col1:
    st.subheader('System Inputs :dart:')
    if len(sss.systems) == 0:
        st.write('No system added yet.')
    else:
        st.write(' ')
        st.write(' ')
        
        # 현재 모드에 유효한 시스템만 필터링
        mode_upper = sss.mode
        systems = get_systems()  # 최신 상태 가져오기
        valid_systems = {}
        
        for sys_name, system in sss.systems.items():
            sys_type = system['type']
            # 현재 모드에 해당 시스템 타입이 존재하는지 확인
            if sys_type in systems[mode_upper]:
                valid_systems[sys_name] = system
        
        if not valid_systems:
            st.write('No valid systems for the current mode.')
        else:
            system_tabs = st.tabs(valid_systems.keys())
            for tab, system in zip(system_tabs, valid_systems.values()):
                with tab:
                    # 시스템 타입에 따른 제목 표시
                    system_info = systems[mode_upper][system['type']]
                    st.write(f"### {system_info['display']['title']} {system_info['display']['icon']}")
                    
                    # 파라미터를 카테고리별로 그룹화
                    params_by_category = {}
                    for k, v in system['parameters'].items():
                        category = v.get('category', 'General')  # category가 없으면 'General'로 분류
                        if category not in params_by_category:
                            params_by_category[category] = []
                        params_by_category[category].append((k, v))

                    # 카테고리별 하위 탭 생성
                    category_tabs = st.tabs([category.capitalize() for category in params_by_category.keys()])
                    for cat_tab, category in zip(category_tabs, params_by_category.keys()):
                        with cat_tab:
                            params = params_by_category[category]
                            n = len(params)
                            col11, col12 = st.columns(2)
                            
                            for i, (k, v) in enumerate(params):
                                if i < (n + 1) // 2:
                                    col = col11
                                else:
                                    col = col12

                                with col:
                                    system['parameters'][k]['value'] = st.number_input(
                                        f"{v['explanation'][LANG]}, {v['latex']} [{v['unit']}]",
                                        value=v['default'],
                                        step=v['step'],
                                        format=f"%.{max(0, -math.floor(math.log10(v['step'])))}f",
                                        key=f"{system['name']}:{k}",
                                    )

                    st.button(
                        'Remove system',
                        use_container_width=True,
                        key=system['name'],
                        on_click=functools.partial(remove_system, name=system['name']),
                    )

    # [system['name'] for system in sss.systems.values()]

# 현재 모드에 유효한 시스템만 평가
mode_upper = sss.mode.upper()
systems = get_systems()
for key in sss.systems.keys():
    try:
        system = sss.systems[key]
        # 현재 모드에 해당 시스템 타입이 존재하는지 확인
        if system['type'] in systems[mode_upper]:
            evaluate_parameters(sss, key)
    except Exception as e:
        print(f"Error evaluating parameters for {key}: {e}")

with col2:
    st.subheader('Output Data :chart_with_upwards_trend:')
    
    # 현재 모드에 유효한 시스템만 필터링
    mode_upper = sss.mode.upper()
    systems = get_systems()  # 최신 상태 가져오기
    valid_system_names = []
    
    for sys_name, system in sss.systems.items():
        sys_type = system['type']
        # 현재 모드에 해당 시스템 타입이 존재하는지 확인
        if sys_type in systems[mode_upper]:
            valid_system_names.append(sys_name)
    
    options = st.multiselect(
        'Select systems to display',
        valid_system_names,
        default=[opt for opt in (sss.selected_options if 'selected_options' in sss else []) if opt in valid_system_names],
        key='selected_options',
    )

    if len(options) != 0:
        # Initialize visualization manager with the registry
        viz_manager = VisualizationManager(registry)
        # 현재 모드에 맞는 시각화만 표시
        viz_manager.render_tabs(sss, options, mode=sss.mode.upper())
