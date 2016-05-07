# -*- coding: utf-8 -*-
import svn.remote
import re

r = svn.remote.RemoteClient(
	'https://192.168.11.3:447/svn/eastward',
	username = 'studio',
	password = '1103'
	)

print r.info( 'Animation/Env' )[ 'commit#revision' ]
# for f in r.list_recursive( 'Animation' ):
# 	print f
	# print r.info( f )

# path = u'设定/TV_1.psd'
# for log in r.log_default( ) :
# 	print log
# xxx = r.cat( path )
# # xxx = r.cat( u'设定/TV_1.psd'.encode('unicode-escape') )
# # f1 = open( 'outout.psd', 'wb' )
# # f1.write( xxx )
# # f1.close()
# mo = re.match( '<([ \w_\-:.]+)>(.*)$', '<ggg.sdf>/abcd' )
# if mo:
# 	print mo.group( 1 ), mo.group( 2 )