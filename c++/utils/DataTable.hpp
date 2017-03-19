#include<string>
#include<vector>
#include<map>
#include<fstream>
#include<boost/lexical_cast.hpp>


#if 1 //DataTable
class DataTable
{
private:
	std::map<std::string, unsigned int>   m_allFieldName;
	std::vector<std::vector<std::string>> m_allDataLine;
	unsigned int                          m_lineIdx;
public:
	DataTable() { clear(); }
	~DataTable() {}
public:
	void clear()
	{
		m_allFieldName.clear();
		m_allDataLine.clear();
		m_lineIdx = 0;
	}
	bool empty()
	{
		return m_allDataLine.empty() ? true : false;
	}
	unsigned int size()
	{
		return m_allDataLine.size();
	}
	void begin()
	{
		m_lineIdx = 0;
	}
	bool end()
	{
		return m_allDataLine.size() <= m_lineIdx ? true : false;
	}

	int loadFile(const std::string& fileName, const std::string& lineDelimiter, const std::string& fieldDelimiter, bool haveHeadLine)
	{
		int returnValue = 0;
		do
		{
			std::string content;
			if (DataTable::loadFile(fileName, content) != 0)
			{
				returnValue = -1;
				break;
			}
			returnValue = loadContent(content, lineDelimiter, fieldDelimiter, haveHeadLine);
		} while (false);
		return returnValue;
	}

	int loadContent(std::string& content, const std::string& rowDelimiter, const std::string& fieldDelimiter, bool haveHeadLine)
	{
		int returnValue = 0;
		//
		const std::string allInvalidChar = " ";//所有的无效的字符.
		//
		unsigned int fieldNum = 0;
		std::vector<std::string> allField;
		std::size_t beg = 0, pos = 0;
		for (beg = pos = 0; (pos = content.find(rowDelimiter, beg)) != std::string::npos; beg = pos = pos + rowDelimiter.size())
		{
			content[pos] = 0x0;
			std::string line = &content[0] + beg;
			//
			if (true)
			{ //跳过空行.
				trim(line, allInvalidChar);
				if (line.empty())
					continue;
			}
			//
			allField.clear();
			split(line, fieldDelimiter, allField);
			for (std::string& field : allField)
				trim(field, allInvalidChar);
			//
			if (fieldNum == 0)
				fieldNum = allField.size();
			//
			if (haveHeadLine)
			{ //允许字段之间有空格,
				for (unsigned int i = 0; i < allField.size(); ++i)
				{
					m_allFieldName.insert(std::pair<std::string, unsigned int>(allField[i], i));
				}
				haveHeadLine = false;
				continue;
			}
			//
			if (allField.size() != fieldNum)
			{
				returnValue = -1;
				break;
			}
			m_allDataLine.push_back(allField);
		}
		//
		if (returnValue != 0)
			clear();
		//
		return returnValue;
	}

	unsigned int stepToNext()
	{
		return (m_lineIdx < m_allDataLine.size()) ? (++m_lineIdx) : m_lineIdx;
	}

