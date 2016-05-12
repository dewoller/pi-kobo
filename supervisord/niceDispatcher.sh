#!/bin/sh
pstree -p $(ps aux | grep python3 | grep -v grep  | awk '{print $2}') -A | cut -b 22- | cut -d'(' -f 2 | cut -d')' -f1 | xargs sudo renice -n -20
ps aux | grep python3 | grep -v grep  | awk '{print $2}' | xargs sudo renice -n -20
