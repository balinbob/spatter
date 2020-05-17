# spatter

CLI tool for working with tags and filenames of audio files using Mutagen


Usage: spatter [options] filenames

Options:
  -h, --help            show this help message and exit
  -t tag=value, --tag=tag=value
                        set a tag
  -a tag=value, --add=tag=value
                        set/add values to a tag, without removing any existing
                        values
  -p '%n %t.flac', --pattern='%n %t.flac'
                        substitution pattern from filename
  --fn2tag=PATTERN      same as -p | --pattern
  -r 'tag' or 'tag=value', --remove='tag' or 'tag=value'
                        remove a tag value or entire tag
  -j, --justify         zero-justify tracknumbers
  --clear               clear all tags
  -n, --noact           just show what changes would be made
  -c, --confirm         show changes and prompt for confirmation to save
  -f FILENAMES, --files=FILENAMES
                        one or more filenames/globs
  -q, --quiet           no output to stdout
  --tag2fn='%n %t.flac'
                        substitution pattern from tags
  -s '!@$&*/\?', --filter='!@$&*/\?'
                        one or more characters to filter from tags used to
                        build filenames
  -m / -, --map=/ -     replace all instances of a char with another char
  -i, --index           index files by filename order (persistent file order)

spatter id3help: for help with id3 tags

example:
spatter -t artist="Jerry Garcia Band" --fn2tag '%n %t.flac' *.flac
