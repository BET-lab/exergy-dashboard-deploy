import math
import copy
import functools
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from exergy_dashboard.system import SYSTEM_CASE
from exergy_dashboard.evaluation import evaluate_parameters_cooling
from exergy_dashboard.chart import (
    plot_waterfall_cooling_ashp,
    plot_waterfall_cooling_gshp,
    plot_waterfall_multi,
)

LANG = 'EN'


def create_dynamic_multiview(dataframes, cols=2):
    """
    다양한 길이의 데이터프레임 리스트로부터 동적 다중 뷰 플롯 생성
    
    Parameters:
    - dataframes: 차트로 만들 데이터프레임 리스트
    - cols: 열의 개수 (기본값 2)
    """
    colors = [
        '#4c95d9',
        '#a8d9ff',
        '#ff6a6a',
        '#ffc4c4',
        '#69c7ba',
        '#a4f3bd',
        '#ffab4c',
        '#ffde96',
        '#9878d2',
        '#e1e5ec',
    ] * 50
    # 각 데이터프레임에 대한 기본 차트 생성 함수
    def create_base_chart(df, title, n):
        # 데이터프레임의 숫자형 컬럼 찾기
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 1:
            # 단일 숫자 컬럼인 경우 히스토그램
            chart = alt.Chart(df).mark_bar(color=colors[n]).encode(
                alt.X(f'{numeric_cols[0]}:Q', bin=True),
                alt.Y('count()', stack=None)
            )
        elif len(numeric_cols) >= 2:
            # 두 개 이상의 숫자 컬럼인 경우 산점도
            chart = alt.Chart(df).mark_circle(color=colors[n]).encode(
                x=f'{numeric_cols[0]}:Q',
                y=f'{numeric_cols[1]}:Q',
                # color=alt.value('steelblue')
            )
        else:
            # 숫자 컬럼이 없는 경우 막대 그래프
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                chart = alt.Chart(df).mark_bar(color=colors[n]).encode(
                    x=f'{categorical_cols[0]}:N',
                    y='count()'
                )
            else:
                raise ValueError("플롯할 적절한 컬럼이 없습니다.")
        
        chart.configure_mark(
            color=colors[n],
        )

        return chart.properties(
            title=title, 
            width=250, 
            height=200
        )
    
    # 동적으로 차트 리스트 생성
    charts = [
        create_base_chart(df, df['system'].iloc[0], i) 
        for i, df in enumerate(dataframes)
    ]
    
    # 열 수에 맞춰 동적으로 레이아웃 생성
    def chunk_charts(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
    
    # 차트들을 chunk로 나누어 수평/수직 결합
    chart_rows = [
        alt.hconcat(*row_charts) 
        for row_charts in chunk_charts(charts, cols)
    ]
    
    # 최종 수직 결합
    return alt.vconcat(*chart_rows)


st.set_page_config(
    page_title='Exergy Analysis',
    page_icon=':fire:',
    layout='wide',
    initial_sidebar_state='expanded'
)

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
    """
    mode: 'cooling' or 'heating' or 'hot_water' ?
    system_name: 'ASHP' or 'GSHP' or 'Boiler' or 'Solar' or 'Battery' ?
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
        # st.stop()
    else:
        st.write(' ')
        st.write(' ')
        tabs = st.tabs(sss.systems.keys())
        for tab, system in zip(tabs, sss.systems.values()):
            with tab:
                if system['type'] == 'ASHP':
                    st.write('### Air Source Heat Pump :snowflake:')
                elif system['type'] == 'GSHP':
                    st.write('### Ground Source Heat Pump :earth_americas:')

                n = len(system['parameters'])
                col11, col12 = st.columns(2)
                for i, (k, v) in enumerate(system['parameters'].items()):
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
                            # label_visibility='collapsed',
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
    evaluate_parameters_cooling(sss, key)


with col2:
    st.subheader('Output Data :chart_with_upwards_trend:')
    options = st.multiselect(
        'Select systems to display',
        [system['name'] for system in sss.systems.values()],
        # sss.seledted_options if 'selected_options' in sss else [],
        default=sss.selected_options if 'selected_options' in sss else None,
        key='selected_options',
    )

    if len(options) != 0:
        st.subheader('1. Exergy Efficiency')
        count = 0
        efficiencies = []
        xins = []
        xouts = []
        for key in options:
            sv = sss.systems[key]['variables']
            if sss.systems[key]['type'] == 'ASHP':
                eff = sv['Xout_A'] / sv['Xin_A'] * 100
                efficiencies.append(eff)
                xins.append(sv['Xin_A'])
                xouts.append(sv['Xout_A'])
            if sss.systems[key]['type'] == 'GSHP':
                eff = sv['Xout_G'] / sv['Xin_G'] * 100
                efficiencies.append(eff)
                xins.append(sv['Xin_G'])
                xouts.append(sv['Xout_G'])

        # Draw bar chart of efficiencies. color is based on options.
        chart_data = pd.DataFrame(
            data={
                'efficiency': efficiencies,
                'xins': xins,
                'xouts': xouts,
                'system': options,
            },
        )

        # st.write(chart_data)
        max_v = chart_data['efficiency'].max()

        # No sort for Y.
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
            height=len(options) * 60 + 50,
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

        c = (c + text)
            

        # # Draw random altair chart. but use options.
        # chart_data = pd.DataFrame(
        #     data={
        #         'a': np.random.randn(100),
        #         'b': np.random.randn(100),
        #         'c': np.random.randn(100),
        #         'system': np.random.choice(options, 100),
        #     },
        # )

        # c = alt.Chart(chart_data).mark_circle().encode(
        #     x='a', y='b', size='c', color='system', tooltip=['a', 'b', 'c']
        # ).interactive()

        st.altair_chart(c, use_container_width=True)

        st.subheader('2. Exergy Consumption Process')

        sources = []
        for key in options:
            sv = sss.systems[key]['variables']
            if sss.systems[key]['type'] == 'ASHP':
                print('new fig')

                labels = ['Input', r'X_{c,int}', r'X_{c,ref}', r'X_{c,ext}', r'X_{ext,out}', 'Output']
                amounts = [sv['Xin_A'], -sv['Xc_int_A'], -sv['Xc_r_A'], -sv['Xc_ext_A'], -sv['X_a_ext_out_A'], 0]
                source = pd.DataFrame({
                    'label': labels,
                    'amount': amounts,
                    'group': [key] * len(labels),
                })

                sources.append(source)
                # })
                # fig = plot_waterfall_cooling_ashp(
                #     Xin_A=sv['Xin_A'],
                #     Xc_int_A=sv['Xc_int_A'],
                #     Xc_r_A=sv['Xc_r_A'],
                #     Xc_ext_A=sv['Xc_ext_A'],
                #     X_a_ext_out_A=sv['X_a_ext_out_A'],
                #     Xout_A=sv['Xout_A'],
                #     n=count,
                #     name=key,
                # )
                count += 1
            if sss.systems[key]['type'] == 'GSHP':
                labels = ['Input', r'X_{c,int}', r'X_{c,ref}', r'X_{c,GHE}', 'Output']
                amounts = [sv['Xin_G'], -sv['Xc_int_G'], -sv['Xc_r_G'], -sv['Xc_GHE'], 0]
                source = pd.DataFrame({
                    'label': labels,
                    'amount': amounts,
                    'group': [key] * len(labels),
                })
 
                sources.append(source)
                count += 1      

        source = pd.concat(sources)
        c = plot_waterfall_multi(source, 'Input', 'Output')
        # figs = []
        # count = 0
        # for key in options:
        #     sv = sss.systems[key]['variables']
        #     if sss.systems[key]['type'] == 'ASHP':
        #         print('new fig')
        #         fig = plot_waterfall_cooling_ashp(
        #             Xin_A=sv['Xin_A'],
        #             Xc_int_A=sv['Xc_int_A'],
        #             Xc_r_A=sv['Xc_r_A'],
        #             Xc_ext_A=sv['Xc_ext_A'],
        #             X_a_ext_out_A=sv['X_a_ext_out_A'],
        #             Xout_A=sv['Xout_A'],
        #             n=count,
        #             name=key,
        #         )
        #         count += 1
        #     if sss.systems[key]['type'] == 'GSHP':
        #         fig = plot_waterfall_cooling_gshp(
        #             Xin_G=sv['Xin_G'],
        #             X_g=sv['X_g'],
        #             Xc_int_G=sv['Xc_int_G'],
        #             Xc_r_G=sv['Xc_r_G'],
        #             Xc_GHE=sv['Xc_GHE'],
        #             Xout_G=sv['Xout_G'],
        #             n=count,
        #             name=key,
        #         )
        #         count += 1                

        #     figs.append(fig)

        # n = len(figs)
        # iter_ = iter(figs)
        # with st.spinner('Loading...'):
        #     for i, fig in enumerate(range((n + 1) // 2)):
        #         if i % 2 == 0:
        #             cols = st.columns(2)

        #         for col in cols:
        #             try:
        #                 col.write(next(iter_))
        #             except StopIteration:
        #                 break
        st.altair_chart(c)