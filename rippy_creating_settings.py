from rippy_help_functions import *
from textwrap import wrap as wp
import os
import subprocess

def true_false_verification(question):
    verification = False
    print(f"{question}")
    choice = ""
    while not verification:
        if choice.strip() not in ["False", "True"]:
            choice = input("Please answer True or False: ")
        else:
            verification = True
    return choice.strip()
        

# Function to handle loading and creating the settings file
def load_or_create_settings(rippy_class):

    try:
        from rippy_settings_file import offset_dict
    except ImportError:
        print()
        spaced_print("It doesn't seem like you have a settings file created. Let's create one! If you want to change settings, open the settings file in an editor and change values, or remove the rippy_settings_file.py and restart Rippy.py. If you've entered a value incorrectly, Rippy will exit and you will have to edit in rippy_settings_file.py or remove it and restart the Rippy.py script. At the end of the script you will get the chance to install all missing dependencies or you may manually install them after completing the script. \n\n")

        create_settings_file(rippy_class)


# Function to create the settings file when not found
def create_settings_file(rippy_class):
    with open("rippy_settings_file.py", "w") as file:
        file.write("# This is the Rippy CD ripping script's settings file.\n")
        file.write("# If you delete this file, it will have to be created again next time you run the Rippy.py script.\n\n")

        # Prompting for and writing the offset
        get_cd_offset(file, rippy_class, True)
        

        # Writing other settings
        missing_dependencies, missing_python_packages, rippy_shared_exist = write_settings(file, rippy_class)

    
    pkg_missing_str = pip_missing_str = ""
    pkg_install_str = pip_install_str = ""


    if missing_dependencies:
        pkg_missing_str = " and ".join(missing_dependencies) if len(missing_dependencies) < 3 else f'{", ".join(missing_dependencies[:-1])} and {missing_dependencies[-1]}'
        pkg_missing_str = f"{'these Linux packages' if len(missing_dependencies) > 1 else 'this Linux package'}: " + pkg_missing_str
        pkg_install_str = f"sudo apt update && sudo apt install {' '.join(missing_dependencies)}"

    if missing_python_packages:
        pip_missing_str = " and ".join(missing_python_packages) if len(missing_python_packages) < 3 else f'{", ".join(missing_python_packages[:-1])} and {missing_python_packages[-1]}'
        pip_missing_str = f"{'these Python packages' if len(missing_python_packages) > 1 else 'this Python package'}: " + pip_missing_str    
        pip_install_str = f"pip install {' '.join(missing_python_packages)} --break-system-packages"

    if missing_dependencies or missing_python_packages:
    
        collected_str = f"{pkg_missing_str}{' and ' if missing_dependencies and missing_python_packages else ''}{pip_missing_str}"
        install_str = f"{pkg_install_str}{' && ' if missing_dependencies and missing_python_packages else ''}{pip_install_str}"
        install_now = ""
        create_shared = ""
        if collected_str:
            install_now = special_input(f"You are missing {collected_str}. Please install (for example with '{install_str}' if you want them system wide, or use a virtual environment) and then run Rippy again. Do you wish to install them system wide now? Write y for yes and press enter, otherwise just press enter: ")
            print()
        if not rippy_shared_exist:
            create_shared = special_input(f"To build rippy_shared_object.so, write y for yes and press enter, otherwise just press enter: ")
            print()
        if install_now == "y" or create_shared == "y":
            if not check_internet_httplib():
                self.abort("Internet connection is needed to install these packages. Please make sure you're connected to the Internet and then try again.")
            else:
                if install_now == "y":
                    subprocess.run(f'{install_str}', shell=True)
                if create_shared == "y":
                    import shutil
                    import urllib.request
                    from setuptools import setup, Extension
                    from setuptools.command.build_ext import build_ext

                    # File to check
                    source_file = "rippy_shared_object.c"
                    download_url = "https://raw.githubusercontent.com/donlombardo/Rippy/main/rippy_shared_object.c"

                    # Check if the file exists, otherwise download it
                    if not os.path.exists(source_file):
                        print(f"{source_file} not found. Downloading from {download_url}...")
                        try:
                            urllib.request.urlretrieve(download_url, source_file)
                            print(f"Downloaded {source_file} successfully.")
                        except Exception as e:
                            print(f"Failed to download {source_file}: {e}")
                            exit(1)

                    # Define the extension module
                    module = Extension(
                        "rippy_shared_object",
                        sources=[source_file],
                        extra_compile_args=["-Wno-unused-result"]
                    )

                    # Custom build command to place .so file in the working directory
                    class BuildExtInPlace(build_ext):
                        def build_extension(self, ext):
                            super().build_extension(ext)
                            build_lib = self.build_lib
                    # Run setup
                    setup(
                        name="rippy_shared_object",
                        ext_modules=[module],
                        cmdclass={"build_ext": BuildExtInPlace},
                        script_args=["build_ext", "--inplace"],
                    )

                    # Clean up build directory
                    shutil.rmtree("build", ignore_errors=True)

                    # Import and use the compiled module
                    import rippy_shared_object
                    print("Successfully built and imported rippy_shared_object")
                print()
                rippy_class.abort("Rerun the Rippy script to continue.")

        else:
            rippy_class.abort("Aborting.")


