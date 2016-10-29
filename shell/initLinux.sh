#!/bin/sh

########################################################len=64##
userName="t1"
userPassword="t1pwd"
gidGroup="root"
userdelPermission=1  # 如果用户存在,允许删除这个用户.
sudoersFilePath="/etc/sudoers"
zoneInfoFilePath="/usr/share/zoneinfo/Asia/Shanghai"
################################################################

# 增加一个用户,并且更新这个用户的密码(无依赖).
AddUserAndUpdatePassword()
{
    local userName="$1"
    local userPassword="$2"
    local gidGroup="$3"
    local userdelPermission=$4
    
    if [ -z ${userName} ] || [ -z ${userPassword} ]; then
        echo "userName(${userName}) or userPassword(${userPassword}) is empty, will terminate."
        return 1
    fi
    
    id ${userName} > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "userName(${userName}) is exist."
        if [ ! ${userdelPermission} -eq 1 ]; then
            echo "have no permission to delete userName, will terminate."
            return 1
        fi
        
        # echo "userName(${userName}) will be deleted."
        userdel -r ${userName}
        if [ $? -ne 0 ]; then
            echo "userName(${userName}) was deleted failed. will terminate."
            return 1
        else
            : # echo "userName(${userName}) was deleted successfully."
        fi
    fi
    
    local cmd=
    if [ -n "${gidGroup}" ]; then
        cmd="useradd ${userName} -g ${gidGroup}"
    else
        cmd="useradd ${userName}"
    fi
    ${cmd}
    if [ $? -ne 0 ]; then
        echo "cmd=(${cmd}) failed, will terminate."
        return 1
    fi
    
    echo "${userPassword}" | passwd --stdin ${userName} > /dev/null
    if [ $? -ne 0 ]; then
        echo "update password of userName(${userName}) fail. will terminate."
        return 1
    fi
    
    echo "=> success. userName(${userName}), gidGroup(${gidGroup}), userdelPermission(${userdelPermission})."
    return 0
}

# 禁止root用户远程登录(无依赖).
ForbidRootLogin()
{
    # -f filename,文件为普通文件则返回0,可以在命令行下[ -f /etc/passwd ]然后 echo $? 测试,可以"man test"查看更多详情.
    local fileName="/etc/ssh/sshd_config"
    if [ ! -f ${fileName} ]; then
        echo "fileName(${fileName}) does not exist. will terminate."
        return 1
    fi
    
    local cntYes=$(sed -r -n "s/^[ \t]*PermitRootLogin[ \t]+yes[ \t#]*.*$/PermitRootLogin no/p" "${fileName}" | wc -l)
    local cntNo=$(grep -E --count --regexp="^[ \t]*PermitRootLogin[ \t]+no[ \t#]*.*$"           "${fileName}")
    if   [ ${cntYes} -eq 0 ] && [ ${cntNo} -eq 1 ]; then
        echo "PermitRootLogin_no, will do nothing."
    elif [ ${cntYes} -eq 1 ] && [ ${cntNo} -eq 0 ]; then
        echo "PermitRootLogin_yes, will forbid it."
        # 将"PermitRootLogin yes"这一行替换为"PermitRootLogin no"这一行.
        sed -r -i "s/^[ \t]*PermitRootLogin[ \t]+yes[ \t#]*.*$/PermitRootLogin no/g" "${fileName}"
        if [ $? -ne 0 ]; then
            echo "fileName(${fileName}) was modified failed. will terminate."
            return 1
        else
            : # echo "fileName(${fileName}) was modified successfully."
        fi
        
        service sshd restart
        if [ $? -ne 0 ]; then
            echo "service_sshd_restart fail, will terminate."
            return 1
        else
            : # echo "service_sshd_restart success."
        fi
    else
        echo "fileName(${fileName}) abnormal, will terminate."
        return 1
    fi
    
    echo "=> success. ForbidRootLogin."
    return 0
}

# 用visudo校验sudoers文件的合法性(被 AddSudoPermission 函数依赖).
VisudoCheck()
{
    visudo -c > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        return 1
    fi
    # 将校验结果转成小写的字符串,然后检索字符串.
    # 找不到"error",找不到"warn",并且能找到"parsed OK",就认为校验绝对成功.
    local msgLowercase=
    declare -l msgLowercase  # 转小写,只需要将变量名字"declare -l"/"typeset -l"后,再给变量赋值,变量的内容即为小写.
    local msgOrigin=$(visudo -c  2>&1)
    msgLowercase=${msgOrigin}
    
    expr match "${msgLowercase}" "^.*error.*$"     > /dev/null
    if [ $? -eq 0 ]; then
        return 2
    fi
    
    expr match "${msgLowercase}" "^.*warn.*$"      > /dev/null
    if [ $? -eq 0 ]; then
        return 3
    fi
    
    expr match "${msgOrigin}"    "^.*parsed OK$"   > /dev/null
    if [ $? -ne 0 ]; then
        return 4
    fi
    
    return 0
}

