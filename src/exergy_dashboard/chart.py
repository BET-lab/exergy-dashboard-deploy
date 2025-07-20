import altair as alt
import pandas as pd

# Colors from streamlit theme.
COLORS = [
    '#69c7ba',
    '#a4f3bd',
    '#ff6a6a',
    '#ffab4c',
    '#a8d9ff',
    '#ffc4c4',
    '#4c95d9',
    '#ffde96',
    '#9878d2',
    '#e1e5ec',
] * 50


def plot_waterfall_multi(source):
    # Define frequently referenced fields
    amount = alt.datum.amount
    label = alt.datum.label
    window_lead_label = alt.datum.window_lead_label
    window_sum_amount = alt.datum.window_sum_amount

    # Define start and end labels
    group_starts = source.groupby("group").first().reset_index()[["group", "label"]].rename(columns={"label": "start_label"})
    group_ends = source.groupby("group").last().reset_index()[["group", "label"]].rename(columns={"label": "end_label"})
    
    # 기존 source에 merge
    source = source.merge(group_starts, on="group")
    source = source.merge(group_ends, on="group")

    # Define frequently referenced/long expressions
    calc_prev_sum = alt.expr.if_(label == alt.datum.end_label, 0, window_sum_amount - amount)
    calc_amount = alt.expr.if_(label == alt.datum.end_label, window_sum_amount, amount)

    calc_text_amount = (
        alt.expr.if_(
            (label != alt.datum.start_label) & (label != alt.datum.end_label) & (calc_amount > 0),
            "+",
            ""
        ) + calc_amount
    )

    bar_size = 50
    fs = bar_size / 3.5
    
    # The "base_chart" defines the transform_window, transform_calculate, and X axis
    base_chart = alt.Chart(source).encode(
        x=alt.X(
        "label:O",
        axis=alt.Axis(
            title="",
            labelAngle=0,
            labelFontSize=fs,   # x축 틱 레이블 폰트 크기
            labelColor="black"  # x축 틱 레이블 컬러
            ),
            sort=None
        ),
        y=alt.Y(
            "calc_prev_sum:Q",
            title="Exergy [W]",
            axis=alt.Axis(
                labelFontSize=fs,   # y축 틱 레이블 폰트 크기
                labelColor="black",  # y축 틱 레이블 컬러
                titleFontSize=fs * 1.2,  # y축 제목 폰트 크기
                titleColor="black",  # y축 제목 컬러
            )
        )
    )

    bar = base_chart.mark_bar(size=bar_size).encode(
        y2=alt.Y2("window_sum_amount:Q"),
        color=alt.Color('group:N').legend(None).sort(None),
        tooltip=[
            alt.Tooltip("desc:N", title="Description"),
        ],
    )

    # 툴팁 영역 확장용 투명 rect (전체 y범위)
    max_y = float(source['amount'].sum()) if not source.empty else 1.0
    hover_rect = alt.Chart(source).mark_rect(opacity=0).encode(
        x=alt.X("label:O", sort=None),
        color=alt.value('rgba(0,0,0,0)'),
        tooltip=[
            alt.Tooltip("desc:N", title="Description"),
        ],
    )

    # The "rule" chart is for the horizontal lines that connect the bars
    rule = base_chart.mark_rule(xOffset=-bar_size / 2, x2Offset=bar_size / 2, strokeWidth=0.5, tooltip=None).encode(
        y="window_sum_amount:Q",
        x2="calc_lead",
    )

    # Add values as text
    text_values_top = base_chart.mark_text(
        baseline="bottom", dy=-4, fontSize=fs, tooltip=None
    ).encode(
        text=alt.Text(
            "calc_amount:Q",
            format="~s",),
        y="calc_top:Q"
    ).transform_calculate(
        calc_amount_abs="abs(datum.calc_amount)",
        calc_amount_fmt="""
            datum.calc_amount_abs >= 100 ? format(datum.calc_amount_abs, ".0f") :
            datum.calc_amount_abs >= 10 ? format(datum.calc_amount_abs, ".1f") :
            format(datum.calc_amount_abs, ".2f")
        """
    ).encode(
        text=alt.Text("calc_amount_fmt:N")
    )
    # text_pos_values_top_of_bar = base_chart.mark_text(baseline="bottom", dy=-4, fontSize=fs, tooltip=None).encode(
    #     text=alt.Text("calc_sum_inc:N"),
    #     y="calc_sum_inc:Q",
    # )
    # text_neg_values_bot_of_bar = base_chart.mark_text(baseline="top", dy=4, fontSize=fs, tooltip=None).encode(
    #     text=alt.Text("calc_sum_dec:N"),
    #     y="calc_sum_dec:Q",
    # )
    # text_bar_values_mid_of_bar = base_chart.mark_text(baseline="middle", fontSize=fs, tooltip=None).encode(
    #     text=alt.Text("calc_text_amount:N"),
    #     y="calc_center:Q",
    #     color=alt.value("white"),
    # )

    chart = alt.layer( # Altair에서 여러 개의 차트(마크)를 하나의 시각화로 "겹쳐서" 보여주는 함수입니다
        bar,
        hover_rect,  # bar 위에 투명 rect를 겹침
        rule,
        text_values_top,
        # text_pos_values_top_of_bar,
        # text_neg_values_bot_of_bar,
        # text_bar_values_mid_of_bar
    ).properties(
        # width=alt.Step(bar_size + 50),
        width='container',
        height=190
    ).facet(
        facet=alt.Facet("group").title('').sort([]),
        columns=1,
    ).configure_header(
        labelFontSize=fs*1.2,
        labelColor='black',
    ).transform_window(
        window_sum_amount="sum(amount)",
        window_lead_label="lead(label)",
        groupby=["group"],
    ).transform_calculate(
        calc_lead=alt.expr.if_((window_lead_label == None), label, window_lead_label),
        calc_prev_sum=calc_prev_sum,
        calc_amount=calc_amount,
        calc_text_amount=alt.expr.format(calc_text_amount, ".2f"),
        calc_center=(window_sum_amount + calc_prev_sum) / 2,
        calc_top=alt.expr.if_(calc_amount > 0, window_sum_amount, calc_prev_sum),  # 새 필드 추가
        calc_sum_dec=alt.expr.if_(window_sum_amount < calc_prev_sum, alt.expr.format(window_sum_amount, ".2f"), None),
        calc_sum_inc=alt.expr.if_(
            window_sum_amount > calc_prev_sum
            | (alt.datum.index != alt.datum.length - 1),
            alt.expr.format(window_sum_amount, ".2f"),
            None
        ),  
    ).resolve_scale(
        x="independent"
    )
    
    return chart