# Function to get CD drive offset
def get_cd_offset(file, rippy_class, from_settings_creating):
    offset_string = "Do you know your CD drive's offset? If so, write your number, positive or negative. If you do not know it, check if your drive is listed in http://www.accuraterip.com/driveoffsets.htm. If it's not listed or marked as [Purged], unfortunately you have to find another way to determine it."
    offset_string_two = "Enter your offset number (remember the + or - before the number): "

    try:
        get_drive_offset(rippy_class)
        offset = special_input(f"{offset_string_two}").strip()

    except:
        offset = special_input(f"{offset_string}\n{offset_string_two}").strip()

    if from_settings_creating:
        file.write(f"# {offset_string}\n")
        file.write(f"# {offset_string_two}\n")


    if not offset:
        if from_settings_creating:
            os.remove("rippy_settings_file.py")
            rippy_class.abort("No settings file could be created, missing offset number. Rippy can not work without offset number. Exiting.")
        else:
            rippy_class.abort("Missing offset number. Rippy can not work without offset number. Exiting.")


    if from_settings_creating:
        offset_dict = {}
        offset_dict[f"{rippy_class.VENDOR_STR}, {rippy_class.MODEL_STR}"] = offset.strip()
        file.write(f"offset_dict = {str(offset_dict)}\n\n")


    else:
        with open("rippy_settings_file.py", "r") as settings_read:
            rippy_settings = [line.strip() for line in settings_read.readlines()]

        with open("rippy_settings_file.py", "w") as settings_write:
            for line in rippy_settings:
                if "offset_dict" in line:
                    import ast
                    offset_dict = ast.literal_eval(line.replace("offset_dict = ",""))
                    offset_dict[f"{rippy_class.VENDOR_STR}, {rippy_class.MODEL_STR}"] = offset.strip()
                    settings_write.write(f"offset_dict = {str(offset_dict)}\n")
                    
                else:
                    settings_write.write(f"{line}\n")

        return offset_dict

