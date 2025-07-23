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
        spacing=50  # facet 간 간격 조절 (기본값은 20 정도)
    ).configure_header(
        labelFontSize=fs*1.2+1,
        labelFontWeight=600,
        labelColor='black',
        labelAnchor='middle',
        labelPadding=2,
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
    cases,
    margin=0.5,
    bottom_height=20,
    top_height=40,
    show_range=False,
    text_rotation=0,
    text_dx=12,
    text_dy=-12,
    grade_unit=10,
    font_size=16,
    grade_ranges = None,
):
    """
    에너지 효율 등급 시각화 생성
    
    Parameters:
    -----------
    cases : list of dict
        케이스 데이터 [{'name': '가스보일러', 'efficiency': 4.5}, ...]
    margin : float, default 0.5
        인접한 등급 간 마진
    bottom_height : int, default 20
        아래쪽 알파 박스의 높이
    top_height : int, default 40
        위쪽 진한색 박스의 높이
    show_range : bool, default False
        효율값 텍스트 표시 여부 (현재 비활성화됨)
    text_rotation : int, default 0
        텍스트 회전 각도 (0 또는 90)
    text_dx : int, default 12
        텍스트 x축 오프셋
    text_dy : int, default -12
        텍스트 y축 오프셋
    grade_unit : int, default 10
        기본 등급 단위 (grade_ranges가 None일 때만 사용)
    font_size : int, default 16
        폰트 크기
    grade_ranges : list of tuple, optional
        각 등급의 (start, end) 범위 리스트. 예: [(0,10), (10,20), (20,30), (30,40), (40,50), (50,60)]
        제공되면 grade_unit은 무시됨
    
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
    
    # 텍스트용 진한 색상 (시인성 개선)
    text_colors = [
        '#E72D19',
        '#FF8C00',
        '#F0CA00',
        '#00E700',
        '#25DA25',
        '#00A752'
    ]

    grades = []
    if grade_ranges is not None:
        # 직접 지정된 범위 사용
        for i, (label, (start, end)) in enumerate(zip(['E', 'D', 'C', 'B', 'A', 'A+'], grade_ranges)):
            grades.append({
                'grade': label,
                'start': start,
                'end': end,
                'color': colors[i]
            })
    else:
        # grade_unit을 사용한 기본 범위
        for i, label in zip(range(6), ['E', 'D', 'C', 'B', 'A', 'A+']):
            grades.append({
                'grade': label,
                'start': i * grade_unit,
                'end': (i + 1) * grade_unit,
                'color': colors[i]
            })
    
    # 마진을 적용한 등급 데이터 생성 (박스 이동 방식)
    grade_data_bottom = []  # 아래쪽 알파 박스
    grade_data_top = []     # 위쪽 진한색 박스
    
    for i, grade in enumerate(grades):
        # 첫 번째 등급은 그대로, 이후 등급들은 마진만큼 이동
        offset = margin * i
        
        # 아래쪽 알파 박스
        grade_data_bottom.append({
            'grade': grade['grade'],
            'start': grade['start'] + offset,
            'end': grade['end'] + offset,
            'real_start': grade['start'],
            'real_end': grade['end'],
            'color': grade['color'],
            'y': 0,
            'height': bottom_height + 1,
            'original_start': grade['start']
        })
        
        # 위쪽 진한색 박스 (등급 텍스트용)
        grade_data_top.append({
            'grade': grade['grade'],
            'start': grade['start'] + offset,
            'end': grade['end'] + offset,
            'real_start': grade['start'],
            'real_end': grade['end'],
            'color': grade['color'],
            'y': bottom_height,  # 아래쪽 박스 위에 위치
            'height': top_height,
            'original_start': grade['start']
        })
    
    # DataFrame 생성 시 명시적으로 데이터 타입 지정 및 JSON 직렬화 안정성 확보
    grade_df_bottom = pd.DataFrame(grade_data_bottom).astype({
        'grade': 'str',
        'start': 'float64',
        'end': 'float64',
        'real_start': 'int',
        'real_end': 'int',
        'color': 'str',
        'y': 'int',
        'height': 'int',
        'original_start': 'int'
    }).copy()  # 명시적 복사로 참조 문제 방지
    
    grade_df_top = pd.DataFrame(grade_data_top).astype({
        'grade': 'str',
        'start': 'float64',
        'end': 'float64',
        'real_start': 'int',
        'real_end': 'int',
        'color': 'str',
        'y': 'int',
        'height': 'int',
        'original_start': 'int'
    }).copy()  # 명시적 복사로 참조 문제 방지
    
    # 포인트 위치 계산 (y=0 위치)
    point_y = 0  # y=0 위치
    
    # 실제 등급 시작점들 (x축 틱 위치용) - 마진의 중간에 위치하도록 조정
    actual_starts = [grade['start'] - 0.5 * margin for grade in grade_data_bottom]
    labels = [int(grade['real_start']) for grade in grade_data_bottom]
    
    # 마지막 박스의 오른쪽 끝 값 추가
    actual_starts.append(grade_data_bottom[-1]['end'] - 0.5 * margin)
    labels.append(int(grade_data_bottom[-1]['real_end']))
    
    # labelExpr을 미리 생성하여 안정성 확보
    label_conditions = []
    for i, (start_val, label_val) in enumerate(zip(actual_starts, labels)):
        label_conditions.append(f"datum.value == {start_val} ? '{label_val}'")
    label_expr = " : ".join(label_conditions) + " : ''"

    # 전체 차트 높이 계산
    chart_height = top_height  # 전체 박스 높이
    
    # 아래쪽 알파 박스 차트
    bottom_chart = alt.Chart(grade_df_bottom).mark_rect(
        # stroke='white',
        # strokeWidth=1,
        opacity=0.3  # 알파 적용
    ).encode(
        x=alt.X('start:Q'),
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
        width='container',
        # height=chart_height
    )
    
    # 위쪽 진한색 박스 차트
    top_chart = alt.Chart(grade_df_top).mark_rect(
        # stroke='white',
        # strokeWidth=1
    ).encode(
        x=alt.X('start:Q', 
                title='',  # 빈 제목으로 설정
                scale=alt.Scale(
                    domain=[actual_starts[0] - margin/2, actual_starts[-1] + margin/2],
                    # range=[{'expr': '- width * 0.03'}, {'expr': 'width - 20'}]  # 좌우 20px 여백으로 균등하게, 사전 정의된 width 사용
                    range=[{'expr': '- width * 0.1'}, {'expr': 'width + 30'}]  # 좌우 20px 여백으로 균등하게, 사전 정의된 width 사용
                ),
                axis=alt.Axis(
                    values=actual_starts,
                    labelExpr=label_expr,
                    grid=False,
                    domain=False,
                    ticks=False,
                    labelFontSize=font_size - 2,
                    labelColor='black',
                    labelPadding=5,  # 틱 라벨과 축 사이의 거리 줄임
                )),
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
    
    # 등급 레이블 추가 (위쪽 박스에) - 데이터 타입 안정성 확보
    grade_labels = grade_df_top.copy()
    grade_labels['x_center'] = (grade_labels['start'] + grade_labels['end']) / 2
    grade_labels['y_center'] = (grade_labels['y'] + grade_labels['height']) / 2
    grade_labels = grade_labels.astype({
        'x_center': 'float64',
        'y_center': 'float64'
    }).copy()  # 이중 복사로 데이터 안정성 확보
    
    label_chart = alt.Chart(grade_labels).mark_text(
        fontSize=font_size * 1.3,
        fontWeight='bold',
        color='white'
    ).encode(
        x=alt.X('x_center:Q'),
        y=alt.Y('y_center:Q'),
        text=alt.Text('grade:N'),
        tooltip=[
            alt.Tooltip('grade:N', title='Grade'),
            alt.Tooltip('real_start:Q', title='Start'),
            alt.Tooltip('real_end:Q', title='End')
        ]
    )
    
    # x축 제목을 별도 텍스트로 추가 (dx 오프셋 적용 가능) - 데이터 타입 지정
    x_center = (actual_starts[0] + actual_starts[-1]) / 2
    title_data = pd.DataFrame([{
        'x': x_center,
        'y': -15,  # x축 아래쪽에 위치
        'title': '엑서지 효율 [%] = 사용된 엑서지 / 투입된 엑서지'
    }]).astype({
        'x': 'float64',
        'y': 'int',
        'title': 'str'
    })
    
    title_chart = alt.Chart(title_data).mark_text(
        fontSize=font_size,
        color='black',
        dx=0,  # 원하는 dx 오프셋
        dy=10,
        align='center'
    ).encode(
        x=alt.X('x:Q'),
        y=alt.Y('y:Q'),
        text=alt.Text('title:N')
    )
    
    # 케이스 데이터를 마진을 고려해서 조정
    adjusted_cases = []
    for case in cases:
        efficiency = case['efficiency']
        # 어느 등급에 속하는지 찾기
        grade_index = 0
        grade_color = colors[0]  # 기본값
        text_color = text_colors[0]  # 텍스트용 기본값
        for i, grade in enumerate(grades):
            if grade['start'] <= efficiency < grade['end']:
                grade_index = i
                grade_color = grade['color']
                text_color = text_colors[i]
                break
            elif efficiency >= grades[-1]['end']:  # A+ 등급 이상
                grade_index = len(grades) - 1
                grade_color = grades[-1]['color']
                text_color = text_colors[-1]
                break
        
        # 해당 등급의 마진 offset 적용
        offset = margin * grade_index
        adjusted_case = case.copy()
        adjusted_case['efficiency'] = efficiency + offset
        adjusted_case['real_efficiency'] = efficiency
        adjusted_case['y'] = point_y  # 위쪽 박스의 윗면과 정확히 일치
        adjusted_case['y2'] = bottom_height
        adjusted_case['grade_color'] = grade_color  # 등급 색상 추가
        adjusted_case['text_color'] = text_color  # 텍스트용 진한 색상 추가
        adjusted_cases.append(adjusted_case)
    
    # case_df도 명시적 타입 지정으로 안정성 향상
    case_df = pd.DataFrame(adjusted_cases)
    if not case_df.empty:
        case_df = case_df.astype({
            'name': 'str',
            'efficiency': 'float64',
            'real_efficiency': 'float64',
            'y': 'int',
            'y2': 'int',
            'grade_color': 'str',
            'text_color': 'str'
        }).copy()  # 명시적 복사로 참조 문제 방지
    
    # 레이어 순서: alpha box (bottom), grade box (top), label (top), title
    layers = [bottom_chart, top_chart, label_chart, title_chart]
    # 포인트에서 알파 박스 높이까지의 점선 수직선
    case_lines = alt.Chart(case_df).mark_rule(
        strokeDash=[2, 2],  # 점선
        strokeWidth=3.5
    ).encode(
        x=alt.X('efficiency:Q'),
        y=alt.Y('y:Q'),
        y2=alt.Y2('y2:Q'),
        color=alt.Color('grade_color:N', scale=None),
        tooltip=[
            alt.Tooltip('name:N', title='Name'),
            alt.Tooltip('real_efficiency:Q', title='Efficiency', format='.1f')
        ]
    )
    layers.append(case_lines)
            
    # 3. 케이스 점 차트 (가장 아래) - 위쪽 박스의 윗면에 정확히 위치
    case_points = alt.Chart(case_df).mark_circle(
        size=150,
        stroke='white',
        strokeWidth=2,
        opacity=1,
    ).encode(
        x=alt.X('efficiency:Q'),
        y=alt.Y('y:Q'),
        color=alt.Color('grade_color:N', scale=None),
        tooltip=[
            alt.Tooltip('name:N', title='Name'),
            alt.Tooltip('real_efficiency:Q', title='Efficiency', format='.1f')
        ]
    )
    layers.append(case_points)
    
    # 2. 케이스 이름 텍스트 (포인트 위) - 회전 옵션 적용
    text_angle = text_rotation
    case_names = alt.Chart(case_df).mark_text(
        fontSize=font_size,
        dx=text_dx,  # 회전 시 위치 조정
        dy=text_dy,
        align='left',
        angle=text_angle
    ).encode(
        x=alt.X('efficiency:Q'),
        y=alt.Y('y:Q'),
        text=alt.Text('name:N'),
        color=alt.Color('text_color:N', scale=None),
        tooltip=[
            alt.Tooltip('name:N', title='Name'),
            alt.Tooltip('real_efficiency:Q', title='Efficiency', format='.1f')
        ]
    )
    layers.append(case_names)
    
    # 모든 레이어 결합
    chart = alt.layer(*layers)

    # view의 외각선 제거 및 안정적인 렌더링을 위한 설정
    chart = chart.configure_view(stroke=None).resolve_scale(color='independent')
    
    # 차트에 고유 이름 설정 (React 키 역할)
    case_names_str = "_".join([case.get('name', '') for case in cases])
    chart_name = f"efficiency_grade_{hash(case_names_str) % 10000}"
    chart = chart.properties(
        width='container',
        name=chart_name  # 고유 식별자 추가
    )


    return chart