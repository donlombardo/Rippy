import os
import subprocess
from rippy_help_functions import *


def format_time(sectors):
    minutes = sectors // 4500
    remaining = sectors % 4500
    seconds = remaining // 75
    frames = remaining % 75
    milliseconds = int((frames * 1000) / 75)
    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

try:
    timezone_abbr = subprocess.check_output(["date", "+%Z"], text=True).strip()
except subprocess.CalledProcessError:
    timezone_abbr = ""


def cue_list_creating(rippy_class, timezone_abbr=timezone_abbr):
    cue_list = []
    cue_list.append(
        f'REM DATE {rippy_class.YEAR_STR}\n'
        f'REM MUSICBRAINZ DISCID {rippy_class.MBID_STR}\n'
        f'REM COMMENT "cdparanoia III release 10.2 (September 11, 2008)"\n'
        f'REM COMMENT "Rippy Noncompliant style cue sheet, EAC style"\n'
        f'PERFORMER "{rippy_class.ARTIST_STR}"\n'
        f'TITLE "{rippy_class.ALBUM_STR}"\n'
        'REM COMPOSER ""'
    )

    with open("cdda.toc", "r") as cdda_file:
        cdda_list = cdda_file.readlines()  # List of lines
        cdda_file.seek(0)  # Move cursor back to the beginning of the file
        rippy_class.CDDA_STR = cdda_file.read()  # Entire file as a string

    os.remove("cdda.toc")

    silence = False
    cd_info = [i.split("\n") for i in ' '.join(cdda_list).split(r"// Track ")[1:]]
    

    for i in cd_info:
        for n in i:
            if n[:8] == " SILENCE":
                silence = True
                silence_time = n[8:]

            if n[:5] == " FILE":
                rippy_class.counted_list.append(n.split(" "))
                rippy_class.pre_gap_list.append(i[i.index(n) + 1][7:])
        if "NO PRE_EMPHASIS" in "".join(i):
            rippy_class.pre_emphasis_list.append("NO")
        else:
            rippy_class.pre_emphasis_list.append("YES")

    print()
    spaced_print("Creating cue and log(s).\n\n")

    for i in range(0, rippy_class.TRACK_AMOUNT_INT):
        if rippy_class.pre_gap_list[i] == '':
            cue_list.append(
                f'FILE "{rippy_class.file_name_list[i]}.wav" WAVE\n'
                f'  TRACK {str(i + 1).zfill(2)} AUDIO\n'
                f'    TITLE "{rippy_class.track_list[i]}"\n'
                f'    PERFORMER "{rippy_class.various_list[i]}"\n'
                '    REM COMPOSER ""\n'
                "    INDEX 01 00:00:00"
            )
        else:
            cue_list.append(
                f'  TRACK {str(i + 1).zfill(2)} AUDIO\n'
                f'    TITLE "{rippy_class.track_list[i]}"\n'
                f'    PERFORMER "{rippy_class.various_list[i]}"\n'
                '    REM COMPOSER ""'
            )

            if i == 0:
                if silence:
                    cue_list.append(
                        f"    {silence_time}\n"
                        "    INDEX 01 00:00:00\n"
                        f'FILE "{rippy_class.file_name_list[0]}.wav" WAVE\n'
                        "    INDEX 01 00:00:00"
                    )
            else:
                if rippy_class.pre_gap_list[i - 1] == '':
                    term_two = 0
                    samples = int(rippy_class.counted_list[i - 1][4][0:2]) * 60 * 75 + int(rippy_class.counted_list[i - 1][4][3:5]) * 75 + int(rippy_class.counted_list[i - 1][4][6:8])
                    minutes = int(samples / (75 * 60))
                    samples -= minutes * 75 * 60
                    seconds = int(samples / 75)
                    samples -= seconds * 75
                    cue_list.append(
                        f"    INDEX 00 {str(minutes).zfill(2)}:{str(seconds).zfill(2)}:{str(samples).zfill(2)}\n"
                        f'FILE "{rippy_class.file_name_list[i]}.wav" WAVE\n'
                        "    INDEX 01 00:00:00"
                    )
                else:
                    term_two = int(rippy_class.pre_gap_list[i - 1][0:2]) * 60 * 75 + int(rippy_class.pre_gap_list[i - 1][3:5]) * 75 + int(rippy_class.pre_gap_list[i - 1][6:8])
                    term_one = int(rippy_class.counted_list[i - 1][4][0:2]) * 60 * 75 + int(rippy_class.counted_list[i - 1][4][3:5]) * 75 + int(rippy_class.counted_list[i - 1][4][6:8])
                    samples = term_one - term_two
                    minutes = int(samples / (75 * 60))
                    samples -= minutes * 75 * 60
                    seconds = int(samples / 75)
                    samples -= seconds * 75
                    cue_list.append(
                        f"    INDEX 00 {str(minutes).zfill(2)}:{str(seconds).zfill(2)}:{str(samples).zfill(2)}\n"
                        f'FILE "{rippy_class.file_name_list[i]}.wav" WAVE\n'
                        "    INDEX 01 00:00:00"
                    )

    with open(f"{rippy_class.FOLDER_STR}.cue", "w") as cue:
        cue.write("\n".join(cue_list))



