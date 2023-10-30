import time
import board
import RPi.GPIO as GPIO
import datetime as dt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW)

# Inisialisasi GPIO untuk sensor jarak ultrasonik
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
iffd = 0

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    return distance

def send_email(data):
    body = MIMEText(data, "plain")
    msg.attach(body)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, email_send, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email sending error:", str(e))


# Konfigurasi untuk kirim data via email
email_user = "mbkmsender@gmail.com"
email_password = "wxyhsysmzyzmdwen"
email_send = "mbkmreceiver@gmail.com"

subject = "Data Sensor"
msg = MIMEMultipart()
msg["From"] = email_user
msg["To"] = email_send
msg["Subject"] = subject

try:
    # Membaca waktu dari RTC DS3231
    t = dt.now()
    # s = t.strftime("%d %m %Y")
    # Membaca data dari sensor jarak ultrasonik
    dist = distance()
    print("Measured Distance = %.1f cm" % dist)

    # Membuat pesan email
    data = f"Waktu: {t}\n"
    data += f"Jarak: {dist:.1f} cm"
    while iffd < 10:
        GPIO.output(14, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(14, GPIO.HIGH)
        time.sleep(0.3)
        iffd + 1
    print("jalan mang")
    print(data)
    send_email(data)
except:
    exit()
finally:
    GPIO.cleanup()

