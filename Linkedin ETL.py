from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.common.by import By
import time
import re

from datetime import date
today = date.today()

chrome_options = Options()
#chrome_options.add_argument("--lang=en-US")
#chrome_options.add_argument("--window-size=1920,1080")
chrome_options.headless = True
driver = webdriver.Chrome(chrome_options=chrome_options)

search_link = 'https://www.linkedin.com/jobs/search/?currentJobId=2884546080&f_E=2&f_JT=F&f_TPR=r86400&geoId=102095887&keywords=data%20analyst&location=California%2C%20United%20States&refresh=true'
driver.get(search_link)

num_jobs = int(driver.find_element(by=By.CSS_SELECTOR, value='h1>span').get_attribute('innerText'))

i = 2
while i <= int(num_jobs/25)+1:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    i = i + 1
    try:
        driver.find_element(by=By.XPATH, value='/html/body/div/div/main/section/button').click()
        time.sleep(2)
    except:
        pass
        time.sleep(2)

job_list = driver.find_element(by=By.CLASS_NAME, value='two-pane-serp-page__results')
jobs = job_list.find_elements(by=By.TAG_NAME, value='li')

job_id = []
job_title = []
company_name = []
location = []
date = []
job_link = []

for job in jobs:
    id0 = job.get_attribute('data-id')
    job_id.append(id0)

    title0 = job.find_element(by=By.CSS_SELECTOR, value='h3').get_attribute('innerText')
    job_title.append(title0)

    name0 = job.find_element(by=By.CSS_SELECTOR, value='h4').get_attribute('innerText')
    company_name.append(name0)

    loc0 = job.find_element(by=By.CSS_SELECTOR, value='[class="job-search-card__location"]').get_attribute('innerText')
    location.append(loc0)

    date0 = job.find_element(by=By.CSS_SELECTOR, value='div>div>time').get_attribute('datetime')
    date.append(date0)

    job_link0 = job.find_element(by=By.CSS_SELECTOR, value='a').get_attribute('href')
    job_link.append(job_link0)

jd = []
seniority = []
emp_type = []
job_func = []
industries = []
all_detailed_info = [jd, seniority, emp_type, job_func, industries]

def get_detailed_info(job, path):
#     print(path[-4:])
    info = ""
    if path[-4:] != 'span':
        try:
            info = job.find_element(by=By.XPATH, value=path).get_attribute('innerText')
        except:
            pass
        jd.append(info)
        return
#     print()
#     print('title', title)
    title = ""
    try:
        title = job.find_element(by=By.XPATH, value=path[:-4]+'h3').get_attribute('innerText')
        info = job.find_element(by=By.XPATH, value=path).get_attribute('innerText')
    except:
        pass
    if title == 'Employment type':
        emp_type.append(info)
    elif title == 'Seniority level':
        seniority.append(info)
    elif title == 'Job function':
        job_func.append(info)
    elif title == 'Industries':
        industries.append(info)
    else:
        lengths = set([len(x) for x in all_detailed_info])
        minL = min(lengths)
        maxL = max(lengths)
        if minL != maxL:
            for info_arr in all_detailed_info:
                if len(info_arr) == minL:
                    info_arr.append(info)
                    break
        else:
            print("error path: ", path)
            exit()
        if len(title):
            print('unknown title: ', title)
        else:
            print('missing attribute')


