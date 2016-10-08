#ifndef NET_IMPL_HPP
#define NET_IMPL_HPP

#include "net.hpp"

/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //SendBuffer
SendBuffer::SendBuffer() :m_capacity(1024 * 64)
{
    Reset();
}

SendBuffer::~SendBuffer(){}

void SendBuffer::Reset()
{
    boost::lock_guard<boost::mutex> lg(m_mutex);
    m_bufWait.clear();
    m_bufWork.clear();
    m_posWork = 0;
    if (m_bufWait.capacity() < m_capacity)
        m_bufWait.reserve(m_capacity);
    if (m_bufWork.capacity() < m_capacity)
        m_bufWork.reserve(m_capacity);
}

void SendBuffer::FeedData(const char* data, uint32_t len)
{
    boost::lock_guard<boost::mutex> lg(m_mutex);
    m_bufWait.append(data, len);
}


//有安全隐患:指针给外部了,如果外部没有及时使用数据的话,数据可能被内部改动,如果外部强制修改数据的话,数据会有问题
//所以,调用此函数后,在没有使用完得到的数据之前,这个类禁止其他操作,
void SendBuffer::TakeData(const char*&data, uint32_t& len)
{
    boost::lock_guard<boost::mutex> lg(m_mutex);
    if (m_bufWork.size() == m_posWork)
    {
        std::swap(m_bufWork, m_bufWait);
        m_posWork = 0;
        m_bufWait.clear();
        //
        data = m_bufWork.c_str();
        len = m_bufWork.size();
        m_posWork += len;
    }
    else
    {
        data = &m_bufWork[m_posWork];
        len = m_bufWork.size() - m_posWork;
        m_posWork += len;
    }
}
#endif//SendBuffer
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //RecvBuffer
RecvBuffer::RecvBuffer() :m_capacity(1024 * 512), m_sortSize(1024 * 4)
{
    Reset();
}

RecvBuffer::~RecvBuffer(){}

void RecvBuffer::Reset()
{
    if (m_buf.size() < m_capacity)
    {
        m_buf.clear();//resize时,可能会对老的数据执行copy操作,clear后就不会copy了,
        m_buf.resize(m_capacity);
    }
    m_posBeg = 0;
    m_posEnd = 0;
}

int RecvBuffer::AvaliableSpace(char*& dataHead, uint32_t& dataSize)
{
    int retVal = 0;
    do
    {
        //(右边的)剩余空间>m_sortSize时,就直接使用剩余空间
        if (m_posEnd + m_sortSize < m_buf.size())
        {
            dataHead = &m_buf[m_posEnd];
            dataSize = m_buf.size() - m_posEnd;
            retVal = 0;
            break;
        }
        //(右边的)剩余空间<=m_sortSize时,就整理内存,然后使用整理后的剩余空间
        if (0 < m_posBeg)
        {
            memcpy(&m_buf[0], &m_buf[m_posBeg], m_posEnd - m_posBeg);
            m_posEnd = m_posEnd - m_posBeg;
            m_posBeg = 0;
            retVal = AvaliableSpace(dataHead, dataSize);
            break;
        }
        //整理内存失败,
        dataHead = &m_buf[m_posEnd];
        dataSize = m_buf.size() - m_posEnd;
        retVal = (dataSize > 0 ? 0 : -1);
    } while (false);
    return retVal;
}

//TakeData函数不允许修改内存(m_buf)(整理内存)
void RecvBuffer::FeedSize(uint32_t len)
{
    assert(m_posEnd + len <= m_buf.size());
    m_posEnd += len;
}

StdStringPtr RecvBuffer::NextMessage()
{
    StdStringPtr msg = RecvBuffer::ParseMessage(m_buf.c_str(), m_posBeg, m_posEnd);
    assert(m_posBeg <= m_posEnd);
    return msg;
}

bool RecvBuffer::CrOrLf(char c)
{
    return ('\r' == c || '\n' == c) ? true : false;
}

//解析原则:当看到\r或\n时,忽略掉前面的\r和\n,最前面需要是END字符串,END前面的就是json字符串,
//然后偏移到第一个"既不是\r也不是\n"的地方,作为下一个json字符串的起点,
StdStringPtr RecvBuffer::ParseMessage(const char* buff, uint32_t& posBeg, uint32_t posEnd)
{
    StdStringPtr msg = nullptr;
    int32_t msgBeg = -1, msgEnd = -1;//<0,表示未初始化
    for (uint32_t i = posBeg; i < posEnd; ++i)
    {
        if (msgBeg < 0 && CrOrLf(buff[i]) == false)
        {
            msgBeg = i;
            continue;
        }
        //for循环里面有(i<posEnd),不用担心i超过posEnd的问题,
        //已经有msgBeg这个位置了,所以不用担心(i-1)越界的问题,
        if (CrOrLf(buff[i]) == true && CrOrLf(buff[i - 1]) == false &&
            msgBeg <= int32_t(i - 3) && memcmp(buff + i - 3, "END", 3) == 0)
        {
            msgEnd = i - 3;//一条消息不包括END结束符
            msg = std::make_shared<std::string>(buff + msgBeg, msgEnd - msgBeg);
            posBeg = i;
            break;
        }
    }
    return msg;
}
#endif//RecvBuffer
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //RunEngine

