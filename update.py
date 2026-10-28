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
    return exit_status, stdout.read().decode("utf-8")


def update():
    if not hostname or not password:
        print("Hata: Lütfen .env dosyasında SSH_HOST ve SSH_PASSWORD değişkenlerini tanımlayın.")
        sys.exit(1)

    print("Sunucuya bağlanılıyor...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Bağlantı başarılı!")

        print("Güncel main.py dosyası sunucuya aktarılıyor...")
        sftp = ssh.open_sftp()
        sftp.put("main.py", "/root/yhtbot/main.py")
        if os.path.exists(".env"):
            sftp.put(".env", "/root/yhtbot/.env")
        sftp.close()
        print("Dosya aktarıldı.")

        print("Eski bot kapatılıyor...")
        execute_command(ssh, "screen -S yhtbot -X quit || true")

        print("Bot güncellenmiş tarih ile yeniden başlatılıyor...")
        execute_command(ssh, "cd /root/yhtbot && screen -dmS yhtbot /root/yhtbot/venv/bin/python main.py")

        _, out = execute_command(ssh, "screen -ls")
        if "yhtbot" in out:
            print("Güncelleme tamamlandı! Yeni tarihlerle arama başladı.")
        else:
            print("Bot başlatılırken bir sorun oluştu.")

    except Exception as e:
        print(f"Hata: {e}")
    finally:
        ssh.close()


if __name__ == "__main__":
    update()
