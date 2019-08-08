import sys
import os


def calc_depth(dirpath, subpath):
    """计算某个子目录subpath相对于父代目录dirpath的深度"""
    dirpath = os.path.abspath(dirpath)
    subpath = os.path.abspath(subpath)
    if subpath.find(dirpath) != 0:
        raise ValueError("subpath应当是dirpath的子目录")
    if subpath != dirpath:
        path_str = subpath[len(dirpath):]
        if path_str.find(os.path.sep) != 0:
            raise ValueError("subpath应当是dirpath的子目录")
    depth = 0
    while subpath != dirpath:
        subpath = os.path.dirname(subpath)
        depth += 1
    return depth


def is_last_subdir(dir):
    """对父目录来说,自己是/不是最后一个一级子目录"""
    dir = os.path.abspath(dir)
    top = os.path.dirname(dir)
    if top == dir:
        raise ValueError("dir没有父目录")
    for dirpath, dirnames, filenames in os.walk(top):
        if dirpath != top:
            raise Exception("逻辑错误")
        if len(dirnames) == 0:
            raise Exception("逻辑错误")
        last_sub_dir = os.path.join(dirpath, dirnames[-1:][0])
        last_sub_dir = os.path.abspath(last_sub_dir)
        break
    return True if dir == last_sub_dir else False


def calc_subdirs_status(top, subdir):
    """计算路径subdir命中的所有子目录的状态(是不是最后一个一级子目录)"""
    status = []
    top = os.path.abspath(top)
    subdir = os.path.abspath(subdir)
    depth = calc_depth(top, subdir)
    if depth:
        while top != subdir:
            status.append(is_last_subdir(subdir))
            subdir = os.path.dirname(subdir)
    status.reverse()
    return status


def calc_show_str(allStatus):
    showStr = ""
    for i in range(len(allStatus)):
        isLast = allStatus[i]
        if i == len(allStatus) - 1:
            if isLast:
                showStr += "└─"
            else:
                showStr += "├─"
        else:
            if isLast:
                showStr += "   "
            else:
                showStr += "│  "
    return showStr


def calc_all_ext(top):
    top = os.path.abspath(top)
    allFilename = []
    for dirpath, dirnames, filenames in os.walk(top):
        allFilename = filenames
        break
    extSet = set()
    for filename in allFilename:
        filename = os.path.basename(filename)
        name, ext = os.path.splitext(filename)
        if len(ext) == 0 and len(name) > 0 and '.' == name[0]:
            ext = name
        extSet.add(ext)
    return extSet


def tree(top):
    top = os.path.abspath(top)
    for dirpath, dirnames, filenames in os.walk(top):
        dirpath = os.path.abspath(dirpath)
        allStatus = calc_subdirs_status(top, dirpath)
        showStr = calc_show_str(allStatus)
        allExt = calc_all_ext(dirpath)
        showStr += os.path.basename(dirpath) + "    " + allExt.__str__()
        print(showStr)


if __name__ == "__main__":
    defalultPath = sys.argv[0]
    if os.path.isfile(defalultPath):
        defalultPath = os.path.dirname(defalultPath)
    path = defalultPath
    if 1 < len(sys.argv):
        possiblePath = sys.argv[1]
        if os.path.isdir(possiblePath):
            path = possiblePath
    tree(path)
    exit(0)

    top = r'C:\new_tdx\vipdoc'
    tree(top)