RunEngine::RunEngine(){}

//dtor函数会自行清理掉一切,不用担心这个类的清理问题,
RunEngine::~RunEngine()
{
    Stop();
}

int RunEngine::Start(uint16_t numBase, uint16_t numDeal)
{
    if (m_ioBaseWork || m_ioDealWork)//如果已经启动过了,就不可以再次启动了
        return -1;

    m_ioBaseWork = std::make_shared<boost::asio::io_service::work>(m_ioBase);
    m_ioDealWork = std::make_shared<boost::asio::io_service::work>(m_ioDeal);

    boost::system::error_code ec;
    for (uint16_t i = 0; i < numBase; ++i)
        m_thgp.create_thread(boost::bind(&boost::asio::io_service::run, boost::ref(m_ioBase), ec));
    for (uint16_t i = 0; i < numDeal; ++i)
        m_thgp.create_thread(boost::bind(&boost::asio::io_service::run, boost::ref(m_ioDeal), ec));

    return 0;
}

//没有Reset函数,因为没法清理掉boost::asio::io_service里面残留的那些handler,调用Stop之后就不建议再用了,
void RunEngine::Stop()
{
    m_ioBaseWork.reset();
    m_ioDealWork.reset();
    if (true)
    {
        m_ioBase.stop();
        m_ioBase.reset();
        m_ioDeal.stop();
        m_ioDeal.reset();
    }
}

boost::asio::io_service& RunEngine::BaseIo()
{
    return m_ioBase;
}

boost::asio::io_service& RunEngine::DealIo()
{
    return m_ioDeal;
}

BoostStrandPtr RunEngine::BaseStrandPtr()
{
    return std::make_shared<boost::asio::io_service::strand>(m_ioBase);
}

BoostStrandPtr RunEngine::DealStrandPtr()
{
    return std::make_shared<boost::asio::io_service::strand>(m_ioDeal);
}
#endif//RunEngine
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //TcpSocket
TcpSocket::TcpSocket(boost::asio::io_service& io)
{
    m_socket = std::make_shared<boost::asio::ip::tcp::socket>(io);
}

//如果传进来了socket,那么可能是server端accept的socket,所以不管怎样,保持socket的状态不要做close等其他操作,
TcpSocket::TcpSocket(BoostSocketPtr sock)
{
    assert(sock);//不能是空指针呀,
    m_socket = sock;
}

TcpSocket::~TcpSocket()
{
    Close();
    m_socket.reset();
}

bool TcpSocket::IsOpen() const
{
    return m_socket->is_open();
}

void TcpSocket::Close()
{
    m_socket->close();
}

boost::asio::ip::tcp::endpoint TcpSocket::LocalEndpoint() const
{
    return m_socket->local_endpoint();
}

boost::asio::ip::tcp::endpoint TcpSocket::RemoteEndpoint() const
{
    return m_socket->remote_endpoint();
}

int TcpSocket::Connect(const std::string& address, uint16_t port)
{
    if (IsOpen())
        return -1;

    boost::asio::ip::tcp::resolver r(m_socket->get_io_service());
    boost::asio::ip::tcp::resolver::query q(address, boost::lexical_cast<std::string>(port));
    auto itr = r.resolve(q);
    boost::system::error_code ec = boost::asio::error::host_not_found;
    for (decltype(itr) end; ec && itr != end; ++itr)
    {
        m_socket->close();
        m_socket->connect(*itr, ec);
    }
    //
    do
    {
        if (ec)
            break;
        m_socket->set_option(boost::asio::ip::tcp::no_delay(true), ec);
        if (ec)
            break;
    } while (false);
    //socket只要被打开了,is_open()就是true,并不是连接上了才是true,
    if (ec)
        Close();

    return (ec ? -1 : 0);
}

uint32_t TcpSocket::SendData(const char* data, uint32_t len)
{
    return m_socket->send(boost::asio::buffer(data, len));
}

uint32_t TcpSocket::SendData(const char* data, uint32_t len, boost::asio::yield_context& yield)
{
    return m_socket->async_send(boost::asio::buffer(data, len), yield);
}

void TcpSocket::SendDataAsync(const char* data, uint32_t len, const boost::function<void(const boost::system::error_code & ec, uint32_t bytesTransferred)>& handler)
{
    m_socket->async_send(boost::asio::buffer(data, len), handler);
}

uint32_t TcpSocket::RecvData(char* data, uint32_t len)
{
    return m_socket->receive(boost::asio::buffer(data, len));
}

uint32_t TcpSocket::RecvData(char* data, uint32_t len, boost::asio::yield_context& yield)
{
    return m_socket->async_receive(boost::asio::buffer(data, len), yield);
}

