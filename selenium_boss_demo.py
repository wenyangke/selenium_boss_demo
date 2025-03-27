import random
import re

from selenium import webdriver
# 方案一：显式等待关键元素加载完成（推荐）
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from lxml import etree
import time
import pandas as pd

class Boss(object):

    #areaBusiness = {'440103':'荔湾区','440111':'白云区','440106':'天河区','440104':'越秀区','440105':'海珠区','440118':'增城区','440117':'从化区','440114':'花都区','440115':'南沙区','440112':'黄埔区','440113':'番禺区'}
    areaBusiness = {'440118':'增城区','440117':'从化区','440114':'花都区','440115':'南沙区','440112':'黄埔区','440113':'番禺区'}


    def __init__(self):
        driver = webdriver.Chrome(service=Service(r"D:\Python313\chromedriver\chromedriver-win64\chromedriver.exe"))
        # 第一重：设置全局隐式等待（作用于所有 find_element 操作）
        driver.implicitly_wait(3)  # 单位：秒
        self.url = "https://www.zhipin.com/web/geek/job?query=Java&areaBusiness={}&page={}"

        self.driver = driver
        # 所有的岗位
        self.job_list = []

    def query_list(self,area,page):
        driver = self.driver
        print(self.url.format(area,page))
        driver.get(self.url.format(area,page))
        time.sleep(random.uniform(0, 1))  # 随机0-1秒

        # 第二重：显式等待（针对核心元素加强等待）
        try:
            # 在显式等待前先检查弹窗
            self.check_login_popup()
            WebDriverWait(driver, 3).until(
                EC.all_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-title.clearfix")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".pagination-area")),
                    # 新增对公司信息容器的等待
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".company-tag-list")),
                )
            )
            # 在显式等待前先检查弹窗
            self.check_login_popup()
        except Exception as e:
            print(e)
            print('页面加载失败')
        html = etree.HTML(driver.page_source)
        data_list = html.xpath('//li[@class="job-card-wrapper"]')

        return data_list

    def parse_list_item(self,area,item):
        company_name = None
        try:
            company_name = item.xpath('.//div/h3[@class="company-name"]/a/text()')[0]
        except Exception as e:
            print(e)
            print('公司名无法获取')

        job_name = None
        try:
            job_name = item.xpath('.//span[@class="job-name"]/text()')[0]
        except Exception as e:
            print(e)
            print('工作岗位无法获取')

        area = None
        try:
            area = item.xpath('.//span[@class="job-area"]/text()')[0]
        except Exception as e:
            print(e)
            print('区域无法获取')

        salary = None
        try:
            salary = item.xpath('.//span[@class="salary"]/text()')[0]
        except Exception as e:
            print(e)
            print('薪资范围无法获取')

        job_year = None
        try:
            job_year = item.xpath('.//div[@class="job-info clearfix"]/ul[@class="tag-list"]/li[1]/text()')[0]
        except Exception as e:
            print(e)
            print('工作年限无法获取')

        # 学历
        education = None
        try:
            education = item.xpath('.//div[@class="job-info clearfix"]/ul[@class="tag-list"]/li[2]/text()')[0]
        except Exception as e:
            print(e)
            print('学历无法获取')

        # 公司行业
        industry = None
        try:
            industry = item.xpath('.//ul[@class="company-tag-list"]/li[1]/text()')[0]
        except Exception as e:
            print(e)
            print('公司行业无法获取')

        # 企业发展阶段
        stage = None
        # 公司行业 和 规模人数是一定有值的，但企业发展阶段不一定有
        if item.xpath('.//ul[@class="company-tag-list"]/li[3]'):
            try:
                stage = item.xpath('.//ul[@class="company-tag-list"]/li[2]/text()')[0]
            except Exception as e:
                print(e)
                print('企业发展阶段无法获取')

        # 规模人数
        scale = None
        try:
            scale = item.xpath('.//ul[@class="company-tag-list"]/li[last()]/text()')[0]
        except Exception as e:
            print(e)
            print('无法获取规模人数')

        # 信息描述
        info_desc = None
        try:
            uls = item.xpath('.//div[@class="job-card-footer clearfix"]/ul')
            # 先处理每个ul内部的li元素
            ul_contents = []
            for ul in uls:
                # 提取当前ul下所有li的文本
                lis = ul.xpath('.//li/text()')
                # 清理空格并过滤空值
                cleaned_lis = [li.strip() for li in lis if li.strip()]
                if cleaned_lis:
                    # 将单个ul内的li用顿号连接
                    ul_contents.append("、".join(cleaned_lis))
            # 最后将所有ul的内容用顿号连接
            info_desc = "、".join(ul_contents) if ul_contents else None
        except Exception as e:
            print(e)
            print('无法获取信息描述')

        welfare = None
        try:
            welfare = item.xpath('.//div[@class="job-card-footer clearfix"]/div/text()')[0]
        except Exception as e:
            print(e)
            print('无法获取福利信息')

        href = None
        try:
            href = item.xpath(".//a/@href")[0]
        except Exception as e:
            print(e)
            print('无法获取链接')

        result = {'区域': area, '公司名称': company_name, '工作岗位': job_name, '薪资范围': salary, '工作年限': job_year,
         '学历': education, '公司行业': industry, '企业发展阶段': stage, '规模人数': scale, '信息描述': info_desc,
         '福利': welfare, '链接': href}
        return result
    def query_detail(self,href):
        driver = self.driver

        driver.get(href)
        time.sleep(random.uniform(0, 1))  # 随机0-1秒
        # 第二重：显式等待（针对核心元素加强等待）
        try:
            # 在显式等待前先检查弹窗
            self.check_login_popup()
            WebDriverWait(driver, 3).until(
                EC.all_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-sec-text")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".boss-active-time")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".location-address")),

                )
            )

            # 在显式等待前先检查弹窗
            self.check_login_popup()
        except Exception as e:
            print(e)
            # 就算这里报异常，下面未必拿不到值
            print('详情页加载失败')
        html = etree.HTML(driver.page_source)
        # 岗位职责
        job_desc = None
        try:
            job_desc = ''.join(html.xpath('//div[@class="job-sec-text"]/text()'))
        except Exception as e:
            print(e)
            print('岗位职责无法获取')

        # 活跃时间（两种方式获取）
        active_time = None
        try:
            if html.xpath('//span[@class="boss-active-time"]/text()'):
                active_time = html.xpath('//span[@class="boss-active-time"]/text()')[0]
            else:
                active_time = self.driver.find_element(By.XPATH, '//span[@class="boss-online-tag"]').text
        except Exception as e:
            print(e)
            print('活跃时间无法获取')

        # 工作地点
        work_address = None
        try:
            work_address = html.xpath('//div[@class="location-address"]/text()')[0]
        except Exception as e:
            print(e)
            print('工作地点无法获取')

        return {'岗位职责':job_desc,'活跃时间':active_time,'工作地点':work_address}
    def run(self):
        all_query_list = []
        # 遍历区域
        for area, area_name in self.areaBusiness.items():
            page = 1
            max_page = None # 最大页码
            current_page_list = None

            while True:
                print(f'正在爬取区域：{area_name}，第{page}页...')
                # 获取当前页的岗位信息
                try:
                    current_page_list = self.query_list(area, page)
                except:
                    continue

                try:
                    if self.driver.find_element(By.XPATH, "//div[@class='job-empty-box']"):
                        break
                except:
                    print(f'第{page}页解析中..')


                # 1.在列表页判断是否已在最后一页，如果是则跳出循环，执行下一个区域爬取
                processed_html = self.driver.page_source.replace('<!---->', '')
                current_html = etree.HTML(processed_html)
                next_page = current_html.xpath('//i[@class="ui-icon-arrow-right"]/../@class')
                if max_page is None:
                    pattern = r'>(\d+)</a>\s*<a\b[^>]*><i\s+class="ui-icon-arrow-right"'
                    match = re.search(pattern, self.driver.page_source)
                    if match:
                        max_page = int(match.group(1))  # 修正为 group(1)

                # 2.解析列表、详情页组装好数据
                job_list = []
                # 解析列表数据
                for item in current_page_list:
                    # 列表数据解析
                    job = self.parse_list_item(area, item)
                    job_list.append(job)
                # 遍历解析详情
                for job in job_list:
                    detail = None
                    if job['链接']:
                        time.sleep(random.uniform(0, 1))  # 随机0-1秒
                        href = f"https://www.zhipin.com{job['链接']}"
                        detail = self.query_detail(href)
                        # 补全链接
                        detail['链接'] = href
                    if detail:
                        job.update(detail)
                    all_query_list.append(job)


                # 3.判断是否翻页，还是跳出
                if (len(next_page)>=1 and next_page[0] == "disabled") or max_page == page or page >= 10  :
                    break
                else:
                    page += 1

            df = pd.DataFrame(all_query_list)
            # 指定输出路径（按需修改）
            df.to_excel(f'boss_jobs{area_name}.xlsx', index=False)
            print(f"区域：{area_name}，第{page}页爬取完成，共 {len(current_page_list)} 条记录")
        print(f"数据已导出到 boss_jobs.xlsx，共 {len(all_query_list)} 条记录")
        #退出
        self.driver.quit()

    # 新增登录弹窗检测
    def check_login_popup(self):
        try:
            # 快速检测弹窗是否存在
            if self.driver.find_elements(By.XPATH, '//div[contains(@class, "boss-login-dialog")]'):
                close_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.boss-login-close'))
                )
                close_btn.click()
                print("检测到登录弹窗并成功关闭")
                return True
        except Exception as e:
            print(f"弹窗处理失败: {str(e)}")
        return False


if __name__ == '__main__':
    boss = Boss()
    boss.run()