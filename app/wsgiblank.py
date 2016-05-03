'''
wsgiblank - blank webserver application based on WSGI

'''

import os
import sys
import urlparse
import imp
import cgi

from cStringIO import StringIO

import ConfigParser
import mimetypes

config = ConfigParser.ConfigParser()
config.read( '/etc/wsgiblank/wsgiblank.conf' ) #TODO: The path is in conf.py as well.

try:
    LIBPATH         = config.get( 'general', 'LIBPATH' )
    INSTALLPATH     = config.get( 'general', 'INSTALLPATH' )
    WEBSERVERHOST   = config.get( 'general', 'WEBSERVERHOST'  )
    WEBSERVERPORT   = config.get( 'general', 'WEBSERVERPORT'  )
    AUTHCOOKIENAME  = config.get( 'authentication', 'COOKIENAME' )
except Exception as e:
    raise Exception( 'error during processing config file: \'%s\'' % e)

sys.path.append( LIBPATH )

import lib.logger as logger
import lib.utils  as utils
import lib.auth   as auth
from lib.conf import *

STATIC = utils.getFolders(os.path.join(INSTALLPATH, 'static'))
if STATIC == 0:
    logger.error( 'Listing static folders failed' )

#All URLs are prefixed with wsgiblank and it's handled differently on Apache and stand-alone wsgi server mode

SERVERISAPACHE = True

# 404 handler
def notFound( environ, startResponse ):
    '''return 404 if content not found'''
    startResponse( "404 " + CODE[404], [( CONTENT_TYPE, CONTENT_TXT ), ( CONTENT_LENGTH, str( len( CODE[404] ) ) )] )
    return [ CODE[404] ]

