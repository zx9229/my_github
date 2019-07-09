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

#include <windows.h>
#include <stdio.h>
#include <psapi.h>

void testGetProcessMemoryInfo(DWORD processID)
{
    HANDLE hProcess = NULL;
    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION, FALSE, processID);
    if (NULL == hProcess)
        return;

    PROCESS_MEMORY_COUNTERS pmc = {};
    if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc)))
    {
        //TODO:
    }

    CloseHandle(hProcess);
}

void testGetProcessTimes(DWORD processID)
{
    HANDLE hProcess = NULL;
    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, processID);
    if (NULL == hProcess)
        return;

    //备注:
    //所有时间都使用FILETIME数据结构表示。这种结构包含两个32位值，它们组合形成一个100纳秒时间单位的64位计数.
    //流程创建和退出时间是以时间表示的时间点，表示为1601年1月1日午夜在英格兰格林威治的时间。应用程序可以使用几种函数将这些值转换为更常用的表单.
    //进程内核模式和用户模式时间是时间量。例如，如果进程在内核模式下花费了一秒钟时间，则此函数将填充由lpKernelTime指定的 FILETIME结构，其值为一千万的64位值。这是一秒钟内100纳秒单位的数量.
    //要检索进程线程使用的CPU时钟周期数，请使用QueryProcessCycleTime函数.

    FILETIME createTime = {}, exitTime = {}, kernelTime = {}, userTime = {};
    GetProcessTimes(hProcess, &createTime, &exitTime, &kernelTime, &userTime);

    SYSTEMTIME cTimeUtc = {};
    FileTimeToSystemTime(&createTime, &cTimeUtc);//UTC

    TIME_ZONE_INFORMATION defaultValue = {};
    GetTimeZoneInformation(&defaultValue);

    //将UTC时间转换为指定时区的时间.
    SYSTEMTIME cTime = {};
    SystemTimeToTzSpecificLocalTime(&defaultValue, &cTimeUtc, &cTime);

    printf("%d-%d-%d %02d:%02d:%02d", cTime.wYear, cTime.wMonth, cTime.wDay, cTime.wHour, cTime.wMinute, cTime.wSecond);

    CloseHandle(hProcess);
}

int main_2(void)
{
    // Get the list of process identifiers.

    DWORD aProcesses[65535], cbNeeded, cProcesses;
    if (!EnumProcesses(aProcesses, sizeof(aProcesses), &cbNeeded))
    {
        return 1;
    }

    // Calculate how many process identifiers were returned.

    cProcesses = cbNeeded / sizeof(DWORD);

    // Print the memory usage for each process

    for (unsigned int i = 0; i < cProcesses; i++)
    {
        testGetProcessMemoryInfo(aProcesses[i]);
        testGetProcessMemoryInfo(aProcesses[i]);
    }

    return 0;
}
