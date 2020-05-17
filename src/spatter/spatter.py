#!/usr/bin/env python3
# vim: ts=4 sw=4 et:
'''
    cli implementations of many mutagen metadata functions,
    created for several compressed audio formats, with the
    intention of mainly being used to tag recordings of live
    concerts, & convert filepaths to tags or tags to filenames
'''

import re
import sys
import os
from optparse import OptionParser as OP
from mutagen import File
from mutagen.mp3 import EasyMP3 as MP3
from spatter.taggr import Subster
#__version__ = '0.1.4'
from spatter import __version__


class Confirmer():
    ''' user confirmation agent '''
    def __init__(self, optt):
        self.opt = optt
        if any([self.opt.tag, self.opt.add, self.opt.remove, self.opt.clear,
                self.opt.pattern, self.opt.tag2fn]):
            self.use = True
        else:
            self.use = False
        self._all = False

    def confirm(self):
        ''' honor certain options regarding actual file-writing,
            and input of y or n to proceed with file-writing.    '''
        if self.use:
            if self.opt.noact:
                return False
            if self._all:
                return True
            if not self.opt.confirm:
                return True
            resp = raw_input('confirm changes? (y/a/[n])')
            if resp[0].lower() == 'y':
                return True
            if resp[0].lower() == 'a':
                self._all = True
                return True
        return False

class Speaker():
    ''' wrapper to simplify printing user messages '''
    def __init__(self, quiet):
        self.x = 0
        self.quiet = quiet

    def speak(self, strng):
        ''' print formatted messages '''
        if not self.quiet:
            if strng[:2] == '\n\t':
                print('\n', ' ' *48, strng[2:],)
                self.x += len(strng)
            elif strng[:1] == '\t':
                strng += ' '*120
                strng = strng[self.x:]
                print(strng[1:],)
            else:
                print(strng,)

def main():
    args = sys.argv
    err = 0
    if 'id3help' in args:
        from mutagen.easyid3 import EasyID3
        for key in  EasyID3.valid_keys.keys():
            print(key,)

    from optparse import OptionParser as OP

    OP = OP()
    OP.usage = ("%prog [options] filenames")
    OP.epilog = '%s id3help: for help with id3 tags' % os.path.basename(args[0])
    OP.add_option('-t', '--tag', dest='tag', action='append',
                  help="set a tag", metavar='tag=value')
    OP.add_option('-a', '--add', dest='add', action='append',
                  help='set/add values to a tag, without removing any existing values',
                  metavar='tag=value')
    OP.add_option('-p', '--pattern', dest='pattern', action='store',
                  help='substitution pattern from filename', metavar="'%n %t.flac'")
    OP.add_option('--fn2tag', dest='pattern', action='store',
                  help='same as -p | --pattern')
    OP.add_option('-r', '--remove', dest='remove', action='append',
                  help='remove a tag value or entire tag', metavar="'tag' or 'tag=value'")
    OP.add_option('-j', '--justify', dest='justify', action='store_true',
                  help='zero-justify tracknumbers')
    OP.add_option('--clear', dest='clear', action='store_true', help='clear all tags')
    OP.add_option('-n', '--noact', dest='noact', action='store_true',
                  help="just show what changes would be made")
    OP.add_option('-c', '--confirm', dest='confirm', action='store_true',
                  help='show changes and prompt for confirmation to save')
    OP.add_option('-f', '--files', dest='filenames', action='append',
                  help='one or more filenames/globs')
    OP.add_option('-q', '--quiet', dest='quiet', action='store_true', help='no output to stdout')
    OP.add_option('--tag2fn', dest='tag2fn', action='store',
                  help='substitution pattern from tags', metavar="'%n %t.flac'")
    OP.add_option('-s', '--filter', dest='symbols', action='store',
                  help='one or more characters to filter from tags used to build filenames',
                  metavar="'!@$&*/\?'")
    OP.add_option('-m', '--map', dest='map', action='store',
                  help='replace all instances of a char with another char',
                  metavar="/ -")
    OP.add_option('-i', '--index', dest='idx', action='store_true',
                  help='index files by filename order (persistent file order)')

    
    print ('%s %s' % (OP.get_prog_name(), __version__))

    argstr = ' '.join(args)


    if len(args) < 2:
        OP.print_usage()
        print("version %s" % __version__)
        print('-h|--help for help\n')
        sys.exit(1)

    p = '(-t|--tag|-a|--add|-p|--pattern|-r|--remove|-f|--files)\ +?\-[^\ ]*'
    mo = re.search(p, argstr)
    if mo:
        print('illegal option combination: ', mo.group())
        sys.exit(1)


    (opt, fnames) = OP.parse_args()

    if opt.filenames:
        fnames += opt.filenames

    for fname in fnames:
        if not os.path.exists(fname):
            print('%s: no such file' % fname)
            err += 1
    if err:
        sys.exit(err)


    cfmr = Confirmer(opt)
    fnum = 0
    idx = 0
    if opt.pattern:
        subster = Subster(opt.pattern)
    elif opt.tag2fn:
        subster = Subster(opt.tag2fn, 'tag2fn')
    else:
        subster = Subster('', '')

    modded = any([opt.clear, opt.remove, opt.add, opt.tag, opt.pattern, opt.justify])
    spkr = Speaker(opt.quiet)
    top_length = 0
    for fname in fnames:
        bfname = os.path.basename(fname)
        top_length = len(bfname) if len(bfname) > top_length else top_length

    for fname in fnames:
        fnum += 1
        vals = {}
        keys = []
        origfn = fname

        if os.path.splitext(fname)[1] == '.mp3':
            try:
                mf = MP3(fname)
            except IOError:
                spkr.speak("\ncan't open %s" % fname)
                continue
            spkr.speak("\nprocessing %s" % fname)
            if opt.clear:
                mf.clear()
            for action in opt.remove or []:
                k, v = (action.split('=', 1)+[''])[:2]
                vals[k] = mf.pop(k, [])
                if k and not v:
                    vals[k] = []

                elif v and v in vals[k]:
                    vals[k].remove(v)
            for action in opt.tag or []:
                k, v = (action.split('=', 1)+[''])[:2]
                vals[k] = [v]
            for action in opt.add or []:
                k, v = (action.split('=', 1)+[''])[:2]
                if vals.get(k, []):
                    vals[k] += mf.pop(k, [])
                else:
                    vals[k] = mf.pop(k, [])
                vals[k].extend([v])
            if subster.pattern:
                d = subster.getdict(fname)
                for k in d:
                    values = d.get(k, [])
                    if not isinstance(values, list):
                        values = [values]
                    try:
                        vals[k].extend(values)
                    except KeyError:
                        vals[k] = values
            if opt.justify:
                if not vals.get('tracknumber'):
                    vals['tracknumber'] = fnum
                width = len(str(len(fnames)))
                n = width - len(str(vals['tracknumber']))
                vals['tracknumber'] = [n*'0' + str(vals['tracknumber'])]

            if not modded:
                if not opt.quiet:
                    print(mf.pprint())
                    continue

            if opt.noact or opt.confirm:
                for k in vals:
                    print(k+'='+str(vals[k]))
            if opt.noact:
                continue
            if opt.confirm and not cfmr.confirm():
                continue
            for k in vals:
                try:
                    mf.update({k:vals[k]})
