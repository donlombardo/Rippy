""" Defines the ripping process """

import subprocess
import os
import hashlib
from rippy_help_functions import *
from rippy_track_analysis_functions import *
import rippy_shared_object



def all_track_rip(rip, rippy_class, correction=""):

    if correction != "-Z":
        correction=rippy_class.ERROR_CORRECTION_STR

    """ 
    cdparanoia rips all tracks the first time of the CD in -Z mode the first time, 
    except the very last sector of the very last track, which is without -Z.
    """
    
    # Rip all tracks except the very last sector of the very last track
    drive = rippy_class.DRIVE_STR
    offset = rippy_class.OFFSET_STR
    speed = rippy_class.SPEED_STR
    last_length = rippy_class.LAST_LENGTH_STR
    last_sector = rippy_class.LAST_SECTOR_STR
    track_amount = rippy_class.TRACK_AMOUNT_INT


    ripping_command = f"cdparanoia 1-{int(track_amount) - 1} {drive} -B {correction} {offset} {speed} '{rip}.wav'"

    ripping = subprocess.Popen(
        ripping_command,
        shell=True, stdout=subprocess.PIPE)
    ripping.wait()

    # Rip the last track with the correct sector length

    ripping = subprocess.Popen(
        f"cdparanoia {track_amount}[.0]-{track_amount}[.{last_length}] {drive} -B {correction} {offset} {speed} '{rip}.a.wav'",
        shell=True, stdout=subprocess.PIPE)
    ripping.wait()

    # Rip the very last sector of the last track

    ripping = subprocess.Popen(
        f"cdparanoia {track_amount}[.{last_sector}]-{track_amount}[.{last_sector}] {drive} -B {offset} {speed} '{rip}.b.wav'",
        shell=True, stdout=subprocess.PIPE)
    ripping.wait()

    # Merge the ripped files into a single track
    merge = subprocess.Popen(
        f"sox track{str(track_amount).zfill(2)}.{rip}.a.wav track{str(track_amount).zfill(2)}.{rip}.b.wav track{str(track_amount).zfill(2)}.{rip}.wav",
        shell=True, stdout=subprocess.PIPE)
    merge.wait()

    # Clean up temporary files
    os.remove(f"track{str(track_amount).zfill(2)}.{rip}.a.wav")
    os.remove(f"track{str(track_amount).zfill(2)}.{rip}.b.wav")
    return rippy_class


def main_ripping_process(rippy_class):
    counter = 1
    
    # Initialize dictionary entries for tracks to be ripped
    rippy_class.update_dicts(suffix=counter)
    
    # Format the rip identifier
    rip = str(counter).zfill(3)

    # Add the list of tracks to be ripped into the dictionary
    rippy_class.tracks_ripped_dict[str(counter)] = [str(i) for i in range(1, rippy_class.TRACK_AMOUNT_INT + 1)]
    
    # Handle error correction or test and copy depending on the level
    if rippy_class.DE_FACTO_LEVEL_STR not in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
        message = "You have to choose a valid level. Change it in the settings file. Rippy will now quit."
        rippy_class.abort(message)

    # Inform the user that the ripping process is starting
    spaced_print(f"Now cdparanoia will rip tracks 1-{rippy_class.TRACK_AMOUNT_INT}. This might take a while, stay tuned.")

    # Perform the ripping process for the tracks
    all_track_rip(rip, rippy_class, correction="-Z")

    # Verify if the expected ripped tracks exist
    track_verify_list = sorted([i for i in os.listdir() if i[-7:] == f"{rip}.wav"])

    in_ar, not_in_ar = main_ripping_function(track_verify_list, counter, rippy_class, rip)

    track_reconstruction(rippy_class, in_ar, not_in_ar)



