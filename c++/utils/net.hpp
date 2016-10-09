#ifndef NET_HPP
#define NET_HPP

#include <cstdint>//cstdint standard header, uint32_t, int32_t,
#include <set>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/signals2.hpp>
#include <boost/atomic.hpp>
#include <boost/thread.hpp>
#include <boost/asio.hpp>
#include <boost/asio/steady_timer.hpp>
#include <boost/asio/spawn.hpp>

/************************************************************************/
/*                                                                      */
/************************************************************************/
typedef std::shared_ptr<std::string> StdStringPtr;
typedef std::shared_ptr<boost::asio::io_service::work> BoostWorkPtr;
typedef std::shared_ptr<boost::asio::io_service::strand> BoostStrandPtr;
typedef std::shared_ptr<boost::asio::ip::tcp::socket> BoostSocketPtr;
typedef std::shared_ptr<boost::asio::steady_timer> BoostSteadyTimerPtr;
/************************************************************************/
/*                                                                      */
/************************************************************************/
class SendBuffer
{
public:
    SendBuffer();
    ~SendBuffer();
public:
    void Reset();
    void FeedData(const char* data, uint32_t len);
    void TakeData(const char*&data, uint32_t& len);
private:
    const std::size_t m_capacity;
    boost::mutex m_mutex;
    std::string m_bufWait;
    std::string m_bufWork;
    std::size_t m_posWork;//当前的位置,再往前的数据都是被使用过的了,都是过时的数据了
};
/************************************************************************/
/*                                                                      */
/************************************************************************/
class RecvBuffer
{
public:
    RecvBuffer();
    ~RecvBuffer();
public:
    void Reset();
    int AvaliableSpace(char*& dataHead, uint32_t&dataSize);
    void FeedSize(uint32_t len);
    StdStringPtr NextMessage();
private:
    static bool CrOrLf(char c);
    static StdStringPtr ParseMessage(const char* buff, uint32_t& posBeg, uint32_t posEnd);
private:
    const std::size_t m_capacity;
    const std::size_t m_sortSize;//(右边的)剩余空间<=m_sortSize时,进行内存整理
    std::string m_buf;
    std::size_t m_posBeg;
    std::size_t m_posEnd;
};
/************************************************************************/
/*                                                                      */
/************************************************************************/
class RunEngine
{
public:
    RunEngine();
    ~RunEngine();
public:
    int Start(uint16_t numBase, uint16_t numDeal);
    void Stop();
    boost::asio::io_service& BaseIo();
    boost::asio::io_service& DealIo();
    BoostStrandPtr BaseStrandPtr();
    BoostStrandPtr DealStrandPtr();
private:
    boost::asio::io_service m_ioBase;//基础IO
    boost::asio::io_service m_ioDeal;//处理IO
    BoostWorkPtr m_ioBaseWork;
    BoostWorkPtr m_ioDealWork;
    boost::thread_group m_thgp;
};
typedef std::shared_ptr<RunEngine> RunEnginePtr;
/************************************************************************/
/*                                                                      */
/************************************************************************/
class TcpSocket
{
public:
    TcpSocket(boost::asio::io_service& io);
    TcpSocket(BoostSocketPtr sock);
    ~TcpSocket();
public:
    bool IsOpen() const;
    void Close();
    boost::asio::ip::tcp::endpoint LocalEndpoint() const;
    boost::asio::ip::tcp::endpoint RemoteEndpoint() const;
    int Connect(const std::string& address, uint16_t port);
    uint32_t SendData(const char* data, uint32_t len);
    uint32_t SendData(const char* data, uint32_t len, boost::asio::yield_context& yield);
    void SendDataAsync(const char* data, uint32_t len, const boost::function<void(const boost::system::error_code& ec, uint32_t)>& handler);
    uint32_t RecvData(char* data, uint32_t len);
    uint32_t RecvData(char* data, uint32_t len, boost::asio::yield_context& yield);
    void RecvDataAsync(char* data, uint32_t len, const boost::function<void(const boost::system::error_code& ec, uint32_t)>& handler);
private:
    BoostSocketPtr m_socket;
};
typedef std::shared_ptr<TcpSocket> TcpSocketPtr;
/************************************************************************/
/*                                                                      */
/************************************************************************/
class NetConnection;
typedef std::shared_ptr<NetConnection> NetConnectionPtr;
class NetConnection :public std::enable_shared_from_this<NetConnection>
{
public:
    NetConnection(bool callSignal, RunEnginePtr engine);
    NetConnection(bool callSignal, RunEnginePtr engine, BoostSocketPtr sock);
    virtual ~NetConnection();
public:
    const char* LocalAddress() const;
    uint16_t    LocalPort() const;
    const char* RemoteAddress() const;
    uint16_t    RemotePort() const;
    void ResetSignals();
    int Connect(const std::string& peerAddress, uint16_t peerPort);
    int StartWithAccept();
    void Stop();
    uint32_t SendData(const char* data, uint32_t len, bool isSync = false);
public:
    virtual void OnConnected(NetConnectionPtr connection);
    virtual void OnDisconnected(NetConnectionPtr connection, int errorValue, const std::string& errorMessage);
    virtual void OnError(NetConnectionPtr connection, int errorValue, const std::string& errorMessage);
    virtual void OnReceivedData(NetConnectionPtr connection, const char* data, uint32_t len);
    virtual void OnReceivedMessage(NetConnectionPtr connection, StdStringPtr message);
private:
    void ReflushLocalEndpointAndRemoteEndpoint(bool regain);
    void DoReset(bool exceptSignal, bool exceptAddrPort, bool exceptSocket);
    void DoConnect(const boost::system::error_code& ec);
    void DoConnectedEvent();
    void DoDisconnectedEvent(int errorValue, const std::string& errorMsg);
    void DoSendDataTopHalf(bool isContinue);
    void DoSendDataBottomHalf(const boost::system::error_code& ec, uint32_t bytesTransferred, uint32_t bytesTotal);
    void DoSendData(boost::asio::yield_context yield);
    void RunRecvDataEvent();
    void DoRecvData(boost::asio::yield_context yield);
    void HandleOnConnected();
    void HandleOnDisconnected(int errorValue, const std::string& errorMessage);
    void HandleOnError(int errorValue, const std::string& errorMessage);
    void HandleOnReceivedData(const char* data, uint32_t len);
    void HandleOnReceivedMessage(StdStringPtr message);
public:
    boost::signals2::signal<void(NetConnectionPtr connection)> m_onConnected;
    boost::signals2::signal<void(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)> m_onDisconnected;
    boost::signals2::signal<void(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)> m_onError;
    boost::signals2::signal<void(NetConnectionPtr connection, const char* data, uint32_t len)> m_onReceivedData;
    boost::signals2::signal<void(NetConnectionPtr connection, StdStringPtr message)> m_onReceivedMessage;
private:
    const bool m_callSignal;//signal or callback.
    const uint32_t m_reconnectInterval;
    //
    std::string m_localAddress;
    uint16_t    m_localPort;
    std::string m_remoteAddress;
    uint16_t    m_remotePort;
    //
    std::string m_peerAddress;
    uint16_t    m_peerPort;
    //
    boost::atomic_bool m_isSending;
    boost::atomic_bool m_isRecving;
    SendBuffer m_bufSend;
    RecvBuffer m_bufRecv;
    //
    RunEnginePtr m_engine;
    TcpSocketPtr m_socket;
    BoostStrandPtr m_strandSend;
    BoostStrandPtr m_strandRecv;
    BoostSteadyTimerPtr m_timer;
};
/************************************************************************/
/*                                                                      */
/************************************************************************/
class NetConnectionManager
{
public:
    NetConnectionManager();
    ~NetConnectionManager();
public:
    void Reset();
    void Insert(NetConnectionPtr conn);
    void Erase(NetConnectionPtr conn);
    uint32_t Size();
private:
    boost::mutex m_mutex;
    std::set<NetConnectionPtr> m_set;
};
typedef std::shared_ptr<NetConnectionManager> NetConnectionManagerPtr;
/************************************************************************/
/*                                                                      */
/************************************************************************/
class TcpClient;
typedef std::shared_ptr<TcpClient> TcpClientPtr;
class TcpClient :public std::enable_shared_from_this<TcpClient>
{
public:
    TcpClient(uint16_t numBase, uint16_t numDeal);
    TcpClient(RunEnginePtr engine);
    virtual ~TcpClient();
public:
    const char* LocalAddress() const;
    uint16_t    LocalPort() const;
    const char* RemoteAddress() const;
    uint16_t    RemotePort() const;
    int Connect(const std::string& peerAddress, uint16_t peerPort);
    void Stop();
    uint32_t SendData(const char* data, uint32_t len, bool isSync = false);
    virtual void OnConnected(NetConnectionPtr connection);
    virtual void OnDisconnected(NetConnectionPtr connection, int errorValue, const std::string& errorMessage);
    virtual void OnError(NetConnectionPtr connection, int errorValue, const std::string& errorMessage);
    virtual void OnReceivedData(NetConnectionPtr connection, const char* data, uint32_t len);
    virtual void OnReceivedMessage(NetConnectionPtr connection, StdStringPtr message);
private:
    void DoConnectSignals();
    const bool m_myEngine;
    RunEnginePtr m_engine;
    NetConnectionPtr m_connection;
};
/************************************************************************/
/*                                                                      */
/************************************************************************/
class TcpAcceptor;
typedef std::shared_ptr<TcpAcceptor> TcpAcceptorPtr;
class TcpAcceptor :public std::enable_shared_from_this<TcpAcceptor>
{
public:
    TcpAcceptor(bool callSignal, boost::asio::io_service& io);
    ~TcpAcceptor();
public:
    bool IsOpen() const;
    boost::asio::ip::tcp::endpoint LocalEndpoint() const;
    void ResetSignals(); 
    void Stop();
    int Accept(const std::string& address, uint16_t port, uint16_t backlog);
    void OnAccepted(TcpAcceptorPtr acceptor, BoostSocketPtr boostSocket);
    void OnError(TcpAcceptorPtr acceptor, int errorValue, const std::string& errorMessage);
private:
    void DoReset(bool exceptSignal);
    void DoAcceptSocketEvent();
    void DoAcceptSocket(boost::asio::yield_context yield);
    void HandleOnAccepted(BoostSocketPtr boostSocket);
    void HandleOnError(int errorValue, const std::string& errorMessage);
public:
    boost::signals2::signal<void(TcpAcceptorPtr acceptor, BoostSocketPtr boostSocket)> m_onAccepted;
    boost::signals2::signal<void(TcpAcceptorPtr acceptor, int errorValue, const std::string& errorMessage)> m_onError;
private:
    const bool m_callSignal;
    boost::asio::ip::tcp::acceptor m_acceptor;
    boost::atomic_bool m_isAccepting;
};
/************************************************************************/
/*                                                                      */
/************************************************************************/
class TcpServer;
typedef std::shared_ptr<TcpServer> TcpServerPtr;
class TcpServer :public std::enable_shared_from_this<TcpServer>
{
public:
    TcpServer(uint16_t numBase, uint16_t numDeal);
    TcpServer(RunEnginePtr engine);
    virtual ~TcpServer();
public:
    const char* LocalAddress() const;
    uint16_t    LocalPort() const;
    bool IsOpen() const;
    int Accept(const std::string& address, uint16_t port, int backlog);
    void Close();
    virtual void OnConnected(NetConnectionPtr connection);
    virtual void OnDisconnected(NetConnectionPtr connection, int errorValue, const std::string& errorMessage);
    virtual void OnError(NetConnectionPtr connection, int errorValue, const std::string& errorMessage);
    virtual void OnReceivedData(NetConnectionPtr connection, const char* data, uint32_t len);
    virtual void OnReceivedMessage(NetConnectionPtr connection, StdStringPtr message);
private:
    void ReflushLocalEndpoint(bool regain);
    void DataMemSignalsConnOrDisconn(bool isConnect);
    void DoReset();
    void DoOnAcceptedSocket(BoostSocketPtr sock);
    void HandleOnConnected(NetConnectionPtr connection);
    void HandleOnDisconnected(NetConnectionPtr connection, int errorValue, const std::string& errorMessage);
private:
    std::string m_localAddress;
    uint16_t    m_localPort;
    //
    const bool m_myEngine;
    RunEnginePtr m_engine;
    TcpAcceptorPtr m_acceptor;
    NetConnectionManagerPtr m_manager;
};
/************************************************************************/
/*                                                                      */
/************************************************************************/

#include "net_impl.hpp"

#endif//NET_HPP
