from bs4 import BeautifulSoup
import requests
import re
import random
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    address = 'https://puppyfinder.com/puppies-for-sale-in-usa?AdSearch[sort]=sort-latest'

    response = requests.get(address)
    times = 0
    linkList = []

    soup = BeautifulSoup(response.text, 'lxml')
    for a in soup.find_all(class_="block-title set-tip"):
        if times <= 9:
            aSecond = str(a).replace("a href=\"", "https://puppyfinder.com")
            aFinal = aSecond.replace("\">", " ")
            link = re.search("(?P<url>https?://[^\s]+)", str(aFinal)).group("url")
            linkList.append(str(link))
        else:
            break
        times += 1
    puppyProfile = random.choice(linkList)
    print(puppyProfile + "\n\n")

    response2 = requests.get(puppyProfile)
    soup2 = BeautifulSoup(response2.text, 'lxml')
    images = []
    for img in soup2.findAll('img'):
        images.append(img.get('src'))

    sub = "AdInfo"
    for t in images:
        if sub not in t:
            images.remove(t)
    puppyIMG = images.pop(1)
    print(puppyIMG+"\n\n")

    tb = BeautifulSoup(response2.text, 'lxml')
    tables = tb.findAll("table", { "style" : "background: rgba(255, 255, 255, 0.75);" })

    endMSG = ''
    new_results = [[col.text.replace('\n', '') for col in row.find_all('td')] for row in tables[0].find_all('tr')]
    for i in new_results:
        endMSG += (' '.join(i) + "\n")
    endMSG = endMSG.split()
    endMSG = str(' '.join(sorted(set(endMSG), key=endMSG.index)))
    s = endMSG

    categories = ['Breed', 'Price', 'Gender', 'Nickname', 'Age', 'Color/Markings',
                  'Size at Maturity', 'Availability Date', 'Shipping Area',
                  'Payment Method', 'Show Potential', 'Champion Bloodlines']

    for cat in categories:
        s = s.replace(cat + ':', '\n' + cat + ':')

    print(s + "\n")
    resp = MessagingResponse()
    sendingMSG = resp.message(s + "\n\n" + puppyProfile)
    sendingMSG.media(puppyIMG)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