void TcpSocket::RecvDataAsync(char* data, uint32_t len, const boost::function<void(const boost::system::error_code & ec, uint32_t bytesTransferred)>& handler)
{
    m_socket->async_receive(boost::asio::buffer(data, len), handler);
}
#endif//TcpSocket
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //NetConnection
NetConnection::NetConnection(bool callSignal, RunEnginePtr engine) :m_callSignal(callSignal), m_reconnectInterval(5)
{
    m_engine = engine;
    m_socket = TcpSocketPtr(new TcpSocket(m_engine->BaseIo()));
    m_strandSend = m_engine->BaseStrandPtr();
    m_strandRecv = m_engine->BaseStrandPtr();
    m_timer = std::make_shared<boost::asio::steady_timer>(m_engine->BaseIo());
    DoReset(false, false, false, false);
}

NetConnection::NetConnection(bool callSignal, RunEnginePtr engine, BoostSocketPtr sock) :m_callSignal(callSignal), m_reconnectInterval(5)
{
    assert(&engine->BaseIo() == &sock->get_io_service());
    m_engine = engine;
    m_socket = TcpSocketPtr(new TcpSocket(sock));
    m_strandSend = m_engine->BaseStrandPtr();
    m_strandRecv = m_engine->BaseStrandPtr();
    m_timer = std::make_shared<boost::asio::steady_timer>(m_engine->BaseIo());
    //如果是自己生成的socket,那就无所谓了,
    //如果是server端accept的socket,那么就需要跳过socket的初始化了,
    //综上,在这个构造函数初始化过程中,socket保持原样的好,
    DoReset(false, false, false, true);
}

NetConnection::~NetConnection()
{
    DoReset(false, false, false, false);
    m_engine.reset();
    m_socket.reset();
    m_strandRecv.reset();
    m_strandSend.reset();
    m_timer.reset();
}

const char* NetConnection::LocalAddress() const
{
    return m_localAddress.c_str();
}

uint16_t NetConnection::LocalPort() const
{
    return m_localPort;
}

const char* NetConnection::RemoteAddress() const
{
    return m_remoteAddress.c_str();
}

uint16_t NetConnection::RemotePort() const
{
    return m_remotePort;
}

int NetConnection::Start(const std::string& peerAddress, uint16_t peerPort)
{
    if (m_socket->IsOpen())
    {
        int errorValue = -1;
        std::string errorMsg = "套接字已打开,请关闭套接字后再启动.";
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), errorValue, errorMsg));
        return errorValue;
    }
    else
    {
        //TODO:执行了一次Connect连接到A,在连接的过程中(IsOpen在true和false的交替中,同时没有连接成功),
        //又执行了Connect连接到B,然后连接到A成功了,并没有连接到B,此情况没有考虑,
        m_peerAddress = peerAddress;
        m_peerPort = peerPort;
        m_engine->BaseIo().post(boost::bind(&NetConnection::DoConnect, shared_from_this(), boost::system::error_code()));
        return 0;
    }
}

int NetConnection::Start()
{
    if (m_socket->IsOpen() == false)
    {
        int errorValue = -1;
        std::string errorMsg = "套接字已关闭,无法启动.";
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), errorValue, errorMsg));
        return errorValue;
    }
    if (m_peerAddress.empty() == false || m_peerPort)
    {
        int errorValue = -1;
        std::string errorMsg = "有问题吧?这个函数用于TcpServer在accept之后的启动.";
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), errorValue, errorMsg));
        return errorValue;
    }
    DoConnectedEvent();
    return 0;
}

void NetConnection::Stop()
{
    DoReset(true, false, true, false);
}

uint32_t NetConnection::SendData(const char* data, uint32_t len, bool isSync /* = false */)
{
    if (isSync)
    {
        return m_socket->SendData(data, len);
    }
    else
    {
        m_bufSend.FeedData(data, len);
        DoSendDataTopHalf(false);
        return len;
    }
}

void NetConnection::OnConnected(NetConnectionPtr connection)
{
    std::string str = (boost::format("[NetConnection::OnConnected   ],")).str();
    std::cout << str << std::endl;
}

void NetConnection::OnDisconnected(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)
{
    std::string str = (boost::format("[NetConnection::OnDisconnected], %|d|, %|s|,") % errorValue%errorMessage).str();
    std::cout << str << std::endl;
}

void NetConnection::OnError(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)
{
    std::string str = (boost::format("[NetConnection::OnError       ], %|d|, %|s|,") % errorValue%errorMessage).str();
    std::cout << str << std::endl;
}

void NetConnection::OnReceivedData(NetConnectionPtr connection, const char* data, uint32_t len)
{
    std::string str = (boost::format("[NetConnection::OnReceivedData], %|d|, [%|s|],") % len%data).str();
    std::cout << str << std::endl;
}

void NetConnection::OnReceivedMsg(NetConnectionPtr connection, StdStringPtr message)
{
    std::string str = (boost::format("[NetConnection::OnReceivedMsg ], %|d|, [%|s|],") % message->size() % *message).str();
    std::cout << str << std::endl;
}

