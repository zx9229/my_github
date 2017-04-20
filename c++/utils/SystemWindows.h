#ifndef SYSTEM_WINDOWS_H
#define SYSTEM_WINDOWS_H

#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")
#include <Netioapi.h>
#include <Iphlpapi.h>
#pragma comment(lib, "Iphlpapi.lib")
#include <comdef.h>
#include <Wbemidl.h>
#pragma comment(lib, "wbemuuid.lib")
// <Windows.h>和<WinBase.h>会和其它头文件冲突,所以这俩头文件最好放到最后面.
// #include <Windows.h>
// #include <WinBase.h>
#include <string>

class WC2MB
{
public:
    /* convert from unicode to utf8 */
    static void UnicodeToUtf8(const wchar_t *wide_string, std::string& sOut)
    {
        int utf8_size = WideCharToMultiByte(CP_UTF8, 0, wide_string, -1, NULL, 0, NULL, NULL);
        sOut.resize(utf8_size, 0x0);
        /* convert from wide_string to utf8_string */
        WideCharToMultiByte(CP_UTF8, 0, wide_string, -1, const_cast<char*>(sOut.c_str()), utf8_size, NULL, NULL);
        while (!sOut.empty() && 0x0 == sOut[sOut.size() - 1])
            sOut.resize(sOut.size() - 1);
    }

    /* convert from selected code page to unicode */
    static void toUnicode(unsigned int codepage, const char *cp_string, std::wstring& wsOut)
    {
        int wide_size = MultiByteToWideChar(codepage, 0, cp_string, -1, NULL, 0);
        wsOut.resize(wide_size, 0x0);
        /* convert from cp_string to wide_string */
        MultiByteToWideChar(codepage, 0, cp_string, -1, const_cast<wchar_t*>(wsOut.c_str()), wide_size);
        while (!wsOut.empty() && 0x0 == wsOut[wsOut.size() - 1])
            wsOut.resize(wsOut.size() - 1);
    }

