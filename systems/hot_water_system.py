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
            'explanation': {'EN': 'environmental temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'service hot water flow rate', 'KR': '최종 온수 사용 유량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.5, 5.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'operating environment',
        },
        'T_w_sup': {
            'explanation': {'EN': 'supply cold water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'T_w_tank': {
            'explanation': {'EN': 'Tank hot water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'T_w_serv': {
            'explanation': {'EN': 'service hot water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup+1.0', 'T_w_tank-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        # hot water tank ------------------------------------------------------------
        'r0': {
            'explanation': {'EN': 'tank inner radius', 'KR': '탱크 반지름'},
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
            'default': 25.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient of external surface', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'hot water tank',
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
            'explanation': {'EN': 'environmental temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'service hot water flow rate', 'KR': '최종 온수 사용 유량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.5, 5.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'operating environment',
        },
        'T_w_sup': {
            'explanation': {'EN': 'supply cold water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'T_w_serv': {
            'explanation': {'EN': 'service hot water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
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
        
        # hot water tank ------------------------------------------------------------
        'T_w_tank': {
            'explanation': {'EN': 'Tank hot water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'tank inner radius', 'KR': '탱크 반지름'},
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
            'default': 25.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient of external surface', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'hot water tank',
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
            'explanation': {'EN': 'environmental temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'service hot water flow rate', 'KR': '최종 온수 사용 유량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.5, 5.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'operating environment',
        },
        'T_w_sup': {
            'explanation': {'EN': 'supply cold water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'T_w_serv': {
            'explanation': {'EN': 'service hot water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'COP': {
            'explanation': {'EN': 'coefficient of performance', 'KR': '히트펌프 COP'},
            'latex': r'$\mathrm{COP}$',
            'default': 2.5,
            'range': [1.0, 6.0],
            'unit': '-',
            'step': 0.1,
            'category': 'operating environment',
        },
        
        'T_r_tank': {
            'explanation': {'EN': 'Mean refrigerant temperature', 'KR': '탱크 측 냉매 평균 온도'},
            'latex': r'$T_{r,tank}$',
            'default': 65.0,
            'range': [0, 100],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        
        # external unit -------------------------------------------------------------
        'T_a_ext_out': {
            'explanation': {'EN': 'external unit outlet air temperature', 'KR': '외기 출구 온도'},
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
            'step': 0.05,
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
        'T_r_ext': {
            'explanation': {'EN': 'Mean refrigerant temperature', 'KR': '실외기 측 냉매 평균 온도'},
            'latex': r'$T_{r,ext}$',
            'default': -10.0,
            'range': [-30, 40],
            'unit': '℃',
            'step': 1.0,
            'category': 'external unit',
        },
        
        # hot water tank ------------------------------------------------------------
        'T_w_tank': {
            'explanation': {'EN': 'Tank hot water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'r0': {
            'explanation': {'EN': 'tank inner radius', 'KR': '탱크 반지름'},
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
            'default': 25.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient of external surface', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
    }
}
SOLAR_ASSISTED_GAS_BOILER = {
    'display': {
        'title': 'Solar assisted gas boiler',
        'icon': ':sunny:',
    },
    'parameters': {
        # Condition ------------------------------------------------------------
        'T_0': {
            'explanation': {'EN': 'environmental temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'service hot water flow rate', 'KR': '최종 온수 사용 유량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.5, 5.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'operating environment',
        },
        'T_w_sup': {
            'explanation': {'EN': 'supply cold water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'T_w_serv': {
            'explanation': {'EN': 'service hot water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup + 1.0', 'T_w_tank - 1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        
        
        # solar thermal collector ------------------------------------------------------------
        'A_stc': {
            'explanation': {'EN': 'Solar thermal collector area', 'KR': '태양열 패널 면적'},
            'latex': r'$A_{stc}$',
            'default': 2.0,
            'range': [0.5, 10.0],
            'unit': 'm²',
            'step': 0.1,
            'category': 'solar thermal collector',
        },
        'h_r': {
            'explanation': {'EN': 'Radiative heat transfer coefficient', 'KR': '복사 열전달계수'},
            'latex': r'$h_r$',
            'default': 2.0,
            'range': [0.5, 10.0],
            'unit': 'W/m²K',
            'step': 0.1,
            'category': 'solar thermal collector',
        },
        'x_air': {
            'explanation': {'EN': 'Solar thermal collector air layer thickness', 'KR': '태양열 집열판 공기층 두께'},
            'latex': r'$x_{air}$',
            'default': 0.01,
            'range': [0.01, 0.05],
            'unit': 'm',
            'step': 0.01,
            'category': 'solar thermal collector',
        },
        'x_ins': {
            'explanation': {'EN': 'Insulation thickness', 'KR': '단열재 두께'},
            'latex': r'$x_{ins}$',
            'default': 0.05,
            'range': [0.01, 0.2],
            'unit': 'm',
            'step': 0.01,
            'category': 'solar thermal collector',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'solar thermal collector',
        },
        'alpha': {
            'explanation': {'EN': 'Absorptivity of Collector', 'KR': '집열판 흡수율'},
            'latex': r'$\alpha$',
            'default': 0.95,
            'range': [0.7, 1.0],
            'unit': '-',
            'step': 0.05,
            'category': 'solar thermal collector',
        },
        'I_DN': {
            'explanation': {'EN': 'Direct Normal Irradiance', 'KR': '직달일사량'},
            'latex': r'$I_{DN}$',
            'default': 500.0,
            'range': [0.0, 1200.0],
            'unit': 'W/m²',
            'step': 50.0,
            'category': 'solar thermal collector',
        },
        'I_dH': {
            'explanation': {'EN': 'Diffuse Horizontal Irradiance', 'KR': '확산수평일사량'},
            'latex': r'$I_{dH}$',
            'default': 200.0,
            'range': [0.0, 500.0],
            'unit': 'W/m²',
            'step': 10.0,
            'category': 'solar thermal collector',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient of external surface', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1, 50],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'solar thermal collector',
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
            'explanation': {'EN': 'Tank hot water temperature', 'KR': '탱크 내 온수 온도'},
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
            'category': 'combustion chamber',
        },
    }
}
GSHP_BOILER = {
    'display': {
        'title': 'Ground source heat pump boiler',
        'icon': ':earth_americas:',  # 흙/땅 느낌의 아이콘으로 변경
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
            'category': 'operating environment',
        },
        'T_0': {
            'explanation': {'EN': 'environmental temperature', 'KR': '기준 온도'},
            'latex': r'$T_0$',
            'default': 0.0,
            'range': [-50.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'dV_w_serv': {
            'explanation': {'EN': 'service hot water flow rate', 'KR': '최종 온수 사용 유량'},
            'latex': r'$\dot{V}_{w,serv}$',
            'default': 1.0,
            'range': [0.5, 5.0],
            'unit': 'L/min',
            'step': 0.1,
            'category': 'operating environment',
        },
        'T_w_sup': {
            'explanation': {'EN': 'supply cold water temperature', 'KR': '상수도 온도'},
            'latex': r'$T_{w,sup}$',
            'default': 10.0,
            'range': [0.0, 50.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },
        'T_w_tank': {
            'explanation': {'EN': 'Tank hot water temperature', 'KR': '탱크 내 온수 온도'},
            'latex': r'$T_{w,tank}$',
            'default': 60.0,
            'range': [0.0, 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'T_w_serv': {
            'explanation': {'EN': 'service hot water temperature', 'KR': '공급 온수 온도'},
            'latex': r'$T_{w,serv}$',
            'default': 45.0,
            'range': ['T_w_sup+1.0', 'T_w_tank-1.0'],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
        },

        # hot water tank ------------------------------------------------------------
        'r0': {
            'explanation': {'EN': 'tank inner radius', 'KR': '탱크 반지름'},
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
            'default': 25.0,
            'range': [1, 100],
            'unit': 'W/m·K',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'k_ins': {
            'explanation': {'EN': 'Insulation thermal conductivity', 'KR': '단열재 열전도율'},
            'latex': r'$k_{ins}$',
            'default': 0.03,
            'range': [0.02, 0.04],
            'unit': 'W/m·K',
            'step': 0.005,
            'category': 'hot water tank',
        },
        'T_r_tank': {
            'explanation': {'EN': 'Mean refrigerant temperature', 'KR': '저탕조 측 냉매 평균 온도'},
            'latex': r'$T_{r,tank}$',
            'default': 65.0,
            'range': ['T_w_tank+1.0', 100.0],
            'unit': '℃',
            'step': 1.0,
            'category': 'hot water tank',
        },
        'h_o': {
            'explanation': {'EN': 'Overall heat transfer coefficient of external surface', 'KR': '종합 열전달계수'},
            'latex': r'$h_o$',
            'default': 15.0,
            'range': [1.0, 50.0],
            'unit': 'W/m²·K',
            'step': 1.0,
            'category': 'hot water tank',
        },

        # Ground heat exchanger -----------------------------------------------------------------
        'H_b': {
            'explanation': {'EN': 'borehole length', 'KR': '보어홀 길이'},
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
            'explanation': {'EN': 'effective borehole thermal resistance', 'KR': '보어홀 유효 열저항'},
            'latex': r'$R_b^*$',
            'default': 0.1,
            'range': [0.01, 0.50],
            'unit': 'm·K/W',
            'step': 0.01,
            'category': 'ground heat exchanger',
        },
        
        'dV_f': {
            'explanation': {'EN': 'Fluid volumetric flow rate', 'KR': '유체 체적 유량'},
            'latex': r'$\dot{V}_f$',
            'default': 24.0,
            'range': [1.0, 50.0],
            'unit': 'L/min',
            'step': 1.0,
            'category': 'ground heat exchanger',
        },
        'E_pmp': {
            'explanation': {'EN': 'circulating pump power', 'KR': '지중 열교환기 펌프 전력'},
            'latex': r'$E_{pmp}$',
            'default': 200.0,
            'range': [150, 250],
            'unit': 'W',
            'step': 10.0,
            'category': 'ground heat exchanger',
        },
        
        # Ground ----------------------------------------------------------------------------
        'k_g': {
            'explanation': {'EN': 'Thermal Conductivity', 'KR': '토양 열전도도'},
            'latex': r'$k_g$',
            'default': 2.0,
            'range': [0.5, 5.0],
            'unit': 'W/m·K',
            'step': 0.1,
            'category': 'ground properties',
        },
        'c_g': {
            'explanation': {'EN': 'Specific Heat', 'KR': '토양 비열'},
            'latex': r'$c_g$',
            'default': 800.0,
            'range': [500, 2000],
            'unit': 'J/kg·K',
            'step': 100.0,
            'category': 'ground properties',
        },
        'rho_g': {
            'explanation': {'EN': 'Density', 'KR': '토양 밀도'},
            'latex': r'$\rho_g$',
            'default': 2000.0,
            'range': [500, 5000],
            'unit': 'kg/m³',
            'step': 100.0,
            'category': 'ground properties',
        },
        'T_g': {
            'explanation': {'EN': 'initial ground temperature', 'KR': '초기 지중 온도'},
            'latex': r'$T_g$',
            'default': 15.0,
            'range': [10, 20],
            'unit': '℃',
            'step': 1.0,
            'category': 'operating environment',
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
            {'label': 'X_w_sup_tank', 'amount': sv['X_w_sup_tank'],
             'desc': 'Exergy of the supply water flowing into the hot water tank.'},
            {'label': 'X_heater', 'amount': sv['X_heater'],
             'desc': 'Exergy input from electricity to the heater.'},
            {'label': 'X_c_tank', 'amount': -sv['X_c_tank'],
             'desc': 'Exergy consumption during the energy conversion process from electricity to thermal energy in the hot water tank.'},
            {'label': 'X_l_tank', 'amount': -sv['X_l_tank'],
             'desc': 'Exergy lost due to heat loss through the tank envelope.'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'],
             'desc': 'Exergy of the cold supply water directed to the mixing valve.'},
            {'label': 'X_c_mix', 'amount': -sv['X_c_mix'],
             'desc': 'Exergy consumed during the mixing of hot water from the tank and cold supply water to achieve the desired service hot water temperature.'},
            {'label': 'X_w_serv', 'amount': 0,
             'desc': 'Exergy contained in the final service hot water supplied to the user.'},
            ]

        if sys_type == 'Gas boiler':
            items = [
            {'label': 'X_w_sup', 'amount': sv['X_w_sup'], 'desc': 'Exergy of the supply water entering the combustion chamber for heating'},
            {'label': 'X_NG', 'amount': sv['X_NG'], 'desc': 'Exergy input from the chemical potential of the natural gas fuel'},
            {'label': 'X_c_comb', 'amount': -sv['X_c_comb'], 'desc': 'Exergy consumption during the energy conversion process from chemical potential to thermal energy in the combustion chamber'},
            {'label': 'X_exh', 'amount': -sv['X_exh'], 'desc': 'Exergy carried away by the hot exhaust gases, which is ultimately consumed as it dissipates into the environment'},
            {'label': 'X_c_tank', 'amount': -sv['X_c_tank'], 'desc': 'Exergy consumption during the heat transfer process within the hot water tank.'},
            {'label': 'X_l_tank', 'amount': -sv['X_l_tank'], 'desc': 'Exergy from heat loss through the tank envelope, which is ultimately consumed'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'], 'desc': 'Exergy of the cold supply water directed to the mixing valve for temperature adjustment'},
            {'label': 'X_c_mix', 'amount': -sv['X_c_mix'], 'desc': 'Exergy consumed during the mixing of hot water from the tank and cold supply water to achieve the desired service hot water temperature.'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in the final service hot water supplied to the user.'},
            ]
        if sys_type == 'Heat pump boiler':
            items = [
                {'label': 'X_fan', 'amount': sv['X_fan'],
                    'desc': 'Exergy input required to operate the fan in the external unit.'},
                {'label': 'X_r_ext(ext side)', 'amount': sv['X_r_ext'],
                    'desc': 'Cool exergy transferred from the external unit side refrigerant to the outdoor air.'},
                {'label': 'X_a_ext_in', 'amount': sv['X_a_ext_in'],
                    'desc': 'Exergy contained in the outdoor air entering the external unit.'},
                {'label': 'X_c_ext', 'amount': -sv['X_c_ext'],
                    'desc': 'Exergy consumed during the heat exchange process in the external unit.'},
                {'label': 'X_a_ext_out', 'amount': -sv['X_a_ext_out'],
                    'desc': 'Exergy contained in the outlet air of the external unit, which is ultimately lost.'},
                {'label': 'X_cmp', 'amount': sv['X_cmp'],
                    'desc': 'Exergy input as electrical work to power the compressor.'},
                {'label': 'X_c_r', 'amount': -sv['X_c_r'],
                    'desc': 'Exergy consumed within the refrigerant cycle, which uses electrical exergy to transfer thermal exergy between the refrigerant in hot water tank and external units.'},
                {'label': 'X_r_ext(ref side)', 'amount': -sv['X_r_ext'],
                    'desc': 'Cool exergy transferred from the external unit side refrigerant to the outdoor air.'},
                {'label': 'X_l_tank', 'amount': -sv['X_l_tank'],
                    'desc': 'Exergy lost due to heat loss through the tank envelope, which is ultimately consumed.'},
                {'label': 'X_c_tank', 'amount': -sv['X_c_tank'],
                    'desc': 'Exergy consumed during heat transfer from the refrigerant to the water in the tank.'},
                {'label': 'X_w_sup_tank', 'amount': sv['X_w_sup_tank'],
                    'desc': 'Exergy of the supply water entering the hot water tank.'},
                {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'],
                    'desc': 'Exergy of the cold supply water directed to the mixing valve.'},
                {'label': 'X_c_mix', 'amount': -sv['X_c_mix'],
                    'desc': 'Exergy consumed during the mixing of hot water from the tank and cold supply water to achieve the desired service hot water temperature.'},
                {'label': 'X_w_serv', 'amount': 0,
                    'desc': 'Exergy contained in the final service hot water supplied to the user.'},
            ]

        if sys_type == 'Solar assisted gas boiler':
            items = [
            {'label': 'X_w_sup', 'amount': sv['X_w_sup'], 'desc': 'Exergy of the supply water entering the solar thermal collector.'},
            {'label': 'X_sol', 'amount': sv['X_sol'], 'desc': 'Supplied exergy coming from solar irradiation before being absorbed by the collector.'},
            {'label': 'X_c_stc', 'amount': -sv['X_c_stc'], 'desc': 'Exergy consumed during the heat transfer process in the solar thermal collector.'},
            {'label': 'X_l', 'amount': -sv['X_l'], 'desc': 'Exergy lost due to heat loss from the solar thermal collector system.'},
            {'label': 'X_NG', 'amount': sv['X_NG'], 'desc': 'Exergy input from the chemical potential of the natural gas fuel.'},
            {'label': 'X_c_comb', 'amount': -sv['X_c_comb'], 'desc': 'Exergy consumed during the combustion process in the gas boiler.'},
            {'label': 'X_exh', 'amount': -sv['X_exh'], 'desc': 'Exergy carried away by the exhaust gases, which is ultimately lost to the environment.'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'], 'desc': 'Exergy of the cold supply water directed to the mixing valve for temperature adjustment.'},
            {'label': 'X_c_mix', 'amount': -sv['X_c_mix'], 'desc': 'Exergy consumed during the mixing of hot water and cold supply water to achieve the desired service hot water temperature.'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in the final service hot water supplied to the user.'},
            ]

        if sys_type == 'Ground source heat pump boiler':
            items = [
            {'label': 'Xin_g', 'amount': sv['Xin_g'], 'desc': 'Exergy input comming from the ground.'},
            {'label': 'Xc_g', 'amount': -sv['Xc_g'], 'desc': 'Exergy consumption during heat extraction from ground to borehole wall surface.'},
            {'label': 'E_pmp', 'amount': sv['E_pmp'], 'desc': 'Exergy input required to operate the circulating pump in the ground heat exchanger.'},
            {'label': 'Xc_GHE', 'amount': -sv['Xc_GHE'], 'desc': 'Exergy consumption in the ground heat exchanger (GHE) during heat transfer.'},
            {'label': 'X_r_exch(GHE side)', 'amount': abs(sv['X_r_exch']), 'desc': f"{'Cool' if sv['X_r_exch'] >= 0 else 'Warm'} exergy supplied by refrigerant to ground heat exchanger loop."},
            {'label': 'Xc_exch', 'amount': -sv['Xc_exch'], 'desc': 'Exergy consumption in the external heat exchanger.'},
            {'label': 'X_cmp', 'amount': sv['X_cmp'], 'desc': 'Exergy input as electrical work to power the compressor.'},
            {'label': 'Xc_r', 'amount': -sv['Xc_r'], 'desc': 'Exergy consumed within the refrigerant cycle, which uses electrical exergy to transfer thermal exergy between the heat exchanger and the refrigerant.'},
            {'label': 'X_r_exch(ref side)', 'amount': -abs(sv['X_r_exch']), 'desc': f"{'Cool' if sv['X_r_exch'] >= 0 else 'Warm'} exergy supplied to the heat exchanger."},
            {'label': 'X_l_tank', 'amount': -sv['X_l_tank'], 'desc': 'Exergy lost due to heat loss through the tank envelope, which is ultimately consumed.'},
            {'label': 'X_w_sup_tank', 'amount': sv['X_w_sup_tank'], 'desc': 'Exergy of the supply water entering the hot water tank.'},
            {'label': 'Xc_tank', 'amount': -sv['Xc_tank'], 'desc': 'Exergy consumed during heat transfer from refrigerant to water in the tank.'},
            {'label': 'X_w_sup_mix', 'amount': sv['X_w_sup_mix'], 'desc': 'Exergy of the cold supply water directed to the mixing valve.'},
            {'label': 'Xc_mix', 'amount': -sv['Xc_mix'], 'desc': 'Exergy consumed during the mixing process to achieve the desired service hot water temperature.'},
            {'label': 'X_w_serv', 'amount': 0, 'desc': 'Exergy contained in the final service hot water supplied to the user.'},
            ]
            
        for item in items:
            item['group'] = key
        source = pd.DataFrame(items)
        sources.append(source)

    if sources:
        source = pd.concat(sources)
        return plot_waterfall_multi(source)
    return alt.Chart(pd.DataFrame({'x': [0], 'y': [0]})).mark_point()

# hot water system 엑서지 효율 등급 정의
E = 10; D = 15; C = 20; B = 25; A = 30; A_plus = 50;
grade_range_hot_water = [(0,E), (E,D), (D,C), (C,B), (B,A), (A,A_plus)]

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
        grade_ranges = grade_range_hot_water,
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
    HPB.COP = params['COP']
    HPB.dP = params['dP']
    HPB.T0 = params['T_0']
    HPB.T_a_ext_out = params['T_a_ext_out']
    HPB.T_r_ext = params['T_r_ext']
    HPB.T_r_tank = params['T_r_tank']
    HPB.T_w_tank = params['T_w_tank']
    HPB.T_w_serv = params['T_w_serv']
    HPB.T_w_sup = params['T_w_sup']
    HPB.dV_w_serv = params['dV_w_serv']
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
    SAGB.A_stc = params['A_stc']
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
    X_w_stc_out = SAGB.X_w_stc_out
    X_l = SAGB.X_l
    X_c_stc = SAGB.X_c_stc

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
    GSHPB.dV_f = params['dV_f']
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