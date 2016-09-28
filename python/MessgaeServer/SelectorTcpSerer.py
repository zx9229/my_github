'''
Created on 2016年8月21日

@author: zhang
'''
###############################
import logging
###############################
class NetBuffer(object):
    """socket使用的网络缓冲区类"""
    
    @staticmethod
    def CreateNetBuffer(theSocket):
        dst = NetBuffer(theSocket)
        return dst
    
    def __init__(self, theSocket) -> None:
        self.__sock = theSocket
        self.__buf = b""
        # 你永远也不知道用户会做出来什么事情,所以,用户可能使用的每一个函数,都需要强行捕获所有异常(-_-!)
        try:
            self.OnSocketCreated()
        except Exception as ex:
            import datetime
            print(datetime.datetime.now(), ", ", ex, sep="")
        return None
    
    def OnSocketCreated(self) -> None:
        """NetBuffer中的socket被外部创建时,此函数被调用"""
        import datetime
        print(datetime.datetime.now(), ", ",
              "getpeername=", self.__sock.getpeername(), ", ",
              "getsockname=", self.__sock.getsockname(), ", ", "OnSocketCreated.", sep="")
        return None
    
    def OnSocketClosed(self) -> None:
        """NetBuffer中的socket被外部销毁时,此函数被调用"""
        self.__buf = b""
        import datetime
        print(datetime.datetime.now(), ", ",
              "getpeername=", self.__sock.getpeername(), ", ",
              "getsockname=", self.__sock.getsockname(), ", ", "OnSocketClosed.", sep="")
        return None
    
    def IsAlive(self) -> bool:
        """NetBuffer中的socket是不是还活着,如果被close了,那么此函数返回False"""
        if (self.__sock == None) or (self.__sock.fileno() == -1):
            return False
        return True
    
    def OnDataReceived(self, receivedData) -> None:
        """socket接收数据后,此函数被调用"""
        self.__buf += receivedData
        import datetime
        print(datetime.datetime.now(), ", ",
              "getpeername=", self.__sock.getpeername(), ", ",
              "getsockname=", self.__sock.getsockname(), ", ", receivedData, sep="")
        return None
    
    def OnExceptionCatched(self, ex):
        """捕获异常时,此函数被调用"""
        import datetime
        print(datetime.datetime.now(), ", ",
              "getpeername=", self.__sock.getpeername(), ", ",
              "getsockname=", self.__sock.getsockname(), ", ", ex, sep="")
        return None
