import paramiko,os

def upload_file_with_key(local_path, remote_path, hostname, port, username, key_file):
    if not os.path.exists(key_file):
        print(f"Error: Private key file does not exist at {key_file}")
        return
    else:
        print("c")
    # 创建SSH客户端
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 使用SSH密钥连接到服务器
    ssh_client.connect(hostname, port, username, key_filename=key_file)

    # 使用SFTP客户端上传文件
    sftp = ssh_client.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()

    # 关闭SSH连接
    ssh_client.close()
    print("File uploaded successfully")

# 用法示例
upload_file_with_key(
    r'C:\Users\Morning\Desktop\my_project\llm_riddle\main.py',  # 本地文件路径
    '/home/opc/', # 远程文件路径
    '130.61.253.72',            # 服务器地址
    22,                    # SSH端口号，默认为22
    'opc',            # 用户名
    r'C:\Users\Morning\.ssh\ssh-key-2023-02-27.key'      # 私钥文件路径，如 ~/.ssh/id_rsa
)
"""
scp -i C:\Users\Morning\.ssh\ssh-key-2023-02-27.key C:\Users\Morning\Desktop\my_project\llm_riddle\main.py opc@130.61.253.72:/www/wwwroot/flask_ques/
scp -i C:\Users\Morning\.ssh\ssh-key-2023-02-27.key C:\Users\Morning\Desktop\my_project\llm_riddle\templates\chat.html opc@130.61.253.72:/www/wwwroot/flask_ques/templates/

"""