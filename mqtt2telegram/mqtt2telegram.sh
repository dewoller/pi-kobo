mosquitto_sub -v -h 192.168.1.38 -t "#"  | while read i; do curl -s --data "chat_id=361388410" --data-urlencode "text=$i" https://api.telegram.org/bot304677462:AAHIuBjv7k4nbRt7pAGKg6idQ6o8UUKKEek/sendMessage; done