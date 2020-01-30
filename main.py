from urllib import parse
import urllib.request
import json
import requests
import time
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

SCKEY = ["xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]

provinceName = '湖北省'

def uploadplot():
    url = 'https://sm.ms/api/v2/upload'
    files = {'smfile': open('province.png', 'rb')}
    data ={'ssl':False,'format':'json'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
    }
    r = requests.post(url, files=files,data=data,headers=headers)
    msg = json.loads(r.text)
    ploturl = msg
    if str(ploturl['success']) == 'False':
        return ploturl['images']
    else:
        return ploturl['data']['url']

def provinceplot(latest = 0, province = '辽宁省'):
    latest = str(latest)
    provincechange = parse.quote(province)
    url = 'https://lab.isaaclin.cn/nCoV/api/area?latest='+latest+'&province='+provincechange
    response = urllib.request.urlopen(url)
    page = response.read()
    msg = json.loads(page)

    times = [time.strftime("%m-%d", time.localtime(msg['results'][0]['updateTime']/1000))]
    confirmedCount = [msg['results'][0]['confirmedCount']]
    suspectedCount = [msg['results'][0]['suspectedCount']]
    curedCount = [msg['results'][0]['curedCount']]
    deadCount = [msg['results'][0]['deadCount']]
    #ploslist = [times, confirmedCount, suspectedCount, curedCount, deadCount]
    for i in msg['results']:
        t = time.strftime("%m-%d", time.localtime(i['updateTime']/1000))
        if t == times[-1]:
            confirmedCount[-1] = i['confirmedCount']
            suspectedCount[-1] = i['suspectedCount']
            curedCount[-1] = i['curedCount']
            deadCount[-1] = i['deadCount']
        else:
            times.append(t)
            confirmedCount.append(i['confirmedCount'])
            suspectedCount.append(i['suspectedCount'])
            curedCount.append(i['curedCount'])
            deadCount.append(i['deadCount'])

    plt.figure()
    plt.plot(times,confirmedCount)
    plt.title(province+'疫情确诊趋势图')
    plt.savefig('province.png')

    return

def push_wechat(title, message, SCKEY):
    ur = 'https://sc.ftqq.com/{}.send'
    url = ur.format(SCKEY)
    data = {"text": title,
            "desp": message}
    r = requests.post(url, data)
    print(r.text)

def updateTime_get():
    f = open('updateTime.txt')
    updateTime_get = f.read()
    return updateTime_get

def updateTime_set(new_updateTime):
    file = open('updateTime.txt','w')
    file.write(str(new_updateTime))
    file.close()

def area(latest = 1, province = '辽宁省'):
    latest = str(latest)
    province = parse.quote(province)
    url = 'https://lab.isaaclin.cn/nCoV/api/area?latest='+latest+'&province='+province
    response = urllib.request.urlopen(url)
    page = response.read()
    msg = json.loads(page)
    return msg

def msgs(msg):  
    updateTime = msg['results'][0]['updateTime']
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(updateTime/1000))

    updateTime_set(updateTime)
    provinceplot(0, provinceName)

    ploturl = uploadplot()
    plotmsgs = '![image]('+ ploturl +')\n\n'
    
    msgs = '全省: {}\t\t确诊人数: {}\t\t疑似感染人数: {}\t\t治愈人数: {}\t\t死亡人数: {}\t\t\n\n'\
        .format(msg['results'][0]['provinceName'],
                msg['results'][0]['confirmedCount'],
                msg['results'][0]['suspectedCount'],
                msg['results'][0]['curedCount'],
                msg['results'][0]['deadCount'])
        
    for i in msg['results'][0]['cities']:
        msg = '城市: {}\t\t确诊人数: {}\t\t疑似感染人数: {}\t\t治愈人数: {}\t\t死亡人数: {}\t\t\n\n'\
            .format(i['cityName'],
                    i['confirmedCount'],
                    i['suspectedCount'],
                    i['curedCount'],
                    i['deadCount'])
        msgs += msg
        
    msgs += '\n\n\n\n 更新时间: {}'.format(dt)
    allmsgs = plotmsgs+msgs
    return allmsgs

def main():
    last_updateTime = updateTime_get()
    
    title = provinceName + '疫情信息概览'
    province = area(1, provinceName)
    updateTime = province['results'][0]['updateTime']
    if last_updateTime != str(updateTime):
        message = msgs(province)
        for i in SCKEY:
            push_wechat(title, message, i)
            time.sleep(10)
    else:
        print('内容未更新')

if __name__ == "__main__":
    while True:
        main()
        time.sleep(900)
