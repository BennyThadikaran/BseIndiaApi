from time import time_ns, sleep


class Throttle:
    '''A class for throttling requests'''

    sec = 10**9
    _min = sec * 60
    penalty_count = 0

    def __init__(self, config: dict, max_penalty_count):
        ts = time_ns()

        for d in config.values():
            d['start'] = ts
            d['count'] = 0

        self.max_penalty_count = max_penalty_count
        self.config = config

    @staticmethod
    def round(x, base) -> float:
        '''Utility method to round to nearest base'''

        return (x / base).__ceil__() * base

    def penalise(self) -> bool:
        '''Sleep 1 second on too many requests.
        Returns True if penalty_count exceeds limit'''

        self.penalty_count += 1
        print('Too many requests to the API')
        sleep(1)
        return self.penalty_count > self.max_penalty_count

    def check(self, key):
        '''Check if api limit exeeded'''

        k = self.config[key]
        k['count'] += 1

        if 'rpm' in k and k['count'] % k['rpm'] == 0:
            elapsed_time = time_ns() - k['start']
            tt_nxt_min = self.round(elapsed_time, self._min) - elapsed_time
            return sleep(tt_nxt_min / self.sec)

        if k['count'] % k['rps'] == 0:
            elapsed_time = time_ns() - k['start']
            tt_nxt_sec = self.round(elapsed_time, self.sec) - elapsed_time
            return sleep(tt_nxt_sec / self.sec)
