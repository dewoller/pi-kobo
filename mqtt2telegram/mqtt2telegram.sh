#!/bin/sh
mosquitto_sub -v -h 192.168.1.38 -t "#"  | \
  while read i; do \
      echo -n "starting " >>/var/log/dispatcher/mqtt2telegram.log
      date >>/var/log/dispatcher/mqtt2telegram.log
      curl -s --data "chat_id=361388410" \
              --data-urlencode "text=$i" \
              https://api.telegram.org/bot304677462:AAHIuBjv7k4nbRt7pAGKg6idQ6o8UUKKEek/sendMessage \
               >>/var/log/dispatcher/mqtt2telegram.log
      echo >>/var/log/dispatcher/mqtt2telegram.log
      echo -n "done " >>/var/log/dispatcher/mqtt2telegram.log
      date >>/var/log/dispatcher/mqtt2telegram.log
  done
