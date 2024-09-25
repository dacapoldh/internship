import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import pymysql


def get_location_id(cursor, location_name):
    query = "SELECT id FROM location_table WHERE location_name = %s"
    cursor.execute(query, (location_name,))
    result = cursor.fetchone()
    return result['id']


connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='monkeypox',
    port=3307,
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

geckodriver_service = Service('../drivers/geckodriver.exe', log_output=open('geckodriver.log', 'w'))

# 初始化 Firefox 浏览器
browser = webdriver.Firefox(service=geckodriver_service)

# 确诊病例和死亡数据的 URL 模板
urls = {
    'cases': "https://ourworldindata.org/explorers/monkeypox?tab=table&Metric=Confirmed+cases&Frequency=Cumulative"
             "&Relative+to+population=false&country=COD~COG~CMR~BDI",
    'deaths': "https://ourworldindata.org/explorers/monkeypox?tab=table&Metric=Confirmed+deaths&Frequency=Cumulative"
              "&Relative+to+population=false&country=COD~COG~CMR~BDI "
}

start_time_str = "2022-05-01"
next_time_str = "2022-05-02"
end_time_str = "2024-09-03"

start_time = datetime.strptime(start_time_str, "%Y-%m-%d")
next_time = datetime.strptime(next_time_str, "%Y-%m-%d")
end_time = datetime.strptime(end_time_str, "%Y-%m-%d")

current_time = start_time

case_list = []
death_list = []
location_set = set()

# 两个类型的数据需要分别爬取
for data_type in ['cases', 'deaths']:

    while next_time <= end_time:
        current_time_str = current_time.strftime("%Y-%m-%d")
        next_time_str = next_time.strftime("%Y-%m-%d")

        full_url = f"{urls[data_type]}&time={current_time_str}..{next_time_str}"
        browser.get(full_url)
        time.sleep(3)

        page_source = browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        time.sleep(3)

        # 选择页面中的表格部分
        table_boby_css = '#ExplorerContainer > div > div.ExplorerFigure > div > div.CaptionedChartAndSidePanel > div > ' \
                         'div.DataTableContainer > div > div.table-wrapper > table > tbody '

        table_body = soup.select_one(table_boby_css)

        # 遍历表格中的所有行（tr 标签）
        rows = table_body.find_all('tr')

        # 提取并处理每一行的数据
        for row in rows:
            cells = row.find_all('td')
            location = cells[0].text.strip()  # 地点
            total_number = cells[2].text.strip()  # 总数（确诊或死亡）
            new_number = cells[3].text.strip().replace('+', '')  # 新增数
            location_set.add(location)

            if data_type == 'cases':
                if total_number != '':
                    case_cell = [location, next_time_str, int(total_number), int(new_number or 0)]
                    case_list.append(case_cell)
            elif data_type == 'deaths':
                if total_number != '':
                    death_cell = [location, next_time_str, int(total_number), int(new_number or 0)]
                    death_list.append(death_cell)

        time.sleep(5)

        print(current_time_str + ' 爬取完毕\n')

        # 更新日期
        current_time += timedelta(days=1)
        next_time += timedelta(days=1)

    # 重置时间以便爬取下一个数据类型
    current_time = start_time
    next_time = datetime.strptime(next_time_str, "%Y-%m-%d")

browser.quit()

# 插入数据库逻辑
insert_cases_sql = """
    INSERT INTO cases_stats (location_id, date, total_cases, new_cases)
    VALUES (%s, %s, %s, %s)
"""

insert_deaths_sql = """
    INSERT INTO deaths_stats (location_id, date, total_deaths, new_deaths)
    VALUES (%s, %s, %s, %s)
"""

insert_location_sql = """
    INSERT INTO location_table (location_name)
    VALUES (%s)
"""

unique_locations = list(location_set)

try:
    with connection.cursor() as cursor:

        for location in unique_locations:
            cursor.execute(insert_location_sql, location)
        connection.commit()

        # 插入 cases_stats 数据
        for cases_item in case_list:
            location_name = cases_item[0]
            location_id = get_location_id(cursor, location_name)

            cursor.execute(insert_cases_sql, (location_id, *cases_item[1:]))

        # 插入 deaths_stats 数据
        for deaths_item in death_list:
            location_name = deaths_item[0]
            location_id = get_location_id(cursor, location_name)

            cursor.execute(insert_deaths_sql, (location_id, *deaths_item[1:]))

    # 提交事务
    connection.commit()

finally:
    connection.close()
