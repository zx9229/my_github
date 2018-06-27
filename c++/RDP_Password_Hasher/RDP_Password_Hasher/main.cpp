#include <string>
#include <fstream>
#include <iostream>
#pragma comment(lib,"Crypt32.lib")
#include <Windows.h>
#include <dpapi.h>


//https://blog.csdn.net/goof/article/details/7662652
// Use wcstombs_s and mbstowcs_s 
std::string ws2s(const std::wstring& ws)
{
    const wchar_t* Source = ws.c_str();
    size_t size = 2 * ws.size() + 1;
    char* Dest = new char[size];
    memset(Dest, 0, size);
    size_t len = 0;
    wcstombs(Dest, Source, size);
    //wcstombs_s(&len, Dest, size, Source, size);
    std::string result = Dest;
    delete[] Dest;

    return result;
}

std::wstring s2ws(const std::string& s)
{
    const char* Source = s.c_str();
    size_t size = s.size() + 1;
    wchar_t* Dest = new wchar_t[size];
    wmemset(Dest, 0, size);
    size_t len = 0;
    mbstowcs(Dest, Source, size);
    //mbstowcs_s(&len, Dest, size, Source, size);
    std::wstring result = Dest;
    delete[] Dest;

    return result;
}

std::string s2hex(const std::string& src)
{
    std::string dst;
    //dst.resize(src.size() * 2, 0x0);
    //for (std::size_t i = 0; i < src.size(); ++i)
    //{
    //    std::snprintf(&dst[i * 2], (2 + 1), "%02X", (unsigned char)src[i]); //(since C++11)
    //}
    dst.reserve(src.size() * 2);
    char buf[4] = { 0x0 };
    for (std::size_t i = 0; i < src.size(); ++i)
    {
        std::sprintf(buf, "%02X", (unsigned char)src[i]);
        dst.append(buf);
    }
    return dst;
}

std::string hex2s(const std::string& src)
{
    std::string dst;
    dst.reserve((src.size() + 1) / 2);
    // src.size 应当是偶数, 同时, 奇数也允许转换.
    for (std::size_t i = 0; i < (src.size() + 1) / 2; i += 1)
    {
        unsigned char uc = (unsigned char)std::strtol(src.substr(i * 2, 2).c_str(), 0x0, 16);
        dst.push_back(*reinterpret_cast<char*>(&uc));
    }
    return dst;
}

int do_CryptProtectData(const std::string& src, std::string& dst)
{
    //https://docs.microsoft.com/zh-cn/windows/desktop/api/dpapi/nf-dpapi-cryptprotectdata
    // Encrypt data from DATA_BLOB DataIn to DATA_BLOB DataOut.
    //--------------------------------------------------------------------
    // Declare and initialize variables.
    std::wstring srcW = s2ws(src);

    DATA_BLOB DataIn;
    DATA_BLOB DataOut;
    BYTE *pbDataInput = reinterpret_cast<BYTE*>(const_cast<wchar_t*>(srcW.c_str()));
    DWORD cbDataInput = srcW.size() * sizeof(wchar_t);


    //--------------------------------------------------------------------
    // Initialize the DataIn structure.


    DataIn.pbData = pbDataInput;

    DataIn.cbData = cbDataInput;


    //--------------------------------------------------------------------
    //  Begin protect phase. Note that the encryption key is created
    //  by the function and is not passed.


    if (CryptProtectData(
        &DataIn,
        L"psw",                             // A description string
        // to be included with the
        // encrypted data.
        NULL,                               // Optional entropy not used.
        NULL,                               // Reserved.
        NULL,                               // Pass NULL for the
        // prompt structure.
        0,
        &DataOut))
    {
        //printf("The encryption phase worked.\n");
        std::string dstRaw = std::string(reinterpret_cast<char*>(DataOut.pbData), DataOut.cbData);
        dst = s2hex(dstRaw);
        return 0;
    }
    else
    {
        //printf("Encryption error using CryptProtectData.\n");
        //exit(1);
        return 10;
    }
}

int do_CryptUnprotectData(const std::string& src, std::string& dst)
{
    //https://docs.microsoft.com/zh-cn/windows/desktop/api/dpapi/nf-dpapi-cryptunprotectdata
    // Decrypt data from DATA_BLOB DataOut to DATA_BLOB DataVerify.
    //--------------------------------------------------------------------
    // Declare and initialize variables.
    std::string srcRaw = hex2s(src);

    DATA_BLOB DataOut;
    {
        DataOut.pbData = reinterpret_cast<BYTE*>(const_cast<char*>(srcRaw.c_str()));
        DataOut.cbData = srcRaw.size();
    }
    DATA_BLOB DataVerify;
    LPWSTR pDescrOut = NULL;
    //--------------------------------------------------------------------
    // The buffer DataOut would be created using the CryptProtectData
    // function. If may have been read in from a file.


    //--------------------------------------------------------------------
    //   Begin unprotect phase.


    if (CryptUnprotectData(
        &DataOut,
        &pDescrOut,
        NULL,                 // Optional entropy
        NULL,                 // Reserved
        NULL,                 // Here, the optional
        // prompt structure is not
        // used.
        0,
        &DataVerify))
    {
        //printf("The decrypted data is: %s\n", DataVerify.pbData);
        //printf("The description of the data was: %s\n", pDescrOut);
        std::wstring dstW = std::wstring(reinterpret_cast<wchar_t*>(DataVerify.pbData), DataVerify.cbData / 2);
        dst = ws2s(dstW);
        return 0;
    }
    else
    {
        //printf("Decryption error!");
        return 20;
    }
}

int generate_rdp_file(const std::string& full_address, const std::string& username, const std::string& password, const std::string& filename)
{
    int retVal = 0;
    std::string pwd, password_check;
    retVal = do_CryptProtectData(password, pwd);
    if (retVal) { return retVal; }
    retVal = do_CryptUnprotectData(pwd, password_check);
    if (retVal) { return retVal; }
    if (password != password_check) { return 30; }

    std::ofstream ofs(filename);
    if (!ofs.is_open()) { return 31; }

    ofs << "full address:s:" << full_address << std::endl;
    ofs << "username:s:" << username << std::endl;
    ofs << "password 51:b:" << pwd << std::endl;
    return 0;
}

int main()
{
    std::string full_address;
    std::cout << "please input [full address]:" << std::endl;
    std::getline(std::cin, full_address);

    std::string username;
    std::cout << "please input [username]:" << std::endl;
    std::getline(std::cin, username);

    std::string password;
    std::cout << "please input [password]:" << std::endl;
    std::getline(std::cin, password);

    std::string filename;
    std::cout << "please input [filename.rdp]:" << std::endl;
    std::getline(std::cin, filename);

    int ret = generate_rdp_file(full_address, username, password, filename);
    std::cout << (ret ? "FAIL" : "SUCCESS") << std::endl;
    return ret;
}
