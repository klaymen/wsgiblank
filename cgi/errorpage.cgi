#!/bin/bash

STIME=`date '+%s%N'`

NAME=`python ../scripts/configReader.py /etc/wsgiblank/wsgiblank.conf maintainer name`
EMAIL=`python ../scripts/configReader.py /etc/wsgiblank/wsgiblank.conf maintainer email`

echo "Content-type: text/html"
echo ""

echo '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>Internal Error</title>
<link href="/styles/cgi.css" rel="stylesheet" type="text/css">
</head>
<body>
<div class="title">
<h1><span style="color:#005fab;">wsgiblank</span> Internal Error</h1>
<p>'''
echo "Sorry for the inconvenience!<br>Please notify <b>$NAME</b> ($EMAIL)."
echo '''
</div>
'''

REMIP="$HTTP_X_FORWARDED_FOR"
if [ -z "$REMIP" ]; then
	REMIP="$REMOTE_ADDR"
fi

LOGFILE=`python ../scripts/configReader.py ../wsgiblank.conf general logFile`

if [[ "$REMIP" =~ ^172 ]]; then
	echo "<div>"
	echo "<h3>Server time</h3>"
	echo "<pre>"
	date
	echo "</pre>"

	echo "<h3>Tail of wsgiblank log</h3>"
	echo "<pre>"
	tail -40 $LOGFILE
	echo "</pre>"
	echo "<h3>Tail of apache/wsgi log</h3>"
	echo "<pre>"
	tail -40 /var/log/apache2/error.log
	echo "</pre>"

	echo "</div>"
else
	echo "<p>"
	echo "Your detected IP: $REMIP"
	echo "<p>"
	echo "You can see the logs only from inside the CAE Engineering network."
	echo "<div>"
	echo "<h3>Server time</h3>"
	echo "<pre>"
	date
	echo "</pre>"
	echo "</div>"
fi

ETIME=`date '+%s%N'`

echo "<h4>Page generated in "
echo $(( (ETIME-STIME)/1000 ))
echo "&micro;s.</h4>"

echo '''
</body>
</html>
'''