//需要m_isRecving的理由(几乎不可能):接收线程刚刚async_recv了数据,还没进行处理呢,程序就主动close了socket,然后立即进行connect并成功连接了,
//然后接收线程处理完了,然后开始async_recv,因为socket重新连接成功了,所以接收线程会正常处理,而不是退出,
//但是重连成功了,自然要重新启动一个接收线程,此时接收线程就有两个了,就会出问题了,
//m_isRecving和m_isSending,建议只在创建对象时初始化一次,以后就不要再修改了(通过DoReset等),而是让逻辑自行修改,
void NetConnection::DoReset(bool exceptSignal, bool exceptAddrPort, bool exceptSendRecvFlag, bool exceptSocket)
{
    if (!exceptSignal)
    {
        m_onConnected.disconnect_all_slots();
        m_onDisconnected.disconnect_all_slots();
        m_onError.disconnect_all_slots();
        m_onReceivedData.disconnect_all_slots();
        m_onReceivedMessage.disconnect_all_slots();
    }
    //m_callSignal,const,不处理
    //m_reconnectInterval,const,不处理
    ReflushLocalEndpointAndRemoteEndpoint(false);//DoReset函数只会将它刷成空,要刷新成最新的数据,请手动刷新,
    //
    if (!exceptAddrPort)
    {
        m_peerAddress = "";
        m_peerPort = 0;
    }
    //
    if (!exceptSendRecvFlag)
    {//m_isRecving和m_isSending,建议只在创建对象时初始化一次,以后就不要再修改了(通过DoReset等),而是让逻辑自行修改,
        m_isSending = false;
        m_isRecving = false;
    }
    //
    m_bufSend.Reset();
    m_bufRecv.Reset();
    //
    //m_engine是外部送进来的运行发动机,不进行任何处理,
    if (!exceptSocket)
        m_socket->Close();
    //m_strandSend不处理
    //m_strandRecv不处理
    m_timer->cancel();
}

void NetConnection::ReflushLocalEndpointAndRemoteEndpoint(bool regain)
{
    if (regain)
    {
        m_localAddress = m_socket->LocalEndpoint().address().to_string();
        m_localPort = m_socket->LocalEndpoint().port();
        m_remoteAddress = m_socket->RemoteEndpoint().address().to_string();
        m_remotePort = m_socket->RemoteEndpoint().port();
    }
    else
    {
        m_localAddress = "";
        m_localPort = 0;
        m_remoteAddress = "";
        m_remotePort = 0;
    }
}

void NetConnection::DoConnect(const boost::system::error_code& ec)
{
    if (ec)
    {
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), ec.value(), ec.message()));
        return;
    }
    if (m_socket->IsOpen())
    {
        int errorValue = -1;
        std::string errorMsg = "套接字已经打开,请关闭套接字后再尝试连接.";
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), errorValue, errorMsg));
        return;
    }
    if (m_peerAddress.empty() || 0 == m_peerPort)
    {
        int errorValue = -1;
        std::string errorMsg = (boost::format("peer_endpoint为无效值,m_peerAddress=[%1%],m_peerPort=[%2%]") % m_peerAddress%m_peerPort).str();
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), errorValue, errorMsg));
        return;
    }
    if (m_socket->Connect(m_peerAddress, m_peerPort) == 0)
    {
        DoConnectedEvent();
        return;
    }
    else
    {
        int errorValue = -1;
        std::string errorMsg = "连接失败,稍后将重新连接.";
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), errorValue, errorMsg));

        m_timer->expires_from_now(std::chrono::seconds(m_reconnectInterval));
        m_timer->async_wait(boost::bind(&NetConnection::DoConnect, shared_from_this(), boost::asio::placeholders::error));
        //async_wait()异步等待的handler要求形式必须是:void handler(const boost::system::error_code& ec);
        //此处我们使用boost::asio::placeholders::error占位符传递错误码,
    }
}

void NetConnection::DoConnectedEvent()
{
    DoReset(true, true, true, true);
    ReflushLocalEndpointAndRemoteEndpoint(true);
    RunRecvDataEvent();
    m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnConnected, shared_from_this()));
}

//因为某些原因,需要执行断开操作,
void NetConnection::DoDisconnectedEvent(int errorValue, const std::string& errorMsg)
{
    DoReset(true, true, true, false);
    ReflushLocalEndpointAndRemoteEndpoint(false);
    m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnDisconnected, shared_from_this(), errorValue, errorMsg));
    //断线重连
    m_timer->expires_from_now(std::chrono::seconds(m_reconnectInterval));
    m_timer->async_wait(boost::bind(&NetConnection::DoConnect, shared_from_this(), boost::asio::placeholders::error));
}

void NetConnection::DoSendDataTopHalf(bool isContinue)
{
    if (m_isSending)
    {//已经有一个线程正在发送中,然后进来了一个新的发送线程,那么这个新的发送线程要直接退出,
        if (!isContinue)
            return;
    }
    else
    {
        m_isSending = true;
    }

    const char* data = nullptr;
    uint32_t len = 0;
    m_bufSend.TakeData(data, len);
    if (!len)
    {//如果没有要发送的数据,就直接退出,
        m_isSending = false;
        return;
    }

    m_socket->SendDataAsync(data, len,
        /*1*/m_strandSend->wrap(
        /*2*/boost::bind(&NetConnection::DoSendDataBottomHalf, shared_from_this(), boost::asio::placeholders::error, boost::asio::placeholders::bytes_transferred, len)
        /*2*/)/*1*/);
}