def main_ripping_function(track_verify_list, counter, rippy_class, rip):
    in_ar, not_in_ar = track_analysis(rippy_class, filenames=track_verify_list, rip=rip, message=counter, ripping_now=track_verify_list)

    if rippy_class.DE_FACTO_LEVEL_STR == "G" and not_in_ar:
        message = "The tracks didn't match the tracks in the AccurateRip™ datebase. Aborting."
        rippy_class.abort(message)

    drive = rippy_class.DRIVE_STR
    offset = rippy_class.OFFSET_STR
    speed = rippy_class.SPEED_STR
    correction = rippy_class.ERROR_CORRECTION_STR
    last_length = rippy_class.LAST_LENGTH_STR
    last_sector = rippy_class.LAST_SECTOR_STR
    track_amount = rippy_class.TRACK_AMOUNT_INT

    # Does not check AccurateRip™ for any rip
    if rippy_class.DE_FACTO_LEVEL_STR in ["C", "D", "E", "F"]:
        for i in range(rippy_class.MATCHING_BYTES_INT - 1):
            counter += 1

            rippy_class.update_dicts(suffix=counter)

            rip = str(counter).zfill(3)

            all_track_rip(rip, rippy_class, correction="-Z")

            track_verify_list = sorted([i for i in os.listdir() if i[-7:] == f"{rip}.wav"])

            rippy_class.tracks_ripped_dict[str(counter)] = [str(i) for i in range(1, track_amount + 1)]

            track_analysis(rippy_class, filenames=track_verify_list, rip=rip, message=counter,ripping_now=track_verify_list)

        find_identical(rippy_class)
        
        not_in_ar_temp = list(rippy_class.needed_correction_list)
        needs_correction = sorted(not_in_ar_temp)
        
        if not rippy_class.ERRONOUS_BOOL:
            spaced_print("All tracks matched.")

    if rippy_class.DE_FACTO_LEVEL_STR not in ["G", "H", "I"]:
        while counter < rippy_class.RETRY_INT: # Breaks when it has reached the set amount of retries
            
            if rippy_class.DE_FACTO_LEVEL_STR in ["A", "B"]:

                if len(in_ar) == track_amount:
                    break #Continues when it has found matches for all tracks in AccurateRip
                elif 1 < len(not_in_ar) < track_amount:
                    print()
                    spaced_print(f"These tracks are not in AccurateRip™ database: {', '.join(map(str, not_in_ar[:-1]))} and {not_in_ar[-1]}.")
                else:
                    print()
                    spaced_print(f"This track is not in AccurateRip™ database: {not_in_ar[0]}")

            elif rippy_class.DE_FACTO_LEVEL_STR in ["C", "D", "E", "F"]:

                if len(needs_correction) == 0:
                    break

            counter += 1
            rip = str(counter).zfill(3)
            print()

            rippy_class.update_dicts(suffix=counter)
            ripping_now = []
            
            if rippy_class.DE_FACTO_LEVEL_STR in ["A", "B"]:
                rip_list = list(not_in_ar)

            elif rippy_class.DE_FACTO_LEVEL_STR in ["C", "D", "E", "F"]:
                needed_correction_len = len(needs_correction)
                rip_list = list(needs_correction)

                print()
                spaced_print(f"All tracks were not matched by your requirement. Requiring re-rips of {'these tracks' if needed_correction_len > 1 else 'this track'}: ")

                spaced_print(f"{', '.join(needs_correction[:-1])} and {needs_correction[-1]}.") if needed_correction_len > 1 else spaced_print(needs_correction[0])

            rippy_class.tracks_ripped_dict[str(counter)] = list(rip_list)

            print(f"Try number {counter} of {rippy_class.RETRY_INT}.\n")

            for track in rip_list:
                ripping_now.append(f"track{int(track):02}.{rip}.wav")

                if int(track) == track_amount:
                    ripping_command_a = (
                        f'cdparanoia {track_amount}[.0]-{track_amount}[.{last_length}] -B {drive} {correction} {offset} {speed} "{rip}.a.wav"'
                    )

                    ripping = subprocess.Popen(ripping_command_a, shell=True, stdout=subprocess.PIPE)
                    ripping.wait()

                    ripping_command_b = (
                        f'cdparanoia {track_amount}[.{last_sector}]-{track_amount}[.{last_sector}] -B {drive} {offset} {speed} "{rip}.b.wav"'
                    )
                    ripping = subprocess.Popen(ripping_command_b, shell=True, stdout=subprocess.PIPE)
                    ripping.wait()

                    merge_command = (
                        f'sox track{str(track_amount).zfill(2)}.{rip}.a.wav '
                        f'track{str(track_amount).zfill(2)}.{rip}.b.wav '
                        f'track{str(track_amount).zfill(2)}.{rip}.wav'
                    )
                    merge = subprocess.Popen(merge_command, shell=True, stdout=subprocess.PIPE)
                    merge.wait()

                    os.remove(f"track{str(track_amount).zfill(2)}.{rip}.a.wav")
                    os.remove(f"track{str(track_amount).zfill(2)}.{rip}.b.wav")
                else:

                    ripping_command = (
                        f'cdparanoia {track} {drive} -B {correction} {offset} {speed} "{rip}.wav"'
                    )

                    ripping = subprocess.Popen(ripping_command, shell=True, stdout=subprocess.PIPE)
                    ripping.wait()

            if rippy_class.DE_FACTO_LEVEL_STR in ["A", "B", "C", "D"]:
                track_verify_list = sorted(rippy_class.accurately_ripped_list + ripping_now)

            elif rippy_class.DE_FACTO_LEVEL_STR in [ "E", "F"]:
                track_verify_list = sorted(ripping_now)
            
            in_ar, not_in_ar = track_analysis(rippy_class, filenames=track_verify_list, rip=rip, message=counter, ripping_now=ripping_now)
                
            if rippy_class.DE_FACTO_LEVEL_STR in ["C", "D", "E", "F"]:            
                needs_correction = []

                print(f"Trying to find differences... This might take a while, if the track was long and there are several files. Otherwise it might be fast.\n")
                for track_not in rippy_class.tracks_ripped_dict[str(counter)]:
                    

                    filenames = [f"track{str(track_not).zfill(2)}.{str(k).zfill(3)}.wav" for k in range(1, counter + 1)]
                    
                    

                    matching_bool = find_differing(filenames, rippy_class)

                    if not matching_bool:
                        needs_correction.append(track_not)
                        print("\n\n")
                        spaced_print(f"More rips required for track {track_not}.")
                    
                    else:
                        spaced_print(f"No more rips required for track {track_not}.")



        if rippy_class.DE_FACTO_LEVEL_STR in ["C", "D", "E", "F"]:   
            not_in_ar = sorted(not_in_ar_temp)
            
            if needs_correction and rippy_class.DE_FACTO_LEVEL_STR in ["D","F"]:
                print("\n\n")
                message = f"Some tracks could not be matched according to your set amount of matching bytes ({rippy_class.MATCHING_BYTES_INT}), aborting."
                rippy_class.abort(message)

    return in_ar, not_in_ar



