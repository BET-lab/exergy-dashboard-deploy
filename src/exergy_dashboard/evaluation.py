import math
import copy
import streamlit as st


c_a	 = 1.005
rho_a =	1.2


def evaluate_parameters_cooling(sss, system_name):
    # Extract all inputs.
    params = {}
    for key, value in sss.items():
        if not key.startswith(system_name + ':'):
            continue

        key = key.split(':')[1]
        if key.startswith('T_'):
            value = value + 273.15
        params[key] = value

    # Evaluate parameters.
    if sss.systems[system_name]['type'] == 'ASHP':        
        T_0 = params['T_0']
        k = params['k']
        T_r_int_A = params['T_r_int_A']
        T_r_ext_A = params['T_r_ext_A']
        Q_r_int_A = params['Q_r_int_A']
        T_a_int_in = params['T_a_int_in']
        T_a_int_out = params['T_a_int_out']
        T_a_ext_out = params['T_a_ext_out']
        E_f_int = params['E_f_int']
        E_f_ext = params['E_f_ext']

        # Outdoor air
        T_a_ext_in = T_0

        # System COP
        cop_A = k * T_r_int_A / (T_r_ext_A - T_r_int_A)

        # System capacity - ASHP
        E_cmp_A = Q_r_int_A / cop_A    # kW, 압축기 전력
        Q_r_ext_A = Q_r_int_A + E_cmp_A    # kW, 실외기 배출열량

        # Air & Cooling water parameters
        V_int = Q_r_int_A / (c_a * rho_a * (T_a_int_in - T_a_int_out))
        V_ext = Q_r_ext_A / (c_a * rho_a * (T_a_ext_out - T_a_ext_in))
        m_int = V_int * rho_a
        m_ext = V_ext * rho_a

        ## Internal unit with evaporator
        X_r_int_A = - Q_r_int_A * (1 - T_0 / T_r_int_A) # 냉매에서 실내 공기에 전달한 엑서지
        X_a_int_out_A = c_a * m_int * ((T_a_int_out - T_0) - T_0 * math.log(T_a_int_out / T_0)) # 실외기 취출 공기 엑서지 
        X_a_int_in_A = c_a * m_int * ((T_a_int_in - T_0) - T_0 * math.log(T_a_int_in / T_0)) # 실외기 흡기 공기 엑서지

        Xin_int_A = E_f_int + X_r_int_A # 엑서지 인풋 (팬 투입 전력 + 냉매에서 실내 공기에 전달한 엑서지)
        Xout_int_A = X_a_int_out_A - X_a_int_in_A # 엑서지 아웃풋
        Xc_int_A = Xin_int_A - Xout_int_A # 엑서지 소비율

        ## Closed refrigerant loop system  
        X_r_ext_A = Q_r_ext_A * (1 - T_0 / T_r_ext_A) # 냉매에서 실외 공기에 전달한 엑서지
        X_r_int_A = - Q_r_int_A * (1 - T_0 / T_r_int_A) # 냉매에서 실내 공기에 전달한 엑서지

        Xin_r_A = E_cmp_A # 엑서지 인풋 (컴프레서 투입 전력)
        Xout_r_A = X_r_ext_A + X_r_int_A # 엑서지 아웃풋
        Xc_r_A = Xin_r_A - Xout_r_A # 엑서지 소비율

        ## External unit with condenser
        X_r_ext_A = Q_r_ext_A * (1 - T_0 / T_r_ext_A) # 냉매에서 실외 공기에 전달한 엑서지
        X_a_ext_out_A = c_a * m_ext * ((T_a_ext_out - T_0) - T_0 * math.log(T_a_ext_out / T_0)) # 실외기 취출 공기 엑서지
        X_a_ext_in_A = c_a * m_ext * ((T_a_ext_in - T_0) - T_0 * math.log(T_a_ext_in / T_0)) # 실외기 흡기 공기 엑서지 (외기)

        Xin_ext_A = E_f_ext + X_r_ext_A # 엑서지 인풋 (팬 투입 전력 + 냉매에서 실외 공기에 전달한 엑서지)
        Xout_ext_A = X_a_ext_out_A - X_a_ext_in_A # 엑서지 아웃풋
        Xc_ext_A = Xin_ext_A - Xout_ext_A # 엑서지 소비율

        ## Total
        Xin_A = E_cmp_A + E_f_int + E_f_ext # 총 엑서지 인풋 (컴프레서 + 실내팬 + 실외팬 전력)
        Xout_A = X_a_int_out_A - X_a_int_in_A # 총 엑서지 아웃풋
        Xc_A = Xin_A - Xout_A # 총 엑서지 소비율
    elif sss.systems[system_name]['type'] == 'GSHP':
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
        # T_a_ext_in = params['T_a_ext_in']
        # T_a_ext_out = params['T_a_ext_out']

        # Outdoor air
        T_ext_in = T_0

        # System COP
        cop_G = k * T_r_int_G / (T_r_ext_G - T_r_int_G)

        # System capacity - GSHP
        E_cmp_G = Q_r_int_G / cop_G    # kW, 압축기 전력
        Q_r_ext_G = Q_r_int_G + E_cmp_G    # kW, 실외기 배출열량
        Q_g = Q_r_ext_G + E_pmp_G    # kW, 토양 열교환량

        # # Air & Cooling water parameters
        V_int = Q_r_int_G / (c_a * rho_a * (T_a_int_in - T_a_int_out))
        # V_ext = Q_r_ext_G / (c_a * rho_a * (T_a_ext_out - T_a_ext_in))
        m_int = V_int * rho_a
        # m_ext = V_ext * rho_a

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

    sss.systems[system_name]['variables'] = {
        k: v for k, v in locals().items()
        if k not in ('sss', 'system_name', 'params', 'key', 'value')
    }

    return {
        k: v for k, v in locals().items()
        if k not in ('sss', 'system_name', 'params', 'key', 'value')
    }

