PWD=`pwd`
DESTINATION=$(install_root)/usr/lib

USER=wsgiblank
GROUP=wsgiblank

CP=cp
LCP=ln -s
CONF_DIR=/etc/wsgiblank
CACHE_DIR=/var/cache/wsgiblank
LOG_DIR=/var/log/wsgiblank

CONFS= wsgiblank.conf

all:
	@echo "Type 'make install' to install package"

install:
	mkdir -p $(DESTINATION)/wsgiblank
	cp -r ./* $(DESTINATION)/wsgiblank
	mkdir -p $(CONF_DIR)
	mkdir -p $(CACHE_DIR)
	chown -R $(USER):$(GROUP) $(CACHE_DIR)
	mkdir -p $(LOG_DIR)
	chown -R $(USER):$(GROUP) $(LOG_DIR)
	@for n in $(CONFS) ; do rm -f $(CONF_DIR)/$$n ; $(CP) $(PWD)/$$n $(CONF_DIR)/$$n; done
