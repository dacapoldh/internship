from pyecharts.charts import Page
import os

Page.save_resize_html('../asset/my_final.html',
                      cfg_file='../asset/chart_config.json',
                      dest='../asset/my_final.html'
                      )

# 获取 HTML 文件的相对路径
file_path = r'..\asset\my_final.html'

# 使用 os.startfile() 在浏览器中打开文件（仅适用于 Windows）
os.startfile(file_path)
