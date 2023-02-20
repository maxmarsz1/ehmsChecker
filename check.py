import requests
from time import sleep, strftime
from bs4 import BeautifulSoup 

FILENAME = "announcements.txt"
CREDS = "creds.txt"


def lprint(text):
    print(f"{strftime('%d.%m.%Y %H:%M:%S')}: {text}")


def getAnnTitles():
    url = 'https://ehms.pk.edu.pl/standard/'
    with open(CREDS, 'r') as f:
        login, password = [line.strip() for line in f.readlines()]

    with requests.Session() as s:
        resp = s.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        form = soup.form
        _, login_name, password_name, counter  = form.find_all('input')
        login_form = login_name.get('name')
        password_form = password_name.get('name')
        counter_form = counter.get('value')
        data = {
            'log_form': 'yes',
            login_form: login,
            password_form: password,
            'counter': counter_form
        }
        s.post(url, data=data)
        resp = s.get(url + '?select_kodf=&kodf=&tokid=431905')
        soup = BeautifulSoup(resp.text, 'html.parser')
        ann = soup.tbody.find_all('tr')
        ann_titles = "\n".join([ann.find_all('td')[1].text for ann in ann])

        return ann_titles


def saveAnn(ann):
    with open(FILENAME, 'w+') as f:
        f.write(ann)


def readAnn():
    try:
        with open(FILENAME, 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        print(e)


def checkIfNewAnn():
    ann = getAnnTitles()
    prev_ann = readAnn()

    lprint("Sprawdzam ogłoszenia...")
    if prev_ann != ann:
        lprint("Nowe ogłoszenie!")
        new_ann = ann.replace(prev_ann, '') if prev_ann is not None else ann
    else:
        lprint('Nic nowego')
        new_ann= False

    saveAnn(ann)
    return new_ann
        


if __name__ == '__main__':
    checkIfNewAnn()