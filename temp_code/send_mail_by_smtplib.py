import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


def an_example():
    host = "smtp.163.com"  # 发件服务器的IP
    port = 25  # 发件服务器的端口
    #
    from_addr_realname = "我在163的测试邮箱"  # 发件人的邮箱昵称
    from_addr_email_address = "my_test@163.com"  # 发件人的邮箱账号
    email_password = None  # 发件人的邮箱密码(对于163邮箱是授权码)
    #
    to_addr_list = [
        ("", "my_test@qq.com"),
        ("我在126的测试邮箱", "my_test@126.com"),
        ("我在sina的测试邮箱", "my_test@sina.com"),
        ("我在sohu的测试邮箱", "my_test@sohu.com"),
    ]  # 收件人的(邮箱昵称,邮箱账号)列表
    #
    mail_subject = "[测试邮件]使用Python的SMTP通过163邮箱发送测试邮件"  # 邮件主题
    mail_subject_charset = 'UTF-8'  # 邮件主题的字符集
    #
    mail_text = """ 邮件正文在这里。你可以将其替换成想要发送的内容 """  # 邮件正文
    mail_text_type = "plain"  # 邮件正文的类型(plain:普通文本).
    mail_text_charset = "utf-8"  # 邮件正文的字符集
    #
    from_addr = formataddr((from_addr_realname, from_addr_email_address))
    to_addrs = [formataddr(pair) for pair in to_addr_list]
    #
    message = MIMEText(mail_text, mail_text_type, mail_text_charset)
    message['From'] = from_addr  # 发件人地址
    message['To'] = ",".join(to_addrs)  # 收件人地址列表
    message['Subject'] = Header(mail_subject, mail_subject_charset)  # 邮件主题
    #
    try:
        smtpObj = smtplib.SMTP(host=host, port=port)
        #
        if email_password:  # 如果配置了密码,就尝试登陆邮箱.
            login_ret = smtpObj.login(from_addr_email_address, email_password)
            print("[邮箱登录成功]", login_ret)
        #
        send_ret = smtpObj.sendmail(from_addr, to_addrs, message.as_string())
        print("[邮件发送成功]", send_ret)
    except Exception as ex:
        print("[邮件发送失败]", ex)


if __name__ == '__main__':
    an_example()
    print("DONE. will exit...")
    exit(0)
