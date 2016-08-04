#ifndef XML_READER_H_H
#define XML_READER_H_H

#include <string>
#include <vector>
#include <tuple>
#include <fstream>
#include "rapidxml/rapidxml.hpp"


class XmlReader
{
public:
	int InitByFile(const std::string& fileName)
	{
		int rv = 0;
		rv = LoadContentFromFile(fileName);
		if (0 != rv)
			return rv;

		m_doc.parse<0>(const_cast<char*>(m_content.c_str()));

		return rv;
	}

	std::string GetValue(const std::string& xmlPath, const std::string& defaultValue = "")
	{
		std::vector<std::tuple<std::string, char, char>> fields;
		GetFields(fields, xmlPath, "/>");
		if (FieldsIsValid(fields) == false)
			return defaultValue;
		return GetValue(nullptr, fields, 1);
	}
private:
	int LoadContentFromFile(const std::string& fileName)
	{
		std::ifstream ifs;
		ifs.open(fileName, std::ios_base::in | std::ios_base::binary);
		if (ifs.is_open() == false)
			return -1;
		ifs.seekg(0, std::ifstream::end);
		std::streamoff fileSize = ifs.tellg();
		ifs.seekg(0, std::ifstream::beg);
		m_content.resize(std::size_t(fileSize), 0x0);
		//ifs.read(&m_content[0], fileSize);//读取到char*
		m_content.assign(std::istreambuf_iterator<char>(ifs), std::istreambuf_iterator<char>());//读取到std::string
		ifs.close();
		return 0;
	}

	void GetFields(std::vector<std::tuple<std::string, char, char>>& fields, const std::string& input, const std::string& separator)
	{
		char beg = 0x0, end = 0x0;
		std::string::size_type begIdx, endIdx;
		for (begIdx = endIdx = 0; endIdx < input.length(); ++endIdx)
		{
			if (separator.find(input[endIdx]) != std::string::npos)
			{
				end = input.at(endIdx);
				fields.push_back(std::tuple<std::string, char, char>(input.substr(begIdx, endIdx - begIdx), beg, end));
				beg = end;
				begIdx = endIdx + 1;
			}
		}
		end = 0x0;
		fields.push_back(std::tuple<std::string, char, char>(input.substr(begIdx, endIdx - begIdx), beg, end));
	}

	bool FieldsIsValid(std::vector<std::tuple<std::string, char, char>>& fields)
	{
		if (fields.size() < 3)//至少为"/node>attribute"
			return false;

		unsigned int idx = 0;
		if ((std::get<0>(fields[idx]).length() == 0 && std::get<1>(fields[idx]) == 0x0 && std::get<2>(fields[idx]) == '/') == false)
			return false;

		idx = fields.size() - 1;
		if ((std::get<0>(fields[idx]).length() > 00 && std::get<1>(fields[idx]) == '>' && std::get<2>(fields[idx]) == 0x0) == false)
			return false;

		std::string field;
		char beg, end;
		for (idx = 1; idx < fields.size() - 2; ++idx)
		{
			std::tie(field, beg, end) = fields[idx];
			if ((field.size()>0 && '/' == beg&&beg == end) == false)
				return false;
		}

		return true;
	}

	/*
	得到fields指向的值,idx:函数应该从fields的第几个位置处开始处理,
	*/
	char* GetValue(rapidxml::xml_node<>* node, std::vector<std::tuple<std::string, char, char>>& fields, int idx = 1)
	{
		if (1 < idx)
			assert(nullptr != node && fields.size() >= 3);

		rapidxml::xml_node<>* initialNode = node;
		int initialIdx = idx;

		if (idx <= 1)
		{
			idx = 1;
			node = m_doc.first_node(std::get<0>(fields[idx]).c_str());
			if (nullptr == node)
				return nullptr;
			initialIdx = ++idx;
			initialNode = node;
		}

		if (std::get<1>(fields[idx]) == '>')//0:字段的名字,1:字段的beg,2:字段的end
		{
			rapidxml::xml_attribute<>* attribute = node->first_attribute(std::get<0>(fields[idx]).c_str());
			return nullptr == attribute ? nullptr : attribute->value();
		}
		else if (std::get<1>(fields[idx]) == '/')
		{
			node = node->first_node(std::get<0>(fields[idx]).c_str());
		}
		else
		{
			assert(false);//字段之间只能以'/'或'>'进行分割.
		}

		if (nullptr == node)
		{
			return nullptr;
		}
		else
		{
			char* value = GetValue(node, fields, idx + 1);
			if (value)
				return value;
		}

		node = initialNode->next_sibling(std::get<0>(fields[initialIdx - 1]).c_str());
		if (node)
		{
			char* value = GetValue(node, fields, initialIdx);
			return value;
		}
		else
		{
			return nullptr;
		}
	}
private:
	std::string m_content;
	rapidxml::xml_document<> m_doc;
};

#endif//XML_READER_H_H
