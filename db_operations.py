import pandas as pd
import pymysql


def get_cases_stats(connection):
    with connection.cursor() as cursor:
        # 查询病例统计数据
        sql_cases = '''
        SELECT location_id, date, total_cases
        FROM cases_stats;
        '''
        cursor.execute(sql_cases)
        cases_result = cursor.fetchall()
        # print(cases_result[0])
        # {'location_id': 1, 'date': datetime.date(2022, 5, 1), 'total_cases': 42}

        cases_data = pd.DataFrame(cases_result)
        # print(cases_data)

        # 生成病例数据的透视表
        pivot_cases_df = cases_data.pivot_table(index='location_id', columns='date', values='total_cases',
                                                aggfunc='max')
        pivot_cases_df = pivot_cases_df.apply(lambda row: row.ffill().fillna(0), axis=1)
        # print(pivot_cases_df)
        # 查询位置映射表
        sql_location = '''
        SELECT * FROM location_table
        '''
        cursor.execute(sql_location)
        location_dict_list = cursor.fetchall()
        # print(location_dict_list[0])
        # {'id': 1, 'location_name': 'Africa'}

        location_mapping = {item['id']: item['location_name'] for item in location_dict_list}

        # 将 location_id 替换为位置名称
        pivot_cases_df.index = pivot_cases_df.index.map(location_mapping)

        return pivot_cases_df


def get_deaths_stats(connection):
    with connection.cursor() as cursor:
        # 查询病例统计数据
        sql_cases = '''
        SELECT location_id, date, total_deaths
        FROM deaths_stats;
        '''
        cursor.execute(sql_cases)
        cases_result = cursor.fetchall()
        cases_data = pd.DataFrame(cases_result)

        # 生成病例数据的透视表
        pivot_cases_df = cases_data.pivot_table(index='location_id', columns='date', values='total_deaths',
                                                aggfunc='max')
        pivot_cases_df = pivot_cases_df.apply(lambda row: row.ffill().fillna(0), axis=1)

        # 查询位置映射表
        sql_location = '''
        SELECT * FROM location_table
        '''
        cursor.execute(sql_location)
        location_dict_list = cursor.fetchall()
        location_mapping = {item['id']: item['location_name'] for item in location_dict_list}

        # 将 location_id 替换为位置名称
        pivot_cases_df.index = pivot_cases_df.index.map(location_mapping)

        return pivot_cases_df


def get_daily_cases_stats(connection, location_id=129):
    with connection.cursor() as cursor:
        # 查询死亡统计数据
        sql_cases = '''
            SELECT new_cases 
            FROM cases_stats 
            WHERE location_id = %s
        '''
        cursor.execute(sql_cases, (location_id,))
        cases_result = cursor.fetchall()
        case_list = [item['new_cases'] for item in cases_result]

        return case_list


def get_daily_death_stats(connection, location_id=129):
    with connection.cursor() as cursor:
        # 查询死亡统计数据
        sql_deaths = '''
            SELECT new_deaths 
            FROM deaths_stats 
            WHERE location_id = %s
        '''
        cursor.execute(sql_deaths, (location_id,))
        deaths_result = cursor.fetchall()
        death_list = [item['new_deaths'] for item in deaths_result]

        return death_list


def main():
    # 创建数据库连接
    connection = pymysql.connect(
        host='localhost',  # 数据库主机地址
        user='root',  # 数据库用户名
        password='',  # 数据库密码
        database='monkeypox',  # 数据库名称
        port=3307,
        charset='utf8',  # 使用的字符集
        cursorclass=pymysql.cursors.DictCursor  # 使用字典游标
    )

    try:
        # 获取病例统计数据
        cases_stats = get_cases_stats(connection)
        # print("病例数据透视表：")
        # print(cases_stats)

        death_stats = get_deaths_stats(connection)
        # print("死亡数据透视表：")
        # print(death_stats)

        # 获取死亡统计数据
        death_daily_stats = get_daily_death_stats(connection)
        # print("\\n死亡数据列表：")
        # print(death_daily_stats)

        cases_daily_stats = get_daily_cases_stats(connection)
        # print("\\n病例数据列表：")
        # print(cases_daily_stats)
        
        return cases_stats,death_stats,death_daily_stats,cases_daily_stats

    finally:
        # 关闭数据库连接
        connection.close()


if __name__ == "__main__":
    main()
