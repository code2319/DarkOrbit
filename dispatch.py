"""
The simplest version of the code that will send a retriever and collect.
Now you can create a task in the Windows or Linux scheduler to run the code every n hours.
"""
import time
import requests
from bs4 import BeautifulSoup


def login_lp(log, pwd, retriever):
    session_ = requests.Session()
    session_.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
    }
    r = session_.get(f'https://wwww.darkorbit.com/')
    soup = BeautifulSoup(r.content, 'lxml')
    form = soup.find('form', {"class": "bgcdw_login_form"})
    request = session_.post(form['action'], data={"username": log, "password": pwd})
    if request.status_code == 200:
        SERVER = request.url.split('//')[-1].split('.')[0]
        if SERVER != 'www':
            print(f"Current server: {SERVER}")
            dispatch(session_, SERVER, retriever)
        else:
            print("Something went wrong...")


def login_sid(sid, SERVER, retriever):
    session_ = requests.Session()
    session_.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
    }
    session_.cookies.set('dosid', sid, domain=f"{SERVER}.darkorbit.com", path='/')
    dispatch(session_, SERVER, retriever)


def dispatch(session_, SERVER, retriever):
    dispatch_page = session_.get(f"https://{SERVER}.darkorbit.com/indexInternal.es?action=internalDispatch")

    if dispatch_page.status_code == 200:
        permit_plus = BeautifulSoup(dispatch_page.text, "lxml").find("input", {"name": "permit plus"}).get('value')
        permit = BeautifulSoup(dispatch_page.text, "lxml").find("input", {"name": "permit"}).get('value')
        ggeu = BeautifulSoup(dispatch_page.text, "lxml").find("input", {"name": "ggeu"}).get('value')

        print(f"\npermit plus: {permit_plus}\n"
              f"permit: {permit}\n"
              f"ggeu: {ggeu}\n")

        dispatch_available = BeautifulSoup(dispatch_page.text, "lxml").find("span", {"class": "dispatch_available_display"})

        # available dispatches
        da = int(dispatch_available.text.split(":")[1].split("/")[0])
        # maximum number of available dispatches
        da_max = int(dispatch_available.text.split(":")[1].split("/")[1].split("\n")[0])
        print(da, da_max)

        if da == 0:
            for i in range(da_max):
                print(f"Trying to collect the reward for {i + 1} retriever")
                rec_dispatch = session_.post(f"https://{SERVER}.darkorbit.com/ajax/dispatch.php",
                                             data={
                                                 "command": "collectDispatch",
                                                 "slot": f"{i + 1}"
                                             })
                if rec_dispatch.status_code == 200:
                    print("\tSuccess!")
                time.sleep(2)
        else:
            while da != 0:
                print(f"{da} slots available, sending a retriever...")
                send_dispatch = session_.post(f"https://{SERVER}.darkorbit.com/ajax/dispatch.php",
                                              data={
                                                  "command": "sendDispatch",
                                                  "dispatchId": f"dispatch_retriever_{retriever}"
                                              })
                if send_dispatch.status_code == 200:
                    print("\tSuccess!")
                da -= 1
                time.sleep(2)


login_lp('login', 'password', 'r01')
# login_sid('sid', 'server', 'r01')
