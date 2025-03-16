# 각 시스템의 파라미터를 설정하세요.
COOLING_ASGP = {
    'display': {
        'title': 'Air Source Heat Pump',
        'icon': ':snowflake:',
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
        'T_a_int_in': {
            'explanation': {'EN': 'Internal Unit Inlet Air Temperature', 'KR': '실내기로 들어가는 공기 온도'},
            'latex': r'$T_{a,int,in}$',
            'default': 24.0,
            'range': [-50, 50],
            'unit': '℃',
            'step': 0.5,
            'category': 'indoor',
        },
        'T_a_int_out': {
            'explanation': {'EN': 'Internal Unit Outlet Air Temperature', 'KR': '실내기에서 나가는 공기 온도'},
            'latex': r'$T_{a,int,out}$',
            'default': 14.0,
            'range': [-60, 'T_a_int_in-0.5'],
            'unit': '℃',
            'step': 0.5,
            'category': 'indoor',
        },
        'T_a_ext_out': {
            'explanation': {'EN': 'External Unit Outlet Air Temperature', 'KR': '실외기에서 나가는 공기 온도'},
            'latex': r'$T_{a,ext,out}$',
            'default': 42.0,
            'range': ['T_0+0.5', 80],
            'unit': '℃',
            'step': 0.5,
            'category': 'outdoor',
        },
        'T_r_int_A': {
            'explanation': {'EN': 'Internal Unit Refrigerant Temperature', 'KR': '실내기 측 냉매 온도'},
            'latex': r'$T_{r,int,A}$',
            'default': 9.0,
            'range': [-80, 'T_a_int_out-0.5'],
            'unit': '℃',
            'step': 0.5,
            'category': 'refrigerant',
        },
        'T_r_ext_A': {
            'explanation': {'EN': 'External Unit Refrigerant Temperature', 'KR': '실외기 측 냉매 온도'},
            'latex': r'$T_{r,ext,A}$',
            'default': 47.0,
            'range': ['T_a_ext_out+2', 100],
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
        'E_f_ext': {
            'explanation': {'EN': 'External Unit Fan Power', 'KR': '실외기 측 팬 전력'},
            'latex': r'$E_{f,ext}$',
            'default': 0.29,
            'range': [0, 1],
            'unit': 'kW',
            'step': 0.01,
            'category': 'power',
        },
        'Q_r_int_A': {
            'explanation': {'EN': 'Internal Unit Heat Absorption', 'KR': '실내기 실내 흡열량'},
            'latex': r'$Q_{r,int,A}$',
            'default': 15.3,
            'range': [0, 30],
            'unit': 'kW',
            'step': 0.1,
            'category': 'capacity',
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

# 정의된 시스템 케이스를 딕셔너리로 정의하세요.
# 1단계 계층은 시스템 종류(COOLING, HEATING, HOT WATER).
# 2단계 계층은 시스템 종류별 시스템 케이스.
SYSTEM_CASE = {
    'COOLING': {
        'ASHP': COOLING_ASGP,
        'GSHP': COOLING_GSHP,
    },
    'HEATING': {
    },
    'HOT WATER': {
      
    },
}
