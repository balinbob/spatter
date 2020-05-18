''' this does most of the parsing and editing work '''
import re
import sys

__version__ = '0.1.11'
__all__ = ['main', 'spatter', 'taggr']
from libspatter.spatter import *
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