void NetConnection::DoSendDataBottomHalf(const boost::system::error_code& ec, uint32_t bytesTransferred, uint32_t bytesTotal)
{
    if (ec)
    {
        m_isSending = false;
        DoDisconnectedEvent(ec.value(), ec.message());
        return;
    }
    if (bytesTransferred != bytesTotal)
    {
        m_isSending = false;
        int errorValue = -1;
        std::string errorMsg = "总共要发送的字节数与已发送的字节数不符.";
        DoDisconnectedEvent(errorValue, errorMsg);
        return;
    }
    DoSendDataTopHalf(true);
}

//采用协程重写DoSendDataTopHalf()和DoSendDataBottomHalf()函数.
void NetConnection::DoSendData(boost::asio::yield_context yield)
{
    if (m_isSending)
    {
        return;
    }
    else
    {
        m_isSending = true;
    }

    boost::system::error_code ec;
    const char* data = nullptr;
    uint32_t len = 0;
    uint32_t bytesTransferred = 0;
    while (m_isSending)
    {
        m_bufSend.TakeData(data, len);
        if (!len)
        {//如果没有要发送的数据,就直接退出,
            m_isSending = false;
            break;
        }
        bytesTransferred = m_socket->SendData(data, len, yield[ec]);
        if (ec)
        {
            m_isSending = false;
            DoDisconnectedEvent(ec.value(), ec.message());
            break;
        }
        if (bytesTransferred != len)
        {
            m_isSending = false;
            int errorValue = -1;
            std::string errorMsg = "总共要发送的字节数与已发送的字节数不符.";
            DoDisconnectedEvent(errorValue, errorMsg);
            break;
        }
    }
    m_isSending = false;
}

void NetConnection::RunRecvDataEvent()
{
    boost::asio::spawn(*m_strandRecv, boost::bind(&NetConnection::DoRecvData, shared_from_this(), _1));
    //spawn()函数产生yield_context对象,再传递给使用yield_context的函数,
    //此处是DoRecvData函数,其中bind的占位符_1将yield_context对象传递给DoRecvData函数,
}

void NetConnection::DoRecvData(boost::asio::yield_context yield)
{
    if (m_isRecving)
    {
        int errorValue = -1;
        std::string errorMsg = "已经有线程正在接收数据,即将退出此接收线程.";
        m_engine->BaseIo().post(boost::bind(&NetConnection::HandleOnError, shared_from_this(), errorValue, errorMsg));
        return;
    }
    else
    {
        m_isRecving = true;
    }

    char* dataHead = nullptr;
    uint32_t dataSize = 0;
    boost::system::error_code ec;
    uint32_t recvLen = 0;
    StdStringPtr msg;
    while (m_isRecving)
    {
        if (m_bufRecv.AvaliableSpace(dataHead, dataSize) != 0)
        {
            m_isRecving = false;
            int errorValue = -1;
            std::string errorMsg = "RecvBuffer有问题.";
            DoDisconnectedEvent(errorValue, errorMsg);
            break;
        }
        recvLen = m_socket->RecvData(dataHead, dataSize, yield[ec]);
        if (ec)
        {
            m_isRecving = false;
            DoDisconnectedEvent(ec.value(), ec.message());
            break;
        }
        //
        HandleOnReceivedData(dataHead, recvLen);
        //
        m_bufRecv.FeedSize(recvLen);
        while (msg = m_bufRecv.NextMessage())
            m_engine->DealIo().post(boost::bind(&NetConnection::HandleOnReceivedMessage, shared_from_this(), msg));
    }
    m_isRecving = false;
}

void NetConnection::HandleOnConnected()
{
    if (m_callSignal)
        m_onConnected(shared_from_this());
    else
        OnConnected(shared_from_this());
}

void NetConnection::HandleOnDisconnected(int errorValue, const std::string& errorMessage)
{
    if (m_callSignal)
        m_onDisconnected(shared_from_this(), errorValue, errorMessage);
    else
        OnDisconnected(shared_from_this(), errorValue, errorMessage);
}

void NetConnection::HandleOnError(int errorValue, const std::string& errorMessage)
{
    if (m_callSignal)
        m_onError(shared_from_this(), errorValue, errorMessage);
    else
        OnError(shared_from_this(), errorValue, errorMessage);
}

void NetConnection::HandleOnReceivedData(const char* data, uint32_t len)
{
    if (m_callSignal)
        m_onReceivedData(shared_from_this(), data, len);
    else
        OnReceivedData(shared_from_this(), data, len);
}

void NetConnection::HandleOnReceivedMessage(StdStringPtr message)
{
    if (m_callSignal)
        m_onReceivedMessage(shared_from_this(), message);
    else
        OnReceivedMsg(shared_from_this(), message);
}
#endif//NetConnection
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //NetConnectionManager
NetConnectionManager::NetConnectionManager(){}

NetConnectionManager::~NetConnectionManager()
{
    Reset();
}