    static void Utf8ToUnicode(const char* utf8_string, std::wstring& wsOut)
    {
        toUnicode(CP_UTF8, utf8_string, wsOut);
    }
};
//////////////////////////////////////////////////////////////////////////
class Utils
{
private:
    //////////////////////////////////////////////////////////////////////////
    class VARIANT_Auto
    {
    public:
        VARIANT_Auto() { VariantInit(&m_v); }
        ~VARIANT_Auto() { VariantClear(&m_v); }
    public:
        VARIANT m_v;
    };
    //////////////////////////////////////////////////////////////////////////
    class ComInitUinitAuto
    {
    public:
        ComInitUinitAuto()
        {
            m_state = false;
            do
            {
                HRESULT hres;
                /* must be called once per each thread */
                hres = CoInitializeEx(0, COINIT_MULTITHREADED);
                if (FAILED(hres))
                    break;
                /* must be called once per process, subsequent calls return RPC_E_TOO_LATE */
                hres = CoInitializeSecurity(NULL, -1, NULL, NULL, RPC_C_AUTHN_LEVEL_DEFAULT,
                    RPC_C_IMP_LEVEL_IMPERSONATE, NULL, EOAC_NONE, NULL);
                if (FAILED(hres) && RPC_E_TOO_LATE != hres)
                {
                    CoUninitialize();
                    break;
                }
                m_state = true;
            } while (false);
        }
        ~ComInitUinitAuto()
        {
            if (m_state)
            {
                CoUninitialize();
                m_state = false;
            }
        }
        bool initState() { return m_state; }
    private:
        bool m_state;
    };
    //////////////////////////////////////////////////////////////////////////
    class IWbemLocator_Auto
    {
    public:
        IWbemLocator_Auto() :m_p(nullptr) {}
        ~IWbemLocator_Auto()
        {
            if (m_p)
            {
                m_p->Release();
                m_p = nullptr;
            }
        }
    public:
        IWbemLocator* m_p;
    };
    //////////////////////////////////////////////////////////////////////////
    class IWbemServices_Auto
    {
    public:
        IWbemServices_Auto() :m_p(nullptr) {}
        ~IWbemServices_Auto()
        {
            if (m_p)
            {
                m_p->Release();
                m_p = nullptr;
            }
        }
    public:
        IWbemServices* m_p;
    };
    //////////////////////////////////////////////////////////////////////////
    class IEnumWbemClassObject_Auto
    {
    public:
        IEnumWbemClassObject_Auto() :m_p(nullptr) {}
        ~IEnumWbemClassObject_Auto()
        {
            if (m_p)
            {
                m_p->Release();
                m_p = nullptr;
            }
        }
    public:
        IEnumWbemClassObject* m_p;
    };
    //////////////////////////////////////////////////////////////////////////
    class IWbemClassObject_Auto
    {
    public:
        IWbemClassObject_Auto() :m_p(nullptr) {}
        ~IWbemClassObject_Auto()
        {
            if (m_p)
            {
                m_p->Release();
                m_p = nullptr;
            }
        }
    public:
        IWbemClassObject* m_p;
    };
    //////////////////////////////////////////////////////////////////////////
    class HKEY_Auto
    {
    public:
        HKEY_Auto() :m_p(nullptr) {}
        ~HKEY_Auto()
        {
            if (nullptr != m_p)
            {
                RegCloseKey(m_p);
                m_p = nullptr;
            }
        }
    public:
        HKEY m_p;
    };
    //////////////////////////////////////////////////////////////////////////
private:
    //////////////////////////////////////////////////////////////////////////
    static int WmiGetVariant(const char *wmi_namespace, const char *wmi_query, VARIANT *vtProp)
    {
        int ret = -1;
        IWbemLocator_Auto iLoc;
        IWbemServices_Auto iService;
        IEnumWbemClassObject_Auto iEnumerator;
        HRESULT hres;

        /* obtain the initial locator to Windows Management on a particular host computer */
        hres = CoCreateInstance(CLSID_WbemLocator, 0, CLSCTX_INPROC_SERVER, IID_IWbemLocator, (LPVOID *)&iLoc.m_p);

        if (FAILED(hres))
            return ret;

        std::wstring wsOut;
        WC2MB::Utf8ToUnicode(wmi_namespace, wsOut);
        hres = iLoc.m_p->ConnectServer(_bstr_t(wsOut.c_str()), NULL, NULL, 0, NULL, 0, 0, &iService.m_p);
        wsOut.clear();

        if (FAILED(hres))
            return ret;

        /* set the IWbemServices proxy so that impersonation of the user (client) occurs */
        hres = CoSetProxyBlanket(iService.m_p, RPC_C_AUTHN_WINNT, RPC_C_AUTHZ_NONE, NULL, RPC_C_AUTHN_LEVEL_CALL,
            RPC_C_IMP_LEVEL_IMPERSONATE, NULL, EOAC_NONE);

        if (FAILED(hres))
            return ret;

        WC2MB::Utf8ToUnicode(wmi_query, wsOut);
        hres = iService.m_p->ExecQuery(_bstr_t("WQL"), _bstr_t(wsOut.c_str()),
            WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY, NULL, &iEnumerator.m_p);
        wsOut.clear();

        if (FAILED(hres))
            return ret;

        ULONG obj_num = 0;
        while (iEnumerator.m_p)
        {
            IWbemClassObject_Auto iClsObj;
            ULONG uReturn = 0;
            do
            {
                hres = iEnumerator.m_p->Next(WBEM_INFINITE, 1, &iClsObj.m_p, &uReturn);

                if (0 == uReturn)
                    return ret;

                obj_num += uReturn;

                if (1 == obj_num)
                {
                    hres = iClsObj.m_p->BeginEnumeration(WBEM_FLAG_NONSYSTEM_ONLY);

                    if (FAILED(hres))
                        break;

                    hres = iClsObj.m_p->Next(0, NULL, vtProp, 0, 0);

                    if (FAILED(hres))
                        break;

                    iClsObj.m_p->EndEnumeration();

                    if (FAILED(hres) || hres == WBEM_S_NO_MORE_DATA)
                        break;
                    else
                        ret = 0;
                }
            } while (false);
        }
        return ret;
    }
    //////////////////////////////////////////////////////////////////////////
public:
    //////////////////////////////////////////////////////////////////////////
    static int WmiGet(const char *wmi_namespace, const char *wmi_query, std::string& utf8_value)
    {
        VARIANT_Auto va;
        ComInitUinitAuto ciu;
        HRESULT hres;

        if (!ciu.initState())
            return -1;

        if (WmiGetVariant(wmi_namespace, wmi_query, &va.m_v) != 0)
            return -2;

        hres = VariantChangeType(&va.m_v, &va.m_v, VARIANT_ALPHABOOL, VT_BSTR);

        if (FAILED(hres))
            return -3;

        WC2MB::UnicodeToUtf8((wchar_t *)_bstr_t(va.m_v.bstrVal), utf8_value);
        return 0;
    }
    //////////////////////////////////////////////////////////////////////////
    static int RegGet(HKEY hKey, const char* subKey, const char* valueName, std::string&dataOut, DWORD ulOptions = 0, REGSAM samDesired = KEY_READ)
    {
        int ret = -1;
        HKEY_Auto keyRegistry;

#ifdef UNICODE
        std::wstring wSubKey;
        WC2MB::Utf8ToUnicode(subKey, wSubKey);
        std::wstring wValueName;
        WC2MB::Utf8ToUnicode(valueName, wValueName);
        const wchar_t* pSubKey = wSubKey.c_str();
        const wchar_t* pValueName = wValueName.c_str();
        std::wstring dOut;
#else
        const char* pSubKey = subKey;
        const char* pValueName = valueName;
        std::string& dOut = dataOut;
#endif

        if (RegOpenKeyEx(hKey, pSubKey, ulOptions, samDesired, &keyRegistry.m_p) != 0)
            return ret;

        DWORD szData = 0;
        if (RegQueryValueEx(keyRegistry.m_p, pValueName, NULL, NULL, NULL, &szData) == 0)
        {
            dOut.resize(szData, 0x0);
            if (RegQueryValueEx(keyRegistry.m_p, pValueName, NULL, NULL, (LPBYTE)dOut.c_str(), &szData) != 0)
            {
                dOut.clear();
                return ret;
            }
            else
            {
                ret = 0;
            }
        }
        else
        {
            return ret;
        }

#ifdef UNICODE
        WC2MB::UnicodeToUtf8(dOut.c_str(), dataOut);
#endif

        return ret;
    }
    //////////////////////////////////////////////////////////////////////////
};
//////////////////////////////////////////////////////////////////////////
class NetUtils
{
public:
    struct MibIfRow
    {
        int m_idx;
        MIB_IFROW m_mir1;
        MIB_IF_ROW2 m_mir2;
    };
private:
    static void setMibIfRowIndex(MibIfRow& ifRow, DWORD index)
    {
        switch (ifRow.m_idx)
        {
        case 1:
            ifRow.m_mir1.dwIndex = index;
            break;
        case 2:
            ifRow.m_mir2.InterfaceLuid.Value = 0;
            ifRow.m_mir2.InterfaceIndex = index;
            break;
        default:
            break;
        }
    }
    static int getMibIfRowIndex(MibIfRow& mir)
    {
        switch (mir.m_idx)
        {
        case 1:
            return mir.m_mir1.dwIndex;
            break;
        case 2:
            return mir.m_mir2.InterfaceIndex;
            break;
        default:
            break;
        }
        return -1;
    }
    static DWORD GetIfEntry_x(MibIfRow& mir)
    {
        switch (mir.m_idx)
        {
        case 1:
            return GetIfEntry(&mir.m_mir1);
            break;
        case 2:
            return GetIfEntry2(&mir.m_mir2);
        default:
            break;
        }
        return -1;
    }
    static void getMibIfRowDescription(MibIfRow& mir, std::string& description)
    {
        if (1 == mir.m_idx)
        {
            unsigned int codepage = CP_ACP;

            /*static */OSVERSIONINFO vi = { 0 };
            if (0 == vi.dwOSVersionInfoSize)
            {
                memset(&vi, 0, sizeof(vi));
                vi.dwOSVersionInfoSize = sizeof(vi);
                if (GetVersionEx(&vi) && 6 <= vi.dwMajorVersion)
                    codepage = CP_OEMCP;
            }
            std::wstring wsOut;
            WC2MB::toUnicode(codepage, (char*)mir.m_mir1.bDescr, wsOut);
            WC2MB::UnicodeToUtf8(wsOut.c_str(), description);
        }
        else if (2 == mir.m_idx)
        {
            WC2MB::UnicodeToUtf8(mir.m_mir2.Description, description);
        }
    }
public:
    static int getMibIfRow(const char* ifName, MibIfRow& mir)
    {
        int ret = -1;
        do
        {
            DWORD dwSize = 0;
            std::string sIPAddrTable;
            MIB_IPADDRTABLE* pIPAddrTable = nullptr;
            if (ERROR_INSUFFICIENT_BUFFER == GetIpAddrTable(NULL, &dwSize, 0))
            {
                sIPAddrTable.resize(dwSize, 0x0);
                pIPAddrTable = (MIB_IPADDRTABLE*)sIPAddrTable.c_str();
                if (GetIpAddrTable(pIPAddrTable, &dwSize, 0) != NO_ERROR)
                    break;
            }
            else
            {
                break;
            }

            dwSize = 0;
            std::string sIfTable;
            MIB_IFTABLE* pIfTable = nullptr;
            if (ERROR_INSUFFICIENT_BUFFER == GetIfTable(NULL, &dwSize, 0))
            {
                sIfTable.resize(dwSize);
                pIfTable = (MIB_IFTABLE*)sIfTable.c_str();
                if (NO_ERROR != GetIfTable(pIfTable, &dwSize, 0))
                    break;
            }
            else
            {
                break;
            }

            std::string utf8Descr;
            IN_ADDR inAddr;
            std::string ip;
            for (unsigned i = 0; i < pIfTable->dwNumEntries; ++i)
            {
                setMibIfRowIndex(mir, pIfTable->table[i].dwIndex);
                if (NO_ERROR != GetIfEntry_x(mir))
                    continue;

                getMibIfRowDescription(mir, utf8Descr);
                if (utf8Descr == ifName)
                {
                    ret = 0;
                    break;
                }

                for (unsigned j = 0; j < pIPAddrTable->dwNumEntries; ++j)
                {
                    if (getMibIfRowIndex(mir) == pIPAddrTable->table[j].dwIndex)
                    {
                        inAddr.S_un.S_addr = pIPAddrTable->table[j].dwAddr;
                        ip = inet_ntoa(inAddr);
                        if (ifName == ip)
                        {
                            ret = 0;
                            break;
                        }
                        if (1)
                        {
                            if (utf8Descr == ifName)
                            {
                                ret = 0;
                                break;
                            }
                            int cmpRv = strcmp(ifName, utf8Descr.c_str());
                            int i = 0;
                        }
                    }
                }
                if (0 == ret)    break;
            }
        } while (false);

        return ret;
    }