# Function to prompt and write general settings to the file
def write_settings(file, rippy_class):
    print("propan")
    output_list, level_list = print_ripping_modes_table()

    missing_dependencies = []
    missing_python_packages = []
    rippy_shared_exist = True

    for line in output_list:
        print(line)
        file.write(f"# {line}\n")

    for line in level_list:
        print(line)
        file.write(f"# {line}\n")

    level_str = f"How accurate do you want your ripping to be? Choose your level (A/B/C/D/E/F/G/H/I)"
    file.write(f"# {level_str}:\n")
    level = special_input(f"{level_str}:").strip()
    while level not in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
        level = input("Please answer a letter A-I: ")
    file.write(f"LEVEL_STR = '{level}'\n\n")
    print()

    
    use_v1_str = f"If you chose A, B, C, D, G or I, do you want to use Accurate Rip Checksum version 1, if version 2 is not in the Accurate Rip database? (True/False)"
    file.write(f"# {use_v1_str} Leave empty if you didn't choose A, B, C, D, G or I.\n")

    if level in ["A", "B", "C", "D", "G", "I"]:
        enable_v1 = true_false_verification(use_v1_str)
        file.write(f"V1_BOOL = {enable_v1}\n\n")
    else:
        file.write(f"V1_BOOL = False\n\n")
    print()    

    de_facto_level_str = f"If you chose A, B, C, D, G or I, which settings level do you want to fall back on if album not in the Accurate Rip database? Choose E, F or H: "
    file.write(f"# {de_facto_level_str} Leave empty if you didn't choose A, B, C, D, G or I.\n")

    if level in ["A", "B", "C", "D", "G", "I"]:
        spaced_print(de_facto_level_str)
        de_facto_level = ""
        while de_facto_level not in ["E", "F", "H"]:
            de_facto_level = input("Please choose E, F or H: ").strip()

        file.write(f"DE_FACTO_LEVEL_STR = '{de_facto_level}'\n\n")

        try:
            import rippy_shared_object

        except ImportError:
            rippy_shared_exist = False
            print()
            spaced_print("To use Accurate Rip and/or byte-for-byte comparison with Rippy, you need the rippy_shared_object.*.so file. This is available to download at Github or rippy.skatepunk.se for both 32 and 64 bit systems.\n"
                         "You can also build it yourself with the setup.py file in the root of the project, or in this script. You need the python package setuptools and the linux meta package build-essential (or gcc) and python3-dev to build it. ")

            result = subprocess.run("dpkg -l | grep build-essential", shell=True, stdout=subprocess.PIPE, text=True)

            if not result.stdout:
                result = subprocess.run("dpkg -l | gcc", shell=True, stdout=subprocess.PIPE, text=True)
                if not result.stdout:
                    missing_dependencies.append("build-essential")

            result = subprocess.run("dpkg -l | grep python3-dev", shell=True, stdout=subprocess.PIPE, text=True)

            if not result.stdout:
                missing_dependencies.append("python3-dev")

            try:
                import setuptools
            except ImportError:
                missing_python_packages.append("setuptools")

    else:
            file.write(f"DE_FACTO_LEVEL_STR = ''\n\n")
    print()


    tagging_string = f"Do you wish to use Rippy for tagging your files? (True/False). You need libtag1-dev and pytaglib. This also enables track bitrate information for the log."
    file.write(f"# {tagging_string}\n")
    enable_tagging = true_false_verification(tagging_string)
    file.write(f"ENABLE_TAGGING_BOOL = {enable_tagging}\n\n")
    print()    

    if enable_tagging == "True":
        enable_tagging = True

        result = subprocess.run("dpkg -l | grep libtag1-dev", shell=True, stdout=subprocess.PIPE, text=True)

        if not result.stdout:
            missing_dependencies.append("libtag1-dev")

        try:
            import taglib
        except ImportError:
            missing_python_packages.append("pytaglib")

    
    musicbrainz_string = f"Do you wish to use Musicbrainz for tagging? (True/False). Musicbrainz is an online music file tag database, that fetches tags from an ID read from the CD. For this you need the python package musicbrainzngs."
    file.write(f"# {musicbrainz_string}\n")


    if enable_tagging:
        musicbrainz_bool = true_false_verification(musicbrainz_string)
        file.write(f"MUSICBRAINZ_BOOL = {musicbrainz_bool}\n\n")
    else:
        file.write(f"MUSICBRAINZ_BOOL = False\n\n")
    print()

    if musicbrainz_bool == "True":
        try:
            import musicbrainzngs
        except ImportError:
            missing_python_packages.append("musicbrainzngs")

    discogs_token_string = f"If you want to use Discogs for tagging, enter Discogs API token or leave empty to not use Discogs. You need python package python3-discogs-client and a Discogs token from https://www.discogs.com/settings/developers."
    file.write(f"# {discogs_token_string}\n")
    discogs_token = ""

    if enable_tagging:
        discogs_token = special_input(f"{discogs_token_string} Enter token here: ")
    file.write(f"DISCOGS_TOKEN_STR = '{discogs_token}'\n\n")
    print()

    if discogs_token != "":
        try:
            import discogs_client
        except ImportError:
            missing_python_packages.append("python3-discogs-client")


    capitalize_str = f"Do you want to capitalize every word when receiving tag data from Musicbrainz or Discogs? (True/False)"
    file.write(f"# {capitalize_str}\n")
    if enable_tagging:
        capitalize_str = true_false_verification(capitalize_str)
        file.write(f"CAPITALIZE_BOOL = {capitalize_str}\n\n")
    else:
        file.write(f"CAPITALIZE_BOOL = False\n\n")
    print()
    
    
    character_string = 'Do you want to change folder and filenames for Linux file system compatibility? (True/False)'
    
    file.write(f"# {character_string}\n")
    linux_comp = true_false_verification(character_string)
    if linux_comp == "True":
        file.write(f"LINUX_BOOL = {linux_comp}\n\n")
    else:
        file.write(f"LINUX_BOOL = False\n\n")
    print()
    character_string = 'Do you want to change folder and filenames for Windows file system compatibility? (True/False)'
    
    file.write(f"# {character_string}\n")
    windows_comp = true_false_verification(character_string)

    if windows_comp == "True":
        file.write(f"WINDOWS_BOOL = {windows_comp}\n\n")
    else:
        file.write(f"WINDOWS_BOOL = False\n\n")   
    print()
    
    linux_dictionary = {'\\0': "0", '/': '-'}

    windows_dictionary = {'"': "''", '\\': '-', '/': '-', ':': '-', '*': 'x', '?': '', '<': '[', '>': ']',  '|': '!'} 
    
    default_dictionary = {'\\0': "0", '/': '-', '"': "''", '\\': '-', ':': '-',  '*': 'x', '?': '', '<': '[', '>': ']', '|': '!'} 
    
    custom_dictionary = {}
    
    file.write(f"linux_dictionary = {str(linux_dictionary)}\n")     
    file.write(f"windows_dictionary = {str(linux_dictionary)}\n")     
    file.write(f"default_dictionary = {str(default_dictionary)}\n")


    if linux_comp == "True":
        custom_dictionary.update(linux_dictionary)
            
    if windows_comp == "True":
        custom_dictionary.update(windows_dictionary)
 

    if linux_comp == "True" or windows_comp == "True":
        for key in custom_dictionary:
            char_value = input(f"Default replacement character for {key} is {custom_dictionary[key]}. If you want to change it, write your non-illegal character here, otherwise just press enter: ")
            if char_value == "":
                continue
            while char_value not in custom_dictionary:
                char_value = special_input("Write a valid non-illegal character here: ").strip()       
                custom_dictionary[key] == char_value

    file.write(f"custom_dictionary = {str(custom_dictionary)}\n\n")                

    apostrophe_string = f"Do you want to correct faulty apostrophes (` or ´ used as ')? (True/False)"
    file.write(f"# {apostrophe_string}\n")
    if enable_tagging == "True":
        apostrophe = true_false_verification(apostrophe_string)
        file.write(f"APOSTROPHE_BOOL = {apostrophe}\n\n")
    else:
        file.write(f"APOSTROPHE_BOOL = False\n\n")
    print()

    eject_string = f"Do you want to eject your CD drive after ripping? (True/False)"
    file.write(f"# {eject_string}\n")
    eject = true_false_verification(eject_string)
    file.write(f"EJECT_BOOL = {eject}\n\n")
    print()

    speed_string = f"If your CD drive can change read speed, and you want to change read speed, write your speed here (whole number)"
    file.write(f"# {speed_string} or leave empty ('') for default speed.\n")
    speed = special_input(f"{speed_string} or press enter to use default speed: ")
    file.write(f"SPEED_STR = '{speed}'\n\n" if speed else "SPEED_STR = ''\n\n")
    print()
    
    log_string = f"Do you want a log with information about your rip? (True/False)"
    file.write(f"# {log_string}\n")
    log = true_false_verification(log_string)
    file.write(f"LOG_BOOL = {log}\n\n")
    print()

    gain_string = "Do you want track gain information in your log? (True/False). If so, you need normalize, a linux software package."
    file.write(f"# {gain_string}\n")
    if log == "True":

        gain = true_false_verification(gain_string)
        if gain == "True":
            file.write(f"GAIN_BOOL = {gain}\n\n")
            print()
            result = subprocess.run("dpkg -l | grep normalize-audio", shell=True, stdout=subprocess.PIPE, text=True)

            if not result.stdout:
                missing_dependencies.append("normalize-audio")
    else:
        file.write(f"GAIN_BOOL = False\n\n")

    cue_string = f"Do you want a cue sheet with information about your rip? You need linux package cdrdao for this. (True/False)"
    file.write(f"# {cue_string}\n")
    cue = true_false_verification(cue_string)
    file.write(f"CUE_BOOL = {cue}\n\n")
    print()

    if cue == "True":
        result = subprocess.run("dpkg -l | cdrdao", shell=True, stderr=subprocess.PIPE, text=True)

        if "show-data" not in result.stderr:
            if "cdrdao" not in missing_dependencies:
                missing_dependencies.append("cdrdao")

    verbose_log_string = f"Do you want a separate, extra verbose, log for the ripping process that documents every rip and fault sectors? You need linux package cdrdao for this. (True/False)"
    file.write(f"# {verbose_log_string}\n")
    verbose_log = true_false_verification(verbose_log_string)
    file.write(f"VERBOSE_BOOL = {verbose_log}\n\n")
    print()

    bonus_log_string = f"Do you want a log with information about your CD drive? (True/False)"
    file.write(f"# {bonus_log_string}\n")
    bonus_log = true_false_verification(bonus_log_string)
    file.write(f"BONUS_BOOL = {bonus_log}\n\n")
    print()

    test_drive_string = f"Do you want to test your CD drive function every time before ripping? Test takes about 15-30 seconds (True/False)"
    file.write(f"# {test_drive_string}\n")
    test_drive = true_false_verification(test_drive_string)
    file.write(f"TEST_DRIVE_BOOL = {test_drive}\n\n")
    print()

    if test_drive == "True":
        result = subprocess.run("dpkg -l | cdrdao", shell=True, stderr=subprocess.PIPE, text=True)

        if "show-data" not in result.stderr:
            if "cdrdao" not in missing_dependencies:
                missing_dependencies.append("cdrdao")


    spectro_string = f"Create spectrogram images for all files? (True/False) For this you need linux package sox and python package pillow."
    file.write(f"# {spectro_string}\n")
    spectro = true_false_verification(spectro_string)
    file.write(f"SPECTRO_BOOL = {spectro}\n\n")
    print()

    if spectro == "True":
        enable_tagging = True

        result = subprocess.run("dpkg -l | grep 'Swiss army knife of sound processing'", shell=True, stdout=subprocess.PIPE, text=True)

        if not result.stdout:
            missing_dependencies.append("sox")

        try:
            import PIL
        except ImportError:
            missing_python_packages.append("pillow")


    retry_string = f"What's the maximum number of times to retry each track (minimum 2, some levels override this)? Write your number:"
    file.write(f"# {retry_string}\n")

    while True:
        try:
            retry = int(special_input(f"{retry_string}"))
            if retry >= 2:
                break
            else:
                print("Please enter an integer that is 2 or more.")
        except ValueError:
            print("Please enter a valid number.")

    file.write(f"RETRY_INT = {retry}\n\n")
    print()

    error_correction_string = f"Enable cdparanoia's built-in error correction? If yes, choose the number of retries cdparanoia does per sector (default is 20) (False/Number of retries):"
    file.write(f"# {error_correction_string}\n")

    while True:
        error_correction = special_input(f"{error_correction_string}").strip()

        if error_correction.lower() == "false":  
            break  # Accept "False" as a valid input
        try:
            error_correction = int(error_correction)
            if error_correction >= 1:  # Ensure at least 1 retry if a number is chosen
                error_correction = str(error_correction)
                break
            else:
                print("Please enter a number of retries that is 1 or more, or type 'False'.")
        except ValueError:
            print("Invalid input. Please enter 'False' or a valid number.")

    if error_correction.lower() == "false":
        file.write(f"ERROR_CORRECTION_STR = False\n\n")
    else:
        file.write(f"ERROR_CORRECTION_STR = '{error_correction}'\n\n")
    print()

    byte_corr_string = f"For test and copy, how many times (2 or more) should each byte match when doing byte-for-byte comparison? Must be less or equal to your number of retries. Write your number:"
    file.write(f"# {byte_corr_string}\n")

    while True:
        try:
            byte_corr = int(special_input(f"{byte_corr_string}"))
            if byte_corr >= 2 and byte_corr <= int(retry):
                break
            else:
                print("Please enter a number that is 2 or more, and equal or bigger than number of retries.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    file.write(f"MATCHING_BYTES_INT = {byte_corr}\n\n")
    print()

    htoa_string = f"Rip Hidden Track One Audio (HTOA) if present? Only certain CD drives can do this. (True/False)"
    file.write(f"# {htoa_string}\n")
    htoa = true_false_verification(htoa_string)
    file.write(f"HTOA_BOOL = {htoa}\n\n")
    print()

    save_path_string = f"Enter path to save ripped CDs:"
    file.write(f"# {save_path_string}\n")
    
    from pathlib import Path
    while True:
        save_path = special_input(f"{save_path_string}").strip()
        
        # Check if the path is absolute and doesn't contain invalid characters
        if save_path and save_path.startswith("/") and not any(c in save_path for c in ['\0']):  
            try:
                resolved_path = Path(save_path).resolve(strict=False)  # Normalize path
                resolved_path.mkdir(parents=True, exist_ok=True)  # Create directory if needed
                break  # Valid path, exit loop
            except Exception as e:
                print(f"Error creating directory: {e}")
        else:
            print("Invalid input. Please enter a valid absolute Linux path (starting with '/').")
    file.write(f"SAVE_PATH = '{save_path}'\n\n")
    print()


    folder_standard_list = [
        "What folder name standard do you want to use? You can choose from:",
        "{artist} = Artist name",
        "{year} = Album release year",
        "{album} = Album name",
        "{comment} = Comment tag",
        "{genre} = Album genre",
        "Or choose your own custom text.",
        "Example: {artist} - {year} - {album} (FLAC) will result in 'Artist - Year - Album (FLAC)'.",
    ]

    for line in folder_standard_list:
        file.write(f"# {line}\n")
        print(line)

    folder_standard = special_input(f"Write your standard: ")
    file.write(f"# Write your standard after 'FOLDER_STANDARD_F_STR = ':\nFOLDER_STANDARD_F_STR = '{folder_standard}'\n\n")
    print()


    various_folder_standard_list = [
        "What folder name standard do you want to use? You can choose from:",
        "{artist} = Artist name",
        "{year} = Album release year",
        "{album} = Album name",
        "{comment} = Comment tag",
        "{genre} = Album genre",
        "Or choose your own custom text.",
        "Example: Various Artists - {year} - {album} (FLAC) will result in 'Various Artists - Year - Album (FLAC)'.",
    ]

    for line in various_folder_standard_list:
        file.write(f"# {line}\n")
        print(line)

    various_folder_standard = special_input(f"Write your standard: ")
    file.write(f"# Write your standard after 'VARIOUS_FOLDER_STANDARD_F_STR = ':\nVARIOUS_FOLDER_STANDARD_F_STR = '{various_folder_standard}'\n\n")
    print()


    # FLAC file naming standard for single artist albums

    file_name_standard_list = [
        "What FLAC file name standard do you want to use? You can choose from:",
        "{artist} = Artist name",
        "{year} = Album release year",
        "{album} = Album name",
        "{track_number} = Track number",
        "{title} = Track title",
        "{genre} = Genre",
        "{comment} = Tag comment",
        "Or choose your own custom text.",
        "Example: {artist} - {track_number} - {title} will result in 'Artist - Track Number - Title.flac'.",
        
    ]

    for line in file_name_standard_list:
        file.write(f"# {line}\n")
        print(line)
    file_name_standard = special_input(f"Write your standard: ")
    file.write(f"# Write your standard after 'FILE_NAME_STANDARD_F_STR = ':\nFILE_NAME_STANDARD_F_STR = '{file_name_standard}'\n\n")
    print()



    # FLAC file naming standard for various artists albums

    various_file_name_standard_list = [
        "What FLAC file name standard do you want to use for Various Artists albums? You can choose from:",
        "{artist} = Artist name",
        "{year} = Album release year",
        "{album} = Album name",
        "{track_number} = Track number",
        "{title} = Track title",
        "{genre} = Genre",
        "{comment} = Tag comment",
        "Or choose your own custom text.",
        "Example: {track_number} - {artist} - {title} will result in 'Track Number - Artist - Title.flac'.",
        
    ]

    for line in various_file_name_standard_list:
        file.write(f"# {line}\n")
        print(line)
    various_file_name_standard = special_input(f"Write your standard: ")
    file.write(f"# Write your standard after 'VARIOUS_FILE_NAME_STANDARD_F_STR = ':\nVARIOUS_FILE_NAME_STANDARD_F_STR = '{various_file_name_standard}'\n\n")
    print()
    
    spaced_print("This concludes your settings file creation. If you wish to redo your settings, just delete rippy_settings_file.py and restart Rippy. Else, you can open rippy_settings_file.py and edit settings, but make sure to read through all settings and set valid choices, otherwise Rippy will break. Deleting the file and redoing it is the safest way to make new settings.")
    
    return missing_dependencies, missing_python_packages, rippy_shared_exist



# Function to print the ripping modes table
def print_ripping_modes_table():
    level_list = [
        "These are the ripping levels of Rippy. Please choose one.",
        "A: Rip once and check with AccurateRip™. If it matches, proceed to FLAC encoding. If it doesn't match, rip again. Check with AccurateRip™ after each time and proceed if match is found. Repeat this up to your set amount of times. If no AccurateRip™ match is found in the end, choose the most common byte sequence or pick the one from the third rip if none is more common. Always complete the process unless cdparanoia gets stuck.",
        "B: Rip once and check with AccurateRip™. If it matches, proceed to FLAC encoding. If it doesn't match, rip again. Check with AccurateRip™ after each time and proceed if match is found. Repeat this up to your set amount of times. If no AccurateRip™ match is found in the end, choose the most common byte sequence only if at least your set amount (MATCHING_BYTES_INT) of matching bytes exist. Otherwise, abort.",
        "C: Always rip at least twice (test and copy), up to your set amount of times. Check AccurateRip™ for information, but it is not decisive. At the end, select the most common byte sequence or pick the one from the third rip if none is more common. Always complete the process unless cdparanoia gets stuck.",
        "D: Always rip at least twice (test and copy), up to your set amount of times. Check AccurateRip™ for information, but it is not decisive. At the end, select the most common byte sequence only if at least your set amount (MATCHING_BYTES_INT) of matching bytes exist. Otherwise, abort.",
        "E: Always rip at least twice (test and copy), up to your set amount of times. Do not check AccurateRip™. At the end, select the most common byte sequence or pick the one from the third rip if none is more common. Always complete the process unless cdparanoia gets stuck.",
        "F: Always rip at least twice (test and copy), up to your set amount of times. Do not check AccurateRip™. At the end, select the most common byte sequence only if at least your set amount (MATCHING_BYTES_INT) of matching bytes exist. Otherwise, abort.",
        "G: Rip only once. Check with AccurateRip™. If it matches, proceed; otherwise, abort immediately (overrides your set amount of times).",
        "H: Rip only once. Do not check AccurateRip™. Proceed directly to FLAC encoding (for extremely difficult-to-read discs). (Overrides your set amount of times).",
        "I: Rip only once. Check AccurateRip™ for information only, then proceed directly to FLAC encoding (for extremely difficult-to-read discs, overrides your set amount of times).",
    ]

    print("Table of level settings. Table shown best in full-screen terminal.\n")
    
    table_list = [
        ["ID", "Ripping Attempts", "AccurateRip™", "Decision on Mismatch", "Always Finish", "Comments"],
        ["A", "Min 1, up to limit", "Yes (critical)", "Retry, choose most common or from third rip", "Yes (unless stuck)", "Tries for match, always finishes"],
        ["B", "Min 1, up to limit", "Yes (critical)", "Retry, choose most common by set amount, else abort", "No", "Similar to A, but aborts if uncertain"],
        ["C", "Min 2, up to limit", "Yes (info only)", "Choose most common or from third rip", "Yes (unless stuck)", "AccurateRip™ is informational only"],
        ["D", "Min 2, up to limit", "Yes (info only)", "Choose most common by set amount, else abort", "No", "Similar to C, but aborts if uncertain"],
        ["E", "Min 2, up to limit", "No", "Choose most common or third rip", "Yes (unless stuck)", "Ignores AccurateRip™ entirely"],
        ["F", "Min 2, up to limit", "No", "Choose most common by set amount, else abort", "No", "Similar to E, but aborts if uncertain"],
        ["G", "Exactly 1", "Yes (critical)", "Abort if no match", "No", "Overrides set amount of times"],
        ["H", "Exactly 1", "No", "Proceed immediately", "Yes", "For difficult-to-read discs"],
        ["I", "Exactly 1", "Yes (info only)", "Proceed immediately", "Yes", "Similar to H, but logs AccurateRip™ info"]
    ]

    # Calculate column widths
    col_widths = [max(len(str(row[i])) for row in table_list) for i in range(len(table_list[0]))]

    def format_row(row, separator=" | "):
        return separator.join(f" {str(item).ljust(col_widths[i])} " for i, item in enumerate(row))

    # Initialize output as a list
    output_list = []

    # Top border
    output_list.append("-" * (sum(col_widths) + len(col_widths) * 3 + 1))

    # Header
    output_list.append(format_row(table_list[0]))

    # Border after header
    output_list.append("-" * (sum(col_widths) + len(col_widths) * 3 + 1))

    # Add table rows
    for row in table_list[1:]:
        output_list.append(format_row(row))

    # Bottom border
    output_list.append("-" * (sum(col_widths) + len(col_widths) * 3 + 1))

    return output_list, level_list

# Function to scrape and suggest CD offset


def get_drive_offset(rippy_class):
    import urllib.request
    import html.parser

    class MyHTMLParser(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_table = False
            self.in_td = False
            self.rows = []
            self.current_row = []
        
        def handle_starttag(self, tag, attrs):
            if tag == "table":
                self.in_table = True
            elif tag == "tr" and self.in_table:
                self.current_row = []
            elif tag == "td" and self.in_table:
                self.in_td = True
        
        def handle_endtag(self, tag):
            if tag == "table":
                self.in_table = False
            elif tag == "tr" and self.in_table:
                if self.current_row:
                    self.rows.append(self.current_row)
            elif tag == "td" and self.in_table:
                self.in_td = False
        
        def handle_data(self, data):
            if self.in_td:
                self.current_row.append(data.strip())

    url = 'http://www.accuraterip.com/driveoffsets.htm'
    offset_list = []

    try:

        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
        
        table_html = '<table>' + html.split('<table border="0" width="100%">')[-1].split('<p align="right">')[0]

        parser = MyHTMLParser()
        parser.feed(table_html)

        for row in parser.rows:
            if row and rippy_class.VENDOR_STR.strip() in row[0] and rippy_class.MODEL_STR in row[0]:
                offset_list.append(row[1])

    except:
        pass

    if not offset_list:
        spaced_print(f"No offset could be found programmatically. Please check {url} or try to find the offset somewhere else.")
    else:
        offset_list = sorted(set(offset_list))
        if len(offset_list) == 1:
            spaced_print(f"According to {url}, your drive offset might be {offset_list[0]}. This is only a suggestion. If it doesn't work, check the website yourself or try to find the offset somewhere else.")
        elif len(offset_list) == 2:
            spaced_print(f"According to {url}, your drive offset might be {' or '.join(offset_list)}. These are only suggestions. If it doesn't work, check the website yourself or try to find the offset somewhere else.")
        else:
            spaced_print(f"According to {url}, your drive offset might be {', '.join(offset_list[:-1])} or {offset_list[-1]}. These are only suggestions. If it doesn't work, check the website yourself or try to find the offset somewhere else.")