for item_idx in range(len(jobs)):
    unclickable = True
    try:
        job_click_path = '/html/body/div/div/main/section[2]/ul/li[{}]/div/a'.format(item_idx + 1)
        job_click = job.find_element(by=By.XPATH, value=job_click_path).click()
        unclickable = False
    except:
        try:
            job_click_path = '/html/body/div/div/main/section[2]/ul/li[{}]/a'.format(item_idx + 1)
            job_click = job.find_element(by=By.XPATH, value=job_click_path).click()
            unclickable = False
        except:
            print("error finding item: ", item_idx + 1)

    if unclickable:
        for info_arr in all_detailed_info:
            info_arr.append("")
        continue
    time.sleep(2)
    #                       /html/body/div[1]/div/section/div[2]/div/section[2]/div/div/section/button[1]
    for section_num in range(1, 4):
        try:
            show_more_path = '/html/body/div[1]/div/section/div[2]/div/section[{}]/div/div/section/button[1]'.format(
                section_num)
            show_more_click = job.find_element(by=By.XPATH, value=show_more_path).click()
        except:
            continue
        break

    jd_path = '/html/body/div[1]/div/section/div[2]/div/section[{}]/div/div/section/div'.format(section_num)
    get_detailed_info(job, jd_path)

    for i in range(1, 5):
        att_path = '/html/body/div[1]/div/section/div[2]/div/section[{}]/div/ul/li[{}]/span'.format(section_num, i)
        get_detailed_info(job, att_path)

    print("Done ", item_idx + 1, "/", len(jobs), " : ",
          jobs[item_idx].find_element(by=By.CSS_SELECTOR, value='h4').get_attribute('innerText'))



def year_of_exp(text):
    x = re.findall(r'\n.*years.*experience.*\n',text)
    inter = ' ,'
    app = re.sub("'",'"',inter.join(x))
    return app

job_exp =[]
Visa_ind = []

for i in jd:
    j = year_of_exp(i)
    job_exp.append(j)

for i in jd:
    cit = re.findall(r'\n.*[Cc]itizen.*\n',i)
    vis = re.findall(r'\n.*[Vv]isa.*\n',i)
    ind = cit + vis
    inter = ' ,'
    app = re.sub('"',"'",inter.join(ind))
    Visa_ind.append(app)

job_data = pd.DataFrame(
    {'Date': date,
    'Company': company_name,
    'Location': location,
    'Title': job_title,
    'Link' : job_link,
    'Description': jd,
    'Visa': Visa_ind,
    'Years_of_Experience': job_exp,
    'Employment_Type': emp_type,
    'Seniority': seniority,
    'Job_Funcrtion':job_func,
    'Industry': industries})

job_data.drop(job_data[job_data['Description'] == ''].index, inplace = True)
#job_data.to_excel(str(today) + 'Job.xlsx')#, index=False)


import mysql.connector
mydb = mysql.connector.connect(host = 'linkedin-project.cjacvsvha6rs.us-west-1.rds.amazonaws.com', user = 'Casper', passwd = 'anderson97', database = 'test')

mycursor = mydb.cursor()

df = job_data
i = 0
lenth = len(df)
text = ''
while i < lenth-2:
    i = i + 1
    text = text + "( DATE '"+df.to_numpy()[i][0]+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][1])+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][2])+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][3])+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][4])+"'"+','+'"'+str(df.to_numpy()[i][6])+'"'+','+"'"+str(df.to_numpy()[i][7])+"'"+','+"'"+str(df.to_numpy()[i][8])+"'"+','+"'"+str(df.to_numpy()[i][9])+"'"+','+"'"+str(df.to_numpy()[i][10])+"'"+','+"'"+str(df.to_numpy()[i][11])+"'"+')'+','
text = text + "( DATE '"+df.to_numpy()[i][0]+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][1])+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][2])+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][3])+"'"+','+"'"+re.sub("'",'',df.to_numpy()[i][4])+"'"+','+'"'+str(df.to_numpy()[i][6])+'"'+','+"'"+str(df.to_numpy()[i][7])+"'"+','+"'"+str(df.to_numpy()[i][8])+"'"+','+"'"+str(df.to_numpy()[i][9])+"'"+','+"'"+str(df.to_numpy()[i][10])+"'"+','+"'"+str(df.to_numpy()[i][11])+"'"+')'
mycursor.execute("INSERT INTO post (Date,Company,Location,Title,Link,Visa,Years_of_Experience,Employment_Type,Seniority,Job_Funcrtion,Industry) VALUES "+text + ';')

mycursor.execute("DELETE t1 FROM post t1 INNER JOIN post t2 WHERE t1.post_id < t2.post_id AND t1.Company = t2.Company AND t1.Title = t2.Title")
