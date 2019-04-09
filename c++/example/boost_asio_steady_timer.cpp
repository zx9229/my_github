#include <boost/asio.hpp>
#include <boost/asio/steady_timer.hpp>
#include <boost/thread.hpp>

class TestCls
{
public:
    void fun1(const boost::system::error_code& ec) { std::printf("fun1, %d, %s", ec.value(), ec.message().c_str()); }
    void fun2(const std::string& p1, const boost::system::error_code& ec) { std::printf("fun2, %d, %s, %s", ec.value(), ec.message().c_str(), p1.c_str()); }
    void fun3(const boost::system::error_code& ec, const std::string& p2) { std::printf("fun3, %d, %s, %s", ec.value(), ec.message().c_str(), p2.c_str()); }
    static void fun4(const boost::system::error_code& ec, const std::string& p2) { std::printf("fun4, %d, %s, %s", ec.value(), ec.message().c_str(), p2.c_str()); }
};

int main()
{
    boost::asio::io_service t_io;
    boost::asio::io_service::work t_work(t_io);
    boost::asio::steady_timer t_timer(t_io);
    boost::thread_group t_thgp;
    t_thgp.create_thread(boost::bind(&boost::asio::io_service::run, boost::ref(t_io)));

    TestCls testObj;
    if (false) {
        t_timer.expires_from_now(std::chrono::milliseconds(1000 * 3));
        t_timer.async_wait(boost::bind(&TestCls::fun1, boost::ref(testObj), boost::placeholders::_1));
    }
    else if (false) {
        t_timer.expires_from_now(std::chrono::milliseconds(1000 * 3));
        t_timer.async_wait(boost::bind(&TestCls::fun2, boost::ref(testObj), "fun2", boost::asio::placeholders::error));
    }
    else if (false) {
        t_timer.expires_from_now(std::chrono::milliseconds(1000 * 3));
        t_timer.async_wait(boost::bind(&TestCls::fun3, boost::ref(testObj), boost::placeholders::_1, "fun3"));
    }
    else {
        t_timer.expires_from_now(std::chrono::milliseconds(1000 * 3));
        t_timer.async_wait(boost::bind(&TestCls::fun4, boost::asio::placeholders::error, "fun4"));
    }
    t_thgp.join_all();
    return 0;
}