void NetConnectionManager::Reset()
{
    boost::lock_guard<boost::mutex> lg(m_mutex);
    for (auto& node : m_set)
    {
        node->Stop();
        //
        node->m_onConnected.disconnect_all_slots();
        node->m_onDisconnected.disconnect_all_slots();
        node->m_onError.disconnect_all_slots();
        node->m_onReceivedData.disconnect_all_slots();
        node->m_onReceivedMessage.disconnect_all_slots();
    }
    m_set.clear();
}

void NetConnectionManager::Insert(NetConnectionPtr conn)
{
    boost::lock_guard<boost::mutex> lg(m_mutex);
    m_set.insert(conn);
}

void NetConnectionManager::Erase(NetConnectionPtr conn)
{
    boost::lock_guard<boost::mutex> lg(m_mutex);
    m_set.erase(conn);
}

uint32_t NetConnectionManager::Size()
{
    boost::lock_guard<boost::mutex> lg(m_mutex);
    return m_set.size();
}
#endif//NetConnectionManager
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //TcpClient

TcpClient::TcpClient(uint16_t numBase, uint16_t numDeal) :m_myEngine(true)
{
    m_engine = RunEnginePtr(new RunEngine);
    m_engine->Start(numBase, numDeal);
    m_connection = std::make_shared<NetConnection>(true, m_engine);
    if (true)
    {
        m_connection->m_onConnected.connect(boost::bind(&TcpClient::OnConnected, this, _1));
        m_connection->m_onDisconnected.connect(boost::bind(&TcpClient::OnDisconnected, this, _1, _2, _3));
        m_connection->m_onError.connect(boost::bind(&TcpClient::OnError, this, _1, _2, _3));
        m_connection->m_onReceivedData.connect(boost::bind(&TcpClient::OnReceivedData, this, _1, _2, _3));
        m_connection->m_onReceivedMessage.connect(boost::bind(&TcpClient::OnReceivedMessage, this, _1, _2));
    }
}

TcpClient::TcpClient(RunEnginePtr engine) :m_myEngine(false)
{
    m_engine = engine;
    m_connection = NetConnectionPtr(new NetConnection(true, m_engine));
    if (true)
    {
        m_connection->m_onConnected.connect(boost::bind(&TcpClient::OnConnected, this, _1));
        m_connection->m_onDisconnected.connect(boost::bind(&TcpClient::OnDisconnected, this, _1, _2, _3));
        m_connection->m_onError.connect(boost::bind(&TcpClient::OnError, this, _1, _2, _3));
        m_connection->m_onReceivedData.connect(boost::bind(&TcpClient::OnReceivedData, this, _1, _2, _3));
        m_connection->m_onReceivedMessage.connect(boost::bind(&TcpClient::OnReceivedMessage, this, _1, _2));
    }
}

TcpClient::~TcpClient()
{
    if (m_myEngine)
        m_engine->Stop();
    m_connection->Stop();
    if (true)
    {
        m_connection->m_onConnected.disconnect_all_slots();
        m_connection->m_onDisconnected.disconnect_all_slots();
        m_connection->m_onError.disconnect_all_slots();
        m_connection->m_onReceivedData.disconnect_all_slots();
        m_connection->m_onReceivedMessage.disconnect_all_slots();
    }
    m_engine.reset();
    m_connection.reset();
}

const char* TcpClient::LocalAddress() const
{
    return m_connection->LocalAddress();
}

uint16_t TcpClient::LocalPort() const
{
    return m_connection->LocalPort();
}

const char* TcpClient::RemoteAddress() const
{
    return m_connection->RemoteAddress();
}

uint16_t TcpClient::RemotePort() const
{
    return m_connection->RemotePort();
}

void TcpClient::Reset()
{
    m_connection->Stop();
}

int TcpClient::Connect(const std::string& peerAddress, uint16_t peerPort)
{
    return m_connection->Start(peerAddress, peerPort);
}

uint32_t TcpClient::SendData(const char* data, uint32_t len, bool isSync /* = false */)
{
    return m_connection->SendData(data, len, isSync);
}

void TcpClient::OnConnected(NetConnectionPtr connection)
{
    std::string str = (boost::format("[TcpClient::OnConnected   ], %|p|,") % connection.get()).str();
    std::cout << str << std::endl;
}

void TcpClient::OnDisconnected(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)
{
    std::string str = (boost::format("[TcpClient::OnDisconnected], %|p|, %|d|, %|s|,") % connection.get() % errorValue%errorMessage).str();
    std::cout << str << std::endl;
}

void TcpClient::OnError(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)
{
    std::string str = (boost::format("[TcpClient::OnError       ], %|p|, %|d|, %|s|,") % connection.get() % errorValue%errorMessage).str();
    std::cout << str << std::endl;
}

void TcpClient::OnReceivedData(NetConnectionPtr connection, const char* data, uint32_t len)
{
    std::string str = (boost::format("[TcpClient::OnReceivedData], %|p|, %|d|, [%|s|],") % connection.get() % len%data).str();
    std::cout << str << std::endl;
}

void TcpClient::OnReceivedMessage(NetConnectionPtr connection, StdStringPtr message)
{
    std::string str = (boost::format("[TcpClient::OnReceivedMsg ], %|p|, %|d|, [%|s|],") % connection.get() % message->size() % *message).str();
    std::cout << str << std::endl;
}
#endif//TcpClient
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //TcpAcceptor
TcpAcceptor::TcpAcceptor(bool callSignal, boost::asio::io_service& io)
:m_callSignal(callSignal), m_acceptor(io)
{
    DoReset(false, false);
}

