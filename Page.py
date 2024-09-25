import db_operations as db  # 导入数据库操作文件
from pyecharts import options as opts
from pyecharts.charts import Map, Timeline, Bar, Line, Page
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
import pandas as pd

confirmed_data, deaths_data, new_death_list, new_confirmed_list = db.main()

lastdate = confirmed_data.columns[-1]  # 获取最新的数据的日期
max_confirmed_number = confirmed_data[lastdate].iloc[:-1].max()  # 获取第二大的确诊病例数值--因为有world的总值
confirmed_total = confirmed_data.iloc[-1, -1]  # 获取目前总的确诊案例总数
deaths_total = deaths_data.iloc[-1, -1]  # 获取死亡总数
deaths_rate = deaths_total / confirmed_total  # 死亡比例


def MyTable():
    headers = ['确诊人数', '死亡人数', '死亡率']
    rows = [
        [confirmed_total, deaths_total, f'{deaths_rate:.2%}', ],
    ]
    table = (
        Table()
            .add(headers, rows)
            .set_global_opts(
            title_opts=ComponentTitleOpts(title=f'({lastdate})全球猴痘情况')
        )
    )
    return table


def My_TotalMap():
    confirmed = confirmed_data.groupby('location_id').agg({lastdate: 'sum'}).to_dict()[lastdate]
    deaths = deaths_data.groupby('location_id').agg({lastdate: 'sum'}).to_dict()[lastdate]
    exists_confirmed = {key: value - deaths[key] for key, value in confirmed.items()}
    b = (
        Map()
            .add("确诊人数", [*confirmed.items()], "world", is_map_symbol_show=False)
            .add("死亡人数", [*deaths.items()], "world", is_map_symbol_show=False)
            .add("现有确诊人数", [*exists_confirmed.items()], "world", is_map_symbol_show=False)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f'({lastdate})全球猴痘现状', subtitle='请单独选择确诊人数/死亡人数/现有确诊人数查看^ ^'),
            visualmap_opts=opts.VisualMapOpts(max_=max_confirmed_number / 2),

        )
    )
    return b

def My_HistoryMap():
    tl = (
        Timeline()
            .add_schema(
            # is_auto_play=True,
            is_loop_play=False,
            play_interval=200,
        )
    )
    target = confirmed_data.columns[0:].to_list()
    target.reverse()
    target = target[::2]
    target.reverse()
    for dt in target:
        confirmed = confirmed_data.groupby('location_id').agg({dt: 'sum'}).to_dict()[dt]
        c = (
            Map()
                .add("确诊人数", [*confirmed.items()], "world", is_map_symbol_show=False)
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts(title="全球疫情历史发展情况"),
                visualmap_opts=opts.VisualMapOpts(max_=max_confirmed_number / 2),

            )
        )
        tl.add(c, dt)
    return tl


def My_Top20():
    index_to_drop = ['North America', 'South America', 'Europe', 'Asia', 'Africa', 'Australia', 'World']
    TOP_confirmed_data = confirmed_data.drop(index_to_drop)
    col_indices = [i for i in range(0, confirmed_data.shape[1], 25)]
    # 使用iloc进行切片
    TOP_confirmed_data = TOP_confirmed_data.iloc[:, col_indices]
    tl1 = (
        Timeline()
            .add_schema(
            # is_auto_play=True,
            is_loop_play=False,
            play_interval=300,
        )
    )

    for dt in TOP_confirmed_data.columns[0:]:
        confirmed = \
            TOP_confirmed_data.groupby('location_id').agg({dt: 'sum'}).sort_values(by=dt, ascending=False)[
            :20].sort_values(
                by=dt).to_dict()[dt]
        bar = (
            Bar()
                .add_xaxis([*confirmed.keys()])
                .add_yaxis("确诊人数", [*confirmed.values()], label_opts=opts.LabelOpts(position="right"))
                .reversal_axis()
                .set_global_opts(
                title_opts=opts.TitleOpts("各国确诊人数排行 TOP20")
            )
        )
        tl1.add(bar, dt)
    return tl1


def My_trend():
    # 预处理--确诊数据在前面已经处理过
    index_to_drop = ['North America', 'South America', 'Europe', 'Asia', 'Africa', 'Australia', 'World']
    TR_confirmed_data = confirmed_data.drop(index_to_drop)
    TR_deaths_data = deaths_data.drop(index_to_drop)
    targets = TR_confirmed_data.columns[0:].to_list()
    exists_confirmed_list = []
    for idx, today in enumerate(targets[0:], 1):
        yesterday = targets[idx - 1]
        exists_confirmed = TR_confirmed_data[today].sum() - TR_deaths_data[today].sum()
        exists_confirmed_list.append(int(exists_confirmed))
    # x:targets[1:] ydeath:new_death_list ycon:exists_confirmed_list
    e = (
        Line()
            .add_xaxis(targets[1:])
            .add_yaxis('现有确诊人数', exists_confirmed_list, label_opts=opts.LabelOpts(is_show=True))
            .add_yaxis('新增确诊人数', new_confirmed_list, label_opts=opts.LabelOpts(is_show=False), is_symbol_show=False)

            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}"),
                                             axisline_opts=opts.AxisLineOpts(
                                                 linestyle_opts=opts.LineStyleOpts(color='pink'))))  # 添加一条蓝色的y轴
            .set_global_opts(title_opts=opts.TitleOpts(title="全球猴痘趋势"),
                             yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}"),
                                                      axisline_opts=opts.AxisLineOpts(
                                                          linestyle_opts=opts.LineStyleOpts(color="red"))))
    )
    death_line = Line().add_xaxis(targets[1:]).add_yaxis("新增死亡人数", new_death_list, yaxis_index=1)
    # confirmed_line=Line().add_xaxis(targets[1:]).add_yaxis("现有确诊人数",exists_confirmed_list,yaxis_index=1)
    e.overlap(death_line)  # 将line2叠加在line1图上
    e.set_colors(["red", "blue", "pink"])

    return e


page = Page(layout=Page.DraggablePageLayout)
page.add(
    MyTable(),
    My_TotalMap(),
    My_HistoryMap(),
    My_Top20(),
    My_trend()
)
page.render('../asset/my_final.html')
