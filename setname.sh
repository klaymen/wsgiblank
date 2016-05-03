#!/bin/bash

echo "Set package name:";
 
read inputline
replace=$inputline

mv wsgiblank.conf $replace.conf
mv ./app/wsgiblank.py ./app/$replace.py

search='wsgiblank'
for file in `find -name '*.py' -o -name '*.conf' -o -name 'Makefile' -o -name '*.cgi'`; do
  grep "$search" $file &> /dev/null
  if [ $? -ne 0 ]; then
    echo "$file skipped..."
  else
    echo "Set name in $file..."
    sed -i "s/$search/$replace/g" $file
  fi
done
echo "done"