# 给一个用户增加最高的sudo权限(依赖 VisudoCheck 函数).
AddSudoPermission()
{
    local fileName="$1"
    local userName="$2"
    local rootExactPattern='^[ \t]*root[ \t]+ALL=\(ALL\)[ \t]+ALL[ \t]*$'
    local userExactPattern="^[ \t]*${userName}[ \t]+ALL=\(ALL\)[ \t]+ALL[ \t]*$"
    local userFuzzyPattern="^[ \t]*${userName}[ \t]+.*$"  # 在双引号("")里面,"\t"就是"\t"字符串,而没有被转换成"Tab".
    local newLineWilAppend="${userName}\tALL=(ALL)\tALL"
    
    # TODO: visudo校验的文件如果和输入的文件名不是同一个文件,就太搞笑了.
    VisudoCheck
    if [ $? -ne 0 ]; then
        echo "VisudoCheck fail. will terminate."
        return 1
    fi
    
    # TODO: 如果sed命令直接失败的话,我们是不知道的,此时返回的结果仅仅是wc命令的结果.
    local cntRoot=$(sed -r -n "s/${rootExactPattern}/&/p" "${fileName}" | wc -l)
    if [ ${cntRoot} -ne 1 ]; then
        echo "fileName(${fileName}) is not recognized, will terminate."
        return 1
    fi
    
    local cntUser=$(sed -r -n "/${userExactPattern}/p"    "${fileName}" | wc -l)
    if [ ${cntUser} -gt 1 ]; then
        echo "fileName(${fileName}) may have error, will terminate."
        return 1
    elif [ ${cntUser} -eq 1 ]; then
        echo "fileName(${fileName}) has been configured userName(${userName}) permissions."
    else
        cntUser=$(sed -r -n   "/${userFuzzyPattern}/p"    "${fileName}" | wc -l)
        if [ ${cntUser} -ne 0 ]; then
            echo "fileName(${fileName}) may contains userName(${userName}), we recommand editing with visudo, will terminate."
            return 1
        fi
        
        chmod u+w "${fileName}"
        if [ $? -ne 0 ]; then
            echo "fileName(${fileName}) 'chmod u+w' fail. will terminate."
            return 1
        fi
        
        sed -r -i "/${rootExactPattern}/a ${newLineWilAppend}" "${fileName}"
        local retVal=$?
        
        chmod u-w "${fileName}"
        if [ $? -ne 0 ]; then
            echo "fileName(${fileName}) 'chmod u-w' fail. just log and do nothing."
        fi
        
        if [ ${retVal} -ne 0 ]; then
            echo "fileName(${fileName}) was modified failed. reasion: Modify command execution failed."
            return 1
        fi
        
        cntUser=$(sed -r -n "/${userFuzzyPattern}/p"  "${fileName}" | wc -l)
        if [ ${cntUser} -ne 1 ]; then
            echo "fileName(${fileName}) was modified failed. reason: userName(${userName}) not found."
            return 1
        fi
        
        VisudoCheck
        if [ $? -ne 0 ]; then
            echo "VisudoCheck fail. will terminate."
            return 1
        fi
    fi
    
    echo "=> success. AddSudoPermission, userName(${userName})"
    return 0
}

# 修改时区,校准时间(无依赖).
ChangeTimeZoneAndSetDateTime()
{
    local zoneInfoFilePath="$1"
    # cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
    \cp -f "${zoneInfoFilePath}" "/etc/localtime"
    if [ $? -ne 0 ]; then
        echo "copy zoneinfo file(${zoneInfoFilePath}) FAIL. will terminate."
        return 1
    fi
    
    echo "yum command begin..."
    yum install -y ntpdate > /dev/null
    echo "yum command end."
    
    ntpdate us.ntp.org.cn
    if [ $? -ne 0 ]; then
        echo "set date and time FAIL. will terminate."
        return 1
    fi
    
    echo "=> success. ChangeTimeZoneAndSetDateTime."
    return 0
}

################################################################

AddUserAndUpdatePassword "${userName}" "${userPassword}" "${gidGroup}" "${userdelPermission}"
[ $? -eq 0 ] && ForbidRootLogin
[ $? -eq 0 ] && AddSudoPermission "${sudoersFilePath}" "${userName}"
[ $? -eq 0 ] && ChangeTimeZoneAndSetDateTime "${zoneInfoFilePath}"

################################################################
