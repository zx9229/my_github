import wmi


# pip install wmi
# 从http://sourceforge.net/projects/pywin32/files/?source=navbar安装win32com。

# code copy from  http://halfish.iteye.com/blog/1706810
def GetDiskInfo():
    """
    获取物理磁盘信息。
    """
    tmplist = []
    theWMI = wmi.WMI()
    for physicalDisk in theWMI.Win32_DiskDrive():
        tmpdict = {}
        tmpdict["Caption"] = physicalDisk.Caption
        tmpdict["Size"] = int(physicalDisk.Size) / 1024 / 1024 / 1024
        tmplist.append(tmpdict)
    return tmplist


def GetFsInfo():
    """
    获取文件系统信息
    包含分区的大小、可用量、挂载点信息
    """
    tmplist = []
    theWMI = wmi.WMI()
    for physicalDisk in theWMI.Win32_DiskDrive():
        for partition in physicalDisk.associators("Win32_DiskDriveToDiskPartition"):
            for logicalDisk in partition.associators("Win32_LogicalDiskToPartition"):
                tmpdict = {}
                tmpdict["Caption"] = logicalDisk.Caption
                tmpdict["Size"] = int(logicalDisk.Size) / 1024 / 1024 / 1024  # TotalSize
                tmpdict["FreeSpace"] = int(logicalDisk.FreeSpace) / 1024 / 1024 / 1024  # 剩余多少空间
                tmplist.append(tmpdict)
    return tmplist


disk = GetDiskInfo()
print("DiskInfo", disk, sep="\n", end="\n\n")
fs = GetFsInfo()
print("FsInfo", fs, sep="\n")
