import requests
import pickle
from time import sleep, strftime
from bs4 import BeautifulSoup

FILENAME_SESSION = "session"


class Checker:
    def __init__(self):
        self.FILENAME_ANN = "announcements.txt"
        self.CREDS = "creds.txt"
        self.URL = "https://ehms.pk.edu.pl/standard/"
        self.URL_ANN = self.URL + "?select_kodf=&kodf=&tokid=431905"
        self.loadSession()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.78 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )
        if not self.checkAuthorized():
            self.authorize()
        # self.checkNewAnn()
        self.saveSession()

    def saveSession(self) -> None:
        self.lprint("Saving authorized session")
        pickle.dump(self.session, open(FILENAME_SESSION, "wb+"))

    def loadSession(self) -> None:
        self.lprint("Loading saved session")
        try:
            self.session = pickle.load(open(FILENAME_SESSION, "rb"))
        except FileNotFoundError:
            self.session = requests.Session()

    def saveAnn(self, ann) -> None:
        with open(self.FILENAME_ANN, "w+") as f:
            f.write(ann)

    def readAnn(self) -> str:
        try:
            with open(self.FILENAME_ANN, "r") as f:
                return f.read()
        except FileNotFoundError as e:
            return ""

    @staticmethod
    def lprint(text) -> None:
        print(f"{strftime('%d.%m.%Y %H:%M:%S')}: {text}")

    def authorize(self) -> None:
        self.lprint("Authorizing")
        with open(self.CREDS, "r") as f:
            login, password = [line.strip() for line in f.readlines()]

        _, login_name, password_name, counter = self.form.find_all("input")
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
        if "niepoprawny UID" in resp.text:
            raise Exception("Failed to authorize")
        self.soup = BeautifulSoup(resp.text, "html.parser")

    def checkAuthorized(self) -> bool:
        self.lprint("Checking access")
        resp = self.session.get(self.URL_ANN)
        is_authorized = "Logowanie do systemu" not in resp.text
        if is_authorized:
            self.soup = BeautifulSoup(resp.text, "html.parser")
        else:
            self.form = BeautifulSoup(resp.text, "html.parser").form
        return is_authorized

    def getNewSoup(self) -> None:
        self.lprint("Getting new soup")
        if not self.checkAuthorized():
            self.authorize()

    def getAnnTitles(self) -> str:
        try:
            ann = self.soup.tbody.find_all("tr")
            ann_titles = "\n".join([ann.find_all("td")[1].text for ann in ann])

        # Catching exception when tbody with announcements is no present (No announcements table present)
        except AttributeError as e:
            print(e)
            ann_titles = ""

        return ann_titles

    def checkNewAnn(self) -> bool:
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
    print(a.new_ann)
