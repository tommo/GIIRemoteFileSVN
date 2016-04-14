import os.path

import constants
import common


class LocalClient(common.CommonClient):
    def __init__(self, path_, *args, **kwargs):
        if os.path.exists(path_) is False:
            raise EnvironmentError("Path does not exist: %s" % (path_))

        super(LocalClient, self).__init__(
            path_, 
            constants.LT_PATH, 
            *args, **kwargs)

    def __repr__(self):
        return ('<SVN(LOCAL) %s>' % (self.path))