###############################
class SelectorTcpSerer(object):
    """使用selectors.DefaultSelector()写的TcpServer"""
    
    def __init__(self, createNetBuffer=NetBuffer.CreateNetBuffer) -> None:
        self.__pairHostPort = None
        self.__listenBacklog = 10
        self.__listenSock = None
        self.__selector = None
        self.__isAlive = True
        self.__createNetBuffer = createNetBuffer  # 可以创建NetBuffer对象(或者它的子类的对象)的一个静态函数
        self.__threadPoolExecutor = None
        self.__maxWorkers = 10  # ThreadPoolExecutor的max_workers
        return None
    
    @property
    def pairHostPort(self):
        return self.__pairHostPort
    
    @pairHostPort.setter
    def pairHostPort(self, new_value) -> None:
        self.__pairHostPort = new_value
        return None
    
    @property
    def listenBacklog(self):
        return self.__listenBacklog
    
    @listenBacklog.setter
    def listenBacklog(self, new_value) -> None:
        self.__listenBacklog = new_value
        return None
    
    @property
    def maxWorkers(self):
        return self.__maxWorkers
    
    @maxWorkers.setter
    def maxWorkers(self, new_value) -> None:
        self.__maxWorkers = new_value
        return None
    
    def Run(self) -> None:
        """参数设定好之后,就可以运行它了"""
        self.__initialize()
        #
        while self.__isAlive:
            tupleList = self.__selector.select(1)
            for key, events in tupleList:
                self.__HandleFileObject(key, events)
        #
        self.__terminate()
        #
        return None
    
    def Close(self) -> bool:
        """调用此函数,关闭这个类,区别在于有没有强制关闭它"""
        self.__isAlive = False
        import time
        for item in (1, 1, 1, 1, 1):
            time.sleep(item)
            if (self.__listenSock == None) and (self.__selector == None):
                return True
            else:
                pass
        # import datetime
        # print(datetime.datetime.now(), ", ", "will force terminate myself!!!", sep="")
        # self.__terminate()  # 暂不支持强制关闭
        return False
    
    def __initialize(self) -> None:
        """命名参考了APR的apr_initialize()函数"""
        # 初始化ThreadPoolExecutor
        import concurrent.futures
        self.__threadPoolExecutor = concurrent.futures.thread.ThreadPoolExecutor(max_workers=self.__maxWorkers)
        # 初始化listenSocket
        import socket
        self.__listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__listenSock.bind(self.__pairHostPort)
        self.__listenSock.listen(self.__listenBacklog)
        # Set the socket to blocking (flag is true) or non-blocking (false).
        # setblocking(True) is equivalent to settimeout(None);
        # setblocking(False) is equivalent to settimeout(0.0).
        self.__listenSock.setblocking(False)
        # 初始化BaseSelector
        import selectors
        self.__selector = selectors.DefaultSelector()
        self.__selector.register(self.__listenSock, (selectors.EVENT_READ | selectors.EVENT_WRITE), None)
        #
        return None
    
    def __terminate(self) -> None:
        """命名参考了APR的apr_terminate()函数"""
        if self.__selector != None:
            # 待删除的fileObj需要先存起来,不然会报错：RuntimeError: dictionary changed size during iteration
            otherList = []
            selectorKeyList = []
            for selectorKey in self.__selector.get_map().values():
                if (self.__listenSock == None) or (selectorKey.fileobj.fileno() != self.__listenSock.fileno()):
                    selectorKeyList.append(selectorKey)
                else:
                    otherList.append(selectorKey)
            # 清理selectors.BaseSelector中的各个SelectorKey,
            for selectorKey in selectorKeyList:
                fileObj = selectorKey.fileobj
                netBuffer = selectorKey.data
                self.__CleanSocket(fileObj, netBuffer, None)
            # 清理其他的selectorKey
            for selectorKey in otherList:
                self.__selector.unregister(selectorKey.fileobj)
            # 关闭selectors.BaseSelector
            self.__selector.close()
            self.__selector = None 
        # 清理监听socket
        if self.__listenSock != None:
            self.__listenSock.close()
            self.__listenSock = None
        # 清理ThreadPoolExecutor
        if self.__threadPoolExecutor != None:
            # Clean-up the resources associated with the Executor.
            self.__threadPoolExecutor.shutdown(wait=True)
            self.__threadPoolExecutor = None
        #
        return None
    
    def __HandleFileObject(self, key, events) -> None:
        """select函数返回的那些个文件对象,此函数就是处理这些文件对象的"""
        import selectors
        fileObj = key.fileobj
        if fileObj.fileno() == self.__listenSock.fileno():
            self.__AcceptFromListenSocket()
        elif events == selectors.EVENT_READ:
            netBuffer = key.data
            self.__RecvDataFromSocket(fileObj, netBuffer)
        elif events == selectors.EVENT_WRITE:
            print("something is error")
        else:
            print("something is error")
        return None
    
    def __AcceptFromListenSocket(self) -> None:
        import selectors
        newSock, peerIpPort = self.__listenSock.accept()
        newSock.setblocking(False)
        peerIpPort = peerIpPort  # 仅仅不想产生"Unused variable: peerIpPort"的警告
        netBuffer = self.__createNetBuffer(newSock)
        self.__selector.register(newSock, selectors.EVENT_READ, netBuffer)
        # 对于accept的socket,其events只可以为selectors.EVENT_READ,
        # 如果设置为(selectors.EVENT_READ | selectors.EVENT_WRITE),它将一直活动下去
        # self.__selector.register(newSock, selectors.EVENT_READ | selectors.EVENT_WRITE, netBuffer)
        return None
    
    def __RecvDataFromSocket(self, fileObj, netBuffer):
        isCleaned = False
        try:
            data = fileObj.recv(4096)
            if data:
                self.__threadPoolExecutor.submit(NetBuffer.OnDataReceived(netBuffer, data))
            else:
                self.__CleanSocket(fileObj, netBuffer, None)
                isCleaned = True
        except (BlockingIOError, ConnectionAbortedError, OSError) as e:
            self.__CleanSocket(fileObj, netBuffer, e)
            isCleaned = True
        except Exception as ex:
            self.__CleanSocket(fileObj, netBuffer, ex)
            isCleaned = True
        finally:
            # 如果使用者在NetBuffer.OnDataReceived函数里面close了这个socket,那么就需要在这里将它清理掉
            if (not netBuffer.IsAlive()) and (not isCleaned):
                self.__CleanSocket(fileObj, netBuffer, None)
        return None
    
    def __CleanSocket(self, fileObj, netBuffer, exceptionInfo=None) -> None:
        import datetime
        if exceptionInfo != None:
            try:
                netBuffer.OnExceptionCatched(exceptionInfo)
            except Exception as ex:
                print(datetime.datetime.now(), ", ", ex, sep="")
        # 你永远也不知道用户会做出来什么事情,所以,用户可能使用的每一个函数,都需要强行捕获所有异常,
        try:
            netBuffer.OnSocketClosed()
        except Exception as ex:
            print(datetime.datetime.now(), ", ", ex, sep="")
        # 如果要清理NetBuffer,需要在这里执行清理操作
        fileObj.close()  # 重复close同一个socket,不会出现异常,
        selectorKey = self.__selector.unregister(fileObj)
        selectorKey = selectorKey
        return None
###############################
def CloseSelectorTcpServer(tcpServer, seconds):
    import time
    time.sleep(seconds)
    rv = tcpServer.Close()
    print("tcpServer.Close() return", rv)
    return None
###############################
if __name__ == "__main__":
    logging.basicConfig(filename="log.log", filemode='w', level=logging.DEBUG,
                        format="%(asctime)s|%(levelname)s|%(name)s|%(process)d|%(thread)d|%(message)s")
    # [%s]->[%(asctime)s],[%d]->[%(thread)d]
    tcpServer = SelectorTcpSerer()
    tcpServer.pairHostPort = ("127.0.0.1", 60000)
    tcpServer.listenBacklog = 10
    import _thread
    _thread.start_new_thread(CloseSelectorTcpServer, (tcpServer, 300))
    tcpServer.Run()
    print("tcpServer.Run() done.")
    exit(0)
