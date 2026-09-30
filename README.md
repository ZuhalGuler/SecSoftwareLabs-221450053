Bu repository, Güvenli Yazılım Geliştirme Laboratuvarı (SecSoftwareLabs) 1. Hafta çalışmaları kapsamında Python çalışma ortamının doğrulanması ve temel Git/GitHub iş akışının kurulması amacıyla hazırlanmıştır.

 Amaç

Python geliştirme ortamının ve versiyonunun kontrol edilmesi

İzole bir sanal ortam (venv) yapısının kurulması

Git sürüm kontrol mekanizmasının başlatılması ve ilk commit/push işlemlerinin gerçekleştirilmesi

 Gereksinimler

Python: 3.11+

Sürüm Kontrolü: Git

İşletim Sistemi/Terminal: Windows (Git Bash / PowerShell), macOS veya Linux Terminal

 Kurulum ve Sanal Ortam (venv)



Haftalık Çalışma Dizinine Geçiş:

cd week01


Sanal Ortamın (venv) Oluşturulması:

python -m venv .venv


Sanal Ortamın Aktif Edilmesi:

Windows (Git Bash / CMD / PowerShell):

.venv\Scripts\activate


macOS / Linux:

source .venv/bin/activate


(Terminal satırının başında (.venv) ifadesi görüldüğünde sanal ortam başarıyla aktif edilmiş demektir.)

(Opsiyonel) Paket Kurulumu:

pip install -r requirements.txt
