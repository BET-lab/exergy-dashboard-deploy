import math
import copy
import functools
import streamlit as st
import importlib
import os
import glob

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
    page_title='Exergy Analyzer',
    page_icon=':fire:',
    layout='wide',
    initial_sidebar_state='expanded'
)

# 사이드바 너비 조절을 위한 CSS 추가
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        width: 350px;
    }
    
    /* 탭 폰트 스타일링 */
    button[data-testid="stTab"] {
        font-weight: normal !important;
        font-size: 16px !important;
    }
    
    /* 탭 내부 텍스트 컨테이너 스타일링 */
    button[data-testid="stTab"] div[data-testid="stMarkdownContainer"] p {
        font-weight: normal !important;
        font-size: 16px !important;
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


def remove_system(name):
    sss.systems.pop(name)
    to_be_removed = []
    for k, v in sss.items():
        if isinstance(k, str) and k.startswith(name):
            to_be_removed.append(k)
    for k in to_be_removed:
        sss.pop(k)

    # selected_options에서 삭제된 시스템의 short name 제거
    if 'selected_options' in sss:
        # short name 생성 (visualization 부분과 동일한 로직)
        short_name = ''.join(c[0] for c in name.title().split()[:-1]) + ' ' + name.title().split()[-1]
        sss.selected_options = [
            option for option in sss.selected_options if option != short_name
        ]


with st.sidebar:
    st.title('Exergy Analyzer')
    st.divider()
    st.header('System Operating Mode')
    systems = get_systems()  # 최신 상태 가져오기
    available_modes = [k.capitalize() for k in systems.keys()]
    if not available_modes:
        st.write('No modes available.')
        st.stop()
    previous_mode = sss.mode if 'mode' in sss else None

    # Segmented control로 모드 선택
    selected_mode = st.segmented_control(
        label="Select mode",
        options=available_modes,
        # index=available_modes.index(sss.mode) if sss.mode in available_modes else 0,
        key="mode_segmented_control",
        label_visibility='collapsed',
        # width="stretch",
    )

    if selected_mode is None:
        st.stop()

    if sss.mode != selected_mode:
        sss.mode = selected_mode
        reset_systems()
        if 'selected_options' in sss:
            sss.selected_options = []
        if 'selected_system_tab' in sss:
            sss.selected_system_tab = None
        st.rerun()

    # --- 공간 추가 ---
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    st.header('Add New System')
    systems = get_systems()  # 최신 상태 가져오기
    if len(systems[sss.mode.upper()]) == 0:
        st.write('No system available for the selected mode.')
        st.stop()
    else:
        selected = st.selectbox(
            'System type', systems[sss.mode.upper()].keys()
        )
        st.button(
            'Add to List',
            use_container_width=True,
            on_click=functools.partial(add_system, type_=selected),
        )

    # --- 공간 추가 ---
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    # 시스템 type 선택을 버튼으로 변경
    mode_upper = sss.mode.upper()
    valid_systems = [sys_name for sys_name, system in sss.systems.items() if system['type'] in systems[mode_upper]]
    if valid_systems:
        st.header('Systems for Comparison')
        # 세션 상태의 선택값이 유효하지 않으면 첫 번째로 자동 설정
        if 'selected_system_tab' not in st.session_state or st.session_state['selected_system_tab'] not in valid_systems:
            st.session_state['selected_system_tab'] = valid_systems[0]
        # 라디오 버튼으로 시스템 선택 (index 항상 유효하게)
        selected_system = st.radio(
            label="Select a system",
            options=valid_systems,
            # index=valid_systems.index(st.session_state['selected_system_tab']),
            key="selected_system_radio",
            label_visibility='collapsed',
        )
        st.session_state['selected_system_tab'] = selected_system
        
        # Remove selected 버튼 추가
        st.button(
            'Remove selected',
            use_container_width=True,
            key=f"remove_{selected_system}",
            on_click=functools.partial(remove_system, name=selected_system),
        )
    else:
        st.session_state['selected_system_tab'] = None

ml, mr = 0.0001, 0.0001
pad = 0.6
col_border = False
_, title_col, title_right_col = st.columns([ml, 4 + pad + 5, mr], border=col_border)
_, title_col1, _, title_col2, _ = st.columns([ml, 2.5, pad, 7.5, mr], border=col_border)
_, col1, _, col2, _ = st.columns([ml, 2.5, pad, 7.5, mr], border=col_border)



with col1:
    st.subheader('System Inputs :dart:')
    if len(sss.systems) == 0 or not st.session_state.get('selected_system_tab'):
        st.write('No system added yet.')
    else:
        system = sss.systems[st.session_state['selected_system_tab']]
        mode_upper = sss.mode.upper()
        systems = get_systems()
        system_info = systems[mode_upper][system['type']]
        st.write(f"#### {system_info['display']['title']} {system_info['display']['icon']}")

        # 파라미터를 카테고리별로 그룹화
        params_by_category = {}
        for k, v in system['parameters'].items():
            category = v.get('category', 'General')
            if category not in params_by_category:
                params_by_category[category] = []
            params_by_category[category].append((k, v))

        # 카테고리별 하위 탭 생성
        category_tabs = st.tabs([category.capitalize() for category in params_by_category.keys()])
        for cat_tab, category in zip(category_tabs, params_by_category.keys()):
            with cat_tab:
                params = params_by_category[category]
                for k, v in params:
                    system['parameters'][k]['value'] = st.number_input(
                        f"{v['explanation'][LANG].capitalize()}, {v['latex']} [{v['unit']}]",
                        value=v['default'],
                        step=v['step'],
                        format=f"%.{max(0, -math.floor(math.log10(v['step'])))}f",
                        key=f"{system['name']}:{k}",
                    )

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
    st.subheader('Results Visualization :chart_with_upwards_trend:')
    
    # 현재 모드에 유효한 시스템만 필터링
    mode_upper = sss.mode.upper()
    systems = get_systems()  # 최신 상태 가져오기
    valid_system_names = []
    
    for sys_name, system in sss.systems.items():
        sys_type = system['type']
        # 현재 모드에 해당 시스템 타입이 존재하는지 확인
        if sys_type in systems[mode_upper]:
            valid_system_names.append(sys_name)
    
    short_name_map = {
        name: ''.join(c[0] for c in name.title().split()[:-1]) + ' ' + name.title().split()[-1]
        for name in valid_system_names
    }

    short_name_reverse_map = {
        v: k for k, v in short_name_map.items()
    }

    options = st.multiselect(
        'Select systems to display',
        short_name_map.values(),
        default=[opt for opt in (sss.selected_options if 'selected_options' in sss else []) if opt in short_name_map.values()],
        key='selected_options',
    )

    options = [short_name_reverse_map[opt] for opt in options]

    if len(options) != 0:
        # Initialize visualization manager with the registry
        viz_manager = VisualizationManager(registry)
        # 현재 모드에 맞는 시각화만 표시
        viz_manager.render_tabs(sss, options, mode=sss.mode.upper())
