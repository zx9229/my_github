// 确保中文编码utf8
#ifndef SAFE_FAST_MAP_H_2
#define SAFE_FAST_MAP_H_2
#include <map>
#include <mutex>
//////////////////////////////////////////////////////////////////////////
//使用需知:
//1. 假定[智能指针]和[裸指针]的性能一致(公认性能几乎一致).
//2. 适用于[多读]&[少写]的场景.
//3. 每一次[写操作]都会复制一次std::map.
//4. 使用它时, 禁用[强制类型转换], 禁用[const_cast]转换.
//////////////////////////////////////////////////////////////////////////
template<typename K, typename V>
class SafeFastMap
{
public:
    //StdMap
    typedef std::map<K, V> SMap;
private:
    //SharedStdMap
    typedef std::shared_ptr<SMap> SSM;
public:
    /////////////////////////////////////////////////////
    //SharedStdMapReader
    class SSMR
    {
    public:
        SSMR() :m_data(new SMap) {}

        SSMR(const SSM& sharedData) :m_data(sharedData) {}

        const SMap& MAP() const
        {
            return *m_data;
        }

        const SMap* MAPTR() const
        {
            return m_data.get();
        }

        bool contains(const K& key) const
        {
            if (m_data->find(key) == m_data->end())
                return false;
            return true;
        }

        const V* at(const K& key, bool* isValid) const
        {
            auto it = m_data->find(key);
            if (m_data->end() != it)
            {
                if (isValid) { *isValid = true; }
                return &(it->second);
            }
            else
            {
                if (isValid) { *isValid = false; }
                return nullptr;
            }
        }

    protected:
        SSM m_data;
    };
    /////////////////////////////////////////////////////
    //SharedStdMapWriter
    class SSMW
    {
    public:
        friend class SafeFastMap;
    public:
        SSMW(const SSMW&) = delete;
        void operator=(const SSMW&) = delete;

        SSMW() :m_data(new SMap) {}

        SMap& MAP()
        {
            return *m_data;
        }

        SMap* MAPTR()
        {
            return m_data.get();
        }

        bool contains(const K& key)
        {
            if (m_data->find(key) == m_data->end())
                return false;
            return true;
        }

        V* at(const K& key, bool* isValid)
        {
            auto it = m_data->find(key);
            if (m_data->end() != it)
            {
                if (isValid) { *isValid = true; }
                return &(it->second);
            }
            else
            {
                if (isValid) { *isValid = false; }
                return nullptr;
            }
        }

        void upsert(const K& key, const V& val)
        {
            (*m_data)[key] = val;
        }

        bool insert(const K& key, const V& val)
        {
            return m_data->insert(std::pair<K, V>(key, val)).second;
        }

        bool remove(const K& key)
        {
            return (m_data->erase(key) != 0);
        }

    protected:
        SSM m_data;
    };
    /////////////////////////////////////////////////////
public:
    const SSMR read() const
    {
        return m_container.m_data;
    }

    void write(std::function<void(SSMW& container)>func)
    {
        std::lock_guard<std::mutex> lg(m_mutex);

        SSM sharedStdMapData(new SMap(m_container.MAP()));

        m_container.m_data.swap(sharedStdMapData);

        func(m_container);
    }

private:
    mutable std::mutex m_mutex;
    SSMW               m_container;
};


/* 使用示例:
int main()
{
using I2STYPE = SafeFastMap<int, std::string>;

I2STYPE safeMap;
safeMap.write([](I2STYPE::SSMW& container) {
container.MAP()[1] = "11";
});
safeMap.write([](I2STYPE::SSMW& container) {
container.MAPTR()->insert(std::make_pair(2, "22"));
});
safeMap.write([](I2STYPE::SSMW& container) {
std::cout << container.contains(3) << std::endl;
});
safeMap.write([](I2STYPE::SSMW& container) {
bool isOk = false;
container.at(4, &isOk);
});
safeMap.write([](I2STYPE::SSMW& container) {
container.upsert(5, "55");
});
safeMap.write([](SafeFastMap<int, std::string>::SSMW& container) {
std::cout << container.insert(6, "66") << std::endl;
});
safeMap.write([](I2STYPE::SSMW& container) {
std::cout << container.remove(7) << std::endl;
});

I2STYPE::SSMR mapR1 = safeMap.read();
mapR1.contains(8);
mapR1.MAP().find(9) != mapR1.MAP().end();

I2STYPE::SSMR mapR2 = safeMap.read();
mapR2.contains(10);
for (auto it = mapR2.MAP().begin(); it != mapR2.MAP().end(); ++it)
{
std::cout << it->first << "," << it->second << std::endl;
}
const I2STYPE::SMap& mapData = mapR2.MAP();
mapData.find(11) != mapData.end();

return 0;
}
*/

#endif//SAFE_FAST_MAP_H_2
