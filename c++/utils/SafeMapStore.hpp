#include <map>
#include <vector>
#include <memory>


//////////////////////////////////////////////////////////////////////////
//  适用场景: 查询数据次数很多 & 修改数据次数很少.
//////////////////////////////////////////////////////////////////////////


//C++标准之所以定义友元类,是因为某些特定场景,在不用友元类的情况下,用正规方式是无法实现的.
//在本例,我可以使用奇技淫巧: 在MapStore里面用"const_cast<std::map<K, V>&>(newPtr->data())"然后修改map中的值.
//在我看来,它和"reinterpret_cast<std::map<K, V>*>((char*)(newPtr.get()) + 8)"一样危险.
//类似的奇技淫巧可以达到目的,但是风险很大.不用友元类,又能使用无风险的奇技淫巧达到目的,这种方式好像没有.
template<typename K, typename V> class MapStore;//提前声明,然后使用友元类.


template <typename K, typename V>
class StdSharedMap :public std::enable_shared_from_this<StdSharedMap<K, V> >
{
public:
    friend class MapStore<K, V>;
public:
    StdSharedMap() {};
    StdSharedMap(const StdSharedMap& other) :m_data(other.m_data) {};
    ~StdSharedMap() {};
    std::shared_ptr<StdSharedMap<K, V> > sharedPtr()
    {
        return std::enable_shared_from_this<StdSharedMap<K, V> >::shared_from_this();
    };
    const std::map<K, V>& data() const { return m_data; }
private:
    std::map<K, V> m_data;
};


template<typename K, typename V>
class MapStore
{
public:
    typedef StdSharedMap<K, V>        SMapType;  // shared map type.
    typedef std::shared_ptr<SMapType> SMapTypePtr;
public:
    MapStore() { reset(); };

    void reset()
    {
        SMapTypePtr newPtr = SMapTypePtr(new SMapType);
        m_rawPtr = newPtr.get();
        m_autoPtr = newPtr;
    };

    SMapTypePtr getData()
    {
        return m_rawPtr->sharedPtr();
    };

    void upsertData(const std::map<K, V>& allPair)
    {
        if (allPair.empty())
            return;

        SMapTypePtr newPtr;
        if (m_rawPtr)
            newPtr = SMapTypePtr(new SMapType(*m_rawPtr));
        else
            newPtr = SMapTypePtr(new SMapType);

        for (auto& p : allPair)
        {
            newPtr->m_data[p.first] = p.second;
        }

        m_rawPtr = newPtr.get();
        m_autoPtr = newPtr;
    };

    void eraseData(const std::vector<K>& allKey)
    {
        if (allKey.empty())
            return;

        SMapTypePtr newPtr;
        if (m_rawPtr)
            newPtr = SMapTypePtr(new SMapType(*m_rawPtr));
        else
            newPtr = SMapTypePtr(new SMapType);

        for (auto& item : allKey)
        {
            newPtr->m_data.erase(item);
        }

        m_rawPtr = newPtr.get();
        m_autoPtr = newPtr;
    };

private:
    SMapTypePtr m_autoPtr;
    SMapType*   m_rawPtr;
};

/*
int main()
{
          MapStore<int, std::string> dataStore;
          MapStore<int, std::string>::SMapTypePtr autoPtr;
    const std::map<int, std::string>* rawPtr = nullptr;
    //
    dataStore.reset();
    autoPtr = dataStore.getData();
    rawPtr = &(autoPtr->data());
    //
    std::map<int, std::string> allPair;
    for (int i = 1; i < 10; ++i)
    {
        char buf[32] = { 0 };
        std::snprintf(buf, sizeof(buf) - 1, "%d", i * 100);
        allPair[i] = buf;
    }
    dataStore.upsetData(allPair);
    autoPtr = dataStore.getData();
    rawPtr = &(autoPtr->data());
    //
    std::vector<int> allKey;
    for (int i = 3; i < 6; ++i)
    {
        allKey.push_back(i);
    }
    dataStore.eraseData(allKey);
    autoPtr = dataStore.getData();
    rawPtr = &(autoPtr->data());
    //
    dataStore.reset();
    autoPtr = dataStore.getData();
    rawPtr = &(autoPtr->data());
    //
    return 0;
}*/