#                mf.save( )
                except ValueError:
                    pass
            mf.save()
        else:
            try:
#            print(fname)
                mf = File(fname)
            except IOError:
                spkr.speak("can't open %s" % fname)
                continue
            spkr.speak('\n' + os.path.basename(fname))

            if opt.idx:
                trn = mf.get('tracknumber', None)
                mf['idx'] = unicode(fnum)
                if trn:
                    mf['idx'] += trn
                mf.save()
                print(' indexed')

            if opt.clear:
                mf.clear()
                spkr.speak('\n\ttags cleared..')
            for action in opt.remove or []:
                k, v = (action.split('=', 1)+[''])[:2]
                t = mf.pop(k, [])
                if v and v in t:
                    t.remove(v)
                    spkr.speak(str(k) + ' removes ' + str(v))
                if v and t:
                    mf.update({k:t})
            for action in opt.tag or []:
                if '=' in action:
                    k, v = action.split('=', 1)
                    if k and v:
                        mf.update({k:[v]})
                        spkr.speak('\n\ttag set: ' + k + '=' + v)
            for action in opt.add or []:
                if '=' in action:
                    k, v = action.split('=', 1)
                    mf.update({k:mf.get(k, [])+[v]})
                    spkr.speak('\n\ttag appended: ' + k + '=' + v)
            if subster.mode == 'fn2tag':
                d = subster.getdict(fname)
                for k in d:
                    mf.update({k:d[k]})
                    spkr.speak('\n\tfrom filename: ' + k + '=' + d[k])

            if subster.mode == 'tag2fn':
                fname = ''
                fnlist = subster.getfnlist()
                if 'tracknumber' in fnlist:
                    tn = 1
                else:
                    tn = 0
                lit = True
                for item in fnlist:
                    lit = not lit
                    if lit:
                        if not tn and item == 'tracknumber':
                            item = 'track'
                        if tn and item == 'track':
                            item = 'tracknumber'
                        if item.startswith('track') and opt.justify:
                            subst = mf[item][0].rjust(2, '0')
                        else:
                            subst = mf[item][0]

                        if opt.symbols:
                            pat = '['+opt.symbols+']'
                            subst = re.sub(pat, '', subst)
                            subst = subst.strip()

                        fname += subst
                    else:
                        fname += item

                    if '/' in fname:
                        fname = re.sub('/', '-', fname)

#            if opt.map:
#                fname = map(fname,opt.map)

                if opt.noact or opt.confirm:
                    pass

            if not any([modded, opt.tag2fn, opt.quiet]):
                print(mf.pprint(),)

            if cfmr.confirm():
                if opt.tag2fn:
                    if opt.map:
                        a, b = opt.map.split()
                        fname = re.sub(a, b, fname)

                    pth = os.path.join(os.path.dirname(origfn), fname)
                    second_column = top_length+2
                    tab = (second_column-len(os.path.basename(origfn)))*' '
                    try:
                        os.rename(origfn, pth)
                        print(tab + '--> ' + fname),
#                    spkr.speak( 'renamed...   ' + fname )
                    except IOError:
                        raise IOError
                else:
                    mf.save()
                    spkr.speak('\tsaved!')
