from urllib import parse
import urllib.request
import json
import requests
import time

SCKEY = ["xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]

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
    url = 'http://lab.isaaclin.cn/nCoV/api/area?latest='+latest+'&province='+province
    response = urllib.request.urlopen(url)
    page = response.read()
    msg = json.loads(page)
    return msg

def msgs(msg):  
    updateTime = msg['results'][0]['updateTime']
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(updateTime/1000))

    updateTime_set(updateTime)
  
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
    return msgs

def main():
    last_updateTime = updateTime_get()
    provinceName = '湖北省'
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
        time.sleep(300)
        
        

