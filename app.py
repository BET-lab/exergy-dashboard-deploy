import math
import copy
import functools
import streamlit as st
from exergy_dashboard.system import SYSTEM_CASE
from exergy_dashboard.evaluation import evaluate_parameters
from exergy_dashboard.visualization import VisualizationManager


LANG = 'EN'


st.set_page_config(
    page_title='Exergy Analysis',
    page_icon=':fire:',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Streamlit의 session_state를 더 짧은 변수명으로 할당
# session_state는 앱의 상태를 저장하는 객체로, 페이지 새로고침 간에 데이터를 유지함
# 사용자 상호작용, 시스템 상태, 계산 결과 등을 저장하는 데 사용됨
# 이 변수를 통해 모드, 시스템 구성, 카운터 등의 상태를 관리
sss = st.session_state

if 'mode' not in sss:
    sss.mode = 'Cooling'

def reset_systems():
    sss.systems = {}
    sss.system_count = {
        k: 0 for k in SYSTEM_CASE[sss.mode.upper()].keys()
    }


if 'systems' not in sss:
    sss.systems = {}

if 'system_count' not in sss:
    sss.system_count = {
        k: 0 for k in SYSTEM_CASE[sss.mode.upper()].keys()
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
    system_name = system_name.upper()

    sss.system_count[system_name] += 1

    system = copy.deepcopy(SYSTEM_CASE[mode][system_name])
    system['name'] = f"{system_name} {sss.system_count[system_name]}"
    system['type'] = system_name

    return system


def add_system(type_):
    data = create_system(mode=sss.mode, system_name=type_)
    sss.systems[data['name']] = data


with st.sidebar:
    st.title('Options')
    st.divider()
    st.header('시스템 모드')
    st.segmented_control(
        'Mode',
        default='Cooling',
        options=['Cooling', 'Heating', 'Hot Water'],
        key='mode',
        selection_mode='single',
        label_visibility='collapsed',

    )
    st.header('시스템 추가')
    if len(SYSTEM_CASE[sss.mode.upper()]) == 0:
        st.write('No system available for the selected mode.')
        st.stop()
    else:
        selected = st.selectbox(
            'System type', SYSTEM_CASE[sss.mode.upper()].keys()
        )
        st.button(
            'Add system',
            use_container_width=True,
            on_click=functools.partial(add_system, type_=selected),
        )

# st.get_option('layout')
ml, mr = 0.0001, 0.0001
pad = 0.2
col_border = False
_, title_col, title_right_col = st.columns([ml, 4 + pad + 5, mr], border=col_border)
_, title_col1, _, title_col2, _ = st.columns([ml, 4, pad, 5, mr], border=col_border)
_, col1, _, col2, _ = st.columns([ml, 4, pad, 5, mr], border=col_border)


with title_col:
    st.header('Exergy Analyzer  ', help='This is a help message.')


def remove_system(name):
    """
    시스템을 제거하는 함수
    
    Parameters
    ----------
    name : str
        제거할 시스템의 이름
        
    Notes
    -----
    - 시스템 딕셔너리에서 해당 시스템을 제거합니다.
    - 해당 시스템과 관련된 세션 상태 변수들도 함께 제거합니다.
    - 선택된 옵션 목록에서도 해당 시스템을 제거합니다.
    """
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
        system_tabs = st.tabs(sss.systems.keys())
        for tab, system in zip(system_tabs, sss.systems.values()):
            with tab:
                # 시스템 타입에 따른 제목 표시
                system_info = SYSTEM_CASE[sss.mode.upper()][system['type']]
                st.write(f"### {system_info['display']['title']} {system_info['display']['icon']}")

                # 파라미터를 카테고리별로 그룹화
                params_by_category = {}
                for k, v in system['parameters'].items():
                    category = v.get('category', 'General')  # category가 없으면 'General'로 분류
                    if category not in params_by_category:
                        params_by_category[category] = []
                    params_by_category[category].append((k, v))

                # 카테고리별 하위 탭 생성
                category_tabs = st.tabs([category.title() for category in params_by_category.keys()])
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
                                    format=f"%.{-math.floor(math.log10(v['step']))}f",
                                    key=f"{system['name']}:{k}",
                                )

                st.button(
                    'Remove system',
                    use_container_width=True,
                    key=system['name'],
                    on_click=functools.partial(remove_system, name=system['name']),
                )

    # [system['name'] for system in sss.systems.values()]


for key in sss.systems.keys():
    evaluate_parameters(sss, key)


with col2:
    st.subheader('Output Data :chart_with_upwards_trend:')
    options = st.multiselect(
        'Select systems to display',
        [system['name'] for system in sss.systems.values()],
        default=sss.selected_options if 'selected_options' in sss else None,
        key='selected_options',
    )

    if len(options) != 0:
        # Initialize visualization manager and render all registered visualizations
        viz_manager = VisualizationManager()
        viz_manager.render_tabs(sss, options)