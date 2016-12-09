#ifndef BOOST_HTTP_SYNC_CLIENT_H
#define BOOST_HTTP_SYNC_CLIENT_H
//////////////////////////////////////////////////////////////////////////
//#include <libs/asio/example/cpp03/http/client/sync_client.cpp>
//此文件以"boost_1_58_0_7z/libs/asio/example/cpp03/http/client/sync_client.cpp"为蓝本,略作修改.
//////////////////////////////////////////////////////////////////////////

//
// sync_client.cpp
// ~~~~~~~~~~~~~~~
//
// Copyright (c) 2003-2015 Christopher M. Kohlhoff (chris at kohlhoff dot com)
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

#include <iostream>
#include <istream>
#include <ostream>
#include <string>
#include <boost/asio.hpp>
#include <boost/format.hpp>

using boost::asio::ip::tcp;

inline int boost_http_sync_client(const std::string& server, const std::string& port, const std::string& path,
    std::string& out_response_status_line, std::string& out_response_headers, std::string& out_response_data,
    std::string& error_message)
{
    error_message = "";
    try
    {
        boost::asio::io_service io_service;

        // Get a list of endpoints corresponding to the server name.
        tcp::resolver resolver(io_service);
        tcp::resolver::query query(server, port/*"http"*/);
        tcp::resolver::iterator endpoint_iterator = resolver.resolve(query);

        // Try each endpoint until we successfully establish a connection.
        tcp::socket socket(io_service);
        boost::asio::connect(socket, endpoint_iterator);

        // Form the request. We specify the "Connection: close" header so that the
        // server will close the socket after transmitting the response. This will
        // allow us to treat all data up until the EOF as the content.
        boost::asio::streambuf request;
        std::ostream request_stream(&request);
        request_stream << "GET " << path/*argv[2]*/ << " HTTP/1.0\r\n";
        request_stream << "Host: " << server/*argv[1]*/ << "\r\n";
        request_stream << "Accept: */*\r\n";
        request_stream << "Connection: close\r\n\r\n";

        // Send the request.
        boost::asio::write(socket, request);

        // Read the response status line. The response streambuf will automatically
        // grow to accommodate the entire line. The growth may be limited by passing
        // a maximum size to the streambuf constructor.
        boost::asio::streambuf response;
        boost::asio::read_until(socket, response, "\r\n");

        if (true)
        {
            boost::asio::streambuf::const_buffers_type cbt = response.data();
            out_response_status_line = std::string(boost::asio::buffers_begin(cbt), boost::asio::buffers_end(cbt));
        }

        // Check that response is OK.
        std::istream response_stream(&response);
        std::string http_version;
        response_stream >> http_version;
        unsigned int status_code;
        response_stream >> status_code;
        std::string status_message;
        std::getline(response_stream, status_message);
        if (!response_stream || http_version.substr(0, 5) != "HTTP/")
        {
            //std::cout << "Invalid response\n";
            error_message = "Invalid response";
            return 1;
        }
        if (status_code != 200)
        {
            //std::cout << "Response returned with status code " << status_code << "\n";
            error_message = (boost::format("Response returned with status code %1%") % status_code).str();
            return 1;
        }

        // Read the response headers, which are terminated by a blank line.
        boost::asio::read_until(socket, response, "\r\n\r\n");

        //if (true)
        //{
        //    boost::asio::streambuf::const_buffers_type cbt = response.data();
        //    out_response_headers = std::string(boost::asio::buffers_begin(cbt), boost::asio::buffers_end(cbt));
        //}

        std::stringstream ss_out_response_headers;
        // Process the response headers.
        std::string header;
        while (std::getline(response_stream, header) && header != "\r")
            ss_out_response_headers/*std::cout*/ << header << "\n";
        //std::cout << "\n";
        ss_out_response_headers << header << "\n";
        out_response_headers = ss_out_response_headers.str();

        std::stringstream ss_out_response_data;
        // Write whatever content we already have to output.
        if (response.size() > 0)
            ss_out_response_data/*std::cout*/ << &response;

        // Read until EOF, writing data to output as we go.
        boost::system::error_code error;
        while (boost::asio::read(socket, response,
            boost::asio::transfer_at_least(1), error))
            ss_out_response_data/*std::cout*/ << &response;
        if (error != boost::asio::error::eof)
            throw boost::system::system_error(error);

        out_response_data = ss_out_response_data.str();
    }
    catch (std::exception& e)
    {
        //std::cout << "Exception: " << e.what() << "\n";
        error_message = (boost::format("Exception: %1%") % e.what()).str();
        return 1;
    }

    return 0;
}

inline int parse_url(const std::string& url, std::string& out_server, std::string& out_port, std::string& out_path)
{
    const std::string http_head = "http://";
    const std::string https_head = "https://";
    unsigned int idx_server, idx_, idx_path;
    //
    if (url.find(http_head) == 0)
        idx_server = http_head.size();
    else if (url.find(https_head) == 0)
        idx_server = https_head.size();
    else
        return 1;
    //
    idx_path = url.find('/', idx_server);
    if (std::string::npos == idx_path)
    {
        out_path = "/";
        idx_path = url.size();
    }
    else
    {
        out_path = url.substr(idx_path);
    }
    //
    idx_ = url.find(':', idx_server);
    if (std::string::npos == idx_ || idx_path <= idx_)
    {
        out_port = "http";
        out_port = "80";
        idx_ = idx_path;
    }
    else
    {
        out_port = url.substr(idx_ + 1, idx_path - idx_ - 1);
    }
    //
    out_server = url.substr(idx_server, idx_ - idx_server);
    //
    return 0;
}

inline int response_from_url(const std::string& url, std::string& response)
{
    int rv = 0;
    do
    {
        std::string server, port, path;
        rv = parse_url(url, server, port, path);
        if (rv)
        {
            response = "parse_url function fail.";
            rv = 1;
            break;
        }
        std::string response_status_line, response_headers, error_message;
        rv = boost_http_sync_client(server, port, path, response_status_line, response_headers, response, error_message);
        if (rv)
        {
            response = error_message;
            rv = 2;
            break;
        }
    } while (false);
    return rv;
}

#if 0  //main
#include <fstream>
#include <boost/date_time/posix_time/posix_time.hpp>
int main()
{
    auto lambda_fun = []()->std::string
    {
        auto pt = boost::posix_time::microsec_clock::local_time();
        return boost::posix_time::to_iso_string(pt);
    };
    //
    std::vector<std::string> vec;
    if (true)
    {
        std::string url;
        url = "https://www.baidu.com";
        vec.push_back(url);
        url = "http://hq.sinajs.cn/list=sh601398";
        vec.push_back(url);
        url = "http://yunhq.sse.com.cn:32041/v1/sh1/snap/601398?callback=jQuery_test&select=name%2Clast%2Cchg_rate%2Cchange%2Camount%2Cvolume%2Copen%2Cprev_close%2Cask%2Cbid%2Chigh%2Clow%2Ctradephase";
        vec.push_back(url);
    }
    //
    std::string response;
    for (const std::string& url : vec)
    {
        const unsigned int max_len = 48;
        int rv = response_from_url(url, response);
        std::cout << "return_value=" << rv << ", part_url=" << url.substr(0, max_len) << (max_len < url.size() ? "..." : "") << std::endl;
        if (true)
        {
            std::string filename = lambda_fun();
            std::ofstream ofs(filename, std::ios_base::out | std::ios_base::binary);
            ofs.write(response.c_str(), response.size());
            ofs.close();
        }
    }
    //
    return 0;
}
#endif //main

#endif//BOOST_HTTP_SYNC_CLIENT_H
