from time import sleep
import selenium
import selenium.webdriver
from selenium.webdriver.support import expected_conditions as EC
import csv
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
def tabClear(driver):
    original_windows = driver.window_handles
    driver.switch_to.new_window('tab')
    sleep(0.5)
    new_window = [handle for handle in driver.window_handles if handle not in original_windows][0]
    for window in original_windows:
        if window in driver.window_handles:
            driver.switch_to.window(window)
            driver.close()
    driver.switch_to.window(new_window)
    driver.get("about:blank")
def getMarket(code):
    code_str = str(code).strip()
    prefix2 = code_str[:2]
    prefix3 = code_str[:3]
    if prefix3 in ['600', '601', '603', '605']:
        return 'sh'  # 沪市主板
    if prefix3 == '688':
        return 'sh'  # 科创板
    if prefix3 in ['000', '001', '002']:
        return 'sz'  # 深市主板/中小板
    if prefix3 == '300':
        return 'sz'  # 创业板
    if prefix2 in ['43', '83', '87', '88']:
        return 'bj'  # 北交所
    if prefix3 == '900':
        return 'sh'  # 沪市B股
    if prefix3 == '200':
        return 'sz'  # 深市B股
    if prefix3 in ['730', '780', '788']:
        return 'sh'  # 沪市新股申购
    if prefix3 == '080':
        return 'sz'  # 深市配股
    return 'unk'  # 未知代码
def query(driver,id="300065",market="sz"):
    driver.get("url"%(id,market))
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME,'clearfix'))).find_element(By.XPATH,'//div[text()="公司资料"]').click()
    sleep(2)
    if "展开" in driver.find_element(By.CLASS_NAME,"isopen").text:
        driver.find_element(By.CLASS_NAME,"isopen").click()
    sn=driver.find_element(By.CLASS_NAME,"ant-typography").text.split()
    sn=re.sub(r"(\d+\.\d*|\.\d+)$","",sn[1])
    ind=driver.find_element(By.XPATH,'//div[contains(text(),"所属行业")]/following-sibling::div'
                            ).find_element(By.TAG_NAME,"span").text
    basic_inf={"股票代码":id,"股票名称":sn,"所属行业":ind}
    """for i in driver.find_elements(By.TAG_NAME,"ul")[1:]:
        for j in i.find_elements(By.TAG_NAME,"li"):
            tmp=[]
            for k in i.find_elements(By.TAG_NAME,"div"):
                if not j.text in tmp:tmp.append(j.text)
            tmp=tmp[0].split("\n")
            #if(tmp[0] in basic_inf.keys()):
            basic_inf[tmp[0]]=tmp[1]"""
    list_info=[]
    for i in basic_inf.keys():
        list_info.append(basic_inf[i])
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME,'clearfix'))
                                   ).find_element(By.XPATH,'//div[text()="股东研究"]').click()
    sleep(1)
    sinf=[]
    for i in driver.find_element(By.ID,"sdltgd").find_element(By.CLASS_NAME,"ant-table-tbody"
                                                              ).find_elements(By.TAG_NAME,"tr"):
        tmp=[id]
        for j in i.find_elements(By.TAG_NAME,"td")[1:]:
            tmp.append(j.find_element(By.TAG_NAME,"span").text)
        sinf.append(tmp[0:6])
    sinf.pop()
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME,'clearfix'))
                                   ).find_element(By.XPATH,'//div[text()="最新动态"]').click()
    sleep(1)
    concept=driver.find_element(By.XPATH,'//div[text()="涉及概念 "]/following-sibling::div[1]'
                                ).find_element(By.TAG_NAME,"span").text
    ct=concept.split(",")
    concept=[]
    for i in ct:
        concept.append([id,i])
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME,'clearfix'))
                                   ).find_element(By.XPATH,'//div[text()="公告看点"]').click()
    sleep(1)
    notice=[]
    if "收起" in driver.find_element(By.CLASS_NAME,"isopen").text:
        driver.find_element(By.CLASS_NAME,"isopen").click()
    for p in range(0,2):
        for i in range(0,10):
            try:
                t=WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID,"ggTitleGszxDetail"+str(p*10+i))))
                driver.execute_script("arguments[0].scrollIntoView();", t)
                title=t.text
                dt=t.find_element(By.XPATH,"./../..").find_element(By.TAG_NAME,"td").text
                driver.execute_script("arguments[0].click();",t)
                sleep(0.5)
                url=WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME,'iframe'))
                                                   ).get_attribute("src")
                try:
                    for _ in range(10):driver.find_element(By.CLASS_NAME,"ant-modal-close").click()
                except:pass
                notice.append([id,dt,title,url])
            except:print("notice err",p,i)
        driver.execute_script("arguments[0].click();",
                              driver.find_element(By.ID,"gsggDetail"
                                                  ).find_element(By.CLASS_NAME,"ant-pagination-next"))
        sleep(1)
    driver.refresh()
    return (list_info,sinf,concept,notice)
def getStocks(start,end):
    holderFile=open("holder.csv","a", encoding="utf-8", newline="")
    holderCSV=csv.writer(holderFile)
    conceptFile=open("concept.csv","a", encoding="utf-8", newline="")
    conceptCSV=csv.writer(conceptFile)
    noticeFile=open("notice.csv","a", encoding="utf-8", newline="")
    noticeCSV=csv.writer(noticeFile)
    basicFile=open("basic.csv","a", encoding="utf-8", newline="")
    basicCSV=csv.writer(basicFile)
    marketFile=open("market.csv","a", encoding="utf-8", newline="")
    marketCSV=csv.writer(marketFile)
    driver = selenium.webdriver.Firefox()
    for i in range(int(start),int(end)):
        sid=str(i)
        while(len(sid)<6):sid="0"+sid
        try:
            a=query(driver,sid,getMarket(sid))
        except Exception as e:
            print("err",i,e)
        else:
            conceptCSV.writerows(a[2])
            holderCSV.writerows(a[1])
            noticeCSV.writerows(a[3])
            basicCSV.writerow(a[0])
            marketCSV.writerow([sid,getMarket(sid)])
            print(sid)
        tabClear(driver)
    holderFile.close()
    conceptFile.close()
    noticeFile.close()
    marketFile.close()
    basicFile.close()
    driver.quit()
getStocks("000001","000050")
getStocks("300001","300050")
getStocks("600001","600050")