import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd

import dartwork_mpl as dm


COLORS = [
    '#4c95d9',
    '#a8d9ff',
    '#ff6a6a',
    '#ffc4c4',
    '#69c7ba',
    '#a4f3bd',
    '#ffab4c',
    '#ffde96',
    '#9878d2',
    '#e1e5ec',
] * 50


def plot_waterfall_cooling_ashp(
    Xin_A,
    Xc_int_A,
    Xc_r_A,
    Xc_ext_A,
    X_a_ext_out_A,
    Xout_A,
    n,
    name,
):
    fig, ax = plt.subplots(figsize=(dm.cm2in(8), dm.cm2in(5)))

    # ASHP plot
    labels_ashp = ['Input', r'$X_{c,int}$', r'$X_{c,ref}$', r'$X_{c,ext}$', r'$X_{ext,out}$', 'Output']
    values_ashp = [Xin_A, -Xc_int_A, -Xc_r_A, -Xc_ext_A, -X_a_ext_out_A, Xout_A]
    x_ashp = np.arange(len(labels_ashp))
    cumulative_values_ashp = np.cumsum(values_ashp)

    # Common settings
    bar_width = 0.4
    y_max = np.max(values_ashp) * 1.1
    x_padding = 0.4
    annotation_size = dm.fs(-0.5)
    line_thickness = 0.1
    text_padding = 0.04

    # Function to draw connecting lines
    def draw_waterfall_lines(ax, x, cumulative_values, line_thickness):
        for i in range(1, len(x)):
            start = cumulative_values[i-1]
            end = cumulative_values[i]
            ax.plot([x[i-1]-bar_width/2, x[i]+bar_width/2], [start, start], color='dm.gray6', linestyle='-', linewidth=line_thickness)

    # Plot bars for ASHP
    for i in range(len(x_ashp)):
        if i == 0 or i == len(x_ashp) - 1:
            ax.bar(x_ashp[i], values_ashp[i], bar_width, color=COLORS[n])
        else:
            ax.bar(x_ashp[i], values_ashp[i], bar_width, bottom=cumulative_values_ashp[i-1], color=COLORS[n])

    # Draw connecting lines for ASHP
    draw_waterfall_lines(ax, x_ashp, cumulative_values_ashp, line_thickness)

    # Axis settings
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.tick_params(axis='y', which='both', left=True, right=False)
    ax.set_yticks([])
    ax.set_ylim(0, y_max)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    # Set x-axis labels and limits
    ax.set_xticks(x_ashp)
    ax.set_xticklabels(labels_ashp, ha='center', fontsize=dm.fs(0.3))
    ax.set_xlim(-x_padding, len(labels_ashp) - 1 + x_padding)

    # Add bar values as text
    for i, value in enumerate(values_ashp):
        if i == 0 or i == len(values_ashp) - 1:
            height = value
            va = 'bottom'
            y_pos = height + text_padding
        else:
            height = cumulative_values_ashp[i]
            va = 'top'
            y_pos = height - text_padding
        
        sign = '-' if value < 0 else ''
        text_value = f'{abs(value):.1f}'
        
        # Combine sign and value, but add a small space between them
        full_text = f'{sign}{text_value}' if sign else text_value
        
        # Add the full text, centered on the bar
        ax.text(i, y_pos, full_text, ha='center', va=va, fontsize=dm.fs(0), weight='normal')

    # Add title for ASHP
    ax.set_title(f'{name}', fontsize=dm.fs(0.5))

    dm.simple_layout(fig, margins=(0.1,0.1,0.1,0.1), bbox=(0, 1, 0, 1), verbose=False)
    # fig_name = 'ASHP_exergy_distribution_waterfall_paper'
    # plt.savefig(save_dir + fig_name + '.png', dpi=600, transparent=True)
    # dm.util.save_and_show(fig, size=600)

    return fig