def wsgiblankApplication( environ, startResponse ):
    '''main function of the wsgiblank'''

    logger.info( 'running in wsgi mode' )

    # reading configuration values
    try:
        urlPath     = environ['PATH_INFO'].strip('/').split('/')
    except StandardError:
        urlPath     = ['']

    try:
        queryString = urlparse.parse_qs( environ['QUERY_STRING'], keep_blank_values = 1 )
    except StandardError:
        queryString = []

    #Serve static for WSGI servers
    if SERVERISAPACHE is False:
        if urlPath[0].lower() in STATIC:
            path = os.path.join(INSTALLPATH, 'static', environ.get('PATH_INFO', '').lstrip('/'))    #set path
            
            if os.path.exists(path):                                                                #it exists?
                filestat = os.stat(path)                                                            #get file stats
                fileToServe   = file(path,'r')                                                      #read file 
                mimeType = mimetypes.guess_type( path )                                             #guess mime-type
                
                #set headers
                if mimeType[0] == None:
                    headers  = [( CONTENT_LENGTH, str( filestat.st_size ) )]
                else:
                    headers  = [( CONTENT_TYPE, mimeType[0] ), ( CONTENT_LENGTH, str( filestat.st_size ) )]
                startResponse('200 OK', headers)                                                    #set response
                return environ['wsgi.file_wrapper'](fileToServe)                                    #return file
            else:
                logger.debug('static content not found: %s' % str(path))
                return notFound(environ, startResponse)                                             #404

    try:
        requestBodySize = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        requestBodySize = 0

    # Saving wsgi.input since it can be read only once
    wsgiInputStorage      = StringIO(environ['wsgi.input'].read(requestBodySize))
    environ['wsgi.input'] = wsgiInputStorage

    try:
        postData    = urlparse.parse_qs( environ['wsgi.input'].read(requestBodySize), True )
    except StandardError:
        postData    = []

    # seek back to the first byte of wsgiInputStorage
    wsgiInputStorage.seek(0)
    environ['wsgi_input'] = wsgiInputStorage

    cookies     = {}

    if 'HTTP_COOKIE' in environ:
        for i in environ['HTTP_COOKIE'].split(';'):
            cookie = i.strip().partition('=')
            try:
                cookies[cookie[0]] = cookie[2].strip()
            except StandardError:
                pass

    logger.debug( '  urlPath:       %s' % str( urlPath ) )
    logger.debug( '  queryString:   %s' % str( queryString ) )

    try:
        logger.debug( '  userAgent:     %s' % str( environ[ 'HTTP_USER_AGENT' ] if 'HTTP_USER_AGENT' in environ else '' ) )
        logger.debug( '  remoteAddr:    %s' % str( environ[ 'REMOTE_ADDR' ] if 'REMOTE_ADDR' in environ else '' ) )
    except StandardError:
        pass

    for i in cookies.keys():
        logger.debug( '  cookie:        %s = %s' % (i, cookies[i]) )

    accessLevel = NO_ACCESS
    userName = ''

    # authentication can be disabled for debug reasons via config file
    enableAuthentication = 1

    try:
        if str( config.get( 'authentication', 'enableAuthentication' ) ).lower() in ['false', '0']:
            enableAuthentication = 0
            accessLevel = int( config.get( 'authentication', 'accessLevel' ) )
            userName    = str( config.get( 'authentication', 'userName' ) )
    except StandardError:
        pass

    # checking authentication
    if enableAuthentication and AUTHCOOKIENAME in cookies:
        try:
            [ uName, key ] = cookies[AUTHCOOKIENAME].strip().split(':')
            accessLevel = auth.querySession( uName, key )
            if accessLevel > NO_ACCESS:
                userName = uName
        except ValueError:
            pass

    logger.debug( '  accessLevel: %d, username: %s' % (accessLevel, userName) )

    if urlPath[0].lower() == 'debug' and accessLevel == RW_ACCESS:
        raise Exception('debug')

    else:
        # serve the requested content
        # decide which module to call
        moduleFile = ''
        moduleName = DEFAULT_MODULE
        if not SERVERISAPACHE:
            if urlPath[0] != 'wsgiblank' or urlPath == []:
                urlPath.insert(0, 'wsgiblank')
            if len(urlPath) == 1: # for evaluating urlPath[0 if SERVERISAPACHE else 1]
                urlPath.insert(1, '')

        if urlPath == [] or not urlPath[0 if SERVERISAPACHE else 1].lower() in MODULES:
            # if the requested module is not available or no module is specified, load the 
            # default one from the config
            logger.debug( '  module not found, falling back to default module: %s' % DEFAULT_MODULE )
            moduleFile = os.path.join( LIBPATH, 'module', MODULES[ DEFAULT_MODULE ][ 'dirname' ], MODULES[ DEFAULT_MODULE ][ 'filename' ] )
        else:
            # loading the selected module
            moduleName = urlPath[0 if SERVERISAPACHE else 1].lower()
            logger.debug( '  trying to load module: %s' % moduleName )
            if MODULES[moduleName]['enabled'] == 'enabled' and MODULES[moduleName]['access'] <= accessLevel:
                # load selected module
                moduleFile = os.path.join( LIBPATH, 'module', MODULES[ moduleName ][ 'dirname' ], MODULES[ moduleName ][ 'filename' ] )
                logger.debug( '  determining module file: %s' % moduleFile )
            else:
                # load default module
                moduleFile = os.path.join( LIBPATH, 'module', MODULES[ DEFAULT_MODULE ][ 'dirname' ], MODULES[ DEFAULT_MODULE ][ 'filename' ] )
                logger.debug( '  don\'t load module because status is disabled or level of access is not met (status: %s, access: %d)' % ( MODULES[moduleName]['enabled'], MODULES[moduleName]['access'] ) )

        try:
            # try to load the module lib
            module = imp.load_source( moduleName, moduleFile )
        except IOError as eIO:
            logger.error( '  unable to load requested module: \'%s\'' % moduleFile )
            logger.error( '  got exception: %s' % eIO )

        logger.debug( '  module loaded: \'%s\'' % moduleFile )
        logger.debug( '  postData:      %s' % str( postData ) )

        responseHeaders, returnStatus, content = module.content( 
                userName, 
                accessLevel,
                command = urlPath[1].lower() if len( urlPath ) > 1 else '',
                queryString = queryString,
                postData = postData,
                cookies = cookies,
                )

    startResponse( returnStatus, responseHeaders )
    return [ content ]

application = wsgiblankApplication

if __name__ == '__main__':
    try:
        logger.info( 'Trying to create local webserver' )
        from wsgiref import simple_server

        print 'Running wsgiblank application at http://%s:%s/ ...' % ( str(WEBSERVERHOST), str(WEBSERVERPORT) )
        SERVERISAPACHE = False
        HTTPD = simple_server.WSGIServer( ( str(WEBSERVERHOST), int(WEBSERVERPORT) ), simple_server.WSGIRequestHandler )
        HTTPD.set_app( application )
        HTTPD.serve_forever( )
    except ImportError:
        logger.info( 'Creating local webserver failed, falling back to stdout output' )
        for cnt in application( {}, lambda status, headers: None ):
            print cnt

