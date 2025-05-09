import wave
import hashlib
import subprocess
import os


def track_analysis(rippy_class, filenames=[], rip="000", message=0, ripping_now=None):

    if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.accuraterip_levels_list:
        import rippy_shared_object # .so-file for calculating AR checksums
        total_tracks = len(filenames)
        checksums = {}

        current_album = rippy_class.accuraterip_dict

        for track_number, filename in enumerate(filenames, start=1):
            with wave.open(filename, "rb") as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
            v1, v2 = rippy_shared_object.compute(frames, track_number, total_tracks)
            checksums[track_number] = {"v1": '%08X' % v1, "v2": '%08X' % v2}

        # Initialize a dictionary to hold v1 and v2 matches
        data = {}

        # Loop over checksums and check for matches in 
        for key, value in checksums.items():
            v1_key, v2_key = value['v1'], value['v2']
            # Store v1 checksum with or without match

            data[key] = {"v1": {}, "v2": {}}

            for sub_dict in current_album:
                for checksum in current_album[sub_dict]:
                    if v1_key == checksum:
                        if not sub_dict in data[key]["v1"]:
                            data[key]["v1"][sub_dict] = {}
                        data[key]["v1"][sub_dict] = current_album[sub_dict][v1_key]
                    if v2_key == checksum:
                        if not sub_dict in data[key]["v2"]:
                            data[key]["v2"][sub_dict] = {}
                        data[key]["v2"][sub_dict] = current_album[sub_dict][v2_key]

            # Store v2 checksum with or without match

        matches = {}


        for key, subdict in data.items():
            for v_key, match_dict in subdict.items():
                for match_num, value in match_dict.items():
                    if match_num not in matches:
                        matches[match_num] = {}
                    if v_key not in matches[match_num]:
                        matches[match_num][v_key] = {}
                    matches[match_num][v_key][key] = value

        matches = {k: matches[k] for k in sorted(matches.keys(), key=int)}

        # Initialize sets to collect unique matches for v1 and v2
        v1_matches = set()
        v2_matches = set()

        # Iterate through the dictionary to collect all matches
        for key, value in data.items():
            v1_matches.update(value['v1'].keys())  # Collect keys of v1
            v2_matches.update(value['v2'].keys())  # Collect keys of v2

        v1_matches = sorted(list(v1_matches))
        v2_matches = sorted(list(v2_matches))
        
        count_v2 = len(v2_matches)
        v1_or_v2 = "v2"        

        output_string = make_table(checksums, data, matches, v1_matches, v2_matches)

        print("\n".join(output_string))
        
        if count_v2 > 1:
            v2_strings = [str(v2) for v2 in v2_matches]
            which_ar = input(f"Which ARv2 version do you want to use? Alternatives: {', '.join(v2_strings)}. Write here: ").strip()
            while which_ar not in v2_strings:
                which_ar = input(f"Your answer must be among {', '.join(v2_strings)}. Write here: ")

        
        elif count_v2 < 1:
            if rippy_class.V1_BOOL:
                count_v1 = len(v1_matches)
                if count_v1 > 1:
                    v1_strings = [str(v1) for v1 in v1_matches]
                    which_ar = input(f"Which ARv1 version do you want to use? Alternatives: {', '.join(v1_strings)}. Write here: ").strip()
                    while which_ar not in v1_strings:
                        which_ar = input(f"Your answer must be among {', '.join(v1_strings)}. Write here: ")
                else:
                    v1_strings = [str(v1) for v1 in v1_matches]
                    which_ar = v1_strings[0]
            v1_or_v2 = "v1"  
        
        else:
            which_ar = v2_matches[0]

        which_ar = int(which_ar)

        rippy_class.V1_OR_V2_STR = v1_or_v2        

        track_numbers = list(range(1, rippy_class.TRACK_AMOUNT_INT + 1))

        in_ar = [str(key) for key in matches[str(which_ar)][v1_or_v2]]
        not_in_ar = [str(track) for track in track_numbers if str(track) not in in_ar]

        if message != "final":
            if rippy_class.VERBOSE_BOOL:
                output_string = "\n".join(output_string)
                rippy_class.verbose_list.append(f"Rip {message}\n\n{output_string}\n\n")
        else:
            output_string = "\n".join(output_string)
            rippy_class.FINAL_OUTPUT_STR = f"Final AccurateRip™ report:\n\n{output_string}\n\n"
            if "2" in rippy_class.tracks_ripped_dict:
                print(rippy_class.FINAL_OUTPUT_STR)

    if rippy_class.DE_FACTO_LEVEL_STR in ["E", "F", "H"]:
        in_ar, not_in_ar = [], []

    for i, track in enumerate(filenames, start=1):
        if rippy_class.DE_FACTO_LEVEL_STR in rippy_class.accuraterip_levels_list:
            if message != "final" and str(i) in in_ar and filenames[i-1] not in rippy_class.accurately_ripped_list:
                rippy_class.accurately_ripped_list.append(filenames[i-1])
            rippy_class.crc_v1_dict[str(message)].append(checksums[i]["v1"])
            rippy_class.crc_v2_dict[str(message)].append(checksums[i]["v2"])
            
            rippy_class.confidence_dict[str(message)].append(matches[str(which_ar)][v1_or_v2][i] if str(i) in in_ar else 0)
        if track in ripping_now:
            rippy_class.md5_list_dict[str(message)].append(hashlib.md5(track.encode('utf-8')).hexdigest())

            if rippy_class.GAIN_BOOL:
                gain = subprocess.Popen(
                    f"normalize-audio -n {track}", 
                    shell=True, encoding='utf8', stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                gain.wait()
                
                # Process and clean up gain output
                gain = gain.stdout.read()
                for white_space in range(3,6):
                    gain = gain.replace(" "*white_space, " ")
                gain = gain.replace("dBFS", "").replace("dB", "").replace("  ", " ").split(" ")[:-1]
                
                rippy_class.gain_list_dict[str(message)].append(gain)

    return in_ar, not_in_ar


        


def make_table(checksums, data, matches, v1_matches, v2_matches):

    """ Creates a table of AccurateRip™ results """

    header_title_str = "AccurateRip™ Checksums and Confidences"
    header_1 = "Track      ARv1         ARv2      "

    for i in v2_matches:
        header_1 += f"ARv2 ({i})   "

    for i in v1_matches:
        header_1 += f"ARv1 ({i})   "

    header_2 = " "*15 + "Checksums" + " "*6 + " "*int((((len(header_1) - 30)/2) - 5)) + "Confidences" + " "*int((((len(header_1) - 30)/2) - 5))

    header_line = "─"*len(header_1)

    header_title = " "*int((len(header_1)/2 - len(header_title_str)/2)) + header_title_str + " "*int((len(header_1)/2 - len(header_title_str)/2))
        
    complete_table = []  
    complete_table.append(header_title)
    complete_table.append(header_line)
    complete_table.append(header_2)
    complete_table.append(header_1)
    complete_table.append(header_line)

    for i in checksums:
        line_string = " "
        line_string += f"{i:2}" + " "*3
        line_string += " "*3 + checksums[i]["v1"] + " "*5
        line_string += checksums[i]["v2"] + " "*4

        for match in matches:
            for key in matches[match]:
                if key == "v2":
                    if i in matches[match]["v2"]:
                        line_string += " "*3 + f"{str(matches[match]['v2'][i]):2}" + " "*6
                    else:
                        line_string += " "*3 + f"{'-':2}" + " "*6

        for match in matches:
            for key in matches[match]:  
                if key == "v1":
                    if i in matches[match]["v1"]:
                        line_string += " "*3 + f"{str(matches[match]['v1'][i]):2}" + " "*6
                    else:
                        line_string += " "*3 + f"{'-':2}" + " "*6

        complete_table.append(line_string)

    complete_table.append(header_line)


    return complete_table
    
    

def rippy_track_verify(rippy_class):

    import urllib.request
    import struct

    all_track_begin_offsets = rippy_class.all_track_begin_offsets_list


    lead_out_offset = rippy_class.LEAD_OUT_OFFSET_INT

    fdid_str = rippy_class.FDID_STR

    accu_1 = sum(all_track_begin_offsets) + lead_out_offset
    accu_2 = (sum([n * max(o, 1) for (n, o) in zip(range(1,len(all_track_begin_offsets) + 1), all_track_begin_offsets)]) + (max(range(1,len(all_track_begin_offsets) + 1)) + 1) * lead_out_offset)

    accu_1 = f"{accu_1 & 0xffffffff:08x}"
    accu_2 = f"{accu_2 & 0xffffffff:08x}"


    accu_url = os.path.join("http://www.accuraterip.com:80", "accuraterip", f"{accu_1[-1]}", f"{accu_1[-2]}", f"{accu_1[-3]}", f"dBAR-{str(rippy_class.TRACK_AMOUNT_INT).zfill(3)}-{accu_1}-{accu_2}-{fdid_str}.bin")


    current_album = {}
    

    try:
        with urllib.request.urlopen(accu_url) as response:
            confidence_lists = response.read()
        
    except urllib.error.HTTPError as e:

        return current_album

    current_album_index = 1
    TRACK_AMOUNT_INT = rippy_class.TRACK_AMOUNT_INT

    while confidence_lists:

        current_bytes = 13 + TRACK_AMOUNT_INT * 9

        confidence_lists[:current_bytes]

        current_album[str(current_album_index)] = {}

        byte_offset = 13

        for track in range(TRACK_AMOUNT_INT):

            confidence = confidence_lists[byte_offset]

            checksum = "%08x" % struct.unpack("<L", confidence_lists[byte_offset + 1:byte_offset + 5])[0]

            current_album[str(current_album_index)][checksum.upper()] = confidence

            byte_offset += 9

        confidence_lists = confidence_lists[current_bytes:]

        current_album_index += 1

    return current_album

