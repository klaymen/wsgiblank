# wsgiblank

Blank webserver application based on WSGI.

## setup
 - To change the default 'wsgiblank' name all over the application, you can use the script ```./setname.h <preferred name>```
 - You need to have a user named as your application: ```useradd <preferred name>```
 - When you are ready navigate to the root folder of the app and install it by: ```sudo make install```

### Apache setup
In order to make it work with Apache, you might need to add the following lines to its config (```/etc/apache2/apache2.conf```). However, before doing that you'd better create a backup of your current config.

```
DocumentRoot /var/www/

WSGIScriptAlias /wsgiblank /usr/lib/wsgiblank/app/wsgiblank.py

<Directory /usr/lib/wsgiblank/app>
    Require all granted
</Directory>
```

## dependencies
- Python 2.7
- Apache 2.4.10
