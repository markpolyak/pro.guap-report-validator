import requests
import pwinput
import json

sess = requests.Session()
sess.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) "
                  "Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}


def authorize(login, password):
    print('Logging in...')
    sess.get('https://pro.guap.ru/user/login')  # Really not working without this XD
    sess.post(
        'https://pro.guap.ru/user/login_check',
        data={'_username': login, '_password': password}
    )
    id_check = sess.get('https://pro.guap.ru/get-user-profile', cookies=sess.cookies)
    if id_check.ok:
        user_info = json.loads(id_check.content)['user']
        print(f'Logged in successfully as {user_info["lastname"]} {user_info["firstname"]} {user_info["middlename"]}')
        return True
    else:
        sess.cookies.clear()
        print(f'Authorization for {login} failed, please try again')
        return False


def pending_reports_transfer():
    reports_limit = 100
    print('Getting user_id...')
    id_check = sess.get('https://pro.guap.ru/get-user-profile', cookies=sess.cookies)
    user_info = json.loads(id_check.content)['user']
    user_id = user_info['user_id']
    print(f'Handling with user_id {user_id}...')
    # awrep_dict = sess.post(
    #     'https://pro.guap.ru/get-awaiting-reports-dictionaries/',
    #     data={'iduser': user_id},
    #     cookies=sess.cookies
    # )
    # awrep_dict = json.loads(awrep_dict.content)
    pending_reports = sess.post(
        'https://pro.guap.ru/get-awaiting-reports/',
        data={'iduser': user_id, 'semester': 0, 'subject': 0,
              'group': 0, 'student': 0, 'owner': 0, 'offset': 0, 'limit': reports_limit, 'status': 1, 'orderField': 2,
              'orderSort': 'DESC'}
    )
    pending_reports = json.loads(pending_reports.content)
    while pending_reports['isyetitems']:
        reports_limit *= 10
        pending_reports = sess.post(
            'https://pro.guap.ru/get-awaiting-reports/',
            data={'iduser': user_id, 'semester': 0, 'subject': 0,
                  'group': 0, 'student': 0, 'owner': 0, 'offset': 0, 'limit': reports_limit, 'status': 1,
                  'orderField': 2,
                  'orderSort': 'DESC'}
        )
        pending_reports = json.loads(pending_reports.content)

    print(f'Found {len(pending_reports["reports"])} reports. Downloading...')
    for i in pending_reports['reports']:
        report_file = sess.get(
            url=f'https://pro.guap.ru{i["filelink"]}',
            allow_redirects=True
        )
        open(f'{i["group_id"]}_{i["user_fio"]}', 'wb').write(report_file.content)
        print(f'{i["group_id"]}_{i["user_fio"]}')
        print(f'№{pending_reports["reports"].index(i)+1}: success')


usr_login = input('Enter login: \n')
# usr_password = pwinput.pwinput(prompt='Enter password: \n', mask='')
usr_password = input('Enter password: \n')
while not (authorize(usr_login, usr_password)):
    usr_login = input('Enter login: \n')
    usr_password = pwinput.pwinput(prompt='Enter password: \n', mask='')
pending_reports_transfer()
