import subprocess
import os
import hashlib
from rippy_help_functions import *

def flac_tagging(rippy_class, commands):

    artist = rippy_class.ARTIST_STR
    album = rippy_class.ALBUM_STR
    genre = rippy_class.GENRE_STR
    comment = rippy_class.COMMENT_STR
    year = rippy_class.YEAR_STR
    various = rippy_class.various_list
    tracklist = rippy_class.track_list

    commands.append(subprocess.Popen("flac -8 -V *.wav", shell=True, encoding='utf8', stdout=subprocess.PIPE, stderr=subprocess.PIPE))

    make_flac = sorted(os.listdir())

    # Process each sound file and generate necessary information
    for sounds, i in enumerate(make_flac):
        rippy_class.wav_size_list.append(os.path.getsize(i))
        
        if rippy_class.SPECTRO_BOOL:
            commands.append(subprocess.Popen(f'sox "{i}" -n spectrogram -t "{rippy_class.file_name_list[sounds]}.flac" -o "{i[:-3]}png"', shell=True))

    # Getting CD pre-gaps
    for process in [i for i in commands]:
        process.wait()

    # Clean up WAV files
    for i in make_flac:
        os.remove(i)


    # Tag and rename FLAC files
    tag_flac = sorted([flac for flac in os.listdir() if ".flac" in flac])
    
    for idx, i in enumerate(tag_flac):
        rippy_class.flac_size_list.append(os.path.getsize(i))
        if rippy_class.ENABLE_TAGGING_BOOL:

            import taglib
            track = taglib.File(i)
            track.tags["ALBUM"] = rippy_class.ALBUM_STR
            track.tags["TITLE"] = rippy_class.track_list[idx]
            track.tags["TRACKNUMBER"] = str(idx + 1).zfill(2)
            track.tags["ARTIST"] = rippy_class.various_list[idx]
            track.tags["COMMENT"] = rippy_class.COMMENT_STR
            track.tags["GENRE"] = rippy_class.GENRE_STR
            track.tags["YEAR"] = rippy_class.YEAR_STR
            track.tags["DATE"] = rippy_class.YEAR_STR
            
            track.save()
            
            rippy_class.bitrate_list.append(str(track.bitrate))
        
        file_name = f"{rippy_class.file_name_list[idx]}.flac"
        os.rename(i, file_name)
