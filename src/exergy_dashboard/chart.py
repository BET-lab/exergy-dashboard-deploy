import altair as alt

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
