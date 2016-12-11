# Python装饰器
# http://www.cnblogs.com/wilber2013/p/4657155.html
# Python装饰器实例：调用参数合法性验证
# http://www.cnblogs.com/huxi/archive/2011/03/31/2001522.html
import queue
import threading
import time
import datetime


class TimeoutError(Exception):
    """比如1/0是ZeroDivisionError,1+"abc"是TypeError,等,遂将它定义为TimeoutError"""
    pass


def timeout(timeout, error_message="函数{name}运行{timeout}秒仍未结束."):
    """timeout以'秒'为单位"""

    def _echo(msg):
        print(datetime.datetime.now().__str__() + " " + msg)

    def _timeout(func):
        def warpper(*args, **kwargs):
            que = queue.Queue(maxsize=1)  # 定义一个Queue,用来存储函数的返回值.

            def _thread_entry(*args, **kwargs):
                # _echo("[_thread_entry] +++ begin...")
                try:
                    return_value = func(*args, **kwargs)
                    que.put(return_value)
                    # _echo("[_thread_entry]put rv=" + str(return_value))
                except Exception as ex:
                    que.put((que, ex))  # 用que来标示这是一个捕获的异常.
                    # _echo("[_thread_entry]put ex=" + ex.__str__())
                finally:
                    # _echo("[_thread_entry] --- end...")
                    pass
                #

            _tmr = threading.Timer(0, _thread_entry, args, kwargs)
            _tmr.start()
            # _echo("join beg, timeout=" + str(timeout))
            _tmr.join(timeout=timeout)  # 浮点数,单位是'秒'
            isTimeOut = _tmr.isAlive()
            # _echo("join end, isTimeOut=" + str(isTimeOut))
            _tmr.cancel()
            if isTimeOut:
                raise TimeoutError(error_message.format(name=func.__name__, \
                                                        timeout=timeout))
            else:
                returnValue = que.get()
                # _echo("returnValue=" + str(returnValue))
                try:
                    _que, ex = returnValue
                    assert que == _que and isinstance(ex, Exception)
                except Exception:
                    return returnValue
                else:
                    raise ex

        # 只将名字修改了一下,其他属性还没有被填充.
        warpper.__name__ = func.__name__
        # warpper.__doc__ = func.__doc__
        return warpper

    return _timeout


def _console(msg):
    print(datetime.datetime.now().__str__() + " " + msg)


@timeout(timeout=6)
def _test_fun(sec):
    _console(_test_fun.__name__ + " BEG...")
    time.sleep(sec)
    _console(_test_fun.__name__ + " END...")
    return sec


if __name__ == "__main__":
    try:
        _console(__name__ + " " + "====== 1")
        _test_fun(3)
        _console(__name__ + " " + "====== 2")
        _test_fun(4)
        _console(__name__ + " " + "====== 3")
        _test_fun(5)
        _console(__name__ + " " + "====== 4")
        _test_fun(11)
        _console(__name__ + " " + "====== 5")
    except Exception as ex:
        _console(ex.__str__())

    for i in range(30):
        time.sleep(1)
    _console("will EXIT...")
    exit(0)


@timeout(60)
def runCmd(strCmd):
    import os
    os.system(strCmd)
    return None


if __name__ == "__main__":
    strCmd = "run.bat"
    runCmd(strCmd)
    exit(0)
