import math
from typing import Any, List, Dict
import pandas as pd
import numpy as np
import altair as alt
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
from exergy_dashboard.chart import plot_waterfall_multi, create_efficiency_grade_chart
import enex_analysis as enex


# 기본 시스템 정의
COOLING_ASHP = {
    'display': {
        'title': 'Air source heat pump',
        'icon': ':snowflake:',
    },
    'parameters':{
        'T_0': {
            'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
            'latex': r'$T_0$',
            'default': 30.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_a_room': {
            'explanation': {'EN': 'Room Air Temperature', 'KR': '실내 공기 온도'},
            'latex': r'$T_{a,room}$',
            'default': 20.0,
            'range': [-50, 'T_0 - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_a_int_out': {
            'explanation': {'EN': 'Internal Unit Air Outlet Temperature', 'KR': '실내기 공기 토출 온도'},
            'latex': r'$T_{a,int,out}$',
            'default': 10.0,
            'range': [-60, 'T_a_room - 1.0'],
            'unit': '℃',
            'step': 0.5,
            'category': 'internal unit',
        },
        'Q_r_int': {
            'explanation': {'EN': 'Cooling load', 'KR': '냉방 부하'},
            'latex': r'$Q_{r,int}$',
            'default': 6000.0,
            'range': [0, 9000],
            'unit': 'W',
            'step': 500.0,
            'category': 'internal unit',
        },
        'Q_r_max': {
            'explanation': {'EN': 'Maximum Cooling Capacity', 'KR': '최대 냉방 용량'},
            'latex': r'$Q_{r,max}$',
            'default': 9000.0,
            'range': ['Q_r_int', 9000],
            'unit': 'W',
            'step': 500.0,
            'category': 'internal unit',
        },
        
        'T_r_int': {
            'explanation': {'EN': 'Internal Unit Refrigerant Temperature', 'KR': '실내기 측 냉매 온도'},
            'latex': r'$T_{r,int}$',
            'default': 5.0,
            'range': [-30, 'T_a_int_out - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'internal unit',
        },
        'T_r_ext': {
            'explanation': {'EN': 'External Unit Refrigerant Temperature', 'KR': '실외기 측 냉매 온도'},
            'latex': r'$T_{r,ext}$',
            'default': 45.0,
            'range': ['T_r_int + 5', 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'external unit',
        },
        
        'T_a_ext_out': {
            'explanation': {'EN': 'External Unit Air Outlet Temperature', 'KR': '실외기 공기 토출 온도'},
            'latex': r'$T_{a,ext,out}$',
            'default': 40.0,
            'range': ['T_0', 80],
            'unit': '℃',
            'step': 1.0,
            'category': 'external unit',
        },
        
    }
}
COOLING_GSHP = {
    'display': {
        'title': 'Ground source heat pump',
        'icon': ':earth_americas:',
    },
    'parameters': {
        't':{
            'explanation': {'EN': 'Operating time', 'KR': '운전 시간'},
            'latex': r'$t$',
            'default': 100.0,
            'range': [0, 2000],
            'unit': 'h',
            'step': 100.0,
            'category': 'Operating condition',
        },
        'T_0': {
            'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
            'latex': r'$T_0$',
            'default': 30.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_g': {
            'explanation': {'EN': 'Ground Temperature', 'KR': '토양온도'},
            'latex': r'$T_g$',
            'default': 15.0,
            'range': [10, 20],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_a_room': {
            'explanation': {'EN': 'Room Air Temperature', 'KR': '실내 공기 온도'},
            'latex': r'$T_{a,room}$',
            'default': 20.0,
            'range': [0, 'T_0-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_a_int_out': {
            'explanation': {'EN': 'Internal Unit Outlet Air Temperature', 'KR': '실내기 토출 공기 온도'},
            'latex': r'$T_{a,int,out}$',
            'default': 10.0,
            'range': [-20, 'T_a_room-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'internal unit',
        },
        'Q_r_int': {
            'explanation': {'EN': 'Cooling load', 'KR': '냉방 부하'},
            'latex': r'$Q_{r,int}$',
            'default': 6000.0,
            'range': [1000, 9000],
            'unit': 'W',
            'step': 500.0,
            'category': 'internal unit',
        },
        
        'T_r_int': {
            'explanation': {'EN': 'Internal Unit Refrigerant Temperature', 'KR': '실내기 측 냉매 온도'},
            'latex': r'$T_{r,int}$',
            'default': 5.0,
            'range': [-25, 'T_a_int_out-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'internal unit',
        },
        'H': {
            'explanation': {'EN': 'Borehole Height', 'KR': '보어홀 길이'},
            'latex': r'$H$',
            'default': 200.0,
            'range': [100, 300],
            'unit': 'm',
            'step': 50.0,
            'category': 'ground heat exchanger',
        },
        'r_b': {
            'explanation': {'EN': 'Borehole Radius', 'KR': '보어홀 반지름'},
            'latex': r'$r_b$',
            'default': 0.08,
            'range': [0.05, 0.1],
            'unit': 'm',
            'step': 0.005,
            'category': 'ground heat exchanger',
        },
        'R_b': {
            'explanation': {'EN': 'Borehole Thermal Resistance', 'KR': '보어홀 유효 열저항'},
            'latex': r'$R_b$',
            'default': 0.1,
            'range': [0.01, 0.5],
            'unit': 'm·K/W',
            'step': 0.01,
            'category': 'ground heat exchanger',
        },
        'V_f': {
            'explanation': {'EN': 'Fluid Velocity', 'KR': '유체 속도'},
            'latex': r'$V_f$',
            'default': 24.0,
            'range': [5.0, 30.0],
            'unit': 'L/min',
            'step': 1.0,
            'category': 'ground heat exchanger',
        },
        'E_pmp': {
            'explanation': {'EN': 'Ground heat exchanger Pump Power', 'KR': 'GHE 펌프 전력'},
            'latex': r'$E_{pmp}$',
            'default': 200.0,
            'range': [150, 250],
            'unit': 'W',
            'step': 10.0,
            'category': 'ground heat exchanger',
        },
        
        'k_g': {
            'explanation': {'EN': 'Ground Thermal Conductivity', 'KR': '토양 열전도도'},
            'latex': r'$k_g$',
            'default': 2.0,
            'range': [0.5, 5.0],
            'unit': 'W/m·K',
            'step': 0.1,
            'category': 'ground',
        },
        'c_g': {
            'explanation': {'EN': 'Ground Specific Heat', 'KR': '토양 비열'},
            'latex': r'$c_g$',
            'default': 800.0,
            'range': [500, 2000],
            'unit': 'J/kg·K',
            'step': 100.0,
            'category': 'ground',
        },
        'rho_g': {
            'explanation': {'EN': 'Ground Density', 'KR': '토양 밀도'},
            'latex': r'$\rho_g$',
            'default': 2000.0,
            'range': [1000, 3000],
            'unit': 'kg/m³',
            'step': 100.0,
            'category': 'ground',
        },
    }
}

# 시스템 등록
register_system('COOLING', 'Air source heat pump', COOLING_ASHP)
register_system('COOLING', 'Ground source heat pump', COOLING_GSHP)


# COOLING 모드 시각화 함수들
@viz_registry.register('COOLING', 'Exergy efficiency')
def plot_exergy_efficiency(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 효율 차트 생성"""
    # COOLING 모드 전용 시각화
    efficiencies = []
    
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        eff = sv['X_eff'] * 100
        efficiencies.append(eff)

    chart_data = pd.DataFrame({
        'efficiency': efficiencies,
        'system': selected_systems,
    })

    max_v = chart_data['efficiency'].max() if len(chart_data) > 0 else 100
    # max_v를 10 단위로 올림, tick_step은 10 또는 max_v에 맞춤
    if max_v <= 10:
        max_v = 10
        tick_step = 1
    else:
        max_v = int(np.ceil(max_v / 10.0)) * 10
        tick_step = max_v // 10

    c = alt.Chart(chart_data).mark_bar(size=30).encode(
        y=alt.Y('system:N', title='System', sort=None)
           .axis(title=None,
                 labelFontSize=18,
                 labelColor='black',
                 labelLimit=300,
                 labelPadding=20),
        x=alt.X('efficiency:Q', title='Exergy Efficiency [%]')
            .axis(
                labelFontSize=20,
                labelColor='black',
                titleFontSize=22,
                titleColor='black',
                values = np.arange(0, max_v + 1, tick_step).tolist(),
            )
            .scale(domain=[0, max_v]),
            color=alt.Color('system:N', legend=None),
        # tooltip=['system', 'efficiency'],
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
        text=alt.Text('efficiency:Q', format='.1f')
    )

    return c + text

@viz_registry.register('COOLING', 'Exergy consumption process')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    # COOLING 모드 전용 시각화
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        sys_type = session_state.systems[key]['type']
        
        if sys_type == 'Air source heat pump':
            items = [
                {'label': 'E_fan_ext', 'amount': sv['E_fan_ext'], 'desc': 'Exergy input from fan (external unit)'},
                {'label': 'X_r_ext(ext side)', 'amount': sv['X_r_ext'], 'desc': 'Cool exergy input from refrigerant (external unit side)'},
                {'label': 'Xc_ext', 'amount': -sv['Xc_ext'], 'desc': 'Exergy consumption (external unit)'},
                {'label': 'X_a_ext_out', 'amount': -sv['X_a_ext_out'], 'desc': 'Exergy output (external unit outlet air)'},
                {'label': 'E_cmp', 'amount': sv['E_cmp'], 'desc': 'Compressor power input (refrigerant)'},
                {'label': 'Xc_r', 'amount': -sv['Xc_r'], 'desc': 'Exergy consumption (refrigerant)'},
                {'label': 'X_r_ext(ref side)', 'amount': -sv['X_r_ext'], 'desc': 'Cool exergy output from refrigerant (external unit side)'},
                {'label': 'X_fan_int', 'amount': sv['E_fan_int'], 'desc': 'Exergy input from fan (internal unit)'},
                {'label': 'X_a_int_in', 'amount': sv['X_a_int_in'], 'desc': 'Exergy from room air'},
                {'label': 'Xc_int', 'amount': -sv['Xc_int'], 'desc': 'Exergy consumption (internal unit)'},
                {'label': 'Output', 'amount': 0, 'desc': 'Exergy output'},
            ]
        
        if sys_type == 'Ground source heat pump':
            items = [
                {'label': 'Xin_g', 'amount': sv['Xin_g'], 'desc': 'Exergy from undisturbed ground'},
                {'label': 'Xc_g', 'amount': -sv['Xc_g'], 'desc': 'Consumption in ground'},
                {'label': 'E_pmp', 'amount': sv['E_pmp'], 'desc': 'Electric input to pump'},
                {'label': 'Xc_GHE', 'amount': -sv['Xc_GHE'], 'desc': 'Consumption in ground heat exchanger'},
                {'label': 'X_r_exch(from refrigerant)', 'amount': abs(sv['X_r_exch']), 'desc': 'Cool exergy supplied by refrigerant' if sv['X_r_exch'] >= 0 else 'Warm exergy supplied by refrigerant'},
                {'label': 'Xc_exch', 'amount': -sv['Xc_exch'], 'desc': 'Consumption in heat exchanger'},
                {'label': 'E_cmp', 'amount': sv['E_cmp'], 'desc': 'Electric input to compressor'},
                {'label': 'Xc_r', 'amount': -sv['Xc_r'], 'desc': 'Consumption in refrigerant loop'},
                {'label': 'X_r_exch(to heat exchanger)', 'amount': -abs(sv['X_r_exch']), 'desc': 'Cool exergy supplied to heat exchanger' if sv['X_r_exch'] >= 0 else 'Warm exergy supplied to heat exchanger'},
                {'label': 'E_fan_int', 'amount': sv['E_fan_int'], 'desc': 'Electric input to fan'},
                {'label': 'X_a_int_in', 'amount': sv['X_a_int_in'], 'desc': 'Exergy from room air'},
                {'label': 'Xc_int', 'amount': -sv['Xc_int'], 'desc': 'Consumption in internal unit'},
                {'label': 'Xout_int', 'amount': 0, 'desc': 'Supply air to room'},
            ]
            
        for item in items:
            item['group'] = key
        source = pd.DataFrame(items)
        sources.append(source)

    if sources:
        source = pd.concat(sources)
        return plot_waterfall_multi(source)
    return alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_point()


# COOLING 모드 시각화 함수들
@viz_registry.register('COOLING', 'Exergy efficiency grade')
def plot_exergy_efficiency_grade(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 효율 차트 생성"""
    # COOLING 모드 전용 시각화
    cases = [

    ]
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        eff = sv['X_eff'] * 100
        name = ''.join(c[0] for c in key.title().split()[:-1]) + ' ' + key.title().split()[-1]
        cases.append({
            'name': name,
            'efficiency': float(eff),
            # No meaning.
            'range': '0-100',
            # No meaning.
            'y': 45,
        })

    chart = create_efficiency_grade_chart(
        cases=cases,
        margin=0.2,
        bottom_height=60,
        top_height=75,
        show_range=True,
        text_rotation=0,
        text_dx=7,
        text_dy=-12,
        grade_unit=8,
    ).properties(height=230)

    print(cases)
    return chart


@eval_registry.register('COOLING', 'Air source heat pump')
def evaluate_cooling_ashp(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    ASHP_C = enex.AirSourceHeatPump_cooling()
    ASHP_C.T0 = params['T_0']
    ASHP_C.T_a_room = params['T_a_room']
    ASHP_C.T_r_int = params['T_r_int']
    ASHP_C.T_a_int_out = params['T_a_int_out']
    ASHP_C.T_a_ext_out = params['T_a_ext_out']
    ASHP_C.T_r_ext = params['T_r_ext']
    ASHP_C.Q_r_int = params['Q_r_int']
    ASHP_C.Q_r_max = params['Q_r_max']
    ASHP_C.system_update()
    
    # fan power
    E_fan_int = ASHP_C.E_fan_int
    E_cmp     = ASHP_C.E_cmp
    E_fan_ext = ASHP_C.E_fan_ext

    X_a_int_in  = ASHP_C.X_a_int_in
    X_a_int_out = ASHP_C.X_a_int_out
    X_a_ext_in  = ASHP_C.X_a_ext_in
    X_a_ext_out = ASHP_C.X_a_ext_out

    X_r_int   = ASHP_C.X_r_int
    X_r_ext   = ASHP_C.X_r_ext

    Xin_int  = ASHP_C.Xin_int
    Xout_int = ASHP_C.Xout_int
    Xc_int   = ASHP_C.Xc_int

    Xin_r  = ASHP_C.Xin_r
    Xout_r = ASHP_C.Xout_r
    Xc_r   = ASHP_C.Xc_r

    Xin_ext  = ASHP_C.Xin_ext
    Xout_ext = ASHP_C.Xout_ext
    Xc_ext   = ASHP_C.Xc_ext

    Xin  = ASHP_C.Xin
    Xout = ASHP_C.Xout
    Xc   = ASHP_C.Xc

    X_eff = ASHP_C.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}


@eval_registry.register('COOLING', 'Ground source heat pump')
def evaluate_cooling_gshp(params: Dict[str, float]) -> Dict[str, float]:
    """GSHP 냉방 모드 평가 함수"""
    GSHP_C = enex.GroundSourceHeatPump_cooling()
    GSHP_C.time = params['t']
    GSHP_C.T0 = params['T_0']
    GSHP_C.T_g = params['T_g']
    GSHP_C.T_a_room = params['T_a_room']
    GSHP_C.T_a_int_out = params['T_a_int_out']
    GSHP_C.T_r_int = params['T_r_int']

    GSHP_C.height = params['H']
    GSHP_C.r_b = params['r_b']
    GSHP_C.R_b = params['R_b']
    m3s_to_Lmin = 1 / 60000 # 1 m³/s = 60000 L/min
    GSHP_C.V_f = params['V_f'] * m3s_to_Lmin # Convert L/min to m³/s
    
    GSHP_C.k_g = params['k_g']
    GSHP_C.c_g = params['c_g']
    GSHP_C.rho_g = params['rho_g']

    GSHP_C.E_pmp = params['E_pmp']
   
    GSHP_C.Q_r_int = params['Q_r_int']
    GSHP_C.system_update()

    # Ground
    Xin_g = GSHP_C.Xin_g
    Xout_g = GSHP_C.X_b
    Xc_g = GSHP_C.Xc_g

    # Ground heat exchanger
    X_r_exch = GSHP_C.X_r_exch
    E_pmp = GSHP_C.E_pmp
    Xin_GHE = GSHP_C.Xin_GHE
    Xout_GHE = GSHP_C.Xout_GHE
    Xc_GHE = GSHP_C.Xc_GHE

    # Heat exchanger
    Xin_exch = GSHP_C.Xin_exch
    Xout_exch = GSHP_C.Xout_exch
    Xc_exch = GSHP_C.Xc_exch

    # Closed refrigerant loop system
    E_cmp = GSHP_C.E_cmp
    Xin_r = GSHP_C.Xin_r
    Xout_r = GSHP_C.Xout_r
    Xc_r = GSHP_C.Xc_r

    # Internal unit
    X_a_int_in = GSHP_C.X_a_int_in
    E_fan_int = GSHP_C.E_fan_int
    Xin_int = GSHP_C.Xin_int
    Xout_int = GSHP_C.Xout_int
    Xc_int = GSHP_C.Xc_int

    # Exergy efficiency
    X_eff = GSHP_C.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}

