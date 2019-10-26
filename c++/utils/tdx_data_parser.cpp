#include <string>
#include <fstream>
#include <iterator>
#include <memory>
#include <algorithm>

static void filename2content(const std::string& filename, std::string& content)
{
    std::copy(std::istreambuf_iterator<char>(std::ifstream(filename, std::ios_base::in | std::ios_base::binary).rdbuf()), std::istreambuf_iterator<char>(), std::back_inserter(content));
}

//通达信5分钟线数据格式解析
//通达信5分钟线*.lc5文件和*.lc1文件
//https://bbs.csdn.net/topics/392327877
//通达信日线 数据格式
//https://www.cnblogs.com/zeroone/archive/2013/07/10/3181251.html

#pragma pack(1) //让编译器对这个结构作1字节对齐.
struct bin_data_lc
{
    std::int16_t m_date;
    std::int16_t m_time;
    std::float_t m_open;
    std::float_t m_high;
    std::float_t m_low;
    std::float_t m_close;
    std::int32_t m_oi; //Open Interest(持仓量)(期货).
    std::int32_t m_volume;
    std::int32_t m_reserved; //保留字段.
};
#pragma pack() //取消1字节对齐,恢复为默认4字节对齐.

#pragma pack(1)
struct bin_data_day
{
    std::int32_t m_date;
    std::float_t m_open;
    std::float_t m_high;
    std::float_t m_low;
    std::float_t m_close;
    std::int32_t m_oi;
    std::int32_t m_volume;
    std::float_t m_settle;
};
#pragma pack()

class line_data
{
public:
    virtual void set(const char* data) = 0;
    virtual std::string get() = 0;
};

class line_data_lc :public line_data
{
public:
    void set(const char* data)
    {
        m_bin = *reinterpret_cast<const bin_data_lc*>(data);
        m_date = calc_yyyymmdd(m_bin.m_date);
        m_time = calc_hhmm(m_bin.m_time);
        m_text = calc_text();
    }
    std::string get() { return m_text; }
private:
    int calc_yyyymmdd(std::int16_t num)
    {
        int yyyy = (num / 2048) + 2004;
        int mm = (num % 2048) / 100;
        int  dd = (num % 2048) % 100;
        return yyyy * 10000 + mm * 100 + dd;
    }
    int calc_hhmm(std::int16_t num)
    {
        int hh = num / 60;
        int mm = num % 60;
        return hh * 100 + mm;
    }
    std::string calc_text()
    {
        char buf[1024] = { 0 };
        std::snprintf(buf, sizeof(buf), "%08d, %04d, %5.4f, %5.4f, %5.4f, %5.4f, %6d, %6d, %08X",
            m_date, m_time, m_bin.m_open, m_bin.m_high, m_bin.m_low, m_bin.m_close, m_bin.m_volume, m_bin.m_oi, m_bin.m_reserved);
        return buf;
    }
private:
    bin_data_lc m_bin;
    int m_date;
    int m_time;
    std::string m_text;
};

class line_data_day :public line_data
{
public:
    void set(const char* data)
    {
        m_bin = *reinterpret_cast<const bin_data_day*>(data);
        m_text = calc_text();
    }
    std::string get() { return m_text; }
private:
    std::string calc_text()
    {
        char buf[1024] = { 0 };
        std::snprintf(buf, sizeof(buf), "%08d, %5.4f, %5.4f, %5.4f, %5.4f, %6d, %6d, %5.4f",
            m_bin.m_date, m_bin.m_open, m_bin.m_high, m_bin.m_low, m_bin.m_close, m_bin.m_volume, m_bin.m_oi, m_bin.m_settle);
        return buf;
    }
private:
    bin_data_day m_bin;
    std::string m_text;
};

std::string file_suffix(const std::string& filename)
{
    if (filename.find_last_of('.') == std::string::npos)
        return "";
    else
        return  filename.substr(filename.find_last_of('.'));
}

int main(int argc, char** argv)
{
    std::string filename = "./tdx_file.lc1";
    if (2 <= argc) { filename = argv[1]; }
    filename = "C:/new_tdxqh/vipdoc/ds/minline/30#AUL8.lc1"; //黄金主连.
    filename = "C:/new_tdxqh/vipdoc/ds/lday/30#AUL8.day"; //黄金主连.

    std::shared_ptr<line_data> container;
    if (file_suffix(filename) == ".lc1" || file_suffix(filename) == ".lc5")
    {
        container = std::shared_ptr<line_data_lc>(new line_data_lc);
    }
    else if (file_suffix(filename) == ".day")
    {
        container = std::shared_ptr<line_data_day>(new line_data_day);
    }
    else
    {
        std::printf("the file suffix should be .day/.lc1/.lc5 !\n");
        std::printf("press ENTER to exit ...");
        while (getchar() != '\n') {}
        return 1;
    }

    std::string content;
    content.reserve(1024 * 1024 * 512);
    filename2content(filename, content);

    for (std::size_t idx = 0; idx < content.size(); idx += 32)
    {
        container->set(content.data() + idx);
        std::printf(container->get().c_str());
        while (getchar() != '\n') {}
        std::printf("");
    }

    std::printf("press ENTER to exit ...");
    while (getchar() != '\n') {}
    return 0;
}