def verbose_log(rippy_class, timezone_abbr=timezone_abbr):
    log_filename = f"{rippy_class.FOLDER_STR} verbose.log"
    
    with open(log_filename, "w") as log_file_writer:
        log_file_writer.write(f"Rippy verbose logfile from {rippy_class.now_str} {timezone_abbr}\n\n")
        
        if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.accuraterip_levels_list:

            log_file_writer.write("\n\nAll AccurateRip™ checksum dictionaries for the album:\n\n")
            
            for item in rippy_class.accuraterip_dict:
                log_file_writer.write(f"{item}: {str(rippy_class.accuraterip_dict[item])}\n")
            
            log_file_writer.write("\n\n")

            log_file_writer.write("AccurateRip™ results:\n\n")
            for items in rippy_class.verbose_list:
                log_file_writer.write(f"{items}\n\n")


        if rippy_class.CUE_BOOL:
            log_file_writer.write(f"\n\nCDDA Table Of Contents (TOC) of CD:\n\n{rippy_class.CDDA_STR}\n")

        if rippy_class.HTOA_RIPPED_BOOL:
            for htoa in rippy_class.htoa_dict:
                if htoa in [str(i) for i in range(1, rippy_class.RETRY_INT + 1)]:
                    log_file_writer.write(f"HTOA rip {htoa}\n\n")

                    if rippy_class.GAIN_BOOL:
                        gain_values = rippy_class.htoa_dict[str(htoa)]['gain']
                        log_file_writer.write(
                            f"     Track level: {gain_values[0]} dBFS\n"
                            f"     Track peak: {gain_values[1]} dBFS\n"
                            f"     Track gain: {gain_values[2]} dB\n"
                        )
                    log_file_writer.write(f"     Track MD5 checksum (wav): {rippy_class.htoa_dict[str(htoa)]['wav_md5']}\n\n")
               
                    if rippy_class.DE_FACTO_LEVEL_STR not in ["G", "H", "I"]:
                        if "0" in rippy_class.test_dict:
                            if rippy_class.test_dict["0"]["sectors"]:
                                log_file_writer.write(f"\nT sectors in track {track}:\n\n")
                                log_file_writer.write(", ".join(map(str, data["sectors"])) + "\n\n")


        for counter, track_data in enumerate(rippy_class.tracks_ripped_dict, start=1):
            if rippy_class.tracks_ripped_dict[track_data]:
                log_file_writer.write(f"Rip {counter}\n\n")
                for position, track in enumerate(rippy_class.tracks_ripped_dict[track_data]):
                    log_file_writer.write(f"Track {track}\n\n")
                    
                    if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.accuraterip_levels_list:
                        log_file_writer.write(
                            f"     CRC ARv1: {rippy_class.crc_v1_dict[str(counter)][position]}\n"
                            f"     CRC ARv2: {rippy_class.crc_v2_dict[str(counter)][position]}\n"
                        )
                    if rippy_class.GAIN_BOOL:
                        gain_values = rippy_class.gain_list_dict[str(counter)][position]
                        log_file_writer.write(
                            f"     Track level: {gain_values[0]} dBFS\n"
                            f"     Track peak: {gain_values[1]} dBFS\n"
                            f"     Track gain: {gain_values[2]} dB\n"
                        )
                    log_file_writer.write(
                        f"     Track MD5 checksum (wav): {rippy_class.md5_list_dict[str(counter)][position]}\n\n")
            
        if rippy_class.DE_FACTO_LEVEL_STR not in ["G", "H", "I"]:
            for track, data in rippy_class.test_dict.items():
                if track != "0":
                    if data["sectors"]:
                        log_file_writer.write(f"\nCorrected sectors in track {track}:\n\n")
                        log_file_writer.write(", ".join(map(str, data["sectors"])) + "\n\n")