    static int getMtu(MibIfRow& mir)
    {
        switch (mir.m_idx)
        {
        case 1:
            return mir.m_mir1.dwMtu;
            break;
        case 2:
            return mir.m_mir2.Mtu;
            break;
        default:
            break;
        }
        return 0;
    }
};
//////////////////////////////////////////////////////////////////////////
#if 1
#include <string>
#include <iostream>
int main_test()
{
    if (1)
    {
        std::string sOut;
        int retW = Utils::WmiGet("root\\cimv2", "SELECT CSName FROM Win32_OperatingSystem", sOut);
        std::cout << "CSName: " << sOut << std::endl;
        int retR = Utils::RegGet(HKEY_LOCAL_MACHINE, "HARDWARE\\DESCRIPTION\\System", "SystemBiosVersion", sOut);
        std::cout << "SystemBiosVersion: " << sOut << std::endl;
    }
    if (1)
    {
        NetUtils::MibIfRow mir;
        memset(&mir, 0, sizeof(mir));
        mir.m_idx = 2;
        int retI = NetUtils::getMibIfRow("127.0.0.1", mir);
        std::cout << "Mtu: " << NetUtils::getMtu(mir) << std::endl;
    }
    for (std::string line; std::cout << "press [q] to quit..." << std::endl&& std::getline(std::cin, line);)
    {
        if ("q" == line)
            break;
    }
    return 0;
}
#endif
//////////////////////////////////////////////////////////////////////////
#endif//SYSTEM_WINDOWS_H
