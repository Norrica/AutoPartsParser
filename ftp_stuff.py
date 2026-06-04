import dataclasses
import os
from ftplib import FTP

from dotenv import load_dotenv


load_dotenv()

@dataclasses.dataclass
class DataRow:
    article: str
    brand: str


def createrow(string: str):
    # split = string.split()
    # article, brand = split[0], ' '.join(split[1:])
    # return DataRow(article, brand)
    return string


def get_articules(ftp:FTP):
    articules = []
    ftp.retrlines('RETR From_1C.csv', lambda e: articules.append(createrow(e)))
    return articules[1:]


def show_files():
    ftp = FTP()
    host = os.environ.get('FTP_IP')
    ftp.connect(host, int(os.environ.get('FTP_PORT')))
    ftp.login(os.environ.get("FTP_LOGIN"),
              os.environ.get("FTP_PWD"))
    ftp.dir()
    articules = []
    ftp.retrlines('RETR From_1C.csv', articules.append)
    for a in articules[1:]:
        print(a)
    ftp.quit()


if __name__ == '__main__':
    show_files()
