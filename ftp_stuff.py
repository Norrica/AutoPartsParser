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


def get_articules():
    ftp = FTP()
    ftp.connect(os.environ.get('FTP_IP'), int(os.environ.get('FTP_PORT')))
    ftp.login(os.environ.get("FTP_LOGIN"),
              os.environ.get("FTP_PWD"))
    articules = []
    ftp.retrlines('RETR test.txt', lambda e: articules.append(createrow(e)))
    ftp.quit()
    return articules


def show_files():
    ftp = FTP()
    host = os.environ.get('FTP_IP')
    ftp.connect(host, int(os.environ.get('FTP_PORT')))
    ftp.login(os.environ.get("FTP_LOGIN"),
              os.environ.get("FTP_PWD"))
    ftp.pwd()
    ftp.dir()
    ftp.quit()


if __name__ == '__main__':
    load_dotenv()
    show_files()
