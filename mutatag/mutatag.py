#!/usr/bin/env python3
import argparse
import sys
import mutagen

class TagSetAction(argparse.Action):
    # pylint: disable=too-few-public-methods
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self.tagname = kwargs.get('const')
        kwargs['default'] = []
        kwargs.setdefault('metavar', self.tagname)
        kwargs.setdefault('help', 'Set the tag for %s' % self.tagname)
        super(TagSetAction, self).__init__(option_strings, 'setting_tags', **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.setting_tags.append((self.tagname, values))

HELP_PROLOG = 'Sets or writes audio metadata tags using Mutagen. ' + \
    'When run without any optional parameters, prints all tags.'

HELP_EPILOG = 'Even though this program supports MP3 and M4A files, the tag names used in ' +\
    'options like --set-tag are always based on VORBISCOMMENT and then converted to the ' +\
    'appropriate ID3/iTunes tag. Don\'t specify ID3 tags like "TPE2" directly.'

def build_parser():
    parser = argparse.ArgumentParser(description=HELP_PROLOG, epilog=HELP_EPILOG)
    parser.add_argument('file', nargs='+', help='Input music files (flac/mp3/ogg/opus/m4a)')
    parser.add_argument('-a', '--artist', action=TagSetAction, const='ARTIST')
    parser.add_argument('--album-artist', action=TagSetAction, const='ALBUMARTIST')
    parser.add_argument('-A', '--album', action=TagSetAction, const='ALBUM')
    parser.add_argument('-t', '--title', action=TagSetAction, const='TITLE')
    parser.add_argument('-n', '--track', action=TagSetAction, const='TRACKNUMBER')
    parser.add_argument('-N', '--track-total', action=TagSetAction, const='TRACKTOTAL')
    parser.add_argument('-d', '--disc', action=TagSetAction, const='DISCNUMBER')
    parser.add_argument('-D', '--disc-total', action=TagSetAction, const='DISCTOTAL')
    parser.add_argument('-G', '--genre', action=TagSetAction, const='GENRE')
    parser.add_argument('--date', action=TagSetAction, const='DATE')
    #TODO print tags in custom format like '--format $(disc)$(track,02).$(title).$(ext)'
    #parser.add_argument('--format')
    #TODO add a --rename option using a similar format string
    parser.add_argument(
        '--set-tag', action='append', metavar='TAGNAME:VALUE',
        help='Sets the value of any arbitrary VORBISCOMMENT tag. If the tag already exists, its ' +
        'value is overwritten.')
    parser.add_argument(
        '--add-tag', action='append', metavar='TAGNAME:VALUE',
        help='Sets the value of any arbitrary VORBISCOMMENT tag. If the tag already exists, a ' +
        'second copy of the tag name is added with the specified value.')
    parser.add_argument(
        '--clear-tag', action='append', metavar='TAGNAME',
        help='Clears the value of any existing tag matching the specified VORBISCOMMENT name.')
    parser.add_argument(
        '--write', action='store_true',
        help='Forces a rewrite of all tags even if nothing changed. This results in all tag ' +
        'names being normalized to UPPERCASE and sorted lexicographically.')
    return parser

def is_valid_tag(mutafile, tagname):
    # ID3 has a small list of supported tags
    if hasattr(mutafile, 'ID3'):
        return tagname.lower() in mutafile.ID3.valid_keys
    # Any arbitrary tag name is valid in VORBISCOMMENT
    return True

def handle_file(filename, setting_tags, adding_tags, force_write=False):
    ftags = mutagen.File(filename, easy=True)
    modified = force_write or len(setting_tags) > 0 or len(adding_tags) > 0
    #TODO split a parameter like "-n 2/13" into TRACKNUMBER and TRACKTOTAL
    for (tagname, tagvalue) in setting_tags:
        if not is_valid_tag(ftags, tagname):
            print('ERROR: Invalid tag for MP3 file:', tagname, file=sys.stderr)
            sys.exit(1)
        if tagvalue is None or tagvalue == '':
            tagvalue = []
        ftags[tagname] = tagvalue
    for (tagname, tagvalue) in adding_tags:
        if not is_valid_tag(ftags, tagname):
            print('ERROR: Invalid tag for MP3 file:', tagname, file=sys.stderr)
            sys.exit(1)
        if tagvalue is None or tagvalue == '':
            continue
        ftags[tagname].append(tagvalue)
    if not modified:
        print(ftags.pprint())
    elif not hasattr(ftags, 'ID3'):
        # Sort all VORBISCOMMENT tags and convert to uppercase
        for key in sorted(ftags.tags.keys()):
            ftags[key.upper()] = ftags[key]
        ftags.save()

def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.set_tag:
        for tag_keyvalue in args.set_tag:
            args.setting_tags.append(tag_keyvalue.split(':', 1))

    if args.clear_tag:
        for tagname in args.clear_tag:
            args.setting_tags.append([tagname, None])

    args.adding_tags = []
    if args.add_tag:
        for tag_keyvalue in args.add_tag:
            args.adding_tags.append(tag_keyvalue.split(':', 1))

    for fname in args.file:
        handle_file(fname, args.setting_tags, args.adding_tags, args.write)

if __name__ == '__main__':
    main()
