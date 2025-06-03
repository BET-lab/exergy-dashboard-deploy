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
            'latex': r'T_{w,tank}',
            'default': 60.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply Water Temperature', 'KR': '공급수 온도'},
            'latex': r'T_{w,sup}',
            'default': 10.0,
            'range': [0, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_w_tap': {
            'explanation': {'EN': 'Tap Water Temperature', 'KR': '수도꼭지 온수 온도'},
            'latex': r'T_{w,tap}',
            'default': 45.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_0': {
            'explanation': {'EN': 'Reference Temperature', 'KR': '기준 온도'},
            'latex': r'T_0',
            'default': 0.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'Environment',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank Water Use', 'KR': '탱크 온수 사용량'},
            'latex': r'\dot{V}_{w,serv}',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'flow',
        },
        'r0': {
            'explanation': {'EN': 'Tank Radius', 'KR': '탱크 반지름'},
            'latex': r'r_0',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'H': {
            'explanation': {'EN': 'Tank Height', 'KR': '탱크 높이'},
            'latex': r'H',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank Shell Thickness', 'KR': '탱크 외벽 두께'},
            'latex': r'x_{shell}',
            'default': 0.01,
            'range': [0.001, 0.05],
            'unit': 'm',
            'step': 0.001,
            'category': 'dimension',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank Insulation Thickness', 'KR': '탱크 단열 두께'},
            'latex': r'x_{ins}',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell Thermal Conductivity', 'KR': '외벽 열전도율'},
            'latex': r'k_{shell}',
            'default': 50.0,
            'range': [0.1, 100],
            'unit': 'W/mK',
            'step': 0.1,
            'category': 'property',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation Thermal Conductivity', 'KR': '단열재 열전도율'},
            'latex': r'k_{ins}',
            'default': 0.03,
            'range': [0.001, 0.1],
            'unit': 'W/mK',
            'step': 0.001,
            'category': 'property',
        },
        'h_o': {
            'explanation': {'EN': 'Overall Heat Transfer Coefficient', 'KR': '종합 열전달계수'},
            'latex': r'h_o',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²K',
            'step': 1.0,
            'category': 'Environment',
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
            'step': 10.0,
            'category': 'temperature',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank Water Use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
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
            'latex': r'$k_{shell}',
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

HEAT_PUMP_BOILER = {
    'display': {
        'title': 'HEAT PUMP BOILER',
        'icon': ':droplet:',
    },
    'parameters': {
        'eta_fan': {
            'explanation': {'EN': 'Fan Efficiency', 'KR': '팬 효율'},
            'latex': r'$\eta_{fan}$',
            'default': 0.6,
            'range': [0.3, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'efficiency',
        },
        'COP_hp': {
            'explanation': {'EN': 'Heat Pump COP', 'KR': '히트펌프 COP'},
            'latex': r'$\mathrm{COP}_{hp}$',
            'default': 2.5,
            'range': [1.0, 6.0],
            'unit': '-',
            'step': 0.01,
            'category': 'efficiency',
        },
        'r_ext': {
            'explanation': {'EN': 'Fan Radius', 'KR': '실외기 반지름'},
            'latex': r'$r_{ext}$',
            'default': 0.2,
            'range': [0.05, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
        'dP': {
            'explanation': {'EN': 'Pressure Difference', 'KR': '압력차'},
            'latex': r'$\Delta P$',
            'default': 200,
            'range': [50, 1000],
            'unit': 'Pa',
            'step': 10,
            'category': 'property',
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
        'T_a_ext_out': {
            'explanation': {'EN': 'Outdoor Air Outlet Temp', 'KR': '외기 출구 온도'},
            'latex': r'$T_{a,ext,out}$',
            'default': -5.0,
            'range': [-30, 40],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_r_ext': {
            'explanation': {'EN': 'Outdoor Refrigerant Temp', 'KR': '외부 냉매 온도'},
            'latex': r'$T_{r,ext}$',
            'default': -10.0,
            'range': [-30, 40],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_r_tank': {
            'explanation': {'EN': 'Tank Refrigerant Temp', 'KR': '탱크 냉매 온도'},
            'latex': r'$T_{r,tank}$',
            'default': 65.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
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
        'T_w_tap': {
            'explanation': {'EN': 'Tap Water Temperature', 'KR': '수도꼭지 온수 온도'},
            'latex': r'$T_{w,tap}$',
            'default': 45.0,
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
        'dV_w_serv': {
            'explanation': {'EN': 'Tank Water Use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
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

SOLAR_HOT_WATER = {
    'display': {
        'title': 'SOLAR HOT WATER',
        'icon': ':sun:',
    },
    'parameters': {
        'alpha': {
            'explanation': {'EN': 'Absorptivity of Collector', 'KR': '집열기 흡수율'},
            'latex': r'$\alpha$',
            'default': 0.95,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'property',
        },
        'eta_comb': {
            'explanation': {'EN': 'Combustion Chamber Efficiency', 'KR': '연소실 효율'},
            'latex': r'$\eta_{comb}$',
            'default': 0.9,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'efficiency',
        },
        'eta_NG': {
            'explanation': {'EN': 'Natural Gas Efficiency', 'KR': '천연가스 효율'},
            'latex': r'$\eta_{NG}$',
            'default': 0.93,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'efficiency',
        },
        'I_DN': {
            'explanation': {'EN': 'Direct Normal Irradiance', 'KR': '직달일사량'},
            'latex': r'$I_{DN}$',
            'default': 800,
            'range': [0, 1200],
            'unit': 'W/m²',
            'step': 10,
            'category': 'solar',
        },
        'I_dH': {
            'explanation': {'EN': 'Diffuse Horizontal Irradiance', 'KR': '확산수평일사량'},
            'latex': r'$I_{dH}$',
            'default': 200,
            'range': [0, 500],
            'unit': 'W/m²',
            'step': 10,
            'category': 'solar',
        },
        'A_stp': {
            'explanation': {'EN': 'Solar Thermal Panel Area', 'KR': '태양열 패널 면적'},
            'latex': r'$A_{stp}$',
            'default': 2.0,
            'range': [0.5, 10.0],
            'unit': 'm²',
            'step': 0.1,
            'category': 'dimension',
        },
        'T_0': {
            'explanation': {'EN': 'Reference Temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
        },
        'T_w_comb': {
            'explanation': {'EN': 'Tank Water Temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,comb}$',
            'default': 60.0,
            'range': [0, 100],
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
        'T_w_sup': {
            'explanation': {'EN': 'Supply Water Temperature', 'KR': '공급수 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0, 50],
            'unit': '℃',
            'step': 1.0,
            'category': 'temperature',
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
        'dV_w_serv': {
            'explanation': {'EN': 'Tank Water Use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'flow',
        },
        'h_o': {
            'explanation': {'EN': 'Overall Heat Transfer Coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²K',
            'step': 1.0,
            'category': 'property',
        },
        'h_r': {
            'explanation': {'EN': 'Radiative Heat Transfer Coefficient', 'KR': '복사 열전달계수'},
            'latex': r'$h_r$',
            'default': 2.0,
            'range': [0.5, 10.0],
            'unit': 'W/m²K',
            'step': 0.1,
            'category': 'property',
        },
        'k_air': {
            'explanation': {'EN': 'Air Thermal Conductivity', 'KR': '공기 열전도율'},
            'latex': r'$k_{air}$',
            'default': 0.025,
            'range': [0.01, 0.05],
            'unit': 'W/mK',
            'step': 0.001,
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
        'x_air': {
            'explanation': {'EN': 'Air Layer Thickness', 'KR': '공기층 두께'},
            'latex': r'$x_{air}$',
            'default': 0.01,
            'range': [0.001, 0.05],
            'unit': 'm',
            'step': 0.001,
            'category': 'dimension',
        },
        'x_ins': {
            'explanation': {'EN': 'Insulation Thickness', 'KR': '단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.05,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'dimension',
        },
    }
}

# 시스템 등록
register_system('HOT WATER', 'ELECTRIC BOILER', ELECTRIC_BOILER)
register_system('HOT WATER', 'GAS BOILER', GAS_BOILER)
register_system('HOT WATER', 'HEAT PUMP BOILER', HEAT_PUMP_BOILER)
register_system('HOT WATER', 'SOLAR HOT WATER', SOLAR_HOT_WATER)

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
        if session_state.systems[key]['type'] == 'HEAT PUMP BOILER':
            eff = sv['X_eff'] * 100
            efficiencies.append(eff)
        if session_state.systems[key]['type'] == 'SOLAR HOT WATER':
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


@viz_registry.register('HOT WATER', 'Exergy Consumption Process')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    # COOLING 모드 전용 시각화
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        if session_state.systems[key]['type'] == 'ELECTRIC BOILER':
            labels = [
                # 'X_{w,sup,tank}',
                # 'X_{heater}',
                # 'X_{c,tank}',
                # 'X_{l,tank}',
                # 'X_{w,sup,mix}',
                # 'X_{c,mix}',
                # 'X_{w,serv}',
                'X1',
                'X2',
                'X3',
                'X4',
                'X5',
                'X6',
                'X7',
            ]
            amounts = [
                sv['X_w_sup_tank'],
                sv['X_heater'],
                -sv['X_c_tank'],
                -sv['X_l_tank'],
                sv['X_w_sup_mix'],
                -sv['X_c_mix'],
                0
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)
            
        if session_state.systems[key]['type'] == 'GAS BOILER':
            labels = [
                'X_{w,sup}',
                'X_{NG}',
                'X_{c,comb}',
                'X_{exh}',
                'X_{c,tank}',
                'X_{l,tank}',
                'X_{w,sup,mix}',
                'X_{c,mix}',
                'X_{w,serv}',
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

        if session_state.systems[key]['type'] == 'HEAT PUMP BOILER':
            labels = [
                'Input',
                r'$X_{fan}$',
                r'$X_{r,ext}$',
                r'$X_{a,ext,in}$',
                r'$X_{c,ext}$',
                r'$X_{a,ext,out}$',
                r'$X_{cmp}$',
                r'$X_{c,r}$',
                r'$X_{r,ext}$',
                r'$X_{l,tank}$',
                r'$X_{c,tank}$',
                r'$X_{w,sup,tank}$',
                r'$X_{w,serv}$',
            ]
            amounts = [
                0,  # Input placeholder, can be set to 0 or sum of inputs if needed
                sv['X_fan'],
                sv['X_r_ext'],
                sv['X_a_ext_in'],
                -sv['X_c_ext'],
                -sv['X_a_ext_out'],
                sv['X_cmp'],
                -sv['X_c_r'],
                -sv['X_r_ext'],
                -sv['X_l_tank'],
                -sv['X_c_tank'],
                sv['X_w_sup_tank'],
                sv['X_w_serv'],
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)
        
        if session_state.systems[key]['type'] == 'SOLAR HOT WATER':
            labels = [
                'X_{w,sup}',
                'X_{sol}',
                'X_{c,stp}',
                'X_{l}',
                'X_{NG}',
                'X_{c,comb}',
                'X_{exh}',
                'X_{w,sup,mix}',
                'X_{c,mix}',
                'X_{w,serv}',
            ]
            amounts = [
                sv['X_w_sup'],
                sv['X_sol'],
                -sv['X_c_stp'],
                -sv['X_l'],
                sv['X_NG'],
                -sv['X_c_comb'],
                -sv['X_exh'],
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
        return plot_waterfall_multi(source)
    return alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_point()


@eval_registry.register('HOT WATER', 'ELECTRIC BOILER')
def evaluate_electric_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    EB = enex.ElectricBoiler()
    EB.T0 = params['T_0']
    EB.T_w_tank = params['T_w_tank']
    EB.T_w_sup = params['T_w_sup']
    EB.T_w_tap = params['T_w_tap']
    EB.dV_w_serv = params['dV_w_serv']*enex.L2m3/enex.m2s
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
    GB.T_exh = params['T_exh']
    GB.T_NG = params['T_NG']
    GB.dV_w_serv = params['dV_w_serv']*enex.L2m3/enex.m2s
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

@eval_registry.register('HOT WATER', 'HEAT PUMP BOILER')
def evaluate_heat_pump_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    HPB = enex.HeatPumpBoiler()
    HPB.eta_fan = params['eta_fan']
    HPB.COP_hp = params['COP_hp']
    HPB.r_ext = params['r_ext']
    HPB.dP = params['dP']
    HPB.T0 = params['T_0']
    HPB.T_a_ext_out = params['T_a_ext_out']
    HPB.T_r_ext = params['T_r_ext']
    HPB.T_r_tank = params['T_r_tank']
    HPB.T_w_tank = params['T_w_tank']
    HPB.T_w_tap = params['T_w_tap']
    HPB.T_w_sup = params['T_w_sup']
    HPB.dV_w_serv = params['dV_w_serv']*enex.L2m3/enex.m2s
    HPB.r0 = params['r0']
    HPB.H = params['H']
    HPB.x_shell = params['x_shell']
    HPB.x_ins = params['x_ins']
    HPB.k_shell = params['k_shell']
    HPB.k_ins = params['k_ins']
    HPB.h_o = params['h_o']
    HPB.system_update()

    # Heat Transfer Rates
    X_fan = HPB.X_fan
    X_cmp = HPB.X_cmp
    X_r_ext = HPB.X_r_ext
    X_r_tank = HPB.X_r_tank
    X_w_sup_tank = HPB.X_w_sup_tank
    X_w_tank = HPB.X_w_tank
    X_l_tank = HPB.X_l_tank
    X_w_sup_mix = HPB.X_w_sup_mix
    X_w_serv = HPB.X_w_serv
    X_a_ext_in = HPB.X_a_ext_in
    X_a_ext_out = HPB.X_a_ext_out

    X_c_ext = HPB.X_c_ext
    X_c_r = HPB.X_c_r
    X_c_tank = HPB.X_c_tank
    X_c_mix = HPB.X_c_mix

    # total
    X_c_tot = HPB.X_c_tot
    X_eff = HPB.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}

@eval_registry.register('HOT WATER', 'SOLAR HOT WATER')
def evaluate_solar_hot_water(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    SHW = enex.SolarHotWater()
    SHW.alpha = params['alpha']
    SHW.eta_comb = params['eta_comb']
    SHW.eta_NG = params['eta_NG']
    SHW.I_DN = params['I_DN']
    SHW.I_dH = params['I_dH']
    SHW.A_stp = params['A_stp']
    SHW.T0 = params['T_0']
    SHW.T_w_comb = params['T_w_comb']
    SHW.T_w_tap = params['T_w_tap']
    SHW.T_w_sup = params['T_w_sup']
    SHW.T_exh = params['T_exh']
    SHW.dV_w_serv = params['dV_w_serv']*enex.L2m3/enex.m2s
    SHW.h_o = params['h_o']
    SHW.h_r = params['h_r']
    SHW.k_air = params['k_air']
    SHW.k_ins = params['k_ins']
    SHW.x_air = params['x_air']
    SHW.x_ins = params['x_ins']
    SHW.system_update()

    X_w_sup = SHW.X_w_sup
    X_sol = SHW.X_sol
    X_w_stp_out = SHW.X_w_stp_out
    X_l = SHW.X_l
    X_c_stp = SHW.X_c_stp

    X_NG = SHW.X_NG
    X_exh = SHW.X_exh
    X_w_comb = SHW.X_w_comb
    X_c_comb = SHW.X_c_comb

    X_w_sup_mix = SHW.X_w_sup_mix
    X_w_serv = SHW.X_w_serv
    X_c_mix = SHW.X_c_mix

    return {k: v for k, v in locals().items() if k not in ('params')}