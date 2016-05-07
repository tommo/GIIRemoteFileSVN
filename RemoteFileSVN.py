from util.RemoteFile import *
from gii.core import app
import svn
import svn.remote
import re
import logging
import os.path
##----------------------------------------------------------------##
def getRemoteInfo( client, path ):
	try:
		info = client.info( path )
		return info
	except Exception, e:
		logging.exception( e )
		return None

##----------------------------------------------------------------##
def copyRemoteFile( client, srcPath, targetPath ):
	try:
		content = client.cat( srcPath )
	except Exception, e:
		return False
	fp = open( targetPath, 'wb' )
	fp.write( content )
	fp.close()
	return True

##----------------------------------------------------------------##
def copyRemoteTree( client, srcPath, targetPath ):
	affirmedPath = {}
	affirmedPath['.'] = True
	os.mkdir( targetPath )
	try:
		for pathDir, entry in client.list_recursive( srcPath ):
			relPath = os.path.relpath( pathDir, srcPath )
			if relPath.startswith( './' ):
				relPath = relPath[ 2: ]
			if not affirmedPath.has_key( relPath ):
				try:
					os.mkdir( targetPath + '/' + relPath )
					affirmedPath[ relPath ] = True
				except Exception, e:
					logging.exception( e )
					#TODO: error info
					return False
			filePath = pathDir + '/' + entry['name']
			targetFilePath = targetPath + '/' + relPath + '/' + entry['name']
			copyRemoteFile( client, filePath, targetFilePath )
	except Exception, e:
		logging.exception( e )
		return False


##----------------------------------------------------------------##
class RemoteFileProviderSVN( RemoteFileProvider ):
	def __init__( self ):
		super( RemoteFileProviderSVN, self ).__init__()
		self.repos = None
		self.clientCache = {}
		
	def loadRepos( self ):
		repos = {}
		reposSettingApp = app.getUserSetting( 'svn_remote', {} )
		for k,v in reposSettingApp.items():
			repos[ k ] = v

		prj = app.getProject()
		if prj:
			reposSettingPrj = prj.getUserSetting( 'svn_remote', {} )
			for k,v in reposSettingPrj.items():
				repos[ k ] = v
		self.repos = repos

	def getRepoInfo( self, id ):
		if not self.repos:
			self.loadRepos()
		return self.repos.get( id, None )

	def parsePath( self, path ):
		mo = re.match( '<([ \w_\-:.]+)>(.*)$', path )
		if mo:
			return ( mo.group(1), mo.group(2) )
		else:
			return ( None, path )

	def requestClientForRepo( self, repoName ):
		client = self.clientCache.get( repoName, None  )
		if client == False: return None

		options = {}
		if not repoName: return False
		repoInfo = self.getRepoInfo( repoName )
		if not repoInfo: return False
		url = repoInfo.get( 'url' )
		if not url:
			return False

		username = repoInfo.get( 'username', None )
		password = repoInfo.get( 'password', None )
		if username: options[ 'username' ] = username
		if password: options[ 'password' ] = password
		client = svn.remote.RemoteClient(	url, **options )

		try:
			client.info()
		except Exception, e:
			self.clientCache[ repoName ] = False
			return client
		self.clientCache[ repoName ] = client
		return client
		
	def fetch( self, protocol, sourcePath, targetPath, context ):
		if protocol != 'svn': return False
		repoName, path = self.parsePath( sourcePath )
		client = self.requestClientForRepo( repoName )
		if not client: return False
		logging.info( u'fetch svn file {0}->{1}'.format( sourcePath, targetPath ) )
		return copyRemoteFile( client, path, targetPath )

	def fetchTree( self, protocol, sourcePath, targetPath, context ):
		if protocol != 'svn': return False
		repoName, path = self.parsePath( sourcePath )
		client = self.requestClientForRepo( repoName )
		if not client:
			logging.warn( 'cannot init SVN client for repo:'+repoName )
			return False
		info = getRemoteInfo( client, path )
		if not info:
			logging.warn( 'fail to get remote info:' + path )
			return False
		if info[ 'entry_kind' ] == 'file':
			logging.info( u'fetch svn file {0}->{1}'.format( path, targetPath ) )
			return copyRemoteFile( client, path, targetPath )

		elif info[ 'entry_kind' ] == 'dir':
			return copyRemoteTree( client, path, targetPath )

		return True

	def getTimestamp( self, protocol, sourcePath, context ):
		if protocol != 'svn': return False
		#TODO
		repoName, path = self.parsePath( sourcePath )
		client = self.requestClientForRepo( repoName )
		if not client:
			logging.warn( 'cannot init SVN client for repo:'+repoName )
			return 0
		info = getRemoteInfo( client, path )
		if not info:
			logging.warn( 'fail to get remote info:' + path )
			return False
		return info.get('commit_revision', info.get('commit#revision', 0 ) )

registerRemoteFileProvider( RemoteFileProviderSVN() )