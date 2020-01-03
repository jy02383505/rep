#!/bin/sh
cd /Application/rep/.venv/


start_rep() {
    echo "rep is running ..."
    nohup ./bin/receiverd > /dev/null 2>&1 &
}


stop_rep() {
    echo "`date  '+%Y-%m-%d %T'` killing rep"
    pid=`ps -eo pid,cmd|grep receiverd|awk '{print $1}'`
    echo kill $pid
    kill -9 $pid
}

case "$1" in
	rep-start)
		start_rep
	;;

	rep-stop)
		stop_rep
	;;
	*)
        echo "Usage: /startup.sh  {rep-[start|stop]} "
		exit 1
	;;
esac

exit 0
