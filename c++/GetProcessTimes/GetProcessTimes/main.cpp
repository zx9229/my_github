// 本文件以 UTF-8 无 BOM 格式编码
#include <windows.h>
#include <stdio.h>

void xxx(DWORD processID)
{
    HANDLE hProcess;

    // Print the process identifier.

    printf("\nProcess ID: %u\n", processID);

    // Print information about the memory usage of the process.

    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, processID);
    if (NULL == hProcess)
        return;


    FILETIME createTime = {}, exitTime = {}, kernelTime = {}, userTime = {};
    if (GetProcessTimes(hProcess, &createTime, &exitTime, &kernelTime, &userTime) == FALSE)
    {
        DWORD errCode = GetLastError();
        return;
    }

    SYSTEMTIME cTimeUtc = {};
    FileTimeToSystemTime(&createTime, &cTimeUtc);//UTC

    TIME_ZONE_INFORMATION defaultValue = {};
    GetTimeZoneInformation(&defaultValue);

    //将UTC时间转换为指定时区的时间.
    SYSTEMTIME cTime = {};
    SystemTimeToTzSpecificLocalTime(&defaultValue, &cTimeUtc, &cTime);

    printf("%04d-%02d-%02d %02d:%02d:%02d", cTime.wYear, cTime.wMonth, cTime.wDay, cTime.wHour, cTime.wMinute, cTime.wSecond);

    CloseHandle(hProcess);
}

int main(int argc, char** argv)
{
    if (2 != argc)
        return 2;

    DWORD pid = atoi(argv[1]);
    xxx(pid);

    return 0;
}
