import math
from typing import Any, List, Dict
import pandas as pd
import altair as alt
import streamlit as st
import en_system_ex_analysis as enex
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
from exergy_dashboard.chart import plot_waterfall_multi


# 기본 시스템 정의
ELECTRIC_BOILER = {
    'display': {
        'title': 'Electric boiler',
        'icon': ':zap:',
    },
    'parameters': {
        # condition ------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'Reference temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'condition',
        },
        # Hot water tank ------------------------------------------------------------
        'T_w_tank': {
            'explanation': {'EN': 'Tank water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.001, 0.1],
            'unit': 'W/m·K',
            'step': 0.001,
            'category': 'hot water tank',
        },
    }
}

GAS_BOILER = {
    'display': {
        'title': 'Gas boiler',
        'icon': ':droplet:',
    },
    'parameters': {
        # condition ------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'Reference temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'condition',
        },
        
        # combustion chamber ------------------------------------------------------------
        'eta_comb': {
            'explanation': {'EN': 'Combustion efficiency', 'KR': '연소 효율'},
            'latex': r'$\eta_{comb}$',
            'default': 0.9,
            'range': [0.5, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'combustion chamber',
        },
        'T_exh': {
            'explanation': {'EN': 'Exhaust gas temperature', 'KR': '배기가스 온도'},
            'latex': r'$T_{exh}$',
            'default': 70.0,
            'range': [0, 200],
            'unit': '℃',
            'step': 10.0,
            'category': 'combustion chamber',
        },
        
        # Hot water tank ------------------------------------------------------------
        'T_w_tank': {
            'explanation': {'EN': 'Tank water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.001, 0.1],
            'unit': 'W/m·K',
            'step': 0.001,
            'category': 'hot water tank',
        },
    }
}

HEAT_PUMP_BOILER = {
    'display': {
        'title': 'Heat pump boiler',
        'icon': ':droplet:',
    },
    'parameters': {
        # condition ------------------------------------------------------------
            'T_0': {
            'explanation': {'EN': 'Reference temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'condition',
        },
        'COP_hp': {
            'explanation': {'EN': 'Heat Pump COP', 'KR': '히트펌프 COP'},
            'latex': r'$\mathrm{COP}_{hp}$',
            'default': 2.5,
            'range': [1.0, 6.0],
            'unit': '-',
            'step': 0.1,
            'category': 'efficiency',
        },
        
        # refrigerant -------------------------------------------------------------
        'T_r_ext': {
            'explanation': {'EN': 'Outdoor Refrigerant Temp', 'KR': '외부 냉매 온도'},
            'latex': r'$T_{r,ext}$',
            'default': -10.0,
            'range': [-30, 40],
            'unit': '℃',
            'step': 1.0,
            'category': 'external unit',
        },
        'T_r_tank': {
            'explanation': {'EN': 'Tank Refrigerant Temp', 'KR': '탱크 냉매 온도'},
            'latex': r'$T_{r,tank}$',
            'default': 65.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 5.0,
            'category': 'temperature',
        },
        
        # external unit -------------------------------------------------------------
        'T_a_ext_out': {
            'explanation': {'EN': 'Outdoor Air Outlet Temp', 'KR': '외기 출구 온도'},
            'latex': r'$T_{a,ext,out}$',
            'default': -5.0,
            'range': [-30, 40],
            'unit': '℃',
            'step': 1.0,
            'category': 'external unit',
        },
        'eta_fan': {
            'explanation': {'EN': 'Fan Efficiency', 'KR': '팬 효율'},
            'latex': r'$\eta_{fan}$',
            'default': 0.6,
            'range': [0.3, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'external unit',
        },
        'r_ext': {
            'explanation': {'EN': 'Fan Radius', 'KR': '실외기 반지름'},
            'latex': r'$r_{ext}$',
            'default': 0.2,
            'range': [0.05, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'external unit',
        },
        'dP': {
            'explanation': {'EN': 'Pressure Difference', 'KR': '압력차'},
            'latex': r'$\Delta P$',
            'default': 200,
            'range': [50, 1000],
            'unit': 'Pa',
            'step': 10,
            'category': 'external unit',
        },
        
        # Hot water tank ------------------------------------------------------------
        'T_w_tank': {
            'explanation': {'EN': 'Tank water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.001, 0.1],
            'unit': 'W/m·K',
            'step': 0.001,
            'category': 'hot water tank',
        },
    }
}

SOLAR_HOT_WATER = {
    'display': {
        'title': 'Solar hot water',
        'icon': ':sun:',
    },
    'parameters': {
        # condition ------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'Reference temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'condition',
        },
        
        
        # solar collector ------------------------------------------------------------
        'A_stp': {
            'explanation': {'EN': 'Solar thermal panel area', 'KR': '태양열 패널 면적'},
            'latex': r'$A_{stp}$',
            'default': 2.0,
            'range': [0.5, 10.0],
            'unit': 'm²',
            'step': 0.1,
            'category': 'solar collector',
        },
        'h_r': {
            'explanation': {'EN': 'Radiative heat transfer coefficient', 'KR': '복사 열전달계수'},
            'latex': r'$h_r$',
            'default': 2.0,
            'range': [0.5, 10.0],
            'unit': 'W/m²K',
            'step': 0.1,
            'category': 'solar collector',
        },
        'x_air': {
            'explanation': {'EN': 'Air layer thickness', 'KR': '공기층 두께'},
            'latex': r'$x_{air}$',
            'default': 0.01,
            'range': [0.01, 0.05],
            'unit': 'm',
            'step': 0.01,
            'category': 'solar collector',
        },
        'x_ins': {
            'explanation': {'EN': 'Insulation thickness', 'KR': '단열재 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.05,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'solar collector',
        },
        'alpha': {
            'explanation': {'EN': 'Absorptivity of Collector', 'KR': '집열판 흡수율'},
            'latex': r'$\alpha$',
            'default': 0.95,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.05,
            'category': 'solar collector',
        },
        'I_DN': {
            'explanation': {'EN': 'Direct Normal Irradiance', 'KR': '직달일사량'},
            'latex': r'$I_{DN}$',
            'default': 500.0,
            'range': [0.0, 1200.0],
            'unit': 'W/m²',
            'step': 50.0,
            'category': 'solar collector',
        },
        'I_dH': {
            'explanation': {'EN': 'Diffuse Horizontal Irradiance', 'KR': '확산수평일사량'},
            'latex': r'$I_{dH}$',
            'default': 200.0,
            'range': [0.0, 500.0],
            'unit': 'W/m²',
            'step': 10.0,
            'category': 'solar collector',
        },
        
        # combustion chamber ------------------------------------------------------------
        'eta_comb': {
            'explanation': {'EN': 'Combustion chamber efficiency', 'KR': '연소실 효율'},
            'latex': r'$\eta_{comb}$',
            'default': 0.9,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.01,
            'category': 'combustion chamber',
        },
        'T_w_comb': {
            'explanation': {'EN': 'Tank water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,comb}$',
            'default': 60.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'combustion chamber',
        },
    }
}

GSHP_BOILER = {
    'display': {
        'title': 'Ground source heat pump boiler',
        'icon': ':earth_americas:',
    },
    'parameters': {
        # Condition ----------------------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'Reference temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'condition',
        },
        
        # Hot water tank ------------------------------------------------------------
        'T_w_tank': {
            'explanation': {'EN': 'Tank water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.001, 0.1],
            'unit': 'W/m·K',
            'step': 0.001,
            'category': 'hot water tank',
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
            'default': 200,
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
        'T_g': {
            'explanation': {'EN': 'Ground temperature', 'KR': '토양온도'},
            'latex': r'$T_g$',
            'default': 15.0,
            'range': [0, 20],
            'unit': '℃',
            'step': 1.0,
            'category': 'condition',
        },
    }
}

# 시스템 등록
register_system('HOT WATER', 'Electric boiler', ELECTRIC_BOILER)
register_system('HOT WATER', 'Gas boiler', GAS_BOILER)
register_system('HOT WATER', 'Heat pump boiler', HEAT_PUMP_BOILER)
register_system('HOT WATER', 'Solar hot water', SOLAR_HOT_WATER)
register_system('HOT WATER', 'Ground source heat pump boiler', GSHP_BOILER)

# HOT WATER 모드 시각화 함수들
@viz_registry.register('HOT WATER', 'Exergy Efficiency')
def plot_exergy_efficiency(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 효율 차트 생성"""
    # HOT WATER 모드 전용 시각화
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


@viz_registry.register('HOT WATER', 'Exergy Consumption Process')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    # COOLING 모드 전용 시각화
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        if session_state.systems[key]['type'] == 'Electric boiler':
            labels = [
                # r'$X_{w,sup,tank}$',
                # r'$X_{heater}$',
                # r'$-X_{c,tank}$',
                # r'$-X_{l,tank}$',
                # r'$X_{w,sup,mix}$',
                # r'$-X_{c,mix}$',
                # r'$X_{w,serv}$',
                r'X_{w,sup,tank}',
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
                # sv['X_w_serv'],
                
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)
            
        if session_state.systems[key]['type'] == 'Gas boiler':
            labels = [
                'X1',
                'X2',
                'X3',
                'X4',
                'X5',
                'X6',
                'X7',
                'X8',
                'X9',
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
                0
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)

        if session_state.systems[key]['type'] == 'Heat pump boiler':
            labels = [
                st.latex(r'X_1'),
                'X2',
                'X3',
                'X4',
                'X5',
                'X6',
                'X7',
                'X8',
                'X9',
                'X10',
                'X11',
                'X12',
            ]
            amounts = [
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
                0,
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)
        
        if session_state.systems[key]['type'] == 'Solar hot water':
            labels = [
                'X1',
                'X2',
                'X3',
                'X4',
                'X5',
                'X6',
                'X7',
                'X8',
                'X9',
                'X10',
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
                0,
            ]
            source = pd.DataFrame({
                'label': labels,
                'amount': amounts,
                'group': [key] * len(labels),
            })
            sources.append(source)
        if session_state.systems[key]['type'] == 'Ground source heat pump boiler':
            labels = [
                'X1',
                'X2',
                'X3',
                'X4',
                'X5',
                'X6',
                'X7',
                'X8',
                'X9',
                'X10',
                'X11',
            ]
            amounts = [
                sv['X_w_sup'],
                sv['X_r_int'],
                sv['X_r_exch'],
                -sv['X_c_r'],
                -sv['X_l_borehole'],
                -sv['X_c_borehole'],
                sv['X_w_sup_tank'],
                -sv['X_c_mix'],
                0,
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


@eval_registry.register('HOT WATER', 'Electric boiler')
def evaluate_electric_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    EB = enex.ElectricBoiler()
    EB.T0 = params['T_0']
    EB.T_w_tank = params['T_w_tank']
    EB.T_w_sup = params['T_w_sup']
    EB.T_w_serv = params['T_w_serv']
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

@eval_registry.register('HOT WATER', 'Gas boiler')
def evaluate_gas_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    GB = enex.GasBoiler()
    GB.T0 = params['T_0']
    GB.T_w_tank = params['T_w_tank']
    GB.T_w_sup = params['T_w_sup']
    GB.T_w_serv = params['T_w_serv']
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

@eval_registry.register('HOT WATER', 'Heat pump boiler')
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
    HPB.T_w_serv = params['T_w_serv']
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

@eval_registry.register('HOT WATER', 'Solar hot water')
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
    SHW.T_w_serv = params['T_w_serv']
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

@eval_registry.register('HOT WATER', 'GSHP boiler')
def evaluate_gshp_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """GSHP 보일러 평가 함수"""
    GSHPB = enex.GroundSourceHeatPumpBoiler()
    GSHPB.alpha = params['alpha']
    GSHPB.eta_comb = params['eta_comb']
    GSHPB.eta_NG = params['eta_NG']
    GSHPB.I_DN = params['I_DN']
    GSHPB.I_dH = params['I_dH']
    GSHPB.A_stp = params['A_stp']
    GSHPB.T0 = params['T_0']
    GSHPB.T_w_comb = params['T_w_comb']
    GSHPB.T_w_serv = params['T_w_serv']
    GSHPB.T_w_sup = params['T_w_sup']
    GSHPB.T_exh = params['T_exh']
    GSHPB.dV_w_serv = params['dV_w_serv']*enex.L2m3/enex.m2s
    GSHPB.h_o = params['h_o']
    GSHPB.h_r = params['h_r']
    GSHPB.k_ins = params['k_ins']
    GSHPB.x_air = params['x_air']
    GSHPB.x_ins = params['x_ins']
    GSHPB.system_update()
    
    # Ground
    Xin_g = GSHPB.Xin_g
    Xout_g = GSHPB.Xout_g
    Xc_g = GSHPB.Xc_g

    Xin_GHE = GSHPB.Xin_GHE
    Xout_GHE = GSHPB.Xout_GHE
    Xc_GHE = GSHPB.Xc_GHE

    Xin_exch = GSHPB.Xin_exch
    Xout_exch = GSHPB.Xout_exch
    Xc_exch = GSHPB.Xc_exch

    Xin_r = GSHPB.Xin_r
    Xout_r = GSHPB.Xout_r
    Xc_r = GSHPB.Xc_r

    Xin_tank = GSHPB.Xin_tank
    Xout_tank = GSHPB.Xout_tank
    Xc_tank = GSHPB.Xc_tank

    Xin_mix = GSHPB.Xin_mix
    Xout_mix = GSHPB.Xout_mix
    Xc_mix = GSHPB.Xc_mix

    X_eff = GSHPB.X_eff


    return {k: v for k, v in locals().items() if k not in ('params')}