def track_reconstruction(rippy_class, in_ar, not_in_ar, htoa_track=False):

    if not htoa_track:
        if rippy_class.DE_FACTO_LEVEL_STR in ["A", "B"]:
            for i in rippy_class.accurately_ripped_list:
                os.rename(i, f"track{i[5:7]}.wav")
                for n in range(1, rippy_class.RETRY_INT + 1):
                    try:
                        os.remove(f"track{i[5:7]}.{str(n).zfill(3)}.wav")
                    except:
                        pass
            for needed_correction in not_in_ar:
                rippy_class.needed_correction_list.append(str(needed_correction))
            if not_in_ar:
                if len(not_in_ar) > 1:
                    tracks_not_in_database = [str(s) for s in not_in_ar]
                    print()
                    spaced_print(f'These tracks are not in AccurateRip™ database and Rippy will try to correct them manually: {", ".join(tracks_not_in_database[:-1])} and {tracks_not_in_database[-1]}.\n')
                else:
                    print()
                    spaced_print(f"This track is not in AccurateRip™ database and Rippy will try to correct it manually: {not_in_ar[0]}")


        elif rippy_class.DE_FACTO_LEVEL_STR in ["C", "D", "E", "F"]:
            if not_in_ar:
                if len(not_in_ar) > 1:
                    tracks_not_in_database = [str(s) for s in not_in_ar]
                    print()
                    spaced_print(f'These tracks did not match identically when ripped and Rippy will try to correct them manually: {", ".join(tracks_not_in_database[:-1])} and {tracks_not_in_database[-1]}.\n')
                else:
                    print()
                    spaced_print(f"This track did not match identically when ripped and Rippy will try to correct it manually: {not_in_ar[0]}")

        if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.more_than_once_list:
            for track_not in not_in_ar:
                output_file = f"track{str(track_not).zfill(2)}.wav"
                rippy_class.test_dict[str(track_not)] = {}
                rippy_class.test_dict[str(track_not)]["sectors"] = set()
                

                spaced_print(f"Trying to correct track {track_not}.")
                print()
                filenames = [track for track in os.listdir() if f"track{str(track_not).zfill(2)}" in track]

                rippy_class.test_dict[str(track_not)]["diffy_lengths"] = reconstruct_track(filenames, rippy_class, output_file)

                for n in range(1, rippy_class.RETRY_INT + 1):
                    try:
                        os.remove(f"track{str(track_not).zfill(2)}.{str(n).zfill(3)}.wav")
                    except:
                        pass
                
                rippy_class.test_dict[str(track_not)]["sectors"] = sorted(list(rippy_class.test_dict[str(track_not)]["sectors"]))



        track_verify_list = sorted([track for track in os.listdir() if ".wav" in track])

        rippy_class.update_dicts(suffix="final")
        track_analysis(rippy_class, track_verify_list, rip="final", message="final",ripping_now=track_verify_list)

        if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.accuraterip_levels_list:     
            if not not_in_ar:
                spaced_print("In the end, all tracks could be verified by AccurateRip™.")
            elif len(not_in_ar) == 1:
                spaced_print(f"In the end, track {not_in_ar[0]} could not be verified by AccurateRip™. \n")
            elif len(not_in_ar) == rippy_class.TRACK_AMOUNT_INT:
                spaced_print("In the end, no tracks could be verified by AccurateRip™. \n")
            else:
                spaced_print(f"In the end, tracks {', '.join(not_in_ar[:-1])} and {not_in_ar[-1]} could not be verified by AccurateRip™. The rest will be noted in the log.")
            if rippy_class.DE_FACTO_LEVEL_STR in ["A", "B"] and len(rippy_class.accurately_ripped_list) != rippy_class.TRACK_AMOUNT_INT:
                rippy_class.ERRONOUS_BOOL = True

    else:
        if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.more_than_once_list:
            spaced_print("Trying to correct HTOA track.")
            output_file = "track00.wav"
            filenames = sorted([track for track in os.listdir() if "track00" in track])
            rippy_class.htoa_dict["diffy_lengths"] = reconstruct_track(filenames, rippy_class, output_file)
        
    spaced_print("Ripping is done. Will commence converting to flac.")