TcpAcceptor::~TcpAcceptor()
{
    DoReset(false, false);
}

bool TcpAcceptor::IsOpen() const
{
    return m_acceptor.is_open();
}

boost::asio::ip::tcp::endpoint TcpAcceptor::LocalEndpoint() const
{
    return m_acceptor.local_endpoint();
}

void TcpAcceptor::Stop()
{
    DoReset(true, true);
}

int TcpAcceptor::Start(const std::string& address, uint16_t port, uint16_t backlog)
{
    if (IsOpen())
    {
        int errorValue = -1;
        std::string errorMsg = "监听套接字已打开,请关闭后再尝试.";
        m_acceptor.get_io_service().post(boost::bind(&TcpAcceptor::HandleOnError, shared_from_this(), errorValue, errorMsg));
        return errorValue;
    }
    boost::asio::ip::address addr = boost::asio::ip::address::from_string(address);
    boost::asio::ip::tcp::endpoint ep(addr, port);
    boost::system::error_code ec;
    if (m_acceptor.open(ep.protocol(), ec))
    {
        m_acceptor.get_io_service().post(boost::bind(&TcpAcceptor::HandleOnError, shared_from_this(), ec.value(), ec.message()));
        return ec.value();
    }
    if (m_acceptor.bind(ep, ec))
    {
        m_acceptor.get_io_service().post(boost::bind(&TcpAcceptor::HandleOnError, shared_from_this(), ec.value(), ec.message()));
        return ec.value();
    }
    if (m_acceptor.listen(backlog, ec))
    {
        m_acceptor.get_io_service().post(boost::bind(&TcpAcceptor::HandleOnError, shared_from_this(), ec.value(), ec.message()));
        return ec.value();
    }
    DoAcceptSocketEvent();
    return 0;
}

void TcpAcceptor::OnAccepted(TcpAcceptorPtr acceptor, BoostSocketPtr boostSocket)
{
    std::string str = (boost::format("[TcpAcceptor::OnAccepted], %|p|, %|p|,") % acceptor.get() % boostSocket.get()).str();
    std::cout << str << std::endl;
}

void TcpAcceptor::OnError(TcpAcceptorPtr acceptor, int errorValue, const std::string& errorMessage)
{
    std::string str = (boost::format("[TcpAcceptor::OnError   ], %|p|, %|d|, %|s|,") % acceptor.get() % errorValue%errorMessage).str();
    std::cout << str << std::endl;
}

void TcpAcceptor::DoReset(bool exceptSignal, bool exceptAcceptFlag)
{
    if (!exceptSignal)
    {
        m_onAccepted.disconnect_all_slots();
        m_onError.disconnect_all_slots();
    }
    //m_callSignal,const,不处理,
    m_acceptor.close();
    if (!exceptAcceptFlag)
    {
        m_isAccepting = false;
    }
}

void TcpAcceptor::DoAcceptSocketEvent()
{
    boost::asio::spawn(m_acceptor.get_io_service(), boost::bind(&TcpAcceptor::DoAcceptSocket, shared_from_this(), _1));
}

void TcpAcceptor::DoAcceptSocket(boost::asio::yield_context yield)
{
    if (m_isAccepting)
    {
        int errorValue = -1;
        std::string errorMessage = "已有线程正在accept,即将退出此线程.";
        m_acceptor.get_io_service().post(boost::bind(&TcpAcceptor::HandleOnError, shared_from_this(), errorValue, errorMessage));
        return;
    }
    else
    {
        m_isAccepting = true;
    }

    boost::system::error_code ec;
    BoostSocketPtr boostSocket;
    while (m_isAccepting)
    {
        boostSocket = std::make_shared<boost::asio::ip::tcp::socket>(m_acceptor.get_io_service());
        m_acceptor.async_accept(*boostSocket, yield[ec]);
        if (ec)
        {
            m_isAccepting = false;
            m_acceptor.get_io_service().post(boost::bind(&TcpAcceptor::HandleOnError, shared_from_this(), ec.value(), ec.message()));
            DoReset(true, true);
            break;
        }
        m_acceptor.get_io_service().post(boost::bind(&TcpAcceptor::HandleOnAccepted, shared_from_this(), boostSocket));
    }
    m_isAccepting = false;
}

void TcpAcceptor::HandleOnAccepted(BoostSocketPtr boostSocket)
{
    if (m_callSignal)
        m_onAccepted(shared_from_this(), boostSocket);
    else
        OnAccepted(shared_from_this(), boostSocket);
}

void TcpAcceptor::HandleOnError(int errorValue, const std::string& errorMessage)
{
    if (m_callSignal)
        m_onError(shared_from_this(), errorValue, errorMessage);
    else
        OnError(shared_from_this(), errorValue, errorMessage);
}
#endif//TcpAcceptor
/************************************************************************/
/*                                                                      */
/************************************************************************/
#if 1 //TcpServer
TcpServer::TcpServer(uint16_t numBase, uint16_t numDeal) :m_myEngine(true)
{
	m_engine = std::make_shared<RunEngine>();
	m_engine->Start(numBase, numDeal);
	m_acceptor = std::make_shared<TcpAcceptor>(true, m_engine->BaseIo());
    SignalsConnOrDisconn(true);
	m_manager = NetConnectionManagerPtr(new NetConnectionManager());
}

