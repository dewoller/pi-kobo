#!/bin/sh
 
### BEGIN INIT INFO
# Provides: dispatcherWatcher
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Put a short description of the service here
# Description: Put a long description of the service here
### END INIT INFO
 
 
. /lib/lsb/init-functions
 
do_start () {
log_daemon_msg "Starting system dispatcherWatcher daemon"
su - pi -c 'tmux new-session -d "mosquitto_sub -v -t \"#\" "'
log_end_msg $?
}
do_stop () {
log_daemon_msg "Stopping system dispatcherWatcher daemon"
start-stop-daemon --stop --pidfile $PIDFILE --retry 10
log_end_msg $?
}
 
case "$1" in
 
start|stop)
do_${1}
;;
 
restart|reload|force-reload)
do_stop
do_start
;;
 

esac
exit 0
