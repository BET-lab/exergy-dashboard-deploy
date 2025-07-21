import math
from typing import Any, List, Dict
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import enex_analysis as enex
from exergy_dashboard.system import register_system
from exergy_dashboard.evaluation import registry as eval_registry
from exergy_dashboard.visualization import registry as viz_registry
from exergy_dashboard.chart import plot_waterfall_multi, create_efficiency_grade_chart


# 기본 시스템 정의
ELECTRIC_BOILER = {
    'display': {
        'title': 'Electric boiler',
        'icon': ':zap:',
    },
    'parameters': {
        # Condition ------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'environment temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'Operating condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_w_tank': {
            'explanation': {'EN': 'Tank water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Hot water tank',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup+1.0', 'T_w_tank-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'Operating condition',
        },
        # Hot water tank ------------------------------------------------------------
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'Hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'Hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'Hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'Hot water tank',
        },
    }
}
GAS_BOILER = {
    'display': {
        'title': 'Gas boiler',
        'icon': ':fire:',
    },
    'parameters': {
        # Condition ------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'environment temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'Operating condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'Operating condition',
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
            'category': 'Hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'Hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'Hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'Hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'Hot water tank',
        },
    }
}
HEAT_PUMP_BOILER = {
    'display': {
        'title': 'Heat pump boiler',
        'icon': ':gear:',
    },
    'parameters': {
        # Condition ------------------------------------------------------------
            'T_0': {
            'explanation': {'EN': 'environment temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'Operating condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'Operating condition',
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
            'category': 'Hot water tank',
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
            'default': 0.20,
            'range': [0.05, 0.4],
            'unit': 'm',
            'step': 0.01,
            'category': 'external unit',
        },
        'dP': {
            'explanation': {'EN': 'Pressure Difference', 'KR': '압력차'},
            'latex': r'$\Delta P$',
            'default': 200.0,
            'range': [50.0, 1000.0],
            'unit': 'Pa',
            'step': 10.0,
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
            'category': 'Hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'Hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'Hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'Hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'Hot water tank',
        },
    }
}
SOLAR_ASSISTED_GAS_BOILER = {
    'display': {
        'title': 'Solar assisted gas boiler',
        'icon': ':sun:',
    },
    'parameters': {
        # Condition ------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'environment temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'Operating condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'Operating condition',
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
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'Hot water tank',
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
        'T_exh': {
            'explanation': {'EN': 'Exhaust gas temperature', 'KR': '배기 가스 온도'},
            'latex': r'$T_{exh}$',
            'default': 70.0,
            'range': ['T_w_sup + 1.0', 200.0],
            'unit': '℃',
            'step': 5.0,
            'category': 'Operating condition',
        },
    }
}
GSHP_BOILER = {
    'display': {
        'title': 'Ground source heat pump boiler',
        'icon': ':ground:',  # 흙/땅 느낌의 아이콘으로 변경
    },
    'parameters': {
        # Condition ----------------------------------------------------------------------------
        't':{
            'explanation': {'EN': 'Operating time', 'KR': '운전 시간'},
            'latex': r'$t$',
            'default': 100.0,
            'range': [0.0, 2000.0],
            'unit': 'h',
            'step': 100.0,
            'category': 'Operating condition',
        },
        'T_0': {
            'explanation': {'EN': 'environment temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'Tank water use', 'KR': '탱크 온수 사용량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.0, 10.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'Operating condition',
        },
        'T_w_sup': {
            'explanation': {'EN': 'Supply water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'T_w_tank': {
            'explanation': {'EN': 'Tank water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Hot water tank',
        },
        'T_w_serv': {
            'explanation': {'EN': 'Service water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup+1.0', 'T_w_tank-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'Operating condition',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1.0, 50.0],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'Operating condition',
        },

        # Hot water tank ------------------------------------------------------------
        'r0': {
            'explanation': {'EN': 'Tank radius', 'KR': '탱크 반지름'},
            'latex': r'$r_0$',
            'default': 0.2,
            'range': [0.1, 1.0],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'H': {
            'explanation': {'EN': 'Tank height', 'KR': '탱크 높이'},
            'latex': r'$H$',
            'default': 0.8,
            'range': [0.1, 2.0],
            'unit': 'm',
            'step': 0.05,
            'category': 'Hot water tank',
        },
        'x_shell': {
            'explanation': {'EN': 'Tank shell thickness', 'KR': '탱크 외피 두께'},
            'latex': r'$x_{shell}$',
            'default': 0.01,
            'range': [0.005, 0.05],
            'unit': 'm',
            'step': 0.005,
            'category': 'Hot water tank',
        },
        'x_ins': {
            'explanation': {'EN': 'Tank insulation thickness', 'KR': '탱크 단열 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.10,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'Hot water tank',
        },
        'k_shell': {
            'explanation': {'EN': 'Shell thermal conductivity', 'KR': '외피 열전도율'},
            'latex': r'$k_{shell}$',
            'default': 50.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'Hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'Hot water tank',
        },
        # Refrigerant ----------------------------------------------------------------------------
        'T_r_tank': {
            'explanation': {'EN': 'Hot water tank side Refrigerant Temperature', 'KR': '저탕조 측 냉매 온도'},
            'latex': r'$T_{r,tank}$',
            'default': 65.0,
            'range': ['T_w_tank+1.0', 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'Hot water tank',
        },

        # Ground heat exchanger -----------------------------------------------------------------
        'H_b': {
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
            'explanation': {'EN': 'Borehole thermal resistance', 'KR': '보어홀 유효 열저항'},
            'latex': r'$R_b$',
            'default': 0.1,
            'range': [0.01, 0.50],
            'unit': 'm·K/W',
            'step': 0.01,
            'category': 'ground heat exchanger',
        },
        
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
            'explanation': {'EN': 'Ground heat exchanger Pump Power', 'KR': 'GHE 펌프 전력'},
            'latex': r'$E_{pmp}$',
            'default': 200.0,
            'range': [150, 250],
            'unit': 'W',
            'step': 10.0,
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
            'category': 'Ground',
        },
        'c_g': {
            'explanation': {'EN': 'Ground Specific Heat', 'KR': '토양 비열'},
            'latex': r'$c_g$',
            'default': 800.0,
            'range': [500, 2000],
            'unit': 'J/kg·K',
            'step': 100.0,
            'category': 'Ground',
        },
        'rho_g': {
            'explanation': {'EN': 'Ground Density', 'KR': '토양 밀도'},
            'latex': r'$\rho_g$',
            'default': 2000.0,
            'range': [500, 5000],
            'unit': 'kg/m³',
            'step': 100.0,
            'category': 'Ground',
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
    }
}

# 시스템 등록
register_system('HOT WATER', 'Electric boiler', ELECTRIC_BOILER)
register_system('HOT WATER', 'Gas boiler', GAS_BOILER)
register_system('HOT WATER', 'Heat pump boiler', HEAT_PUMP_BOILER)
register_system('HOT WATER', 'Solar assisted gas boiler', SOLAR_ASSISTED_GAS_BOILER)
register_system('HOT WATER', 'Ground source heat pump boiler', GSHP_BOILER)

# HOT WATER 모드 시각화 함수들
@viz_registry.register('HOT WATER', 'Exergy efficiency')
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
        tooltip=[],
    ).properties(
        width='container',
        height=len(selected_systems) * 60 + 50
    )

    text = alt.Chart(chart_data).mark_text(
        align='left',
        baseline='middle',
        dx=3,
        fontSize=20,
        fontWeight='normal',
    ).encode(
        y=alt.Y('system:N', sort=None),
        x=alt.X('efficiency:Q'),
        text=alt.Text('efficiency:Q', format='.1f')
    )

    # LayerChart에 padding을 직접 지정
    chart = alt.layer(c, text).properties(
        width='container',
        height=len(selected_systems) * 60 + 50,
        padding={'left': 20, 'right': 10, 'top': 10, 'bottom': 10}
    )
    return chart


@viz_registry.register('HOT WATER', 'Exergy consumption process')
def plot_exergy_consumption(session_state: Any, selected_systems: List[str]) -> alt.Chart:
    """엑서지 소비 과정 차트 생성"""
    # COOLING 모드 전용 시각화
    sources = []
    for key in selected_systems:
        sv = session_state.systems[key]['variables']
        sys_type = session_state.systems[key]['type']
        # 라벨별 설명문 매핑 (EN 기준)
        if sys_type == 'Electric boiler':
            items = [
            {'label': 'X_w_sup_tank', 'amount': sv['X_w_sup_tank'], 'desc': 'Exergy supplied to tank'},
            {'label': 'X_heater', 'amount': sv['X_heater'], 'desc': 'Exergy input by heater'},
            {'label': 'X_c_tank', 'amount': -sv['X_c_tank'], 'desc': 'Exergy consumption due to heat loss'},
            {'label': 'X_l_tank', 'amount': -sv['X_l_tank'], 'desc': 'Exergy loss (tank leakage)'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'], 'desc': 'Exergy contained in the supply water to the mixing valve'},
            {'label': 'X_c_mix', 'amount': -sv['X_c_mix'], 'desc': 'Exergy consumption by mixing process'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in service hot water'},
            ]

        if sys_type == 'Gas boiler':
            items = [
            {'label': 'X_w_sup', 'amount': sv['X_w_sup'], 'desc': 'Exergy supplied to tank'},
            {'label': 'X_NG', 'amount': sv['X_NG'], 'desc': 'Exergy input by natural gas'},
            {'label': 'X_c_comb', 'amount': -sv['X_c_comb'], 'desc': 'Exergy loss (combustion)'},
            {'label': 'X_exh', 'amount': -sv['X_exh'], 'desc': 'Exergy loss (exhaust)'},
            {'label': 'X_c_tank', 'amount': -sv['X_c_tank'], 'desc': 'Exergy consumption due to heat loss'},
            {'label': 'X_l_tank', 'amount': -sv['X_l_tank'], 'desc': 'Exergy loss (tank leakage)'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'], 'desc': 'Exergy contained in the supply water to the mixing valve'},
            {'label': 'X_c_mix', 'amount': -sv['X_c_mix'], 'desc': 'Exergy consumption by mixing process'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in service hot water'},
            ]

        if sys_type == 'Heat pump boiler':
            items = [
            {'label': 'X_fan', 'amount': sv['X_fan'], 'desc': 'Exergy input by fan'},
            {'label': 'X_r_ext', 'amount': sv['X_r_ext'], 'desc': 'Exergy from external refrigerant'},
            {'label': 'X_a_ext_in', 'amount': sv['X_a_ext_in'], 'desc': 'Exergy from external air (in)'},
            {'label': 'X_c_ext', 'amount': -sv['X_c_ext'], 'desc': 'Exergy loss (external)'},
            {'label': 'X_a_ext_out', 'amount': -sv['X_a_ext_out'], 'desc': 'Exergy loss (external air out)'},
            {'label': 'X_cmp', 'amount': sv['X_cmp'], 'desc': 'Exergy input by compressor'},
            {'label': 'X_c_r', 'amount': -sv['X_c_r'], 'desc': 'Exergy loss (refrigerant)'},
            {'label': 'X_l_tank', 'amount': -sv['X_l_tank'], 'desc': 'Exergy loss (tank leakage)'},
            {'label': 'X_c_tank', 'amount': -sv['X_c_tank'], 'desc': 'Exergy consumption due to heat loss'},
            {'label': 'X_w_sup_tank', 'amount': sv['X_w_sup_tank'], 'desc': 'Exergy supplied to tank'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in service hot water'},
            ]

        if sys_type == 'Solar assisted gas boiler':
            items = [
            {'label': 'X_w_sup', 'amount': sv['X_w_sup'], 'desc': 'Exergy supplied to tank'},
            {'label': 'X_sol', 'amount': sv['X_sol'], 'desc': 'Exergy input by solar'},
            {'label': 'X_c_stp', 'amount': -sv['X_c_stp'], 'desc': 'Exergy loss (solar panel)'},
            {'label': 'X_l', 'amount': -sv['X_l'], 'desc': 'Exergy loss (system leakage)'},
            {'label': 'X_NG', 'amount': sv['X_NG'], 'desc': 'Exergy input by natural gas'},
            {'label': 'X_c_comb', 'amount': -sv['X_c_comb'], 'desc': 'Exergy loss (combustion)'},
            {'label': 'X_exh', 'amount': -sv['X_exh'], 'desc': 'Exergy loss (exhaust)'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'], 'desc': 'Exergy contained in the supply water to the mixing valve'},
            {'label': 'X_c_mix', 'amount': -sv['X_c_mix'], 'desc': 'Exergy consumption by mixing process'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in service hot water'},
            ]

        if sys_type == 'Ground source heat pump boiler':
            items = [
            {'label': 'Xin_g', 'amount': sv['Xin_g'], 'desc': 'Exergy input from ground'},
            {'label': 'Xc_g', 'amount': -sv['Xc_g'], 'desc': 'Exergy loss (ground)'},
            {'label': 'E_pmp', 'amount': sv['E_pmp'], 'desc': 'Pump power'},
            {'label': 'Xc_GHE', 'amount': -sv['Xc_GHE'], 'desc': 'Exergy loss (GHE)'},
            {'label': 'X_r_exch(from refrigerant)', 'amount': abs(sv['X_r_exch']), 'desc': 'Cool exergy supplied by refrigerant' if sv['X_r_exch'] >= 0 else 'Warm exergy supplied by refrigerant'},
            {'label': 'Xc_exch', 'amount': -sv['Xc_exch'], 'desc': 'Exergy loss (external)'},
            {'label': 'X_cmp', 'amount': sv['X_cmp'], 'desc': 'Exergy input by compressor'},
            {'label': 'Xc_r', 'amount': -sv['Xc_r'], 'desc': 'Exergy loss (refrigerant)'},
            {'label': 'X_r_exch(to heat exchanger)', 'amount': -abs(sv['X_r_exch']), 'desc': 'Cool exergy supplied to heat exchanger' if sv['X_r_exch'] >= 0 else 'Warm exergy supplied to heat exchanger'},
            {'label': 'X_l_tank', 'amount': -sv['X_l_tank'], 'desc': 'Exergy loss (tank leakage)'},
            {'label': 'X_w_sup_tank', 'amount': sv['X_w_sup_tank'], 'desc': 'Exergy supplied'},
            {'label': 'Xc_tank', 'amount': -sv['Xc_tank'], 'desc': 'Exergy consumption due to heat loss'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'], 'desc': 'Exergy contained in the supply water to the mixing valve'},
            {'label': 'Xc_mix', 'amount': -sv['Xc_mix'], 'desc': 'Exergy consumption by mixing process'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in service hot water'},
            ]
            
        for item in items:
            item['group'] = key
        source = pd.DataFrame(items)
        sources.append(source)

    if sources:
        source = pd.concat(sources)
        return plot_waterfall_multi(source)
    return alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_point()


# HEATING 모드 시각화 함수들
@viz_registry.register('HOT WATER', 'Exergy efficiency grade')
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



@eval_registry.register('HOT WATER', 'Electric boiler')
def evaluate_electric_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    EB = enex.ElectricBoiler()
    EB.T0 = params['T_0']
    EB.T_w_tank = params['T_w_tank']
    EB.T_w_sup = params['T_w_sup']
    EB.T_w_serv = params['T_w_serv']
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

@eval_registry.register('HOT WATER', 'Gas boiler')
def evaluate_gas_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    GB = enex.GasBoiler()
    GB.T0 = params['T_0']
    GB.T_w_tank = params['T_w_tank']
    GB.T_w_sup = params['T_w_sup']
    GB.T_w_serv = params['T_w_serv']
    GB.T_exh = params['T_exh']
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
    HPB.dV_w_serv = params['dV_w_serv']
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

@eval_registry.register('HOT WATER', 'Solar assisted gas boiler')
def evaluate_SOLAR_ASSISTED_GAS_BOILER(params: Dict[str, float]) -> Dict[str, float]:
    """ASHP 냉방 모드 평가 함수"""
    SAGB = enex.SolarAssistedGasBoiler()
    SAGB.alpha = params['alpha']
    SAGB.eta_comb = params['eta_comb']
    SAGB.I_DN = params['I_DN']
    SAGB.I_dH = params['I_dH']
    SAGB.A_stp = params['A_stp']
    SAGB.T0 = params['T_0']
    SAGB.T_w_comb = params['T_w_comb']
    SAGB.T_w_serv = params['T_w_serv']
    SAGB.T_w_sup = params['T_w_sup']
    SAGB.T_exh = params['T_exh']
    SAGB.dV_w_serv = params['dV_w_serv']
    SAGB.h_o = params['h_o']
    SAGB.h_r = params['h_r']
    SAGB.k_ins = params['k_ins']
    SAGB.x_air = params['x_air']
    SAGB.x_ins = params['x_ins']
    SAGB.system_update()

    X_w_sup = SAGB.X_w_sup
    X_sol = SAGB.X_sol
    X_w_stp_out = SAGB.X_w_stp_out
    X_l = SAGB.X_l
    X_c_stp = SAGB.X_c_stp

    X_NG = SAGB.X_NG
    X_exh = SAGB.X_exh
    X_w_comb = SAGB.X_w_comb
    X_c_comb = SAGB.X_c_comb

    X_w_sup_mix = SAGB.X_w_sup_mix
    X_w_serv = SAGB.X_w_serv
    X_c_mix = SAGB.X_c_mix
    
    X_eff = SAGB.X_w_serv / SAGB.X_NG

    return {k: v for k, v in locals().items() if k not in ('params')}

@eval_registry.register('HOT WATER', 'Ground source heat pump boiler')
def evaluate_gshp_boiler(params: Dict[str, float]) -> Dict[str, float]:
    """GSHP 보일러 평가 함수"""
    GSHPB = enex.GroundSourceHeatPumpBoiler()
    GSHPB.time = params['t']
    GSHPB.T0 = params['T_0']
    GSHPB.T_w_tank = params['T_w_tank']
    GSHPB.T_w_sup = params['T_w_sup']
    GSHPB.T_w_serv = params['T_w_serv']
    GSHPB.dV_w_serv = params['dV_w_serv']
    
    GSHPB.r0 = params['r0']
    GSHPB.H = params['H']
    GSHPB.x_shell = params['x_shell']
    GSHPB.x_ins = params['x_ins']
    GSHPB.k_shell = params['k_shell']
    GSHPB.k_ins = params['k_ins']
    GSHPB.h_o = params['h_o']
    
    GSHPB.T_r_tank = params['T_r_tank']
    
    GSHPB.H_b = params['H_b']
    GSHPB.r_b = params['r_b']
    GSHPB.R_b = params['R_b']
    GSHPB.V_f = params['V_f']* enex.L2m3 / enex.m2s  # Convert L/min to m³/s
    GSHPB.E_pmp = params['E_pmp']
    
    GSHPB.k_g = params['k_g']
    GSHPB.c_g = params['c_g']
    GSHPB.rho_g = params['rho_g']
    GSHPB.T_g = params['T_g']
    GSHPB.system_update()
    
    # Ground
    Xin_g = GSHPB.Xin_g
    Xc_g = GSHPB.Xc_g
    
    E_pmp = GSHPB.E_pmp
    Xc_GHE = GSHPB.Xc_GHE
    Xc_exch = GSHPB.Xc_exch
    X_cmp = GSHPB.X_cmp
    Xc_r = GSHPB.Xc_r
    
    X_r_exch = GSHPB.X_r_exch
    X_l_tank = GSHPB.X_l_tank
    X_w_sup_tank = GSHPB.X_w_sup_tank
    Xc_tank = GSHPB.Xc_tank
    X_w_sup_mix = GSHPB.X_w_sup_mix
    Xc_mix = GSHPB.Xc_mix
    X_w_serv = GSHPB.X_w_serv

    Xin_GHE = GSHPB.Xin_GHE
    Xout_GHE = GSHPB.Xout_GHE
    
    Xin_exch = GSHPB.Xin_exch
    Xout_exch = GSHPB.Xout_exch
    
    Xin_r = GSHPB.Xin_r
    Xout_r = GSHPB.Xout_r
    
    Xin_tank = GSHPB.Xin_tank
    Xout_tank = GSHPB.Xout_tank
    
    Xin_mix = GSHPB.Xin_mix
    Xout_mix = GSHPB.Xout_mix

    X_eff = GSHPB.X_eff

    return {k: v for k, v in locals().items() if k not in ('params')}