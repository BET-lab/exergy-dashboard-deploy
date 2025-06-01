import math
from typing import Any, List, Dict
import pandas as pd
import altair as alt
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
from exergy_dashboard.chart import plot_waterfall_multi
import en_system_ex_analysis as enex

c_a	 = 1.005
rho_a =	1.2
c_w = 4.186
rho_w = 1000.0

# 기본 시스템 정의
ELECTRIC_BOILER = {
    'display': {
        'title': 'ELECTRIC BOILER',
        'icon': ':droplet:',
    },
    'parameters': {
        'T_w_tank': {
            'explanation': {'EN': 'Tank Water Temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply Water Temperature', 'KR': '공급수 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_w_tap': {
            'explanation': {'EN': 'Tap Water Temperature', 'KR': '수도꼭지 온수 온도'},
            'latex': r'$T_{w,tap}$',
            'default': 45.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_0': {
            'explanation': {'EN': 'Reference Temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'envrionment',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank Water Use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 0.0002,
            'range': [0, 0.01],
            'unit': 'm³/s',
            'step': 0.0001,
            'category': 'flow',
        },
        'r0': {
            'explanation': {'EN': 'Tank Radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'H': {
            'explanation': {'EN': 'Tank Height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank Shell Thickness', 'KR': '탱크 외벽 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.001, 0.05],
            'unit': 'm',
            'step': 0.001,
            'category': 'dimension',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank Insulation Thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell Thermal Conductivity', 'KR': '외벽 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [0.1, 100],
            'unit': 'W/mK',
            'step': 0.1,
            'category': 'property',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation Thermal Conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.001, 0.1],
            'unit': 'W/mK',
            'step': 0.001,
            'category': 'property',
        },
        'h_o': {
            'explanation': {'EN': 'Overall Heat Transfer Coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²K',
            'step': 1.0,
            'category': 'envrionment',
        },
    }
}

GAS_BOILER = {
    'display': {
        'title': 'GAS BOILER',
        'icon': ':droplet:',
    },
    'parameters': {
        'eta_comb': {
            'explanation': {'EN': 'Combustion Efficiency', 'KR': '연소 효율'},
            'latex': r'$\eta_{comb}$',
            'default': 0.9,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'efficiency',
        },
        'eta_NG': {
            'explanation': {'EN': 'Natural Gas Efficiency', 'KR': '천연가스 엑서지 효율'},
            'latex': r'$\eta_{NG}$',
            'default': 0.93,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'efficiency',
        },
        'T_w_tank': {
            'explanation': {'EN': 'Tank Water Temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply Water Temperature', 'KR': '공급수 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_w_tap': {
            'explanation': {'EN': 'Tap Water Temperature', 'KR': '수도꼭지 온수 온도'},
            'latex': r'$T_{w,tap}$',
            'default': 45.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_0': {
            'explanation': {'EN': 'Reference Temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'environment',
        },
        'T_exh': {
            'explanation': {'EN': 'Exhaust Gas Temperature', 'KR': '배기가스 온도'},
            'latex': r'$T_{exh}$',
            'default': 70.0,
            'range': [0, 500],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_NG': {
            'explanation': {'EN': 'Natural Gas Flame Temperature', 'KR': '천연가스 화염 온도'},
            'latex': r'$T_{NG}$',
            'default': 1400.0,
            'range': [500, 2000],
            'unit': '℃',
            'step': 10,
            'category': 'temperature',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank Water Use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 0.0002,
            'range': [0, 0.01],
            'unit': 'm³/s',
            'step': 0.0001,
            'category': 'flow',
        },
        'r0': {
            'explanation': {'EN': 'Tank Radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'H': {
            'explanation': {'EN': 'Tank Height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank Shell Thickness', 'KR': '탱크 외벽 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.001, 0.05],
            'unit': 'm',
            'step': 0.001,
            'category': 'dimension',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank Insulation Thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell Thermal Conductivity', 'KR': '외벽 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [0.1, 100],
            'unit': 'W/mK',
            'step': 0.1,
            'category': 'property',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation Thermal Conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.001, 0.1],
            'unit': 'W/mK',
            'step': 0.001,
            'category': 'property',
        },
        'h_o': {
            'explanation': {'EN': 'Overall Heat Transfer Coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²K',
            'step': 1.0,
            'category': 'environment',
        },
    }
}

COOLING_GSHP = {
    'display': {
        'title': 'Ground Source Heat Pump',
        'icon': ':earth_americas:',
    },
    'parameters':{
        'T_0': {
            'explanation': {'EN': 'Environment Temperature', 'KR': '환경온도'},
            'latex': r'$T_0$',
            'default': 32.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 0.5,
            'category': 'environment',
        },
        'T_g': {
            'explanation': {'EN': 'Ground Temperature', 'KR': '토양온도'},
            'latex': r'$T_g$',
            'default': 19.0,
            'range': [-30, 'T_0-0.5'],
            'unit': '℃',
            'step': 0.5,
            'category': 'environment',
        },
        'T_a_int_in': {
            'explanation': {'EN': 'Internal Unit Inlet Air Temperature', 'KR': '실내기로 들어가는 공기 온도'},
            'latex': r'$T_{a,int,in}$',
            'default': 24.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 0.5,
            'category': 'air',
        },
        'T_a_int_out': {
            'explanation': {'EN': 'Internal Unit Outlet Air Temperature', 'KR': '실내기에서 나가는 공기 온도'},
            'latex': r'$T_{a,int,out}$',
            'default': 14.0,
            'range': [-60, 'T_a_int_in-0.5'],
            'unit': '℃',
            'step': 0.5,
            'category': 'air',
        },
        'T_r_int_G': {
            'explanation': {'EN': 'Internal Unit Refrigerant Temperature', 'KR': '실내기 측 냉매 온도'},
            'latex': r'$T_{r,int,G}$',
            'default': 9.0,
            'range': [-80, 'T_a_int_out-0.5'],
            'unit': '℃',
            'step': 0.5,
            'category': 'refrigerant',
        },
        'T_r_ext_G': {
            'explanation': {'EN': 'External Unit Refrigerant Temperature', 'KR': '실외기 측 냉매 온도'},
            'latex': r'$T_{r,ext,G}$',
            'default': 29.0,
            'range': ['T_g+0.5', 'T_0-0.5'],
            'unit': '℃',
            'step': 0.5,
            'category': 'refrigerant',
        },
        'k': {
            'explanation': {'EN': 'COP Correction Factor', 'KR': 'COP 보정 계수'},
            'latex': r'$k$',
            'default': 0.4,
            'range': [0, 1],
            'unit': '-',
            'step': 0.01,
            'category': 'performance',
        },
        'E_f_int': {
            'explanation': {'EN': 'Internal Unit Fan Power', 'KR': '실내기 측 팬 전력'},
            'latex': r'$E_{f,int}$',
            'default': 0.21,
            'range': [0, 1],
            'unit': 'kW',
            'step': 0.01,
            'category': 'power',
        },
        'E_pmp_G': {
            'explanation': {'EN': 'Ground Heat Exchanger Pump Power', 'KR': '지열 순환 펌프 전력'},
            'latex': r'$E_{pmp,G}$',
            'default': 0.48,
            'range': [0, 1],
            'unit': 'kW',
            'step': 0.01,
            'category': 'power',
        },
        'Q_r_int_G': {
            'explanation': {'EN': 'Internal Unit Heat Absorption', 'KR': '실내기 실내 흡열량'},
            'latex': r'$Q_{r,int,G}$',
            'default': 15.3,
            'range': [0, 30],
            'unit': 'kW',
            'step': 0.1,
            'category': 'capacity',
        },
    }
}

# 시스템 등록
register_system('HOT WATER', 'ELECTRIC BOILER', ELECTRIC_BOILER)
register_system('HOT WATER', 'GAS BOILER', GAS_BOILER)
# register_system('COOLING', 'GSHP', COOLING_GSHP)


# HOT WATER 모드 시각화 함수들
@viz_registry.register('HOT WATER', 'Exergy Efficiency')
def plot_exergy_efficiency(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 효율 차트 생성"""
    # HOT WATER 모드 전용 시각화
    efficiencies = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        if session_state.systems[key]['type'] == 'ELECTRIC BOILER':
            eff = sv['X_eff'] * 100
            efficiencies.append(eff)
        if session_state.systems[key]['type'] == 'GAS BOILER':
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


# @viz_registry.register('COOLING', 'Exergy Consumption Process')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    # COOLING 모드 전용 시각화
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        if session_state.systems[key]['type'] == 'ELECTRIC BOILER':
            labels = [
                r'X_{w,sup,tank}',
                r'X_{heater}',
                r'-X_{c,tank}',
                r'-X_{l,tank}',
                r'X_{w,sup,mix}',
                r'-X_{c,mix}',
                r'X_{w,serv}',
            ]
            amounts = [
                sv['X_w_sup_tank'],
                sv['X_heater'],
                -sv['X_c_tank'],
                -sv['X_l_tank'],
                sv['X_w_sup_mix'],
                -sv['X_c_mix'],
                sv['X_w_serv'],
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)
            
        if session_state.systems[key]['type'] == 'GAS BOILER':
            labels = [
                'Input',
                r'$X_{w,sup}$',
                r'$X_{NG}$',
                r'$-X_{c,comb}$',
                r'$-X_{exh}$',
                r'$-X_{c,tank}$',
                r'$-X_{l,tank}$',
                r'$X_{w,sup,mix}$',
                r'$-X_{c,mix}$',
                r'$X_{w,serv}$',
            ]
            amounts = [
                sv['X_w_sup'],
                sv['X_NG'],
                -sv['X_c_comb'],
                -sv['X_exh'],
                -sv['X_c_tank'],
                -sv['X_l_tank'],
                sv['X_w_sup_mix'],
                -sv['X_c_mix'],
                sv['X_w_serv'],
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)

    if sources:
        source = pd.concat(sources)
        return plot_waterfall_multi(source, 'Input', 'Output')
    return alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_point() 



@eval_registry.register('HOT WATER', 'ELECTRIC BOILER')
def evaluate_electric_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    EB = enex.ElectricBoiler()
    EB.T0 = params['T_0']
    EB.T_w_tank = params['T_w_tank']
    EB.T_w_sup = params['T_w_sup']
    EB.T_w_tap = params['T_w_tap']
    EB.dV_w_serv = params['dV_w_serv']
    EB.r0 = params['r0']
    EB.H = params['H']
    EB.x_shell = params['x_shell']
    EB.x_ins = params['x_ins']
    EB.k_shell = params['k_shell']
    EB.k_ins = params['k_ins']
    EB.h_o = params['h_o']
    EB.system_update()

    # Heat Transfer Rates
    X_heater = EB.X_heater
    X_w_sup_tank = EB.X_w_sup_tank
    X_w_tank = EB.X_w_tank
    X_l_tank = EB.X_l_tank
    X_c_tank = EB.X_c_tank

    X_w_sup_mix = EB.X_w_sup_mix
    X_w_serv = EB.X_w_serv
    X_c_mix = EB.X_c_mix

    X_c_tot = EB.X_c_tot
    X_eff = EB.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}

@eval_registry.register('HOT WATER', 'GAS BOILER')
def evaluate_gas_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    GB = enex.GasBoiler()
    GB.T0 = params['T_0']
    GB.T_w_tank = params['T_w_tank']
    GB.T_w_sup = params['T_w_sup']
    GB.T_w_tap = params['T_w_tap']
    GB.dV_w_serv = params['dV_w_serv']
    GB.r0 = params['r0']
    GB.H = params['H']
    GB.x_shell = params['x_shell']
    GB.x_ins = params['x_ins']
    GB.k_shell = params['k_shell']
    GB.k_ins = params['k_ins']
    GB.h_o = params['h_o']
    GB.system_update()

    # Heat Transfer Rates
    X_NG = GB.X_NG
    X_w_sup = GB.X_w_sup
    X_w_comb_out = GB.X_w_comb_out
    X_exh = GB.X_exh
    X_c_comb = GB.X_c_comb

    X_w_tank = GB.X_w_tank
    X_l_tank = GB.X_l_tank
    X_c_tank = GB.X_c_tank

    X_w_sup_mix = GB.X_w_sup_mix
    X_w_serv = GB.X_w_serv
    X_c_mix = GB.X_c_mix

    # total
    X_c_tot = GB.X_c_tot
    X_eff = GB.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}


@eval_registry.register('COOLING', 'GSHP')
def evaluate_cooling_gshp(params: Dict[str, float]) -> Dict[str, float]:
    """GSHP 냉방 모드 평가 함수"""
    T_0 = params['T_0']
    T_r_int_G = params['T_r_int_G']
    T_r_ext_G = params['T_r_ext_G']
    Q_r_int_G = params['Q_r_int_G']
    E_pmp_G = params['E_pmp_G'] 
    T_g = params['T_g']
    k = params['k']
    T_a_int_in = params['T_a_int_in']
    T_a_int_out = params['T_a_int_out']
    E_f_int = params['E_f_int']

    # Outdoor air
    T_ext_in = T_0

    # System COP
    cop_G = k * T_r_int_G / (T_r_ext_G - T_r_int_G)

    # System capacity - GSHP
    E_cmp_G = Q_r_int_G / cop_G    # kW, 압축기 전력
    Q_r_ext_G = Q_r_int_G + E_cmp_G    # kW, 실외기 배출열량
    Q_g = Q_r_ext_G + E_pmp_G    # kW, 토양 열교환량

    # Air & Cooling water parameters
    V_int = Q_r_int_G / (c_a * rho_a * (T_a_int_in - T_a_int_out))
    m_int = V_int * rho_a

    ## Internal unit with evaporator
    X_r_int_G = - Q_r_int_G * (1 - T_0 / T_r_int_G) # 냉매에서 실내 공기에 전달한 엑서지
    X_a_int_out_G = c_a * m_int * ((T_a_int_out - T_0) - T_0 * math.log(T_a_int_out / T_0)) # 실외기 취출 공기 엑서지
    X_a_int_in_G = c_a * m_int * ((T_a_int_in - T_0) - T_0 * math.log(T_a_int_in / T_0)) # 실외기 흡기 공기 엑서지

    Xin_int_G = E_f_int + X_r_int_G # 엑서지 인풋 (팬 투입 전력 + 냉매에서 실내 공기에 전달한 엑서지)
    Xout_int_G = X_a_int_out_G - X_a_int_in_G # 엑서지 아웃풋
    Xc_int_G = Xin_int_G - Xout_int_G # 엑서지 소비율

    ## Closed refrigerant loop system
    X_r_ext_G = - Q_r_ext_G * (1 - T_0 / T_r_ext_G) # 냉매에서 실외기측에 전달한 엑서지
    X_r_int_G = - Q_r_int_G * (1 - T_0 / T_r_int_G) # 냉매에서 실내 공기에 전달한 엑서지

    Xin_r_G = E_cmp_G + X_r_ext_G # 엑서지 인풋 (컴프레서 투입 전력 + 냉매에서 실외기측에 전달한 엑서지)
    Xout_r_G = X_r_int_G # 엑서지 아웃풋
    Xc_r_G = Xin_r_G - Xout_r_G # 엑서지 소비율

    ## Circulating water in GHE
    X_g = - Q_g * (1 - T_0 / T_g) # 땅에서 추출한 엑서지
    X_r_ext_G = - Q_r_ext_G * (1 - T_0 / T_r_ext_G) # 냉매에서 실내 공기에 전달한 엑서지

    Xin_ext_G = E_pmp_G + X_g # 엑서지 인풋 (펌프 투입 전력 + 땅에서 추출한 엑서지)
    Xout_ext_G = X_r_ext_G # 엑서지 아웃풋
    Xc_GHE = Xin_ext_G - Xout_ext_G # 엑서지 소비율

    ## Total
    Xin_G = E_cmp_G + E_f_int + E_pmp_G + X_g # 총 엑서지 인풋 (컴프레서 + 실내팬 + 펌프 전력 + 땅에서 추출한 엑서지)
    Xout_G = X_a_int_out_G - X_a_int_in_G # 총 엑서지 아웃풋
    Xc_G = Xin_G - Xout_G # 총 엑서지 소비율

    return {k: v for k, v in locals().items() if k not in ('params')}