	template<typename _Type>
	_Type getFieldValueByKey(const std::string& _k, _Type _default)
	{
		bool isDefault;
		return getFieldValueExByKey(_k, _default, isDefault);
	}
	template<typename _Type>
	_Type getFieldValueExByKey(const std::string& _k, _Type _default, bool& isDefault)
	{
		const std::vector<std::string>& dataLine = m_allDataLine[m_lineIdx];
		auto itr = m_allFieldName.find(_k);
		if (m_allFieldName.end() == itr)
		{
			isDefault = true;
			return _default;
		}
		else
		{
			isDefault = false;
			try
			{
				return boost::lexical_cast<_Type>(dataLine[itr->second]);
			}
			catch (...)
			{
				isDefault = true;
				return _default;
			}
		}
	}
	//
	template<typename _Type>
	_Type getFieldValueByIdx(unsigned int _idx, _Type _default)
	{
		bool isDefault;
		return getFieldValueExByIdx(_idx, _default, isDefault);
	}
	template<typename _Type>
	_Type getFieldValueExByIdx(unsigned int _idx, _Type _default, bool& isDefault)
	{
		const std::vector<std::string>& data = m_allDataLine[m_lineIdx];
		if (data.size() <= _idx)
		{
			isDefault = true;
			return _default;
		}
		else
		{
			isDefault = false;
			try
			{
				return boost::lexical_cast<_Type>(data[_idx]);
			}
			catch (...)
			{
				isDefault = true;
				return _default;
			}
		}
	}
private:
	static int loadFile(const std::string& fileName, std::string& content)
	{
		std::ifstream ifs;
		ifs.open(fileName, std::ios_base::in | std::ios_base::binary);
		if (ifs.is_open() == false)
			return -1;
		ifs.seekg(0, std::ifstream::end);
		std::streamoff fileSize = ifs.tellg();
		ifs.seekg(0, std::ifstream::beg);
		content.resize(std::size_t(fileSize), 0x0);
		//ifs.read(&m_content[0], fileSize);//读取到char*
		content.assign(std::istreambuf_iterator<char>(ifs), std::istreambuf_iterator<char>());//读取到std::string
		ifs.close();
		return 0;
	}
	static void split(const std::string& srcStr, char sep, std::vector<std::string>& vecOut)
	{
		std::size_t begIdx, endIdx;
		for (begIdx = endIdx = 0; (endIdx = srcStr.find(sep, begIdx)) != std::string::npos; begIdx = ++endIdx)
		{
			vecOut.push_back(srcStr.substr(begIdx, endIdx - begIdx));
		}
		vecOut.push_back(srcStr.substr(begIdx, srcStr.length() - begIdx));
	}
	static void split(const std::string& srcStr, const std::string& sep, std::vector<std::string>& vecOut)
	{
		std::size_t begIdx, endIdx;
		for (begIdx = endIdx = 0; (endIdx = srcStr.find(sep, begIdx)) != std::string::npos; begIdx = endIdx += sep.length())
		{
			vecOut.push_back(srcStr.substr(begIdx, endIdx - begIdx));
		}
		vecOut.push_back(srcStr.substr(begIdx, srcStr.length() - begIdx));
	}
	static std::string& rtrim(std::string& s, const std::string& allSep = " ")
	{
		std::string::size_type index = s.size();
		for (; index >= 1; --index)
			if (allSep.find(s[index - 1]) == std::string::npos)
				break;
		if (index != s.size())
			s.erase(index);
		return s;
	}
	static std::string& ltrim(std::string& s, const std::string& allSep = " ")
	{
		std::string::size_type index = 0;
		for (; index < s.size(); ++index)
			if (allSep.find(s[index]) == std::string::npos)
				break;
		if (index != 0)
			s.erase(0, index);
		return s;
	}
	static std::string& trim(std::string& s, const std::string& allSep = " ")
	{
		return ltrim(rtrim(s));
	}
};
#endif//DataTable

#if 1  //test
#include<iostream>
int main()
{
	std::string content =
		" id  | name | date     \r\n"
		" A01 | a1   | 20120101 \r\n"
		" A02 | a2   | 20120202 \r\n"
		" A03 | a3   | 20120303 \r\n"
		"\r\n"
		"\r\n";
	std::string lineDelimiter = "\r\n";
	std::string fieldDelimiter = "|";
	bool haveHeadLine = true;
	DataTable dt;
	if (dt.loadContent(content, lineDelimiter, fieldDelimiter, haveHeadLine))
	{
		std::cout << "ERROR" << std::endl;
		return -1;
	}
	for (dt.begin(); dt.end() == false; dt.stepToNext())
	{
		std::string id = dt.getFieldValueByKey<std::string>("id", "");
		std::string name = dt.getFieldValueByKey<std::string>("name", "");
		int date = dt.getFieldValueByKey<int>("date", 0);
		double xxx = dt.getFieldValueByKey<double>("xxx", 0);
		//
		std::string f1 = dt.getFieldValueByIdx<std::string>(0, "");
		std::string f2 = dt.getFieldValueByIdx<std::string>(1, "");
		std::string f3 = dt.getFieldValueByIdx<std::string>(2, "");
		std::string f4 = dt.getFieldValueByIdx<std::string>(3, "");
		std::cout << "" << std::endl;
	}
	return 0;
}
#endif // 1  //test
