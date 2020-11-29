import requests,csv,webbrowser,time,os,bs4
from config import *

oldicao = ''

if update<=300:
    update = 300

with requests.Session() as s:
    with open('airports.txt') as f:
        r = f.read()
    import json
    dct = json.loads(str(r).replace('<html><head></head><body>','').replace('</body></html>',''))
    airportscsv = dct['rows']
a=0
while a<1:
    a=2
    with requests.Session() as s:
        url = f'https://icrew.{vadomain}.com/live_uplink.php'
        r = s.get(url)
        soup = bs4.BeautifulSoup(r.content, 'html5lib')
        trs = soup.find_all('table', class_="table table-responsive table-hover table-striped")[0].find_all('tr')
        flights = []
        for j in trs:
            i = j.find_all('td')
            flight = {}
            try:
                flight.update({'flightnum' : str(i[1]).replace('<td>','').replace('</td>','')})
                flight.update({'url' : str((((i[-1])).find_all('a')[0])['href'])})
                flights.append(flight)
            except:
                pass
        for i in flights:
            if str(i['flightnum'])==str(flightnumber):
                theflight = i
        url = theflight['url']
        r = s.get(url)
        soup = bs4.BeautifulSoup(r.content, 'html5lib')

        lat = str(soup.find_all('table', class_="table table-responsive")[0].find_all('td')[5]).replace('<td>','').replace('</td>','')
        lon = str(soup.find_all('table', class_="table table-responsive")[0].find_all('td')[6]).replace('<td>','').replace('</td>','')

        closest = 1000000000000000000000000000000000000000.0
        name = ''
        icao = ''
        avail = []
        with requests.Session() as s:
            url = 'https://www.liveatc.net/map/markers.js'
            r = s.get(url)
            soup = bs4.BeautifulSoup(r.content, 'html5lib')
            import json
            dct = json.loads(str(soup).replace('<html><head></head><body>markers = ','').replace('</body></html>',''))
            found = 0
            for i in dct:
                avail.append(i['name'])

        import math
        c=0
        for i in airportscsv:
            if c==0:
                c=1
            else:
                if i['icao'] in avail:
                    R = 6373.0
                    lat1 = math.radians(float(lat))
                    lon1 = math.radians(float(lon))
                    lat2 = math.radians(float(i['lat']))
                    lon2 = math.radians(float(i['lon']))
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                    distance = R * c
                    if distance<closest:
                        icao = i['icao']
                        name = i['name']
                        closest = distance

    if oldicao !=icao:
        print(icao)
        os.system(f"taskkill /im {browser}.exe /f")
        with requests.Session() as s:
            url = 'https://www.liveatc.net/map/markers.js'
            r = s.get(url)
            soup = bs4.BeautifulSoup(r.content, 'html5lib')
            import json
            dct = json.loads(str(soup).replace('<html><head></head><body>markers = ','').replace('</body></html>',''))
            found = 0
            for i in dct:
                if i["name"]==icao:
                    found = i['url'].replace('\\','')
            if found != 0:
                while 1:
                    try:
                        with requests.Session() as s:
                            url = found
                            r = s.get(url)
                            soup = bs4.BeautifulSoup(r.content, 'html5lib')
                            for i in soup.find_all('a'):
                                try:
                                    if 'myHTML5Popup' in i['onclick']:
                                        mount = i['onclick'].replace('myHTML5Popup','').replace('(','').replace(')','').replace("'",'').split(',')[0]
                                        icao = i['onclick'].replace('myHTML5Popup','').replace('(','').replace(')','').replace("'",'').split(',')[1]
                                except:
                                    continue
                            webbrowser.open_new_tab(f"https://www.liveatc.net/hlisten.php?mount={mount}&icao={icao}")
                        break
                    except Exception as e:
                        print(e)
        oldicao = icao
    time.sleep(update)