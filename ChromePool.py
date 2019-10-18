from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.select import Select
import time


class chromepool():

    def __init__(self, maxsize=5, minsize=1, timeout=10, options=ChromeOptions()):
        self.pool = []
        self.maxsize = maxsize
        self.minsize = minsize
        self.timeout = timeout
        self.new(minsize, options=options)

    def new(self, cut=1, options=ChromeOptions()):
        for i in range(cut):
            _ch = Chrome(options=options)
            id = _ch.session_id
            _temp = {'num': i, 'id': id, 'd': _ch, 'buzy': False,
                     'st': time.perf_counter()}
            self.pool.append(_temp)

    def delete(self, _target):
        for i in self.pool:
            if i['id'].session_id == _target.session_id:
                i['d'].quit()
                self.pool.remove(i)
                return True
        return False

    def delete_all(self):
        try:
            for i in self.pool:
                i['d'].quit()
                self.pool.remove(i)
            return True
        except Exception:
            return False

    def get(self):
        for i in self.pool:
            if i['buzy'] == False:
                i['st'] = time.perf_counter()
                i['buzy'] = True
                return i['d']
        else:
            self.new()
            return self.pool[-1]['d']

    def release(self, _target=''):
        if _target == '':
            return False
        for i in self.pool:
            if i['id'] == _target.session_id:
                _target.delete_all_cookies()
                i['buzy'] = False
                return True

    def monitor(self, level=1):
        while True:
            for i in self.pool:
                _time = time.perf_counter()
                if _time - i['st'] >= self.timeout:
                    self.release(i)
