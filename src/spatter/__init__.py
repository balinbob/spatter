
import re
import sys

__version__ = '0.1.5'
__all__ = ['main', 'spatter', 'tagger']
from spatter.spatter import *
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
