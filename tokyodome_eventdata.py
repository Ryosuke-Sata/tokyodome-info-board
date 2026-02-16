import requests
from bs4 import BeautifulSoup
import json

req = requests.get("https://www.tokyo-dome.co.jp/dome/event/schedule.html")
req.encoding = req.apparent_encoding

bsObj = BeautifulSoup(req.text, "html.parser")

month_elements = bsObj.find_all("p", class_ = "c-ttl-set-calender")
month = []
for i in month_elements:
    month.append(i.text)

calender_elements = bsObj.find_all(class_ = "c-mod-calender__item")
calender = []
calender = [i.text.split("\n") for i in calender_elements]
calender = [list(filter(None, i)) for i in calender]

month_count = -1
for i in calender:
    if i[0] == "01":
        month_count += 1
        i.insert(0, month[month_count])
    else:
        i.insert(0, month[month_count])

for i in range(len(calender)):
    if len(calender[i]) >= 5:
        if calender[i][4] == "TOKYO DOME TOUR":
            del calender[i][3:5]
        else:
            pass
    else:
        pass

with open("event_data.json", "w", encoding="utf-8") as f:
    json.dump(calender, f, indent=4, ensure_ascii=False)
