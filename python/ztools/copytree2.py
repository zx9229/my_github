import os
import shutil


def copytree2(srcDir, dstDir):
    """
    hutil.copytree(src, dst)中的src和dst都只能是目录,且dst必须不存在,
    这个代码中的dst可以存在.
    """
    if not os.path.exists(dstDir):
        shutil.copytree(srcDir, dstDir)
    else:
        for curDirpath, subDirnames, filenames in os.walk(srcDir):
            for srcSubDir in subDirnames:
                dstSubDir = os.path.join(dstDir, srcSubDir)
                srcSubDir = os.path.join(curDirpath, srcSubDir)
                copytree2(srcSubDir, dstSubDir)
            for filename in filenames:
                filename = os.path.join(curDirpath, filename)
                shutil.copy2(filename, dstDir)


if __name__ == "__main__":
    exit(0)
