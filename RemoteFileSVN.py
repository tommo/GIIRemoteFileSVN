from util.RemoteFile import *
from gii.core import app
import svn
import svn.remote
import re

##----------------------------------------------------------------##


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

		try:
			content = client.cat( path )
		except Exception, e:
			return False
		fp = open( targetPath, 'wb' )
		fp.write( content )
		fp.close()
		return True

	def fetchTree( self, protocol, sourcePath, targetPath, context ):
		if protocol != 'svn': return False
		if os.path.isfile( sourcePath ):
			shutil.copy2( sourcePath, targetPath )
		elif os.path.isdir( sourcePath ):
			shutil.copytree( sourcePath, targetPath )
		return True

	def getTimestamp( self, protocol, sourcePath, context ):
		if protocol != 'svn': return False
		#TODO
		return 0

registerRemoteFileProvider( RemoteFileProviderSVN() )