def find_identical(rippy_class):
    for current_rip in range(1, rippy_class.TRACK_AMOUNT_INT + 1):
        filenames = sorted([track for track in os.listdir() if f"track{str(current_rip).zfill(2)}" in track])
        diffy = find_differing(filenames, rippy_class, finding_identical=True, current_rip=current_rip)
        if diffy:
            os.rename(f"track{str(current_rip).zfill(2)}.001.wav", f"track{str(current_rip).zfill(2)}.wav")
            rippy_class.identical_list.append(f"track{str(current_rip).zfill(2)}.wav")
            for i in filenames:
                try:
                    os.remove(i)
                except:
                    pass
        else:
            if current_rip not in rippy_class.needed_correction_list:
                rippy_class.needed_correction_list.append(str(current_rip))
    rippy_class.needed_correction_list.sort()
    if rippy_class.needed_correction_list:
        rippy_class.ERRONOUS_BOOL = True




def htoa_rip(rippy_class):

    drive = rippy_class.DRIVE_STR
    offset = rippy_class.OFFSET_STR
    speed = rippy_class.SPEED_STR
    track_amount = rippy_class.TRACK_AMOUNT_INT
    htoa_last = rippy_class.HTOA_LAST_SECTOR_STR

    spaced_print("Now cdparanoia will try to rip track 0 (HTOA) your set amount of times.")

    correction = "-Z "
    htoa_rip_list = list(range(1, rippy_class.MATCHING_BYTES_INT + 1)) if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.more_than_once_list else [1]

    for counter in htoa_rip_list:

        rip = str(counter).zfill(3)
        track = f"track00.{rip}.wav"
        ripping_command = (
            f'cdparanoia "0[.0]-0[.{htoa_last}]" {drive} -B {correction} {offset} {correction} {speed} "{rip}.wav"'
        )
        ripping = subprocess.Popen(ripping_command, shell=True, stdout=subprocess.PIPE)
        ripping.wait()

        rippy_class.htoa_dict[str(counter)] = {}

        rippy_class.htoa_dict[str(counter)]["wav_md5"] = hashlib.md5(track.encode('utf-8')).hexdigest()
        rippy_class.htoa_dict[str(counter)]["wav_size"] = os.path.getsize(track)

        if rippy_class.GAIN_BOOL:
            gain = subprocess.Popen(
                f"normalize-audio -n {track}", 
                shell=True, encoding='utf8', stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            gain.wait()
            gain = gain.stdout.read()
            # Process and clean up gain output
            for white_space in range(3,6):
                gain = gain.replace(" "*white_space, " ")
            gain = gain.replace("dBFS", "").replace("dB", "").replace("  ", " ").split(" ")[:-1]
            
            rippy_class.htoa_dict[str(counter)]["gain"] = gain

    if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.more_than_once_list:
        filenames = [f"track00.00{i}.wav" for i in range(1, rippy_class.MATCHING_BYTES_INT + 1)]
        diffy = find_differing(filenames, rippy_class, finding_identical=True)

        if diffy:
            os.rename("track00.001.wav", "HTOA.wav")
            remove_int = 2
            while True:
                filename = f"track00.00{remove_int}.wav"
                if os.path.exists(filename):
                    os.remove(filename)
                    remove_int += 1
                else:
                    break

        else:
            while counter < rippy_class.RETRY_INT:
                if diffy:
                    spaced_print("HTOA track matched your required amount of times.")
                    break
                else:
                    spaced_print("HTOA track was not matched your required amount of times. Requiring re-rips.")

                    counter += 1
                    rip = str(counter).zfill(3)

                    track = f"track00.{rip}.wav"

                    rippy_class.htoa_dict[str(counter)] = {}
                    spaced_print(f"Try {counter} of {rippy_class.RETRY_INT}.")

                    ripping = subprocess.Popen(
                        f'cdparanoia "0[.0]-0[.{htoa_last}]" {drive} -B {correction} {offset} {correction} {speed} "{rip}.wav"',
                        shell=True,
                        stdout=subprocess.PIPE
                    )                
                    ripping.wait()

                    rippy_class.htoa_dict[str(counter)]["wav_md5"] = hashlib.md5(track.encode('utf-8')).hexdigest()
                    rippy_class.htoa_dict[str(counter)]["wav_size"] = os.path.getsize(track)

                    if rippy_class.GAIN_BOOL:
                        gain = subprocess.Popen(
                            f"normalize-audio -n {track}", 
                            shell=True, encoding='utf8', stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                        gain.wait()
                        gain = gain.stdout.read()
                        # Process and clean up gain output
                        for white_space in range(3,6):
                            gain = gain.replace(" "*white_space, " ")
                        gain = gain.replace("dBFS", "").replace("dB", "").replace("  ", " ").split(" ")[:-1]
                        
                        rippy_class.htoa_dict[str(counter)]["gain"] = gain
                

                    filenames = [i for i in os.listdir() if "track00" in i]
                    diffy = find_differing(filenames)

            track_reconstruction(rippy_class, in_ar, not_in_ar, htoa_track=True)
        
        rippy_class.htoa_dict["wav_size"] = os.path.getsize("HTOA.wav")
        rippy_class.htoa_dict["wav_md5"] = hashlib.md5("HTOA.wav".encode('utf-8')).hexdigest()

        if rippy_class.GAIN_BOOL:
            gain = subprocess.Popen(
                f"normalize-audio -n HTOA.wav", 
                shell=True, encoding='utf8', stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            gain = gain.stdout.read()
            # Process and clean up gain output
            for white_space in range(3,6):
                gain = gain.replace(" "*white_space, " ")
            gain = gain.replace("dBFS", "").replace("dB", "").replace("  ", " ").split(" ")[:-1]
                        
            rippy_class.htoa_dict["gain"] = gain

        new_filename = rippy_class.HTOA_FILE_NAME_STR

        if rippy_class.SPECTRO_BOOL:
            spectro_command = (f'sox "HTOA.wav" -n spectrogram -t "{new_filename}" -o "track00.png"')
            subprocess.Popen(spectro_command, shell=True)

        htoa_flac = subprocess.Popen("flac -8 -V HTOA.wav", shell=True,encoding='utf8',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        htoa_flac.wait()
        os.remove("HTOA.wav")
        rippy_class.htoa_dict["flac_md5"] = hashlib.md5("HTOA.flac".encode('utf-8')).hexdigest()
        rippy_class.htoa_dict["flac_size"] = os.path.getsize("HTOA.flac")
        if rippy_class.ENABLE_TAGGING_BOOL:
            import taglib
            track_tag = taglib.File("HTOA.flac")
            track_tag.tags["ALBUM"] = rippy_class.ALBUM_STR
            track_tag.tags["TITLE"] = rippy_class.HTOA_TITLE_STR
            track_tag.tags["TRACKNUMBER"] = "00"
            track_tag.tags["ARTIST"] = rippy_class.ARTIST_STR
            track_tag.tags["COMMENT"] = rippy_class.COMMENT_STR
            track_tag.tags["GENRE"] = rippy_class.GENRE_STR
            track_tag.tags["YEAR"] = rippy_class.YEAR_STR
            track_tag.tags["DATE"] = rippy_class.YEAR_STR
            track_tag.save()
            rippy_class.htoa_dict["htoa_bitrate"] = str(track_tag.bitrate)


        os.rename("HTOA.flac", new_filename + ".flac")
        rippy_class.HTOA_RIPPED_BOOL = True


# Help function for reconstruct_track
def most_frequent(byte_list, rippy_class, reconstruction=False):
    """
    Returns the most frequent byte from the list of differing bytes.
    If no byte appears at least MATCHING_BYTES_INT times, returns None or behaves differently depending on mode.
    """

    counter = Counter(byte_list)
    most_common = counter.most_common()  # List of (byte, count) sorted by frequency

    if not most_common:
        return None  # Edge case: empty list

    # Check for reconstruction behavior
    if reconstruction:
        if rippy_class.DE_FACTO_LEVEL_STR in ["A", "C", "E"]:
            # If all bytes are equally frequent or the top two are tied
            if len(set(count for _, count in most_common)) == 1 or most_common[0][1] == most_common[1][1]:
                return byte_list[2] if len(byte_list) > 2 else byte_list[0]  # Return 3rd byte if exists
            else:
                return most_common[0][0]

        else:
            # For other levels, just return the most common if it meets the threshold
            if most_common[0][1] >= rippy_class.MATCHING_BYTES_INT:
                return most_common[0][0]
            else:
                message = f"Some tracks could not be matched according to your set amount of matching bytes ({rippy_class.MATCHING_BYTES_INT}), aborting."
                rippy_class.abort(message)
    else:
        # Not in reconstruction mode: return True/False depending on threshold
        if most_common[0][1] >= rippy_class.MATCHING_BYTES_INT:
            return True
        else:
            return False



#Finds differing bytes
def find_differing(filenames, rippy_class, finding_identical=False, current_rip=None):

    chunk_size = 1024 * 1024 // len(filenames)

    """
    Efficiently finds differing bytes across multiple files using NumPy.
    Reads files in chunks to improve performance without using mmap.
    """
    
    filenames = tuple(filenames)

    if not filenames:
        raise ValueError("Error: No input files provided!")

    if not all(os.path.exists(fn) for fn in filenames):
        missing = [fn for fn in filenames if not os.path.exists(fn)]
        raise FileNotFoundError(f"Error: Files not found: {', '.join(missing)}")

    file_handlers = [open(fn, 'rb') for fn in filenames if os.path.getsize(fn) > 0]

    if not file_handlers:
        raise ValueError("Error: All input files are empty!")

    total_size = os.path.getsize(filenames[0])

    position = 0


    try:
        import numpy as np
        got_numpy = True
    except:
        got_numpy = False



    if got_numpy:
        while True:
            # Read a chunk from each file
            chunks = [f.read(chunk_size) for f in file_handlers]

            # Stop when all files reach EOF
            if all(not chunk for chunk in chunks):
                break


            # Find the smallest chunk length to avoid index errors
            min_len = min(len(chunk) for chunk in chunks)
            buffers = [np.frombuffer(chunk[:min_len], dtype=np.uint8) for chunk in chunks]

            # NumPy-based fast comparison
            acc = np.zeros_like(buffers[0], dtype=bool)
            for a, b in zip(buffers, buffers[1:]):
                acc |= (a != b)

            # Store differing positions
            differing_indices = np.where(acc)[0]
            
            if finding_identical:
                if len(differing_indices) != 0:
                    print()
                    print(f"Track {current_rip} was not identical.\n")
                    return False


            # For each differing position, find the most frequent byte
            for i in differing_indices:
                differing_bytes = [buf[i] for buf in buffers]
                most_common_byte = most_frequent(differing_bytes, rippy_class)
                if not most_common_byte:
                    return False

            position += min_len  # Update file position
            progress_bar(position, total_size)


    else:
        while True:
            # Read a chunk from each file
            chunks = [f.read(chunk_size) for f in file_handlers]


            # Stop when all files reach EOF
            if all(not chunk for chunk in chunks):
                break

            # Find the smallest chunk length to avoid index errors
            min_len = min(len(chunk) for chunk in chunks)
            buffers = [chunk[:min_len] for chunk in chunks]


            differing_indices = rippy_shared_object.compare_buffers(buffers, min_len)
            if finding_identical:
                if differing_indices:
                    print()
                    print(f"Track {current_rip} was not identical.\n")
                    return False

            for i in differing_indices:
                differing_bytes = [buf[i] for buf in buffers]
                most_common_byte = most_frequent(differing_bytes, rippy_class)
                if not most_common_byte:
                    return False

            position += min_len  # Update file position
            progress_bar(position, total_size)
        
    # Close files
    for f in file_handlers:
        f.close()
    print("\n")
    return True
    



#Reconstructs track based on most common byte
def reconstruct_track(filenames, rippy_class, output_file):
    sector_set = rippy_class.test_dict[str(int(output_file.replace("track","").replace(".wav","")))]["sectors"]
    first_file = filenames[0]
    
    chunk_size = 1024 * 1024 // len(filenames)
    """
    Efficiently reconstructs the track by comparing files MB by MB and 
    directly writing the most frequent byte for each differing position.
    """
    if not filenames:
        raise ValueError("Error: No input files provided!")

    filenames = tuple(filenames)

    if not all(os.path.exists(fn) for fn in filenames):
        missing = [fn for fn in filenames if not os.path.exists(fn)]
        raise FileNotFoundError(f"Error: Files not found: {', '.join(missing)}")

    file_handlers = [open(fn, 'rb') for fn in filenames if os.path.getsize(fn) > 0]

    if not file_handlers:
        raise ValueError("Error: All input files are empty!")

    shutil.copy(first_file, output_file)  # Start with a copy of the first file
    
    total_size = os.path.getsize(filenames[0])

    position = 0
    total_fixed_bytes = 0
    diffy = {}

    try:
        import numpy as np
        got_numpy = True
    except:
        got_numpy = False

    got_numpy = False

    with open(output_file, "r+b") as new_file:
        position = 0

        if got_numpy:
            while True:
                # Read a chunk from each file
                chunks = [f.read(chunk_size) for f in file_handlers]

                # Stop when all files reach EOF
                if all(not chunk for chunk in chunks):
                    break


                # Find the smallest chunk length to avoid index errors
                min_len = min(len(chunk) for chunk in chunks)
                buffers = [np.frombuffer(chunk[:min_len], dtype=np.uint8) for chunk in chunks]

                # NumPy-based fast comparison
                acc = np.zeros_like(buffers[0], dtype=bool)
                for a, b in zip(buffers, buffers[1:]):
                    acc |= (a != b)

                # Store differing positions
                differing_indices = np.where(acc)[0]
                total_fixed_bytes += len(differing_indices)
                
                # For each differing position, find the most frequent byte
                for i in differing_indices:
                    differing_bytes = [buf[i] for buf in buffers]
                    most_common_byte = most_frequent(differing_bytes, rippy_class, reconstruction=True)

                    # Write the most common byte back to the output file
                    sector_set.add(int((position + i - 43) / 2352))
                    new_file.seek(position + i)
                    new_file.write(bytes([most_common_byte]))

                # Move the position pointer forward by the size of the smallest chunk
                position += min_len  # Update file position
                progress_bar(position, total_size)

        else:
            while True:
                # Read a chunk from each file
                chunks = [f.read(chunk_size) for f in file_handlers]


                # Stop when all files reach EOF
                if all(not chunk for chunk in chunks):
                    break

                # Find the smallest chunk length to avoid index errors
                min_len = min(len(chunk) for chunk in chunks)
                buffers = [chunk[:min_len] for chunk in chunks]


                differing_indices = rippy_shared_object.compare_buffers(buffers, min_len)
                total_fixed_bytes += len(differing_indices)
               

                # For each differing position, find the most frequent byte
                for i in differing_indices:
                    differing_bytes = [buf[i] for buf in buffers]
                    most_common_byte = most_frequent(differing_bytes, rippy_class, reconstruction=True)

                    sector_set.add(int((position + i - 43) / 2352))
                    new_file.seek(position + i)
                    new_file.write(bytes([most_common_byte]))
                    

                # Move the position pointer forward by the size of the smallest chunk
                position += min_len
                progress_bar(position, total_size)
    # Close all file handlers
    for f in file_handlers:
        f.close()
    print("\n")
    
    print(f"Reconstruction complete: {output_file}")
    print(f"Processed {position} bytes.\n")
    return total_fixed_bytes


# Function to display the progress bar
def progress_bar(position, total_size, bar_length=50):
    percent = f"{position} / {total_size} {((position / total_size) * 100):.0f}"
    filled_length = int(bar_length * position // total_size)
    bar = '=' * filled_length + ' ' * (bar_length - filled_length)
    sys.stdout.write(f'\r[{bar}] {percent}%')
    sys.stdout.flush()


