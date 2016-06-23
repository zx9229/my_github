import os
import paramiko
#github上搜索paramiko，点击第一位的repository，可以看到readme，readme里面有链接：
#http://docs.paramiko.org/en/1.17/

# http://blog.chinaunix.net/xmlrpc.php?r=blog/article&uid=28841896&id=4812584
# http://www.2cto.com/kf/201510/446146.html
# ssh://56f2bc7d0c1e66ebac000017@python-zx9229test.rhcloud.com/~/git/python.git/
sshClient = paramiko.SSHClient()
# 加载本地的known_hosts文件，该文件是纪录连到对方时，对方给的 host key。每次连线时都会检查目前对方给的 host key 与纪录的 host key 是否相同，可以简单验证连结是否又被诈骗等相关事宜。
sshClient.load_system_host_keys()

if False:
    # 加上这句话不用担心选yes的问题，会自动选上（用ssh连接远程主机时，第一次连接时会提示是否继续进行远程连接，选择yes）
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

openSSHppk = os.path.expanduser(r"E:\my_code\SSH2_RSA_2048.ppk_ToOpenSSH.OpenSSHppk")
pkey = paramiko.RSAKey.from_private_key_file(openSSHppk, "Wap1234567")
print("will connect...")
sshClient.connect(hostname="python-zx9229test.rhcloud.com",
                  port=22,
                  username="56f2bc7d0c1e66ebac000017",
                  pkey=pkey)
print("connect success.")
stdin, stdout, stderr = sshClient.exec_command("cd app-deployments/zx_test/")
print(stdout.read())
stdin, stdout, stderr = sshClient.exec_command("ls -alh")
print(stdout.read())
sshClient.close()