def create_efficiency_grade_chart(
    cases=None,
    margin=0.5,
    bottom_height=20,
    top_height=40,
    show_range=False,
    text_rotation=0,
    text_dy=-12,
    grade_unit=10,
):
    """
    에너지 효율 등급 시각화 생성
    
    Parameters:
    -----------
    cases : list of dict, optional
        케이스 데이터 [{'name': '가스보일러', 'efficiency': 4.5, 'range': '4-6'}, ...]
    margin : float, default 0.5
        인접한 등급 간 마진
    bottom_height : int, default 20
        아래쪽 진한색 박스의 높이
    top_height : int, default 40
        위쪽 연한색 박스의 높이
    show_range : bool, default True
        range 텍스트 표시 여부
    text_rotation : int, default 0
        텍스트 회전 각도 (0 또는 90)
    
    Returns:
    --------
    alt.Chart
        Altair 차트 객체
    """
    
    # 효율 등급 정의
    colors = [
        '#E74C3C',
        '#FF8C00',
        '#FFD700',
        '#90EE90',
        '#32CD32',
        '#228B22'
    ]

    grades = []
    for i, label in zip(range(6), ['F', 'D', 'C', 'B', 'A', 'A+']):
        grades.append({
            'grade': label,
            'start': i * grade_unit,
            'end': (i + 1) * grade_unit,
            'color': colors[i]
        })
    
    # 마진을 적용한 등급 데이터 생성 (박스 이동 방식)
    grade_data_bottom = []  # 아래쪽 진한색 박스
    grade_data_top = []     # 위쪽 연한색 박스
    
    for i, grade in enumerate(grades):
        # 첫 번째 등급은 그대로, 이후 등급들은 마진만큼 이동
        offset = margin * i
        
        # 아래쪽 진한색 박스 (등급 텍스트용)
        grade_data_bottom.append({
            'grade': grade['grade'],
            'start': grade['start'] + offset,
            'end': grade['end'] + offset,
            'real_start': grade['start'],
            'real_end': grade['end'],
            'color': grade['color'],
            'y': 0,
            'height': bottom_height,
            'original_start': grade['start']
        })
        
        # 위쪽 연한색 박스 (알파 적용)
        grade_data_top.append({
            'grade': grade['grade'],
            'start': grade['start'] + offset,
            'end': grade['end'] + offset,
            'real_start': grade['start'],
            'real_end': grade['end'],
            'color': grade['color'],
            'y': bottom_height - 0.5,  # 아래쪽 박스 위에 위치
            'height': top_height,
            'original_start': grade['start']
        })
    
    grade_df_bottom = pd.DataFrame(grade_data_bottom)
    grade_df_top = pd.DataFrame(grade_data_top)
    
    # 포인트 위치 계산 (위쪽 박스의 윗면과 정확히 일치)
    point_y = top_height  # 위쪽 박스의 윗면 위치
    
    # 실제 등급 시작점들 (x축 틱 위치용)
    actual_starts = [grade['start'] for grade in grade_data_bottom]
    labels= [grade['real_start'] for grade in grade_data_bottom]
    print(labels)

    # 전체 차트 높이 계산 (range 텍스트를 위한 여백 추가)
    chart_height = point_y + 0  # 포인트 위치 + 텍스트 여백 (80에서 30으로 줄임)
    
    # 아래쪽 진한색 박스 차트
    bottom_chart = alt.Chart(grade_df_bottom).mark_rect(
        stroke='white',
        strokeWidth=1
    ).encode(
        x=alt.X('start:Q', 
                title='엑서지 효율 [%] = 사용된 엑서지 / 투입된 엑서지',
                axis=alt.Axis(
                    values=actual_starts,
                    labelExpr=f"datum.value == {actual_starts[0]} ? '{labels[0]}' : datum.value == {actual_starts[1]} ? '{labels[1]}' : datum.value == {actual_starts[2]} ? '{labels[2]}' : datum.value == {actual_starts[3]} ? '{labels[3]}' : datum.value == {actual_starts[4]} ? '{labels[4]}' : datum.value == {actual_starts[5]} ? '{labels[5]}' : ''",
                    grid=False,
                    domain=False,
                    ticks=False
                )),
        x2=alt.X2('end:Q'),
        y=alt.Y('y:Q', 
                scale=alt.Scale(domain=[0, chart_height]),
                axis=None),
        y2=alt.Y2('height:Q'),
        color=alt.Color('color:N', scale=None),
        tooltip=[
            alt.Tooltip('grade:N', title='Grade'),
            alt.Tooltip('real_start:Q', title='Start'),
            alt.Tooltip('real_end:Q', title='End')
        ]
    ).properties(
        width=600,
        height=chart_height
    )
    
    # 위쪽 연한색 박스 차트 (알파 적용)
    top_chart = alt.Chart(grade_df_top).mark_rect(
        stroke='white',
        strokeWidth=1,
        opacity=0.3  # 알파 적용
    ).encode(
        x=alt.X('start:Q'),
        x2=alt.X2('end:Q'),
        y=alt.Y('y:Q'),
        y2=alt.Y2('height:Q'),
        color=alt.Color('color:N', scale=None),
        tooltip=[
            alt.Tooltip('grade:N', title='Grade'),
            alt.Tooltip('real_start:Q', title='Start'),
            alt.Tooltip('real_end:Q', title='End')
        ]
    )
    
    # 등급 레이블 추가 (아래쪽 박스에)
    grade_labels = grade_df_bottom.copy()
    grade_labels['x_center'] = (grade_labels['start'] + grade_labels['end']) / 2
    grade_labels['y_center'] = grade_labels['y'] + grade_labels['height'] / 2
    
    label_chart = alt.Chart(grade_labels).mark_text(
        fontSize=16,
        fontWeight='bold',
        color='white'
    ).encode(
        x=alt.X('x_center:Q'),
        y=alt.Y('y_center:Q'),
        text=alt.Text('grade:N')
    )
    
    # 케이스 데이터가 있으면 점과 텍스트 추가
    if cases:
        # 케이스 데이터를 마진을 고려해서 조정
        adjusted_cases = []
        for case in cases:
            efficiency = case['efficiency']
            # 어느 등급에 속하는지 찾기
            grade_index = 0
            for i, grade in enumerate(grades):
                if grade['start'] <= efficiency < grade['end']:
                    grade_index = i
                    break
                elif efficiency >= grades[-1]['end']:  # A+ 등급 이상
                    grade_index = len(grades) - 1
                    break
            
            # 해당 등급의 마진 offset 적용
            offset = margin * grade_index
            adjusted_case = case.copy()
            adjusted_case['efficiency'] = efficiency + offset
            adjusted_case['real_efficiency'] = efficiency
            adjusted_case['y'] = point_y  # 위쪽 박스의 윗면과 정확히 일치
            adjusted_cases.append(adjusted_case)
        
        case_df = pd.DataFrame(adjusted_cases)
        
        # 레이어 순서: point, text, range (y축 낮은 순서대로 추가, 그려질 때는 높은 순서)
        layers = [bottom_chart, top_chart, label_chart]
        
        # 3. 케이스 점 차트 (가장 아래) - 위쪽 박스의 윗면에 정확히 위치
        case_points = alt.Chart(case_df).mark_circle(
            size=90,
            color='black',
            stroke='white',
            strokeWidth=2
        ).encode(
            x=alt.X('efficiency:Q'),
            y=alt.Y('y:Q'),
            tooltip=[
                alt.Tooltip('name:N', title='Name'),
                alt.Tooltip('real_efficiency:Q', title='Efficiency')
            ]
        )
        layers.append(case_points)
        
        # 2. 케이스 이름 텍스트 (포인트 위) - 회전 옵션 적용
        text_angle = text_rotation
        case_names = alt.Chart(case_df).mark_text(
            fontSize=9,
            dx=text_dy,  # 회전 시 위치 조정
            align='left',
            angle=text_angle
        ).encode(
            x=alt.X('efficiency:Q'),
            y=alt.Y('y:Q'),
            text=alt.Text('name:N')
        )
        layers.append(case_names)
        
        # 1. 케이스 range 텍스트 (가장 위에) - show_range가 True일 때만
        if show_range:
            case_texts = alt.Chart(case_df).mark_text(
                fontSize=10,
                fontWeight='normal',
                color='black',
                # stroke='white',
                # strokeWidth=0.5,
                dy=15,  # 포인트 위로 15px 이동
                align='center'
            ).encode(
                x=alt.X('efficiency:Q'),
                y=alt.Y('y:Q'),
                text=alt.Text('real_efficiency:N')
            )
            layers.append(case_texts)
        
        # 모든 레이어 결합
        chart = alt.layer(*layers)
    else:
        # 케이스 없이 등급만 표시
        chart = alt.layer(bottom_chart, top_chart, label_chart)
    
    # view의 외각선 제거
    chart = chart.configure_view(stroke=None).resolve_scale(color='independent')
    
    return chart