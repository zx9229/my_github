//http://www.pstips.net/remove-file-to-recycle-bin.html
//http://www.bathome.net/viewthread.php?tid=37633
//http://blog.csdn.net/xiaolongwang2010/article/details/9987355
//http://blog.csdn.net/julius819/article/details/6990594


#include <string>
#include <iostream>
#include <windows.h>
#include <Shlwapi.h>
#pragma comment(lib,"Shlwapi.lib")


void formatMessage(int dwMessageId, std::string& msgOut)
{
    LPVOID lpMsgBuf = NULL;
    FormatMessage(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
        NULL,
        dwMessageId,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), //Default language  
        (LPTSTR)&lpMsgBuf,
        0,
        NULL
    );
    msgOut = (LPCTSTR)lpMsgBuf;
    LocalFree(lpMsgBuf);
}

int main(int argc, char** argv)
{
    if (2 != argc)
    {
        std::cout << "无输入/输入过多,程序不予处理,即将退出..." << std::endl;
        return -1;
    }
    if (MAX_PATH < std::strlen(argv[1]))
    {
        std::cout << "输入参数过长,程序不予处理,即将退出..." << std::endl;
        return -1;
    }

    TCHAR strSrcFilePath[MAX_PATH + 1] = { 0 };
    std::strncpy(strSrcFilePath, argv[1], sizeof(strSrcFilePath) - 1);

    if (!PathFileExists(strSrcFilePath))
    {
        std::cout << "输入的路径不存在,,程序不予处理,即将退出..." << std::endl;
        return -1;
    }

    SHFILEOPSTRUCT sfos = { 0 };//ShellFileOperatorStruct;
    sfos.hwnd = NULL;
    sfos.wFunc = FO_DELETE; //删除操作
    sfos.pFrom = strSrcFilePath;
    sfos.pTo = NULL; //一定要是NULL
    sfos.fFlags = FOF_ALLOWUNDO/*允许放到回收站*/ | FOF_NOCONFIRMATION/*不出现确认对话框*/;
    sfos.hNameMappings = NULL;

    int retVal = SHFileOperation(&sfos);
    if (retVal)
    {
        std::string msgDesc;
        formatMessage(retVal, msgDesc);
        std::cout << msgDesc << std::endl;
    }

    return retVal;
}
