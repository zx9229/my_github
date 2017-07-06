# !/bin/bash

# 此脚本做了哪些操作:
# 将 DATA_PATH 下面的 ALL_FILE_NAME 里面列的文件拷贝到 GIT_PATH 下.
# 然后在 GIT_PATH 目录下执行 add commit pull push 操作.
# 说明:
#     : 需要预先安装 expect (yum install expect) 才行.
#     : 文件的编码应为UTF-8, 应以'LF'作为换行符.
# 问题:
#     : 如果密码错误,git会要求重新输入密码,此时脚本会死在那里.该问题未解决.


GIT_PATH="/home/test/git_store/data/"
DATA_PATH="/home/test/data_folder/"
ALL_FILE_NAME=("file1.csv"  "file2.dat"  "file3.txt")
GIT_PASSWORD="mima"


cd ${GIT_PATH}
if [ $? -ne 0 ]; then
    echo "ERROR, cd"
    exit 1
fi

cd ${DATA_PATH}
if [ $? -ne 0 ]; then
    echo "ERROR, cd"
    exit 1
fi



for((i=0;i<${#ALL_FILE_NAME[@]};++i)); do
    filename=${ALL_FILE_NAME[${i}]}
    cp ${filename} ${GIT_PATH}
    if [ $? -ne 0 ]; then
        echo "ERROR, copy"
        exit 1
    fi
done

cd ${GIT_PATH}
if [ $? -ne 0 ]; then
    echo "ERROR, cd"
    exit 1
fi

for((i=0;i<${#ALL_FILE_NAME[@]};++i)); do
    filename=${ALL_FILE_NAME[${i}]}
    git add ${filename}
    if [ $? -ne 0 ]; then
        echo "ERROR, git add"
        exit 1
    fi
done

need_not_commit=$(git status|grep --count -E "nothing +(added +to)|(to) +commit")
if [ ${need_not_commit} -ne 0 ]; then
    echo "nothing to commit."
    exit 0
fi

date_time_str=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "files updated. script auto. update_time is ${date_time_str}"
if [ $? -ne 0 ]; then
    echo "ERROR, git commit"
    exit 1
fi

expect -c '
spawn git pull --rebase
expect "Password:"
send '${GIT_PASSWORD}'\n
set timeout 120
expect eof
set timeout 1
catch wait result
exit [lindex $result 3]
'
if [ $? -ne 0 ]; then
    echo "ERROR, git pull"
    exit 1
fi

expect -c '
spawn git push
expect "Password:"
send '${GIT_PASSWORD}'\n
expect eof
catch wait result
exit [lindex $result 3]
'
if [ $? -ne 0 ]; then
    echo "ERROR, git push"
    exit 1
fi
