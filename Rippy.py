#Rippy V1.3 from 
#Todo nu:
#Testa alla versioner

#Senare:
#Fix a gui for inputting album info manually, with Tkinter


import os
import subprocess
import time
import datetime
import json
import uuid
import sys
from rippy_help_functions import *
from rippy_creating_settings import *


class RippyClass:
    def __init__(self):
        self.tracks_ripped_dict = {}
        self.md5_list_dict = {}
        self.htoa_dict = {}
        self.confidence_dict = {}
        self.crc_v1_dict = {}
        self.crc_v2_dict = {}
        self.gain_list_dict = {}
        self.test_dict = {}
        self.sector_set_dict = {}
        self.bonus_log_dict = {}
        self.accuraterip_dict = {}
        self.needed_correction_list = []
        self.identical_list = []
        self.verbose_list = []
        self.accurately_ripped_list = []
        self.track_length_list = []
        self.all_track_begin_offsets_list = []
        self.track_list = []
        self.various_list = []
        self.bitrate_list = []
        self.wav_size_list = []
        self.flac_size_list = []
        self.pre_emphasis_list = []
        self.counted_list = []
        self.pre_gap_list = [] 
        self.file_name_list = []
        self.accuraterip_levels_list = ["A", "B", "C", "D", "G", "I"]
        self.more_than_once_list = ["A", "B", "C", "D", "E", "F"]
        self.FINAL_OUTPUT_STR = ""
        self.FOLDER_STR = ""
        self.HTOA_FILE_NAME_STR = ""
        self.VENDOR_STR = ""
        self.MODEL_STR = ""
        self.REVISION_STR = ""
        self.TEMP_STR = ""
        self.OFFSET_STR = ""
        self.OFFSET_STR_LOG = ""
        self.DRIVE_STR = ""
        self.CHOSEN_DRIVE_STR = ""
        self.TOC_READ_STR = ""
        self.LAST_LENGTH_STR = ""
        self.LAST_SECTOR_STR = ""
        self.HTOA_LAST_SECTOR_STR = ""
        self.HTOA_TITLE_STR = ""
        self.FDID_STR = ""
        self.MBID_STR = ""
        self.ALBUM_STR = ""
        self.ARTIST_STR = ""
        self.YEAR_STR = ""
        self.GENRE_STR = ""
        self.COMMENT_STR = ""
        self.CDDA_STR = ""
        self.USED_DRIVE_STR = ""
        self.now_str = ""
        self.V1_OR_V2_STR = ""
        self.TRACK_AMOUNT_INT = 0
        self.LEAD_OUT_OFFSET_INT = 0 
        self.ERRONOUS_BOOL = False
        self.HTOA_EXIST_BOOL = False
        self.HTOA_RIPPED_BOOL = False
        self.RIPPY_VERSION_STR = "1.3"
        self.VERSION_DATE_STR = "March 3rd 2025"
        self.APOSTROPHE_BOOL = None
        self.BONUS_BOOL = None
        self.CAPITALIZE_BOOL = None
        self.CUE_BOOL = None
        self.DE_FACTO_LEVEL_STR = ""
        self.DISCOGS_TOKEN_STR = None
        self.EJECT_BOOL = None
        self.ENABLE_TAGGING_BOOL = None
        self.ERROR_CORRECTION_STR = ""
        self.FILE_NAME_STANDARD_F_STR = None
        self.FOLDER_STANDARD_F_STR = None
        self.GAIN_BOOL = None
        self.HTOA_BOOL = None
        self.LEVEL_STR = None
        self.LINUX_BOOL = None
        self.LOG_BOOL = None
        self.MATCHING_BYTES_INT = None
        self.MUSICBRAINZ_BOOL = None
        self.RETRY_INT = None
        self.SAVE_PATH = None
        self.SPEED_STR = ""
        self.SPECTRO_BOOL = None
        self.TEST_DRIVE_BOOL = None
        self.V1_BOOL = None
        self.VARIOUS_FILE_NAME_STANDARD_F_STR = None
        self.VARIOUS_FOLDER_STANDARD_F_STR = None
        self.VERBOSE_BOOL = None
        self.WINDOWS_BOOL = None

        self.dicts_list = [
            self.tracks_ripped_dict,
            self.md5_list_dict,
            self.confidence_dict,
            self.crc_v1_dict,
            self.crc_v2_dict,
            self.gain_list_dict
        ]


    def abort(self, message=""):
        import shutil

        spaced_print(message)
        if "The ripping process has finished" not in message:        
            if self.TEMP_STR != "" and self.TEMP_STR in os.getcwd():

                os.chdir("..")
                shutil.rmtree(self.TEMP_STR)

        try:
            os.remove(f"temp_data_{self.TEMP_STR}.py")
        except:
            pass

        #time.sleep(5)
        sys.exit()

    def update_dicts(self, suffix):
        for dict_obj in self.dicts_list:
            key_name = str(suffix)
            dict_obj[key_name] = []

    def check_if_disc(self):

        """
        Testing to see if a CD drive with a CD in it is connected to your computer and at the same time 
        getting amounts of tracks of the CD. Rippy quits after 20 seconds if there is no CD
        """

        print("Rippy will now try to read your CD. If it doesn't find one, it will exit.")

        import shutil


        # Check if cdparanoia is installed
        missing_dependencies = []


        if not shutil.which("cdparanoia"):
            missing_dependencies.append("cdparanoia")

        if not shutil.which("cd-drive"):
            missing_dependencies.append("libcdio-utils")

        if not shutil.which("flac"):
            missing_dependencies.append("flac")



        if missing_dependencies:
            install_str = " ".join(missing_dependencies)
            missing_str = " and ".join(missing_dependencies) if len(missing_dependencies) < 3 else f'{", ".join(missing_dependencies[:2])} and {missing_dependencies[2]}'
            input_str = f"Error: {missing_str} not installed. Please install (sudo apt install {install_str}) and try again. Do you wish to install now? Write y for yes and press enter, otherwise just press enter."
            print()
            install_now = special_input(input_str)

            if install_now == "y":
                if not check_internet_httplib():
                    message = "Internet connection is needed to install these packages. Please make sure you're connected to the Internet and then try again.\n"
                    self.abort(message)
                else:
                    subprocess.run(f'sudo apt install {install_str}', shell=True)
            else:
                self.abort()

        for i in range(21):
            def detect_sr_devices():
                sr_devices = [f"/dev/{dev}" for dev in os.listdir("/dev") if dev.startswith("sr")]
                return sr_devices

            def select_sr_device():
                sr_devices = sorted(detect_sr_devices())

                if not sr_devices:
                    print("No optical drives found.")
                    self.abort()
                    return None

                if len(sr_devices) == 1:
                    return f"{sr_devices[0]}"

                print("Multiple optical drives found:")
                for i, dev in enumerate(sr_devices):
                    print(f"{i}. {dev}")

                while True:
                    try:
                        choice = int(input("Select a device by number: "))
                        if 0 <= choice <= len(sr_devices):
                            return f"{sr_devices[choice]}"
                        else:
                            print("Invalid selection. Try again.")
                    except ValueError:
                        print("Please enter a valid number.")

            # Example usage
            self.CHOSEN_DRIVE_STR = select_sr_device()
            cdparanoia_option = f"-d {self.CHOSEN_DRIVE_STR}"

            result = subprocess.run(
                f'cdparanoia {cdparanoia_option} -sQ 2>&1 | grep -P "^\\s+\\d+\\." | wc -l', 
                shell=True, capture_output=True, text=True
            )

            self.TRACK_AMOUNT_INT = int(result.stdout.strip() or 0)

            if self.TRACK_AMOUNT_INT:
                break
            if i == 20:
                message = "No disc in the CD drive, put a CD in or try again later."
                self.abort(message)

            time.sleep(1)


    def drive_info(self):

        """ Getting and printing CD drive information """

        cd_drive_command = f"cd-drive --cdrom-device={self.CHOSEN_DRIVE_STR}"
        cd_drive_info = subprocess.run(cd_drive_command, shell=True, capture_output=True, text=True).stdout.split("\n")

        for line in cd_drive_info:
            if line.startswith("Vendor"):
                self.VENDOR_STR = line.split(":")[1].strip()
            elif line.startswith("Model"):
                self.MODEL_STR = line.split(":")[1].strip()
            elif line.startswith("Revision"):
                self.REVISION_STR = line.split(":")[1].strip()

        
        self.USED_DRIVE_STR = f"{self.VENDOR_STR}, {self.MODEL_STR} {self.REVISION_STR}".strip(", ")
        
        return cd_drive_info


    def drive_settings(self):

        """ Loading settings """


        try:

            load_or_create_settings(self)
            import importlib
            module = importlib.import_module("rippy_settings_file")
            for name in dir(module):
                if not name.startswith("__"):
                    setattr(self, name, getattr(module, name))
            
            if f"{self.VENDOR_STR}, {self.MODEL_STR}" not in self.offset_dict:
                
                get_cd_offset(None, self, False)  

                importlib.reload(module)
                for name in dir(module):
                    if not name.startswith("__"):
                        setattr(self, name, getattr(module, name))
                
        except SystemExit:
            raise

        except Exception as e:
            load_or_create_settings(self)
            import importlib
            module = importlib.import_module("rippy_settings_file")
            for name in dir(module):
                if not name.startswith("__"):
                    setattr(self, name, getattr(module, name))


        self.OFFSET_STR_LOG = self.offset_dict[f"{self.VENDOR_STR}, {self.MODEL_STR}"]


        ALLOWED_OVERRIDES = {
            "APOSTROPHE_BOOL": {"type": bool, "allowed": [True, False]},
            "BONUS_BOOL": {"type": bool, "allowed": [True, False]},
            "CAPITALIZE_BOOL": {"type": bool, "allowed": [True, False]},
            "CUE_BOOL": {"type": bool, "allowed": [True, False]},
            "DE_FACTO_LEVEL_STR": {"type": str, "allowed": ["E", "F", "G", "H"]},
            "DISCOGS_TOKEN_STR": {"type": str},
            "EJECT_BOOL": {"type": bool, "allowed": [True, False]},
            "ENABLE_TAGGING_BOOL": {"type": bool, "allowed": [True, False]},
            "ERROR_CORRECTION_STR": {"type": str},
            "FILE_NAME_STANDARD_F_STR": {"type": str},
            "FOLDER_STANDARD_F_STR": {"type": str},
            "GAIN_BOOL": {"type": bool, "allowed": [True, False]},
            "HTOA_BOOL": {"type": bool, "allowed": [True, False]},
            "LEVEL_STR": {"type": str, "allowed": ["A", "B", "C", "D", "E", "F", "G", "H", "I"]},
            "LINUX_BOOL": {"type": bool, "allowed": [True, False]},
            "LOG_BOOL": {"type": bool, "allowed": [True, False]},
            "MATCHING_BYTES_INT": {"type": int, "allowed": list(range(2, 33))},
            "MUSICBRAINZ_BOOL": {"type": bool, "allowed": [True, False]},
            "RETRY_INT": {"type": int, "allowed": list(range(2, 33))},
            "SAVE_PATH": {"type": str},
            "SPEED_STR": {"type": str},
            "SPECTRO_BOOL": {"type": bool, "allowed": [True, False]},
            "TEST_DRIVE_BOOL": {"type": bool, "allowed": [True, False]},
            "V1_BOOL": {"type": bool, "allowed": [True, False]},
            "VARIOUS_FILE_NAME_STANDARD_F_STR": {"type": str},
            "VARIOUS_FOLDER_STANDARD_F_STR": {"type": str},
            "VERBOSE_BOOL": {"type": bool, "allowed": [True, False]},
            "WINDOWS_BOOL": {"type": bool, "allowed": [True, False]},
        }

        

        def str_to_type(value, typ):
            if typ is bool:
                if value.lower() in ('true', '1'):
                    return True
                elif value.lower() in ('false', '0'):
                    return False
                else:
                    raise ValueError("Invalid boolean")
            elif typ is int:
                return int(value)
            elif typ is str:
                return value
            else:
                raise ValueError("Unsupported type")


        def apply_overrides_from_argv(argv, instance):
            updates = {}

            for arg in argv:
                if not arg.startswith("--") or "=" not in arg:
                    continue

                key_val = arg[2:].split("=", 1)
                if len(key_val) != 2:
                    continue

                key, val_str = key_val
                if key not in ALLOWED_OVERRIDES:
                    continue

                spec = ALLOWED_OVERRIDES[key]
                try:
                    val = str_to_type(val_str, spec["type"])
                except Exception:
                    continue

                if "allowed" in spec and val not in spec["allowed"]:
                    continue

                updates[key] = val

            for k, v in updates.items():
                print(f"Setting {k} = {v}")
                setattr(instance, k, v)


        apply_overrides_from_argv(sys.argv[1:], self)


        self.make_correct_var(self.OFFSET_STR_LOG, self.SPEED_STR, self.CHOSEN_DRIVE_STR, self.ERROR_CORRECTION_STR)

        """ Checks if your set amount of matching bytes is larger than retries """

        if self.MATCHING_BYTES_INT > self.RETRY_INT:
            message = (f"Amount of matching bytes (MATCHING_BYTES_INT = {MATCHING_BYTES_INT} now) "
                           "must be less or equal to the amounts of retries (RETRY_INT = {RETRY_INT} now) "
                           "in the settings file. Please change this. Exiting.")

            self.abort(message)
        
        missing_dependencies = []
        missing_python_packages = []
        rippy_shared_exist = True

        if self.LEVEL_STR in self.accuraterip_levels_list or self.MUSICBRAINZ_BOOL or self.DISCOGS_TOKEN_STR:
            if not check_internet_httplib():
                message = "Internet connection is needed for the settings you have chosen. Please make sure you're connected to the Internet and then try again.\n"
                self.abort(message)


        if self.ENABLE_TAGGING_BOOL:
            result = subprocess.run("dpkg -l | grep libtag1-dev", shell=True, stdout=subprocess.PIPE, text=True)

            if not result.stdout:
                missing_dependencies.append("libtag1-dev")

            try:
                import taglib
            except ImportError:
                missing_python_packages.append("pytaglib")
        

        if self.LEVEL_STR in self.accuraterip_levels_list or self.more_than_once_list:
            try:
                import rippy_shared_object

            except ImportError:
                print()
                spaced_print("To use Accurate Rip and/or byte-for-byte comparison with Rippy, you need the rippy_shared_object.*.so file. This is available to download at Github or rippy.skatepunk.se for both 32 and 64 bit systems.\n"
                         "You can also build it yourself with the setup.py file in the root of the project, or through this script, after installing all packages. "
                         "You need the python package setuptools and the linux meta package build-essential (or gcc) and python3-dev to build it. ")
                rippy_shared_exist = False

                result = subprocess.run("dpkg -l | grep build-essential", shell=True, stdout=subprocess.PIPE, text=True)

                if not result.stdout:
                    result = subprocess.run("dpkg -l | grep gcc", shell=True, stdout=subprocess.PIPE, text=True)
                    if not result.stdout:
                        missing_dependencies.append("build-essential")

                result = subprocess.run("dpkg -l | grep python3-dev", shell=True, stdout=subprocess.PIPE, text=True)

                if not result.stdout:
                    missing_dependencies.append("python3-dev")

                try:
                    import setuptools
                except ImportError:
                    missing_python_packages.append("setuptools")

        
        if self.MUSICBRAINZ_BOOL:

            try:
                import musicbrainzngs
            except ImportError:
                missing_python_packages.append("musicbrainzngs")

        if self.DISCOGS_TOKEN_STR != "":
            try:
                import discogs_client
            except ImportError:
                missing_python_packages.append("python3-discogs-client")

        if self.GAIN_BOOL:
            result = subprocess.run("dpkg -l | grep normalize-audio", shell=True, stdout=subprocess.PIPE, text=True)

            if not result.stdout:
                missing_dependencies.append("normalize-audio")

        if self.CUE_BOOL or self.TEST_DRIVE_BOOL:
            result = subprocess.run("dpkg -l | cdrdao", shell=True, stderr=subprocess.PIPE, text=True)

            if "show-data" not in result.stderr:
                if "cdrdao" not in missing_dependencies:
                    missing_dependencies.append("cdrdao")

        if self.SPECTRO_BOOL:

            result = subprocess.run("dpkg -l | grep 'Swiss army knife of sound processing'", shell=True, stdout=subprocess.PIPE, text=True)

            if not result.stdout:
                missing_dependencies.append("sox")

            try:
                import PIL
            except ImportError:
                missing_python_packages.append("pillow")

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



        if missing_dependencies or missing_python_packages or not rippy_shared_exist:
        
            collected_str = f"{pkg_missing_str}{' and ' if missing_dependencies and missing_python_packages else ''}{pip_missing_str}"
            install_str = f"{pkg_install_str}{' && ' if missing_dependencies and missing_python_packages else ''}{pip_install_str}"
            install_now = ""
            create_shared = ""
            if collected_str:
                install_now = special_input(f"You are missing {collected_str}. Please install (for example with '{install_str}' if you want them system wide, or use a virtual environment) and then run Rippy again. Do you wish to install them system wide now? Write y for yes and press enter, otherwise just press enter: ")
                print()

            if not rippy_shared_exist:
                create_shared = special_input(f"Write y for yes and press enter if you want to build rippy_shared_object.so, otherwise just press enter: ")
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
                        download_url = "https://raw.githubusercontent.com/yourusername/yourrepo/main/rippy_shared_object.c"

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
                    self.abort("Rerun the Rippy script to continue.")
            else:
                self.abort("Aborting.")



    def make_correct_var(self, offset, speed, drive, error):

        """ Setting the correct ripping strings """

        self.OFFSET_STR = f"-O {offset}"
        self.DRIVE_STR = f"-d {drive}"
            
        if speed != "":
            self.SPEED_STR = f"-S {speed}"

        if error == "False" or error == False:
            self.ERROR_CORRECTION_STR = "-Z"
        else:    
            self.ERROR_CORRECTION_STR = f"-z={error}"


    def toc(self):

        """
        Getting and storing the Table Of Contents, TOC. 
        Gets the last track, so the rip will work for that track. 
        Checks if there is a hidden track before all other tracks and getting track lengths
        """
        

        toc_read_list = subprocess.Popen(f"cdparanoia {self.DRIVE_STR} -Q", shell=True, encoding='utf8',stderr=subprocess.PIPE).stderr.read().split("\n")[4:]

        tracks_in_toc_list = toc_read_list[2:-2]

        last_track_length_int = int(tracks_in_toc_list[-2].split("[")[0].split(".")[1].strip())

        self.LAST_LENGTH_STR = str(last_track_length_int - 2)
        self.LAST_SECTOR_STR = str(last_track_length_int - 1)

        self.TOC_READ_STR = "\n".join(toc_read_list)
        print(self.TOC_READ_STR)

        for htoa_int, toc_list in enumerate(tracks_in_toc_list[:-1]):
            getting_track_lengths = remove_excessive_space(toc_list).split(" ")
            self.track_length_list.append(getting_track_lengths[3].replace("[","").replace("]",""))
            self.all_track_begin_offsets_list.append(int(getting_track_lengths[4]))
            if htoa_int == 0 and int(getting_track_lengths[4]) > 150:
                self.HTOA_EXIST_BOOL = True
                self.HTOA_LAST_SECTOR_STR = str(int(getting_track_lengths[4]) - 1)

        self.LEAD_OUT_OFFSET_INT = int(remove_excessive_space(tracks_in_toc_list[-1]).split(" ")[1])



        # Find all the sector offsets using the pattern
        offsets = [self.LEAD_OUT_OFFSET_INT + self.all_track_begin_offsets_list[0] + 150] + [int(match) + 150 for match in self.all_track_begin_offsets_list]
        first_track = 1
        last_track = self.TRACK_AMOUNT_INT
        n = 0

        for i in range(first_track, last_track + 1):
            seconds = offsets[i] // 75
            while seconds > 0:
                n += seconds % 10
                seconds //= 10

        t = offsets[0] // 75 - offsets[1] // 75

        freedb_id = ((n % 0xff) << 24) | (t << 8) | last_track

        self.FDID_STR = f"{freedb_id:08x}"

        import hashlib
        import base64

        sha1 = hashlib.sha1()

        # First and last track numbers
        sha1.update(f"{first_track:02X}".encode())
        sha1.update(f"{last_track:02X}".encode())

        # 100 offsets (pad with zeros if less)
        for i in range(100):
            # If the index is less than the length of offsets, use the offset. Otherwise, pad with zero.
            offset = offsets[i] if i < len(offsets) else 0

            sha1.update(f"{offset:08X}".encode())  # Pad the offset to 8 hex digits

        digest = sha1.digest()

        self.MBID_STR = base64.b64encode(digest).decode().replace("+",".").replace("=","-").replace(r"/","_")

        if self.LEVEL_STR in self.accuraterip_levels_list:
            self.accuraterip_dict = rippy_track_verify(self)
            
            if not self.accuraterip_dict and self.LEVEL_STR in self.accuraterip_levels_list:
                print(f"Album not in Accurate Rip database. Falling back on level {self.DE_FACTO_LEVEL_STR}.\n")

            else:
                self.DE_FACTO_LEVEL_STR = self.LEVEL_STR


            if self.DE_FACTO_LEVEL_STR == "G" and not self.accuraterip_dict:
                message = "Album not in in Accurate Rip database. Aborting."
                self.abort(message)
        else:
            self.DE_FACTO_LEVEL_STR = self.LEVEL_STR


    def testing_cd_drive(self):

        # Inform the user about the CD-drive analysis
        spaced_print("Performing CD-drive analysis with cdparanoia, this may take somewhere between 15 seconds and a minute, depending on your drive speed.\n\n")
        
        # Run cdparanoia command and get drive info
        cdparanoia_drive_info = subprocess.Popen(f"cdparanoia {self.DRIVE_STR} -A -L", shell=True, encoding='utf8')
        cdparanoia_drive_info.wait()
        
        # Read the cdparanoia output from the log file
        with open("cdparanoia.log", "r") as cdp:
            cdparanoia_drive_info = cdp.read().split("\n")
        
        # Remove the log file after processing
        os.remove("cdparanoia.log")
        
        # Check if the drive test passed
        if "Drive tests OK with Paranoia." not in cdparanoia_drive_info[-3]:
            drive_not_ok = special_input("Your drive did not pass Paranoia's drive test, do you wish to continue? If no, write n and press enter. If yes, just press enter.")
            
            # Exit if the user does not wish to continue
            if drive_not_ok == "n":
                self.abort("Rip aborted because of negative drive test.")
       
        # Run cdrdao command and get drive info
        cdrdao_drive_info = subprocess.Popen(f"cdrdao drive-info --device {self.CHOSEN_DRIVE_STR}", shell=True, encoding='utf8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cdrdao_drive_info.wait()
        
        # Read the output of cdrdao command
        cdrdao_drive_info = cdrdao_drive_info.stdout.read().split("\n")
        
        # Append the results to bonus_log if self.BONUS_BOOL is True
        if self.BONUS_BOOL:
            self.bonus_log_dict["cdrdao_drive_info"] = cdrdao_drive_info
            self.bonus_log_dict["cdparanoia_drive_info"] = cdparanoia_drive_info




    def working_directory(self):

        """ Making temp folder """

        self.TEMP_STR = str(uuid.uuid4())
        os.mkdir(self.TEMP_STR)

    def get_tag_data(self):

        """ Tries to find tags through MusicBrainz, otherwise Discogs or manual """

        if self.ENABLE_TAGGING_BOOL:
            if self.MUSICBRAINZ_BOOL:
                try:
                    self.ALBUM_STR, self.ARTIST_STR, self.YEAR_STR, self.GENRE_STR, self.COMMENT_STR, self.track_list, self.various_list = musicbrainz_function(self)
                    if not self.ALBUM_STR:
                        raise ValueError  # Forces fallback to Discogs or Manual tagging
                except:
                    pass  # Fall back to Discogs or Manual tagging

            # If tagging is enabled but MusicBrainz fails, fall back
            if not self.MUSICBRAINZ_BOOL or not self.ALBUM_STR:
                self.ALBUM_STR, self.ARTIST_STR, self.YEAR_STR, self.GENRE_STR, self.COMMENT_STR, self.track_list, self.various_list = discogs_or_manual(self)
        else:
            self.ALBUM_STR, self.ARTIST_STR, self.YEAR_STR, self.GENRE_STR, self.COMMENT_STR, self.track_list, self.various_list = discogs_or_manual(self)

        """ Defining tags """

        defining_tags(self)

        import importlib.util
        import sys

        module_name = f"temp_data_{self.TEMP_STR}"
        file_path = f"temp_data_{self.TEMP_STR}.py"  # Construct file path

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Now you can access the variables
        album = module.album
        artist = module.artist
        year = module.year
        genre = module.genre
        comment = module.comment
        track_list = module.track_list
        various_list = module.various_list

        self.YEAR_STR = year
        self.ALBUM_STR = reverse_placeholding(album)
        self.ARTIST_STR = reverse_placeholding(artist)
        self.GENRE_STR = reverse_placeholding(genre)
        self.COMMENT_STR = reverse_placeholding(comment)
        self.track_list = [reverse_placeholding(place) for place in track_list]
        self.various_list = [reverse_placeholding(place) for place in various_list]

        artist = self.ARTIST_STR
        album = self.ALBUM_STR
        genre = self.GENRE_STR
        comment = self.COMMENT_STR
        year = self.YEAR_STR
        
        for i, title in enumerate(self.track_list):
            track_number = str(i + 1).zfill(2)
            artist = self.various_list[i] 
    
            file_name = eval(f"f'{self.VARIOUS_FILE_NAME_STANDARD_F_STR}'") if len(list(set(self.various_list))) != 1 else eval(f"f'{self.FILE_NAME_STANDARD_F_STR}'")

            if self.LINUX_BOOL or self.WINDOWS_BOOL:
                for char in self.custom_dictionary:
                    file_name = file_name.replace(char, self.custom_dictionary[char])

            self.file_name_list.append(file_name)
            

        
        self.FOLDER_STR = eval(f"f'{self.VARIOUS_FOLDER_STANDARD_F_STR}'") if len(list(set(self.various_list))) != 1 else eval(f"f'{self.FOLDER_STANDARD_F_STR}'")

        if self.LINUX_BOOL or self.WINDOWS_BOOL:
            for char in self.custom_dictionary:
                self.FOLDER_STR = self.FOLDER_STR.replace(char, self.custom_dictionary[char])


        if self.HTOA_BOOL and self.HTOA_EXIST_BOOL:
            print()
            self.HTOA_TITLE_STR = special_input("Hidden Track One Audio (HTOA) found, do you want to give it a title? Otherwise, standard (HTOA) will be used. Write here or just press Enter: ") or "HTOA"
            track_number = "00"
            title = self.HTOA_TITLE_STR
            artist = self.ARTIST_STR
            self.HTOA_FILE_NAME_STR = eval(f"f'{self.VARIOUS_FILE_NAME_STANDARD_F_STR}'") if artist == "Various Artists" else eval(f"f'{self.FILE_NAME_STANDARD_F_STR}'")

        os.chdir(self.TEMP_STR)

    def move_folder(self):

        """ Moving folder and adding erronous comment to folder if it couldn't be ripped perfectly """

        erronous = " (erronous)" if rippy_class.ERRONOUS_BOOL else ""
        os.chdir("..")
        os.makedirs(os.path.join(self.SAVE_PATH, f"{self.FOLDER_STR}{erronous}"), 0o755)
        os.rename(self.TEMP_STR, os.path.join(self.SAVE_PATH, f"{self.FOLDER_STR}{erronous}"))


    def eject_drive(self):

        """ Ejecting CD from drive """

        if self.EJECT_BOOL:
            eject_command = f"eject {self.CHOSEN_DRIVE_STR}"
            subprocess.run(eject_command, shell=True, check=True)


if __name__ == "__main__":


    rippy_class = RippyClass()


    print()
    spaced_print((
        f"Welcome to Rippy V.{rippy_class.RIPPY_VERSION_STR}, a Python script for ripping full CDs "
        "to flac files meticulously with cdparanoia III release 10.2 (September 11, 2008). "
    ))


    rippy_class.CHOSEN_DRIVE = rippy_class.check_if_disc()

    cd_drive_info = rippy_class.drive_info()


    """ Loading settings """

    rippy_class.drive_settings()


    if rippy_class.BONUS_BOOL:
        rippy_class.bonus_log_dict["cd_drive_info"] = "\n".join(cd_drive_info)

    

    from rippy_cd_info_functions import *

    from rippy_ripping_functions import *

    from rippy_log_functions import *

    from rippy_flac_function import *

    if rippy_class.SPECTRO_BOOL:
        from rippy_spectro_function import *

    print()

    
    spaced_print(f"Your drive is: {rippy_class.USED_DRIVE_STR} with offset {rippy_class.OFFSET_STR_LOG}.")


    """ Getting album information """

    rippy_class.toc()

    rippy_class.working_directory()
    

    rippy_class.get_tag_data()
    print()

    """ Actual rip starts here """

    rip_start = time.time()


    """ If test_drive is set as True, CD drive will be tested now """

    if rippy_class.TEST_DRIVE_BOOL:
        rippy_class.testing_cd_drive()


    """ ALL RIPPING IS DONE HERE """

    main_ripping_process(rippy_class)


    if rippy_class.HTOA_BOOL and rippy_class.HTOA_EXIST_BOOL:
        htoa_rip(rippy_class)

    """ Setting up to get TOC for cue sheet and verbose log if needed"""
    
    commands = []

    if rippy_class.CUE_BOOL:
        commands.append(subprocess.Popen(f"cdrdao read-toc --device {rippy_class.CHOSEN_DRIVE_STR} cdda.toc", shell=True, encoding='utf8', stdout=subprocess.PIPE))
    

    """ Converting to flac """
    
    flac_tagging(rippy_class, commands)


    """ Ripping HTOA if it exists """




    """ Creating cue sheet """
    
    if rippy_class.CUE_BOOL:
        cue_list_creating(rippy_class)


    """ Creating logs """

    now = datetime.datetime.now()
    rippy_class.now_str = now.strftime('%B') + f" {now.day}, " + now.strftime('%Y, %H:%M:%S')


    if rippy_class.VERBOSE_BOOL:
        verbose_log(rippy_class)

    if rippy_class.BONUS_BOOL:
        bonus_log_function(rippy_class)

    if rippy_class.LOG_BOOL:
        main_log_function(rippy_class)


    """ Creating spectrograms """

    if rippy_class.SPECTRO_BOOL:
        spectro_function(rippy_class)


    """ Moving folder """

    rippy_class.move_folder()


    """ Exiting """

    final_time = time.time() - rip_start
    minutes = int(final_time / 60)
    seconds = round(final_time - minutes*60)

    rippy_class.eject_drive()

    message = f"The ripping process has finished. It took {minutes} minutes and {seconds} seconds."

    rippy_class.abort(message)

