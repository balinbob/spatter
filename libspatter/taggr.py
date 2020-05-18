# vim: ts=4 sw=4 et:

from __future__ import absolute_import
import re
from os.path import sep

from libspatter import __version__

class Subster():
    '''
        s = Subster(pattern, mode)
        or
        s = Subster('%a/%l/%n - %t.flac', mode='fn2tag')
    '''
    keydict = {'a':'artist',
               'l':'album',
               'n':'tracknumber',
               't':'title',
               'd':'date',
               'g':'genre',
               'c':'composer',
               'j':'junk',
               'i':'discnumber'}

    keystr = ''.join(list(keydict.keys()))
    keypat = '%[' + keystr + ']'
    keypat = re.compile(keypat)
    fname = ''

    def __init__(self, pattern='', mode='fn2tag'):
        self.pattern = pattern or ''
        if mode == 'tag2fn':
            self.tag2fn = pattern or ''
        elif mode == 'fn2tag':
            self.fn2tag = pattern or ''
        self.mode = mode
        self.keys = [mp[1] for mp in re.findall(self.keypat, self.pattern)]
        self.lits = re.split(self.keypat, self.pattern)
        self.keyiter = iter(self.keys)
        self.literals = iter(self.lits)

    def pathstrip(self, ptn, pth):
        n = len(ptn.strip(sep).split(sep))
        pthlist = pth.strip(sep).split(sep)[-n:]
        return sep.join(pthlist)

    def _get_regex(self, reg, lit):
        if reg == 'n':
            return '[0-9]+?'+lit
        return '.+?'+lit

    def init(self):
        if self.lits[0] == '':
            literal = next(self.literals)
        try:
            self.fname = self.fname[len(literal):]
        except AttributeError:
            pass
        except ValueError:
            raise ValueError

    def nextpair(self):
        try:
            key = next(self.keyiter)
        except StopIteration:
            raise StopIteration
        try:
            lit = next(self.literals)
        except StopIteration:
            lit = ''
        matchpat = self._get_regex(key, lit)
        mo = re.match(matchpat, self.fname)
        if mo:
            val = mo.group()[:-len(lit)]
            self.fname = self.fname[len(lit+val):]
            keyname = self.keydict[key]
            return {keyname:val}
        raise ValueError

    def getdict(self, fname):
        self.fname = self.pathstrip(self.pattern, fname)
        try:
            self.init()
        except ValueError:
            return {}
        gdict = {}
        while True:
            try:
                gdict.update(self.nextpair())
            except ValueError:
                return {}
            except StopIteration:
                break
        return gdict

    def getfnlist(self):
        fnlist = []
        self.keyiter = iter(self.keys)
        self.literals = iter(self.lits)

        while True:
            try:
                fnlist.append(next(self.literals))
                fnlist.append(self.keydict[next(self.keyiter)].lower())
            except StopIteration:
                break
        return fnlist
