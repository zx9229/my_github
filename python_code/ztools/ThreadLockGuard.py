# -*- coding:utf-8 -*-
# coding=utf-8
import time
import datetime
import threading


class ThreadLockGuard(object):
    """用法见下方的测试用例"""

    def __init__(self, thread_lock):
        self.__thread_lock = thread_lock
        return None

    def __enter__(self):
        self.__thread_lock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.__thread_lock.release()


def _test(threadLock, sec):
    """测试用例的函数"""
    try:
        isLock = False
        isLock = threadLock.acquire()
        print(datetime.datetime.now().__str__() + "  _test beg...")
        #
        time.sleep(sec)
        print(datetime.datetime.now().__str__() + "  _test end...")
    finally:
        if isLock:
            threadLock.release()
    return None


if __name__ == "__main__":
    lk = threading.Lock()
    #
    with ThreadLockGuard(lk) as g:
        print(datetime.datetime.now().__str__() + "  main1 beg...")
        #
        timer = threading.Timer(0, _test, (lk, 4))
        timer.start()
        #
        time.sleep(4)
        print(datetime.datetime.now().__str__() + "  main1 end...")
    #
    time.sleep(1)
    #
    with ThreadLockGuard(lk):
        print(datetime.datetime.now().__str__() + "  main2 beg...")
        time.sleep(4)
        print(datetime.datetime.now().__str__() + "  main2 end...")
    #
    print("will EXIT...")
    exit(0)
