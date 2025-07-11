import math
from typing import Any, List, Dict
import pandas as pd
import altair as alt
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
from exergy_dashboard.chart import plot_waterfall_multi
import en_system_ex_analysis as enex


# 기본 시스템 정의
COOLING_ASHP = {
    'display': {
        'title': 'Air Source Heat Pump',
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
            'category': 'condition',
        },
        'T_a_room': {
            'explanation': {'EN': 'Room Air Temperature', 'KR': '실내 공기 온도'},
            'latex': r'$T_{a,room}$',
            'default': 20.0,
            'range': [-50, 'T_0 - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
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
            'explanation': {'EN': 'Internal Unit Heat Absorption', 'KR': '실내기 실내 흡열량'},
            'latex': r'$Q_{r,int}$',
            'default': 10000.0,
            'range': [0, 20000],
            'unit': 'W',
            'step': 100.0,
            'category': 'internal unit',
        },
        'Q_r_max': {
            'explanation': {'EN': 'Maximum Cooling Capacity', 'KR': '최대 냉방 용량'},
            'latex': r'$Q_{r,max}$',
            'default': 10000.0,
            'range': ['Q_r_int', 20000],
            'unit': 'W',
            'step': 100.0,
            'category': 'internal unit',
        },
        
        'T_r_int': {
            'explanation': {'EN': 'Internal Unit Refrigerant Temperature', 'KR': '실내기 측 냉매 온도'},
            'latex': r'$T_{r,int}$',
            'default': 5.0,
            'range': [-30, 'T_a_int_out - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
        },
        'T_r_ext': {
            'explanation': {'EN': 'External Unit Refrigerant Temperature', 'KR': '실외기 측 냉매 온도'},
            'latex': r'$T_{r,ext}$',
            'default': 45.0,
            'range': ['T_r_int + 5', 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
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
        'title': 'Ground Source Heat Pump(temporary)',
        'icon': ':earth_americas:',
    },
    'parameters': {
        'T_0': {
            'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
            'latex': r'$T_0$',
            'default': 32.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_g': {
            'explanation': {'EN': 'Ground Temperature', 'KR': '토양온도'},
            'latex': r'$T_g$',
            'default': 19.0,
            'range': [0, 20],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_a_room': {
            'explanation': {'EN': 'Room Air Temperature', 'KR': '실내 공기 온도'},
            'latex': r'$T_{a,room}$',
            'default': 20.0,
            'range': [0, 'T_0-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        
        'T_a_int_out': {
            'explanation': {'EN': 'Internal Unit Outlet Air Temperature', 'KR': '실내기 토출 공기 온도'},
            'latex': r'$T_{a,int,out}$',
            'default': 14.0,
            'range': [-20, 'T_a_room-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'internal unit',
        },
        'Q_r_int': {
            'explanation': {'EN': 'Internal Unit Heat Absorption', 'KR': '실내기 실내 흡열량'},
            'latex': r'$Q_{r,int}$',
            'default': 10000.0,
            'range': [0, 30000],
            'unit': 'W',
            'step': 500.0,
            'category': 'internal unit',
        },
        
        'T_r_int': {
            'explanation': {'EN': 'Internal Unit Refrigerant Temperature', 'KR': '실내기 측 냉매 온도'},
            'latex': r'$T_{r,int}$',
            'default': 9.0,
            'range': [-25, 'T_a_int_out-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
        },
        'T_r_exch': {
            'explanation': {'EN': 'Heat Exchanger Refrigerant Temperature', 'KR': '열교환기 측 냉매 온도'},
            'latex': r'$T_{r,exch}$',
            'default': 29.0,
            'range': ['T_g+1.0', 'T_0-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
        },
        
        'D': {
            'explanation': {'EN': 'Borehole Depth', 'KR': '보어홀 시작 깊이'},
            'latex': r'$D$',
            'default': 150.0,
            'range': [50, 300],
            'unit': 'm',
            'step': 10.0,
            'category': 'borehole',
        },
        'H': {
            'explanation': {'EN': 'Borehole Height', 'KR': '보어홀 길이'},
            'latex': r'$H$',
            'default': 100.0,
            'range': [10, 300],
            'unit': 'm',
            'step': 1.0,
            'category': 'borehole',
        },
        'r_b': {
            'explanation': {'EN': 'Borehole Radius', 'KR': '보어홀 반지름'},
            'latex': r'$r_b$',
            'default': 0.075,
            'range': [0.05, 0.2],
            'unit': 'm',
            'step': 0.001,
            'category': 'borehole',
        },
        'R_b': {
            'explanation': {'EN': 'Borehole Thermal Resistance', 'KR': '보어홀 유효 열저항'},
            'latex': r'$R_b$',
            'default': 0.1,
            'range': [0.01, 0.5],
            'unit': 'm·K/W',
            'step': 0.01,
            'category': 'borehole',
        },
        'V_f': {
            'explanation': {'EN': 'Fluid Velocity', 'KR': '유체 속도'},
            'latex': r'$V_f$',
            'default': 24.0,
            'range': [1.0, 50.0],
            'unit': 'L/min',
            'step': 1.0,
            'category': 'ground heat exchanger',
        },
        'E_pmp': {
            'explanation': {'EN': 'Ground Heat Exchanger Pump Power', 'KR': 'GHE 펌프 전력'},
            'latex': r'$E_{pmp}$',
            'default': 200,
            'range': [0, 1000],
            'unit': 'W',
            'step': 50.0,
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
register_system('COOLING', 'ASHP', COOLING_ASHP)
register_system('COOLING', 'GSHP', COOLING_GSHP)


# COOLING 모드 시각화 함수들
@viz_registry.register('COOLING', 'Exergy Efficiency')
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


@viz_registry.register('COOLING', 'Exergy Consumption Process')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    # COOLING 모드 전용 시각화
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        sys_type = session_state.systems[key]['type']
        label_exps = {
            'ASHP': {
                'Input': 'Exergy input',
                'X_c_int': 'Exergy consumption (internal unit)',
                'X_c_ref': 'Exergy consumption (refrigerant)',
                'X_c_ext': 'Exergy consumption (external unit)',
                'X_ext_out': 'Exergy loss (external air out)',
                'Output': 'Exergy output',
            },
            'GSHP': {
                'Input': 'Exergy input',
                'X_c_int': 'Exergy consumption (internal unit)',
                'X_c_ref': 'Exergy consumption (refrigerant)',
                'X_c_GHE': 'Exergy consumption (ground heat exchanger)',
                'Output': 'Exergy output',
            },
            'EH': {
                'Input': 'Exergy input',
                'X_c_int': 'Exergy consumption (internal unit)',
                'X_c_ref': 'Exergy consumption (heater)',
                'X_c_GHE': 'Exergy consumption (heat transfer)',
                'Output': 'Exergy output',
            },
        }
        if sys_type == 'ASHP':
            labels = ['Input', 'X_c_int', 'X_c_ref', 'X_c_ext', 'X_ext_out', 'Output']
            labels_exp = [label_exps[sys_type].get(l, l) for l in labels]
            amounts = [sv['Xin_A'], -sv['Xc_int_A'], -sv['Xc_r_A'], -sv['Xc_ext_A'], -sv['X_a_ext_out_A'], 0]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
                'desc': labels_exp,
            })
            sources.append(source)
        
        if sys_type == 'GSHP':
            labels = ['Input', 'X_c_int', 'X_c_ref', 'X_c_GHE', 'Output']
            labels_exp = [label_exps[sys_type].get(l, l) for l in labels]
            amounts = [sv['Xin_G'], -sv['Xc_int_G'], -sv['Xc_r_G'], -sv['Xc_GHE'], 0]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
                'desc': labels_exp,
            })
            sources.append(source)
        
        if sys_type == 'EH':
            labels = ['Input', 'X_c_int', 'X_c_ref', 'X_c_GHE', 'Output']
            labels_exp = [label_exps[sys_type].get(l, l) for l in labels]
            amounts = [sv['Xin_G'], -sv['Xc_int_G'], -sv['Xc_r_G'], -sv['Xc_GHE'], 0]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
                'desc': labels_exp,
            })
            sources.append(source)

    if sources:
        source = pd.concat(sources)
        return plot_waterfall_multi(source)
    return alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_point()


@eval_registry.register('COOLING', 'ASHP')
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


@eval_registry.register('COOLING', 'GSHP')
def evaluate_cooling_gshp(params: Dict[str, float]) -> Dict[str, float]:
    """GSHP 냉방 모드 평가 함수"""
    GSHP_C = enex.GroundSourceHeatPump_cooling()
    GSHP_C.T0 = params['T_0']
    GSHP_C.T_g = params['T_g']
    GSHP_C.T_a_room = params['T_a_room']
    GSHP_C.T_a_int_out = params['T_a_int_out']
    GSHP_C.T_r_int = params['T_r_int']
    GSHP_C.T_r_exch = params['T_r_exch']

    GSHP_C.depth = params['D']
    GSHP_C.height = params['H']
    GSHP_C.r_b = params['r_b']
    GSHP_C.R_b = params['R_b']
    m3s_to_Lmin = 1 / 60000 # 1 m³/s = 60000 L/min
    GSHP_C.V_f = params['V_f'] * m3s_to_Lmin # Convert L/min to m³/s
    
    GSHP_C.k_g = params['k_g']
    GSHP_C.c_g = params['c_g']
    GSHP_C.rho_g = params['rho_g']
    
    GSHP_C.E_f_int = params['E_f_int']
    GSHP_C.E_pmp = params['E_pmp']
   
    GSHP_C.Q_r_int = params['Q_r_int']
    GSHP_C.system_update()

    # Ground
    Xin_g = GSHP_C.X_g
    Xout_g = GSHP_C.X_b
    Xc_g = Xin_g - Xout_g

    # Ground heat exchanger
    Xin_GHE = GSHP_C.E_pmp + Xout_g + GSHP_C.X_f_in
    Xout_GHE = GSHP_C.X_f_out 
    Xc_GHE = Xin_GHE - Xout_GHE

    # Heat exchanger
    Xin_exch = Xout_GHE 
    Xout_exch = GSHP_C.X_r_exch + GSHP_C.X_f_in
    Xc_exch = Xin_exch - Xout_exch

    # Closed refrigerant loop system
    Xin_r = GSHP_C.E_cmp + GSHP_C.X_r_exch
    Xout_r = GSHP_C.X_r_int
    Xc_r = Xin_r - Xout_r

    # Internal unit
    Xin_int = GSHP_C.E_fan_int + GSHP_C.X_r_int + GSHP_C.X_a_int_in
    Xout_int = GSHP_C.X_a_int_out
    Xc_int = Xin_int - Xout_int

    # Exergy efficiency
    X_eff = GSHP_C.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}

