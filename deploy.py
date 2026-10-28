import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()

hostname = os.getenv("SSH_HOST", "")
username = os.getenv("SSH_USER", "root")
password = os.getenv("SSH_PASSWORD", "")


def execute_command(ssh, command):
    print(f"Komut çalıştırılıyor: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode("utf-8")
    err = stderr.read().decode("utf-8")
    if exit_status == 0:
        print("Bitti.")
    else:
        print(f"Hata Kodu: {exit_status}\nÇıktı: {output}\nHata: {err}")
    return exit_status, output


def deploy():
    if not hostname or not password:
        print("Hata: Lütfen .env dosyasında SSH_HOST ve SSH_PASSWORD değişkenlerini tanımlayın.")
        sys.exit(1)

    print("Sunucuya bağlanılıyor...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Bağlantı başarılı!")

        execute_command(ssh, "apt-get update")
        execute_command(
            ssh,
            "DEBIAN_FRONTEND=noninteractive apt-get install python3 python3-pip python3-venv chromium-browser chromium-chromedriver screen -y",
        )
        execute_command(ssh, "mkdir -p /root/yhtbot")

        print("main.py dosyası sunucuya kopyalanıyor...")
        sftp = ssh.open_sftp()
        sftp.put("main.py", "/root/yhtbot/main.py")
        if os.path.exists(".env"):
            sftp.put(".env", "/root/yhtbot/.env")
        sftp.close()
        print("Dosya kopyalandı.")

        execute_command(ssh, "python3 -m venv /root/yhtbot/venv")
        execute_command(ssh, "/root/yhtbot/venv/bin/pip install selenium requests python-dotenv")
        execute_command(ssh, "screen -S yhtbot -X quit || true")

        print("Bot arka planda başlatılıyor...")
        execute_command(ssh, "cd /root/yhtbot && screen -dmS yhtbot /root/yhtbot/venv/bin/python main.py")

        _, out = execute_command(ssh, "screen -ls")
        if "yhtbot" in out:
            print("Kurulum tamamlandı! Bot başarıyla sunucuda çalışıyor.")
        else:
            print("Bot başlatılırken bir sorun oluştu.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        ssh.close()


if __name__ == "__main__":
    deploy()