TcpServer::TcpServer(RunEnginePtr engine) :m_myEngine(false)
{
	m_engine = engine;
	m_acceptor = std::make_shared<TcpAcceptor>(true, m_engine->BaseIo());
    SignalsConnOrDisconn(true);
	m_manager = std::make_shared<NetConnectionManager>();
}

TcpServer::~TcpServer()
{
    SignalsConnOrDisconn(false);
    Reset();
    m_acceptor.reset();
    m_manager.reset();
}

const char* TcpServer::LocalAddress() const
{
    return m_localAddress.c_str();
}

uint16_t TcpServer::LocalPort() const
{
    return m_localPort;
}

void TcpServer::Reset()
{
    ReflushLocalEndpoint(false);
    //m_myEngine
    //m_engine
    m_acceptor->Stop();
    m_manager->Reset();
}

int TcpServer::Accept(const std::string& address, uint16_t port, int backlog)
{
    return m_acceptor->Start(address, port, backlog);
}

bool TcpServer::IsOpen() const
{
    return m_acceptor->IsOpen();
}

void TcpServer::Close()
{
    Reset();
}

void TcpServer::OnConnected(NetConnectionPtr connection)
{
    std::string str = (boost::format("[TcpServer::OnConnected   ], %|p|,") % connection.get()).str();
    std::cout << str << std::endl;
}

void TcpServer::OnDisconnected(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)
{
    std::string str = (boost::format("[TcpServer::OnDisconnected], %|p|, %|d|, %|s|,") % connection.get() % errorValue%errorMessage).str();
    std::cout << str << std::endl;
}

void TcpServer::OnError(NetConnectionPtr connection, int errorValue, const std::string& errorMessage)
{
    std::string str = (boost::format("[TcpServer::OnError       ], %|p|, %|d|, %|s|,") % connection.get() % errorValue%errorMessage).str();
    std::cout << str << std::endl;
}

void TcpServer::OnReceivedData(NetConnectionPtr connection, const char* data, uint32_t len)
{
    std::string str = (boost::format("[TcpServer::OnReceivedData], %|p|, %|d|, [%|s|],") % connection.get() % len%data).str();
    std::cout << str << std::endl;
}

void TcpServer::OnReceivedMessage(NetConnectionPtr connection, StdStringPtr message)
{
    std::string str = (boost::format("[TcpServer::OnReceivedMsg ], %|p|, %|d|, [%|s|],") % connection.get() % message->size() % *message).str();
    std::cout << str << std::endl;
}

void TcpServer::ReflushLocalEndpoint(bool regain)
{
    if (regain)
    {
        m_localAddress = m_acceptor->LocalEndpoint().address().to_string();
        m_localPort = m_acceptor->LocalEndpoint().port();
    }
    else
    {
        m_localAddress = "";
        m_localPort = 0;
    }
}

void TcpServer::SignalsConnOrDisconn(bool isConnect)
{
    if (isConnect)
    {
        m_acceptor->m_onAccepted.connect(boost::bind(&TcpServer::DoOnAcceptedSocket, this, _2));
        m_acceptor->m_onError.connect(boost::bind(&TcpServer::OnError, this, nullptr, _2, _3));
    }
    else
    {
        m_acceptor->m_onAccepted.disconnect_all_slots();
        m_acceptor->m_onError.disconnect_all_slots();
    }
}

void TcpServer::DoOnAcceptedSocket(BoostSocketPtr boostSocket)
{
    NetConnectionPtr conn = std::make_shared<NetConnection>(true, m_engine, boostSocket);
    if (true)
    {
        conn->m_onConnected.connect(boost::bind(&TcpServer::OnConnected, /*shared_from_this()*/this, _1));
        conn->m_onDisconnected.connect(boost::bind(&TcpServer::OnDisconnected, /*shared_from_this()*/this, _1, _2, _3));
        conn->m_onError.connect(boost::bind(&TcpServer::OnError, /*shared_from_this()*/this, /*_1*/nullptr, _2, _3));
        conn->m_onReceivedData.connect(boost::bind(&TcpServer::OnReceivedData, /*shared_from_this()*/this, _1, _2, _3));
        conn->m_onReceivedMessage.connect(boost::bind(&TcpServer::OnReceivedMessage, /*shared_from_this()*/this, _1, _2));
    }
    m_manager->Insert(conn);
    if (conn->Start() != 0)
    {
        int errorValue = -1;
        std::string errorMessage = "accept了一个socket,然后Start失败了.";
        m_engine->BaseIo().post(boost::bind(&TcpServer::OnError, shared_from_this(), conn, errorValue, errorMessage));
    }
}

#endif//TcpServer
/************************************************************************/
/*                                                                      */
/************************************************************************/
#endif//NET_IMPL_HPP
