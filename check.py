import requests
from time import sleep, strftime
from bs4 import BeautifulSoup


class Checker:
    def __init__(self):
        self.FILENAME_ANN = "announcements.txt"
        self.CREDS = "creds.txt"
        self.URL = "https://ehms.pk.edu.pl/standard/"
        self.URL_ANN = self.URL + "?select_kodf=&kodf=&tokid=431905"
        self.session = requests.Session()
        self.is_authorized = self.authorize()

    @staticmethod
    def lprint(text) -> None:
        print(f"{strftime('%d.%m.%Y %H:%M:%S')}: {text}")

    def authorize(self) -> bool:
        with open(self.CREDS, "r") as f:
            login, password = [line.strip() for line in f.readlines()]

        resp = self.session.get(self.URL)
        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.form
        _, login_name, password_name, counter = form.find_all("input")
        login_form = login_name.get("name")
        password_form = password_name.get("name")
        counter_form = counter.get("value")
        data = {
            "log_form": "yes",
            login_form: login,
            password_form: password,
            "counter": counter_form,
        }
        resp = self.session.post(self.URL, data=data)
        return resp.status_code == 200

    def getNewSoup(self) -> None:
        resp = self.session.get(self.URL_ANN)
        self.soup = BeautifulSoup(resp.text, "html.parser")

    def getAnnTitles(self) -> str:
        self.getNewSoup()
        try:
            ann = self.soup.tbody.find_all("tr")
            ann_titles = "\n".join([ann.find_all("td")[1].text for ann in ann])

        # Catching exception when tbody with announcements is no present (No announcements table present)
        except AttributeError as e:
            print(e)
            ann_titles = ""

        return ann_titles

    def saveAnn(self, ann) -> None:
        with open(self.FILENAME_ANN, "w+") as f:
            f.write(ann)

    def readAnn(self) -> str:
        try:
            with open(self.FILENAME_ANN, "r") as f:
                return f.read()
        except FileNotFoundError as e:
            return ""

    def checkIfNewAnn(self) -> bool:
        ann = self.getAnnTitles()
        prev_ann = self.readAnn()

        self.lprint("Checking announcements...")
        if prev_ann != ann:
            self.lprint("New announcement/s!")
            self.new_ann = ann.replace(prev_ann, "")
        else:
            self.lprint("Nothing new")
            self.new_ann = ""

        self.saveAnn(ann)
        return self.new_ann != ""


if __name__ == "__main__":
    a = Checker()
    if a.is_authorized:
        a.checkIfNewAnn()
        print(a.new_ann)
