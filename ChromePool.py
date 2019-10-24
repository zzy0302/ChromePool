from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.select import Select
import time
import threading


class chromepool():

    def __init__(self, maxsize=5, minsize=1, timeout=10, options=ChromeOptions(),monitor=False):
        self.pool = []
        self.monitor_start = monitor
        self.maxsize = maxsize
        self.current = 0
        self.minsize = minsize
        self.timeout = timeout
        self.new(minsize, options=options)
        if self.monitor_start:
            self.start_monitor()
        self.getting = False

    def new(self, cut=1, options=ChromeOptions()):
        for i in range(cut):
            if self.current+1 < self.maxsize:
                _ch = Chrome(options=options)
                id = _ch.session_id
                _temp = {'num': i, 'id': id, 'd': _ch, 'buzy': False,
                         'st': time.perf_counter()}
                self.current += 1
                self.pool.append(_temp)
            else:
                return False
        return True

    def delete(self, _target):
        for i in self.pool[:]:
            if i['id'].session_id == _target.session_id:
                i['d'].quit()
                self.pool.remove(i)
                self.current -= 1
                return True
        return False

    def delete_all(self):
        while self.getting:
            time.sleep(0.01)
        self.getting = True
        try:
            for i in self.pool[:]:
                i['d'].quit()
                self.pool.remove(i)
                self.getting = False
            return True
        except Exception:
            self.getting = False
            return False

    def get(self):
        while self.getting:
            time.sleep(0.01)
        self.getting = True
        print(self.getting)
        for i in self.pool:
            if i['buzy'] == False:
                i['st'] = time.perf_counter()
                i['buzy'] = True
                self.getting = False
                return i['d']
        else:
            if self.new():
                self.getting = False
                self.pool[-1]['buzy'] = True
                return self.pool[-1]['d']
            else:
                self.getting = False
                return False

    def release(self, _target=''):
        if _target == '':
            return False
        for i in self.pool:
            if i['id'] == _target.session_id:
                _target.delete_all_cookies()
                i['buzy'] = False
                return True

    def start_monitor(self, level=1):
        _temp = threading.Thread(target=self.monitor, args={level})
        _temp.start()
        _temp.join()
        self.monitor_start=_temp

    def stop_monitor(self):
        self.monitor_start._stop()

    def monitor(self, level=1):
        while True:
            for i in self.pool:
                _time = time.perf_counter()
                if _time - i['st'] >= self.timeout:
                    self.release(i)