def bonus_log_function(rippy_class, timezone_abbr=timezone_abbr):

    with open(f"{rippy_class.USED_DRIVE_STR}.log", "w") as bonus_file:
        bonus_file.write(f"Rippy bonus logfile from {rippy_class.now_str} {timezone_abbr}\n\n")
        
        bonus_file.write(
            "This bonus log shows the additional information about your drive that you have chosen to include. "
            "This bonus log does not contain information about the rip, but the state of your CD drive from the "
            "Linux software packages cd-drive, cdrdao, and cdparanoia.\n\nYour cd-drive information:\n\n"
        )
        
        bonus_file.write(f"{rippy_class.bonus_log_dict['cd_drive_info']}\n")
        
        if rippy_class.TEST_DRIVE_BOOL:
            bonus_file.write("Your cdrdao information:\n\n")
            for i in rippy_class.bonus_log_dict["cdrdao_drive_info"]:
                bonus_file.write(f"{i}\n")
            
            bonus_file.write("Your cdparanoia analysis information:\n\n")
            for i in rippy_class.bonus_log_dict["cdparanoia_drive_info"]:
                bonus_file.write(f"{i}\n")



def main_log_function(rippy_class, timezone_abbr=timezone_abbr):
    with open(f"{rippy_class.FOLDER_STR}.log", "w") as log:
        log.write(
            f"Rippy V.{rippy_class.RIPPY_VERSION_STR} from {rippy_class.VERSION_DATE_STR}\n\n"
            f"Rippy extraction logfile from {rippy_class.now_str} {timezone_abbr}\n\n"
            f"Artist: {rippy_class.ARTIST_STR}\n"
            f"Album: {rippy_class.ALBUM_STR}\n\n"
            f"Used drive                                  : {rippy_class.USED_DRIVE_STR}\n"
            f"Ripper                                      : cdparanoia III release 10.2 (September 11, 2008)\n"
            f"Utilize accurate stream                     : Yes (if CD drive supports accurate stream)\n"
            f"Defeat audio cache                          : Yes (cdparanoia III will try to defeat CD drive cache)\n"
            f"Make use of C2 pointers                     : No (cdparanoia III does not support C2 pointers and works best with CD drives without C2 pointers)\n"
            f"Read offset correction                      : {rippy_class.OFFSET_STR_LOG}\n"
            f"Overread into Lead-In and Lead-Out          : No\n"
            f"Fill up missing offset samples with silence : Yes (cdparanoia III does this automatically if your drive can read into the lead-in and lead-out, otherwise cdparanoia will throw an error.)\n"
            f"Delete leading and trailing silent blocks   : No\n"
            f"Null samples used in CRC calculations       : Yes\n"
            f"Gap handling                                : Appended to previous track (cdparanoia III does this automatically)\n")
            
        log.write(f"MusicBrainz ID                              : {rippy_class.MBID_STR}\n")
        log.write(f"Freedb ID                                   : {rippy_class.FDID_STR}\n")
            
        log.write(
            f"Used output format                          : FLAC with -8 -V parameter\n\n\n"        
            f"TOC of the extracted CD\n\n{rippy_class.TOC_READ_STR}\n\n"
            f"Using cdda library version: 10.2\n"
            f"Using paranoia library version: 10.2\n\n\n"
        )

        log.write(rippy_class.FINAL_OUTPUT_STR)

        if rippy_class.FINAL_OUTPUT_STR:
            log.write(f"\n{len(rippy_class.accurately_ripped_list)} out of {rippy_class.TRACK_AMOUNT_INT} ripped correctly, according to AccurateRip™. See each track for more details.\n\n")

        if rippy_class.HTOA_BOOL and rippy_class.HTOA_EXIST_BOOL:
            
            log.write(f"Hidden Track One Audio (HTOA):\n\n")
            log.write(f"     Filename: {rippy_class.HTOA_FILE_NAME_STR}.flac\n\n")

            if rippy_class.CUE_BOOL:                
                log.write(f"     Track length: {str(rippy_class.pre_gap_list[0])}\n")

            if rippy_class.GAIN_BOOL:
                log.write(
                    f"     Track level: {rippy_class.htoa_dict['gain'][0]} dBFS\n"
                    f"     Track peak: {rippy_class.htoa_dict['gain'][1]} dBFS\n"
                    f"     Track gain: {rippy_class.htoa_dict['gain'][2]} dB\n")

            if rippy_class.ENABLE_TAGGING_BOOL:
                log.write(f"     Track bitrate: {rippy_class.htoa_dict['htoa_bitrate']} kbps\n")

            log.write(
                f"     Track MD5 checksum (flac)): {rippy_class.htoa_dict['flac_md5']}\n"
                f"     Track file size (wav): {str(rippy_class.htoa_dict['wav_size'])} bytes\n"
                f"     Track file size (flac): {str(rippy_class.htoa_dict['flac_size'])} bytes (without tags)\n"
                f"     Track compression: {str(round((rippy_class.htoa_dict['flac_size']/rippy_class.htoa_dict['wav_size'])*100, 2))} % of original wave file\n\n\n")

            if "3" in rippy_class.htoa_dict:
                log.write("     Track needed several rips and manual correction. Track quality: \n")
                for pos in rippy_class.test_dict:
                    if pos == "0":
                        log.write(
                            f"     Track needed correction at {str(rippy_class.test_dict[pos]['diffy_lengths'])} bytes "
                            f"and has an identical bytes track quality of {str(100 - round((int(rippy_class.test_dict[pos]['diffy_lengths'])/int(rippy_class.htoa_dict['flac_size']))*100, 5))} % .\n"
                        )
                        start = format_time(sectors[0])
                        stop = format_time(sectors[-1])
                    
                        log.write(f"     Track needed correction somewhere between times (in min:sec:msec) {start} and {stop}.\n\n")

        
        for i in range(0, rippy_class.TRACK_AMOUNT_INT):
            log.write(
                f"Track {i + 1}\n\n"
                f"     Filename: {rippy_class.file_name_list[i]}.flac\n\n"
                f"     Track length: {rippy_class.track_length_list[i]} (min:sec.sectors)\n"
                f"     Track length: {rippy_class.track_length_list[i][:5]}:{str(round(int(rippy_class.track_length_list[i][6:])*(40/3))).zfill(3)} (min:sec:msec, rounded to closest msec)\n"
            )
            if rippy_class.CUE_BOOL:
                if rippy_class.pre_gap_list[i] == "":
                    pre_gap = "00:00:00 (0 seconds)"
                    log.write(f"     Pre-gap length {pre_gap}\n")
                else:
                    if rippy_class.HTOA_BOOL and i == 0 and rippy_class.HTOA_EXIST_BOOL:
                        pass
                    pre_gap = f"{rippy_class.pre_gap_list[i]} ({str(round(int(rippy_class.pre_gap_list[i][:2])*60 + int(rippy_class.pre_gap_list[i][3:5]) + int(rippy_class.pre_gap_list[i][6:])*(0.04/3), 3))} seconds)"
                    log.write(f"     Pre-gap length: {pre_gap}\n")

                if rippy_class.pre_emphasis_list:
                     log.write(f"     Track pre-emphasis: {str(rippy_class.pre_emphasis_list[i])}\n")

            if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.accuraterip_levels_list:

                log.write(
                    f"     CRC ARv1: {rippy_class.crc_v1_dict['final'][i]}\n"
                    f"     CRC ARv2: {rippy_class.crc_v2_dict['final'][i]}\n"
                    )

            if rippy_class.GAIN_BOOL:
                gain_1, gain_2, gain_3 = rippy_class.gain_list_dict["final"][i]
                log.write(
                    f"     Track level: {gain_1} dBFS\n"
                    f"     Track peak: {gain_2} dBFS\n"
                    f"     Track gain: {gain_3} dB\n"
                )

            if rippy_class.ENABLE_TAGGING_BOOL:
                log.write(f"     Track bitrate: {rippy_class.bitrate_list[i]} kbps\n")

            log.write(
                f"     Track MD5 checksum (flac): {rippy_class.md5_list_dict['final'][i]}\n"
                f"     Track file size (wav): {rippy_class.wav_size_list[i]} bytes\n"
                f"     Track file size (flac): {rippy_class.flac_size_list[i]} bytes (without tags)\n"
                f"     Track compression: {round((rippy_class.flac_size_list[i]/rippy_class.wav_size_list[i])*100, 2)} % of original wave file\n"

            )

            if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.accuraterip_levels_list:
                log.write(f"\n     This track had a AccurateRip™ {rippy_class.V1_OR_V2_STR} checksum confidence match of {rippy_class.confidence_dict['final'][i]}.\n")

            if str(i + 1) in rippy_class.needed_correction_list:
                log.write(f"\n     Track needed several rips and correction.\n")

                for pos_data in rippy_class.test_dict:

                    if pos_data == str(i + 1) and len(rippy_class.test_dict[pos_data]["sectors"]) > 0:
                        track_quality = 100 - round((int(rippy_class.test_dict[pos_data]["diffy_lengths"]) / rippy_class.wav_size_list[i]) * 100, 5)
                        log.write(f"     Track needed correction at {rippy_class.test_dict[pos_data]['diffy_lengths']} places and has a perfect track quality of {track_quality} %.\n")
                        sectors = sorted(rippy_class.test_dict[pos_data]["sectors"])
                        

                        start = format_time(sectors[0])
                        stop = format_time(sectors[-1])
                        log.write(f"     Track needed correction somewhere between times (in min:sec:msec) {start} and {stop}.\n")

                    elif pos_data == str(i + 1):
                        log.write(f"     The track matched at all positions, identically, for all bytes. This suggests the AccurateRip™ database entry is faulty.\n")
            else:
                log.write(f"\n     Track ripped without errors. Track quality: 100 %.\n")
                
            log.write("\n")
                