def plot_waterfall_cooling_gshp(
    Xin_G,
    X_g,
    Xc_int_G,
    Xc_r_G,
    Xc_GHE,
    Xout_G,
    n,
    name,
):
    fig, ax = plt.subplots(figsize=(dm.cm2in(8), dm.cm2in(5)))

    print(f'{Xin_G=}, {X_g=}, {Xc_int_G=}, {Xc_r_G=}, {Xc_GHE=}, {Xout_G=}')

    # ASHP plot
    labels_gshp = ['Input', r'$X_{c,int}$', r'$X_{c,ref}$', r'$X_{c,GHE}$', 'Output']
    values_gshp = [Xin_G, -Xc_int_G, -Xc_r_G, -Xc_GHE, Xout_G]
    x_ashp = np.arange(len(labels_gshp))
    cumulative_values_ashp = np.cumsum(values_gshp)

    # Common settings
    bar_width = 0.4
    y_max = np.max(values_gshp) * 1.1
    x_padding = 0.4
    annotation_size = dm.fs(-0.5)
    line_thickness = 0.1
    text_padding = 0.04

    # Function to draw connecting lines
    def draw_waterfall_lines(ax, x, cumulative_values, line_thickness):
        for i in range(1, len(x)):
            start = cumulative_values[i-1]
            end = cumulative_values[i]
            ax.plot([x[i-1]-bar_width/2, x[i]+bar_width/2], [start, start], color='dm.gray6', linestyle='-', linewidth=line_thickness)

    # Plot bars for ASHP
    for i in range(len(x_ashp)):
        if i == 0 or i == len(x_ashp) - 1:
            ax.bar(x_ashp[i], values_gshp[i], bar_width, color=COLORS[n])
        else:
            ax.bar(x_ashp[i], values_gshp[i], bar_width, bottom=cumulative_values_ashp[i-1], color=COLORS[n])

    # Draw connecting lines for ASHP
    draw_waterfall_lines(ax, x_ashp, cumulative_values_ashp, line_thickness)

    # Axis settings
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.tick_params(axis='y', which='both', left=True, right=False)
    ax.set_yticks([])
    ax.set_ylim(0, y_max)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    # Set x-axis labels and limits
    ax.set_xticks(x_ashp)
    ax.set_xticklabels(labels_gshp, ha='center', fontsize=dm.fs(0.3))
    ax.set_xlim(-x_padding, len(labels_gshp) - 1 + x_padding)

    # Add bar values as text
    for i, value in enumerate(values_gshp):
        if i == 0 or i == len(values_gshp) - 1:
            height = value
            va = 'bottom'
            y_pos = height + text_padding
        else:
            height = cumulative_values_ashp[i]
            va = 'top'
            y_pos = height - text_padding
        
        sign = '-' if value < 0 else ''
        text_value = f'{abs(value):.1f}'
        
        # Combine sign and value, but add a small space between them
        full_text = f'{sign}{text_value}' if sign else text_value
        
        # Add the full text, centered on the bar
        ax.text(i, y_pos, full_text, ha='center', va=va, fontsize=dm.fs(0), weight='normal')

    # Add title for ASHP
    ax.set_title(f'{name}', fontsize=dm.fs(0.5))

    dm.simple_layout(fig, margins=(0.1,0.1,0.1,0.1), bbox=(0, 1, 0, 1), verbose=False)
    # fig_name = 'ASHP_exergy_distribution_waterfall_paper'
    # plt.savefig(save_dir + fig_name + '.png', dpi=600, transparent=True)
    # dm.util.save_and_show(fig, size=600)

    return fig




def plot_waterfall_cooling_ashp_altair(
    Xin_A,
    Xc_int_A,
    Xc_r_A,
    Xc_ext_A,
    X_a_ext_out_A,
    Xout_A
):
    # values_ashp = [Xin_A, -Xc_int_A, -Xc_r_A, -Xc_ext_A, -X_a_ext_out_A, Xout_A]
    data = [
        {"label": "Begin", "amount": Xin_A},
        {"label": "Jan", "amount": -Xc_int_A},
        {"label": "Feb", "amount": -Xc_r_A},
        {"label": "Mar", "amount": -Xc_ext_A},
        {"label": "Apr", "amount": -X_a_ext_out_A},
        {"label": "End", "amount": Xout_A},
    ]
    source = pd.DataFrame(data)

    # Define frequently referenced fields
    amount = alt.datum.amount
    label = alt.datum.label
    window_lead_label = alt.datum.window_lead_label
    window_sum_amount = alt.datum.window_sum_amount

    # Define frequently referenced/long expressions
    calc_prev_sum = alt.expr.if_(label == "End", 0, window_sum_amount - amount)
    calc_amount = alt.expr.if_(label == "End", window_sum_amount, amount)
    calc_text_amount = (
        alt.expr.if_((label != "Begin") & (label != "End") & calc_amount > 0, "+", "")
        + calc_amount
    )

    # The "base_chart" defines the transform_window, transform_calculate, and X axis
    base_chart = alt.Chart(source).transform_window(
        window_sum_amount="sum(amount)",
        window_lead_label="lead(label)",
    ).transform_calculate(
        calc_lead=alt.expr.if_((window_lead_label == None), label, window_lead_label),
        calc_prev_sum=calc_prev_sum,
        calc_amount=calc_amount,
        calc_text_amount=calc_text_amount,
        calc_center=(window_sum_amount + calc_prev_sum) / 2,
        calc_sum_dec=alt.expr.if_(window_sum_amount < calc_prev_sum, window_sum_amount, ""),
        calc_sum_inc=alt.expr.if_(window_sum_amount > calc_prev_sum, window_sum_amount, ""),
    ).encode(
        x=alt.X("label:O", axis=alt.Axis(title="Months", labelAngle=0), sort=None)
    )

    color_coding = (
        alt.when((label == "Begin") | (label == "End"))
        .then(alt.value("#878d96"))
        .when(calc_amount < 0)
        .then(alt.value("#24a148"))
        .otherwise(alt.value("#fa4d56"))
    )

    bar = base_chart.mark_bar(size=45).encode(
        y=alt.Y("calc_prev_sum:Q", title="Amount"),
        y2=alt.Y2("window_sum_amount:Q"),
        color=color_coding,
    )

    # The "rule" chart is for the horizontal lines that connect the bars
    rule = base_chart.mark_rule(xOffset=-22.5, x2Offset=22.5).encode(
        y="window_sum_amount:Q",
        x2="calc_lead",
    )

    # Add values as text
    text_pos_values_top_of_bar = base_chart.mark_text(baseline="bottom", dy=-4).encode(
        text=alt.Text("calc_sum_inc:N"),
        y="calc_sum_inc:Q",
    )
    text_neg_values_bot_of_bar = base_chart.mark_text(baseline="top", dy=4).encode(
        text=alt.Text("calc_sum_dec:N"),
        y="calc_sum_dec:Q",
    )
    text_bar_values_mid_of_bar = base_chart.mark_text(baseline="middle").encode(
        text=alt.Text("calc_text_amount:N"),
        y="calc_center:Q",
        color=alt.value("white"),
    )

    return alt.layer(
        bar,
        rule,
        text_pos_values_top_of_bar,
        text_neg_values_bot_of_bar,
        text_bar_values_mid_of_bar
    ).properties(
        width=600,
        height=450
    )