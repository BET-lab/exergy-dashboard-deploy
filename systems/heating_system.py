import math
from typing import Any, List, Dict
import pandas as pd
import numpy as np
import altair as alt
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
from exergy_dashboard.chart import plot_waterfall_multi
import en_system_ex_analysis as enex


# 기본 시스템 정의
HEATING_ASHP = {
    'display': {
        'title': 'Air source heat pump',
        'icon': ':snowflake:',
    },
    'parameters':{
        'T_0': {
            'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_a_room': {
            'explanation': {'EN': 'Room Air Temperature', 'KR': '실내 공기 온도'},
            'latex': r'$T_{a,room}$',
            'default': 20.0,
            'range': ['T_0 + 1.0', 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_a_int_out': {
            'explanation': {'EN': 'Internal Unit Air Outlet Temperature', 'KR': '실내기 공기 토출 온도'},
            'latex': r'$T_{a,int,out}$',
            'default': 30.0,
            'range': ['T_a_room + 1.0', 60],
            'unit': '℃',
            'step': 1.0,
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
            'explanation': {'EN': 'Maximum HEATING Capacity', 'KR': '최대 냉방 용량'},
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
            'default': 35.0,
            'range': ['T_a_room + 1.0', 80],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
        },
        'T_r_ext': {
            'explanation': {'EN': 'External Unit Refrigerant Temperature', 'KR': '실외기 측 냉매 온도'},
            'latex': r'$T_{r,ext}$',
            'default': -15.0,
            'range': [-40 , 'T_a_ext_out - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
        },
        'T_a_ext_out': {
            'explanation': {'EN': 'External Unit Air Outlet Temperature', 'KR': '실외기 공기 토출 온도'},
            'latex': r'$T_{a,ext,out}$',
            'default': -10.0,
            'range': [-30, 'T_0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'external unit',
        },
        
    }
}
HEATING_GSHP = {
    'display': {
        'title': 'Ground source heat pump',
        'icon': ':earth_americas:',
    },
    'parameters': {
        # Condition ----------------------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-30, 30],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_g': {
            'explanation': {'EN': 'Ground Temperature', 'KR': '토양온도'},
            'latex': r'$T_g$',
            'default': 15.0,
            'range': [0, 20],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_a_room': {
            'explanation': {'EN': 'Room Air Temperature', 'KR': '실내 공기 온도'},
            'latex': r'$T_{a,room}$',
            'default': 20.0,
            'range': ['T_0+1.0', 40],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        
        # Internal Unit ----------------------------------------------------------------------------
        'T_a_int_out': {
            'explanation': {'EN': 'Internal Unit Outlet Air Temperature', 'KR': '실내기 토출 공기 온도'},
            'latex': r'$T_{a,int,out}$',
            'default': 30.0,
            'range': ['T_a_room+1.0', 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'internal unit',
        },
        'Q_r_int': {
            'explanation': {'EN': 'Internal Unit Heat Absorption', 'KR': '실내기 실내 흡열량'},
            'latex': r'$Q_{r,int}$',
            'default': 4000.0,
            'range': [0, 30000],
            'unit': 'W',
            'step': 500.0,
            'category': 'internal unit',
        },
        
        # Refrigerant ----------------------------------------------------------------------------
        'T_r_int': {
            'explanation': {'EN': 'Internal Unit Refrigerant Temperature', 'KR': '실내기 측 냉매 온도'},
            'latex': r'$T_{r,int}$',
            'default': 35.0,
            'range': ['T_a_room + 1.0', 60],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
        },
        'T_r_exch': {
            'explanation': {'EN': 'Heat Exchanger Refrigerant Temperature', 'KR': '열교환기 측 냉매 온도'},
            'latex': r'$T_{r,exch}$',
            'default': 5.0,
            'range': [-30, 'T_g-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'refrigerant',
        },
        
        # borehole ----------------------------------------------------------------------------
        'D': {
            'explanation': {'EN': 'Borehole Depth', 'KR': '보어홀 시작 깊이'},
            'latex': r'$D$',
            'default': 0.0,
            'range': [50, 300],
            'unit': 'm',
            'step': 10.0,
            'category': 'borehole',
        },
        'H': {
            'explanation': {'EN': 'Borehole Height', 'KR': '보어홀 길이'},
            'latex': r'$H$',
            'default': 200.0,
            'range': [10, 300],
            'unit': 'm',
            'step': 1.0,
            'category': 'borehole',
        },
        'r_b': {
            'explanation': {'EN': 'Borehole Radius', 'KR': '보어홀 반지름'},
            'latex': r'$r_b$',
            'default': 0.08,
            'range': [0.05, 0.2],
            'unit': 'm',
            'step': 0.001,
            'category': 'borehole',
        },
        'R_b': {
            'explanation': {'EN': 'Borehole Thermal Resistance', 'KR': '보어홀 유효 열저항'},
            'latex': r'$R_b$',
            'default': 0.108,
            'range': [0.01, 0.5],
            'unit': 'm·K/W',
            'step': 0.01,
            'category': 'borehole',
        },
        
        # Ground Heat Exchanger ----------------------------------------------------------------------------
        'V_f': {
            'explanation': {'EN': 'Fluid volumetric flow rate', 'KR': '유체 체적 유량'},
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
            'default': 200.0,
            'range': [0, 1000],
            'unit': 'W',
            'step': 50.0,
            'category': 'ground heat exchanger',
        },
        
        # Ground ----------------------------------------------------------------------------
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
            'range': [500, 5000],
            'unit': 'kg/m³',
            'step': 100.0,
            'category': 'ground',
        },
    }
}
ELECTRIC_HEATER = {
    'display': {
        'title': 'Electric Heater',
        'icon': ':electric_plug:',
    },
    'parameters': {
        # Condition ----------------------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
            'latex': r'$T_0$',
            'default': 10.0,
            'range': [-30, 30],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_mr': {
            'explanation': {'EN': 'Mean Radiant Temperature', 'KR': '평균 복사 온도'},
            'latex': r'$T_{mr}$',
            'default': 15.0,
            'range': [0, 20],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_a_room': {
            'explanation': {'EN': 'Room Air Temperature', 'KR': '실내 공기 온도'},
            'latex': r'$T_{a,room}$',
            'default': 20.0,
            'range': ['T_0+1.0', 40],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
            
        # Heater material properties ------------------------------------------------------------
        'c_heater': {
            'explanation': {'EN': 'Heater Specific Heat', 'KR': '히터 비열'},
            'latex': r'$c$',
            'default': 500.0,
            'range': [100, 1000],
            'unit': 'J/kg·K',
            'step': 10.0,
            'category': 'heater material',
        },
        'rho_heater': {
            'explanation': {'EN': 'Heater Density', 'KR': '히터 밀도'},
            'latex': r'$\rho$',
            'default': 7800.0,
            'range': [1000, 9000],
            'unit': 'kg/m³',
            'step': 100.0,
            'category': 'heater material',
        },
        'k_heater': {
            'explanation': {'EN': 'Heater Thermal Conductivity', 'KR': '히터 열전도도'},
            'latex': r'$k$',
            'default': 50.0,
            'range': [10, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'heater material',
        },
        
        # Heater geometry -----------------------------------------------------------------------
        'D': {
            'explanation': {'EN': 'Heater Thickness', 'KR': '히터 두께'},
            'latex': r'$D$',
            'default': 0.005,
            'range': [0.001, 0.02],
            'unit': 'm',
            'step': 0.001,
            'category': 'heater geometry',
        },
        'H': {
            'explanation': {'EN': 'Heater Height', 'KR': '히터 높이'},
            'latex': r'$H$',
            'default': 0.5,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'heater geometry',
        },
        'W': {
            'explanation': {'EN': 'Heater Width', 'KR': '히터 폭'},
            'latex': r'$W$',
            'default': 1.0,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'heater geometry',
        },
        'D': {
            'explanation': {'EN': 'Heater Diameter', 'KR': '히터 직경'},
            'latex': r'$D$',
            'default': 0.005,
            'range': [0.001, 0.02],
            'unit': 'm',
            'step': 0.001,
            'category': 'heater geometry',
        },
    }
}

# 시스템 등록
register_system('HEATING', 'Air source heat pump', HEATING_ASHP)
register_system('HEATING', 'Ground source heat pump', HEATING_GSHP)
register_system('HEATING', 'Electric heater', ELECTRIC_HEATER)

# HEATING 모드 시각화 함수들
@viz_registry.register('HEATING', 'Exergy efficiency')
def plot_exergy_efficiency(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 효율 차트 생성"""
    # HEATING 모드 전용 시각화
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
        color=alt.Color('system:N', sort=None, legend=None),
        # tooltip=['system', 'efficiency'],
    ).properties(
        width='container',
        height=len(selected_systems) * 60 + 50,
    )
        # tooltip=['system', 'efficiency'],
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

@viz_registry.register('HEATING', 'Exergy consumption crocess')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    # HEATING 모드 전용 시각화
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        sys_type = session_state.systems[key]['type']
        
        if sys_type == 'Air source heat pump':
            items = [
                {'label': 'Input', 'amount': sv['E_fan_ext'], 'desc': 'Exergy input from fan (external unit)'},
                {'label': 'X_r_ext(internal)', 'amount': sv['X_r_ext'], 'desc': 'Cool exergy input from refrigerant (internal unit side)'},
                {'label': 'X_c_ext', 'amount': -sv['Xc_ext'], 'desc': 'Exergy consumption (external unit)'},
                {'label': 'X_a_ext_out', 'amount': -sv['X_a_ext_out'], 'desc': 'Exergy output (external unit outlet air)'},
                {'label': 'E_cmp', 'amount': sv['E_cmp'], 'desc': 'Compressor power input (refrigerant)'},
                {'label': 'X_c_r', 'amount': -sv['Xc_r'], 'desc': 'Exergy consumption (refrigerant)'},
                {'label': 'X_r_ext(ref)', 'amount': -sv['X_r_ext'], 'desc': 'Cool exergy input from refrigerant (external unit side)'},
                {'label': 'X_c_int', 'amount': -sv['Xc_int'], 'desc': 'Exergy consumption (internal unit)'},
                {'label': 'Output', 'amount': 0, 'desc': 'Exergy output'},
            ]

        if sys_type == 'Ground source heat pump':
            items = [
                {'label': 'Xin_g', 'amount': sv['Xin_g'], 'desc': 'Exergy from undisturbed ground'},
                {'label': 'Xc_g', 'amount': -sv['Xc_g'], 'desc': 'Consumption in ground'},
                {'label': 'E_pmp', 'amount': sv['E_pmp'], 'desc': 'Electric input to pump'},
                {'label': 'Xc_GHE', 'amount': -sv['Xc_GHE'], 'desc': 'Consumption in ground heat exchanger'},
                {'label': 'Xc_exch', 'amount': -sv['Xc_exch'], 'desc': 'Consumption in heat exchanger'},
                {'label': 'E_cmp', 'amount': sv['E_cmp'], 'desc': 'Electric input to compressor'},
                {'label': 'Xc_r', 'amount': -sv['Xc_r'], 'desc': 'Consumption in refrigerant loop'},
                {'label': 'E_fan_int', 'amount': sv['E_fan_int'], 'desc': 'Electric input to fan'},
                {'label': 'X_a_int_in', 'amount': sv['X_a_int_in'], 'desc': 'Exergy from room air'},
                {'label': 'Xc_int', 'amount': -sv['Xc_int'], 'desc': 'Consumption in internal unit'},
                {'label': 'Xout_int', 'amount': 0, 'desc': 'Supply air to room'},
            ]

        if sys_type == 'Electric heater':
           items = [
                {'label': 'X_heater', 'amount': sv['X_heater'], 'desc': 'Exergy input'},
                {'label': 'X_c_hb', 'amount': -sv['X_c_hb'], 'desc': 'Exergy consumption (heater body)'},
                {'label': 'X_c_hs', 'amount': -sv['X_c_hs'], 'desc': 'Exergy consumption (heater surface)'},
                {'label': 'Output', 'amount': 0, 'desc': 'Exergy output (heat transfer)'},
            ]
            
        for item in items:
            item['group'] = key
        source = pd.DataFrame(items)
        sources.append(source)

    if sources:
        source = pd.concat(sources)
        return plot_waterfall_multi(source)
    return alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_point() 


@eval_registry.register('HEATING', 'Air source heat pump')
def evaluate_heating_ashp(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    ASHP_H = enex.AirSourceHeatPump_heating()
    ASHP_H.T0 = params['T_0']
    ASHP_H.T_a_room = params['T_a_room']
    ASHP_H.T_r_int = params['T_r_int']
    ASHP_H.T_a_int_out = params['T_a_int_out']
    ASHP_H.T_a_ext_out = params['T_a_ext_out']
    ASHP_H.T_r_ext = params['T_r_ext']
    ASHP_H.Q_r_int = params['Q_r_int']
    ASHP_H.Q_r_max = params['Q_r_max']
    ASHP_H.system_update()
    
    # fan power
    E_fan_int = ASHP_H.E_fan_int
    E_cmp     = ASHP_H.E_cmp
    E_fan_ext = ASHP_H.E_fan_ext

    X_a_int_in  = ASHP_H.X_a_int_in
    X_a_int_out = ASHP_H.X_a_int_out
    X_a_ext_in  = ASHP_H.X_a_ext_in
    X_a_ext_out = ASHP_H.X_a_ext_out

    X_r_int   = ASHP_H.X_r_int
    X_r_ext   = ASHP_H.X_r_ext

    Xin_int  = ASHP_H.Xin_int
    Xout_int = ASHP_H.Xout_int
    Xc_int   = ASHP_H.Xc_int

    Xin_r  = ASHP_H.Xin_r
    Xout_r = ASHP_H.Xout_r
    Xc_r   = ASHP_H.Xc_r

    Xin_ext  = ASHP_H.Xin_ext
    Xout_ext = ASHP_H.Xout_ext
    Xc_ext   = ASHP_H.Xc_ext

    Xin  = ASHP_H.Xin
    Xout = ASHP_H.Xout
    Xc   = ASHP_H.Xc

    X_eff = ASHP_H.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}

@eval_registry.register('HEATING', 'Ground source heat pump')
def evaluate_heating_gshp(params: Dict[str, float]) -> Dict[str, float]:
    """GSHP 냉방 모드 평가 함수"""
    GSHP_H = enex.GroundSourceHeatPump_heating()
    GSHP_H.T0 = params['T_0']
    GSHP_H.T_g = params['T_g']
    GSHP_H.T_a_room = params['T_a_room']
    GSHP_H.T_a_int_out = params['T_a_int_out']
    GSHP_H.T_r_int = params['T_r_int']
    GSHP_H.T_r_exch = params['T_r_exch']

    GSHP_H.depth = params['D']
    GSHP_H.height = params['H']
    GSHP_H.r_b = params['r_b']
    GSHP_H.R_b = params['R_b']
    m3s_to_Lmin = 1 / 60000 # 1 m³/s = 60000 L/min
    GSHP_H.V_f = params['V_f'] * m3s_to_Lmin # Convert L/min to m³/s
    
    GSHP_H.k_g = params['k_g']
    GSHP_H.c_g = params['c_g']
    GSHP_H.rho_g = params['rho_g']

    GSHP_H.E_pmp = params['E_pmp']
   
    GSHP_H.Q_r_int = params['Q_r_int']
    GSHP_H.system_update()

    # Ground
    Xin_g = GSHP_H.Xin_g
    Xout_g = GSHP_H.X_b
    Xc_g = GSHP_H.Xc_g

    # Ground heat exchanger
    E_pmp = GSHP_H.E_pmp
    Xin_GHE = GSHP_H.Xin_GHE
    Xout_GHE = GSHP_H.Xout_GHE
    Xc_GHE = GSHP_H.Xc_GHE

    # Heat exchanger
    Xin_exch = GSHP_H.Xin_exch
    Xout_exch = GSHP_H.Xout_exch
    Xc_exch = GSHP_H.Xc_exch

    # Closed refrigerant loop system
    E_cmp = GSHP_H.E_cmp
    Xin_r = GSHP_H.Xin_r
    Xout_r = GSHP_H.Xout_r
    Xc_r = GSHP_H.Xc_r

    # Internal unit
    X_a_int_in = GSHP_H.X_a_int_in
    E_fan_int = GSHP_H.E_fan_int
    Xin_int = GSHP_H.Xin_int
    Xout_int = GSHP_H.Xout_int
    Xc_int = GSHP_H.Xc_int

    # Exergy efficiency
    X_eff = GSHP_H.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}

@eval_registry.register('HEATING', 'Electric heater')
def evaluate_heating_EH(params: Dict[str, float]) -> Dict[str, float]:
    """GSHP 냉방 모드 평가 함수"""
    EH = enex.ElectricHeater()
    EH.T0 = params['T_0']
    EH.T_mr = params['T_mr']
    EH.T_a_room = params['T_a_room']
    
    EH.c_heater = params['c_heater']
    EH.rho_heater = params['rho_heater']
    EH.k_heater = params['k_heater']
    
    EH.D = params['D']
    EH.H = params['H']
    EH.W = params['W']
    EH.system_update()

    # Exergy input and output
    X_heater = EH.X_heater
    X_c_hb = EH.X_c_hb
    X_cond = EH.X_cond
    X_rad_rs = EH.X_rad_rs
    X_c_hs = EH.X_c_hs
    X_conv = EH.X_conv
    X_rad_hs = EH.X_rad_hs

    # Exergy efficiency
    X_eff = EH.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}