'''
wsgiblank sample module

comments starting with ==> to be removed when using this as a template

'''
module = '_sample'

#==> standard pyton module includes as needed

import sys
import pickle
import ConfigParser

#==/ 

#==> custom includes from the common lib as needed

sys.path.append('../../')

import lib.utils    as utils
import lib.logger   as logger
import lib.cache    as cache
from   lib.conf import *

#==/ 

#==> custom includes from the module lib as needed

#import module_lib.some_lib as some_lib

#==/

#==> read global config as needed (module specific config values should be in module specific config files located in /etc/ptree/<module_name>.conf)

config = ConfigParser.ConfigParser()
config.read( CONFIG_FILE )

try:
    LIBPATH         = config.get( 'general', 'LIBPATH' )
    ENABLECACHING   = config.get( 'cache', 'ENABLECACHING' )
except IOError as eIO:
    print( 'error during processing config file: \'%s\'' % eIO )
    sys.exit(1)

#==/

#==> defining supported filters

FILTERS = [ 'html', 'pdf', 'xls', 'csv', 'xlsx' ]
DEFAULTFILTER = FILTERS[0]


def buildData(data):
    '''
    build data to cache
    '''
    return ''

def buildHtml(data):
    '''
    Build html page based on data if necessary
    '''
    
    return 'hello world'

#==/

#==> content() is the standard interface of the module towards the main program, 
#    the return values and function parameters are always identical.
def content(
        userName        = '',
        accessLevel     = '',
        newUrl          = '',
        command         = '',
        queryString     = '',
        postData        = '',
        cookies         = '',
        uploadFile      = ''
        ):
    '''
    What this module does?
    '''

    #==> extracting keys from queryString
    #==> key = utils.getKey( queryString )

    cacheFile = cache.cacheFile( '_____', module ) # ==> cache.cacheFile( key, module )


    # searching for cached data
    noCache = 0
    data    = ''

    if ENABLECACHING is 1:
        # valid cache found
        # loading data from cache

        try:
            cacheStream = open ( cacheFile, 'r')
            data = pickle.load( cacheStream )
            cacheStream.close ()
        except IOError:
            logger.error( 'failed to load cacheFile: \'%s\'' % cacheFile )
            noCache = 1 #Needs to load data
    else:
        noCache = 1 #Needs to load data

    if len(data) is 0:
        noCache = 1

    if noCache:
        # no or out-of date cache, building new one
        data = buildData(1) #==> To be replaced with a specific call
        # creating cache
        if ENABLECACHING is 1:
            try:
                cacheStream = open ( cacheFile, 'w')
                pickle.dump( data, cacheStream )
                cacheStream.close()
            except IOError:
                logger.error( 'failed to save cacheFile: \'%s\'' % cacheFile )

    #==> determinate the requested output filter
        #==> raise a warning

    returnStatus = "200 OK"
    
    #==> build content using the selected filter
    cnt = buildHtml(data)
    
    responseHeaders = [ ( "Content-Type", CONTENT_HTML ),
                        ( "Content-Length", str( len( cnt ) ) ) ]

    #==> generate headers, status and return them with the actual content
    return responseHeaders, returnStatus, cnt
