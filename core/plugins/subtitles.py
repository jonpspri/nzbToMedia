from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from babelfish import Language
import subliminal

import core
from core import logger


def import_subs(filename):
    if not core.GETSUBS:
        return
    try:
        subliminal.region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})
    except Exception:
        pass

    languages = set()
    for item in core.SLANGUAGES:
        try:
            languages.add(Language(item))
        except Exception:
            pass
    if not languages:
        return

    logger.info('Attempting to download subtitles for {0}'.format(filename), 'SUBTITLES')
    try:
        video = subliminal.scan_video(filename)
        subtitles = subliminal.download_best_subtitles({video}, languages)
        subliminal.save_subtitles(video, subtitles[video])
    except Exception as e:
        logger.error('Failed to download subtitles for {0} due to: {1}'.format(filename, e), 'SUBTITLES')

def rename_subs(path):
    filepaths = []
    sub_ext = ['.srt', '.sub', '.idx']
    vidfiles = core.list_media_files(path, media=True, audio=False, meta=False, archives=False)
    if not vidfiles or len(vidfiles) > 1: # If there is more than 1 video file, or no video files, we can't rename subs.
        return
    name = os.path.splitext(os.path.split(vidfiles[0])[1])[0]
    for directory, _, filenames in os.walk(path):
        for filename in filenames:
            filepaths.extend([os.path.join(directory, filename)])
    subfiles = [item for item in filepaths if os.path.splitext(item)[1] in sub_ext]
    for sub in subfile:
        if name in sub: # The sub file name already includes the video name.
            continue
        subname, ext = os.path.splitext(sub)
        words = subname.split()
        # parse the words for language descriptors.
        lan = ''
        for word in words:
            try:
                if len(word) == 2:
                    lan = Language.fromalpha2(word)
                if len(word) > 3:
                    lan = Language(words[0:2])
                if lan:
                    break
            except:
                continue
        #if not lan: # Could call ffprobe to parse the sub information and get language     
        # rename the sub file as name.lan.ext
        new_sub_name = '{name}.{lan}.{ext}'.format(name=name, lan=lan, ext=ext)
        new_sub = os.path.join(directory, new_sub_name)
        if os.path.isfile(new_sub): # Don't copy over existing
            logger.debug('Unable to rename sub file {old} as destination {new} already exists'.format(old=sub, new=new_sub))
            continue
        logger.debug('Renaming sub file from {old} to {new}'.format
                 (old=sub, new=new_sub))
        try:
            os.rename(sub, new_sub)
        except Exception as error:
            logger.error('Unable to rename sub file due to: {error}'.format(error=error))
    return
