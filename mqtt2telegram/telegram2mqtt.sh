python /code/pi-kobo/mqtt2telegram/getTelegramBot.py | while read i; do mosquitto_pub -h 192.168.1.38 -t "dispatcher" -m "$i"; done 
