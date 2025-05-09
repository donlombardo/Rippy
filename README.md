<p align="center">
  <img src="https://rippy.skatepunk.se/static/Rippy.svg" alt="Rippy Logo" width="40%">
</p>


Rippy is a Python 3 script for Linux, for ripping full CDs to flac files meticulously with cdparanoia III release 10.2 (September 11, 2008).

This document outlines the required and optional software dependencies, how to install them, and how to run the program. Rippy is only tested on 64-bit systems, and works for Python 3.7 - 3.14.

## Required Software

You must have the following software installed before running Rippy:

### Essential (must be installed manually)

- Python 3 — required to run the script
- pip for Python 3 — required to install Python packages

Install them using:

```bash
sudo apt update && sudo apt install python3 python3-pip
```

### Additional required packages (can be installed manually or via the install script)

- cdparanoia III 10.1 — required to rip CDs
- libcdio-utils — required to read CD information
- flac — required to convert WAV to FLAC

## Optional Packages

The following software is not required, but enables additional features:

- cdrdao — enables cue sheet creation
- normalize — enables gain analysis

## AccurateRip Support

To use AccurateRip for track verification, you need to compile a shared C object file. For that, install:

```bash
sudo apt install python3-dev build-essential -y
```

You can also choose to download the specific file from the Rippy Shared Object folder in this project.

## Tagging Support

To enable metadata tagging of audio files:

- libtag1-dev — required by the tag library
- pytaglib — Python wrapper for taglib (not working with Python 3.7 or Python 3.14)

## Metadata Tagging via Online Sources

To enable tagging from online databases:

- Discogs:
  ```bash
  pip install python3-discogs-client
  ```

- MusicBrainz:
  ```bash
  pip install musicbrainzngs
  ```

## Spectrogram Generation

To enable spectrogram generation, install pillow (not working with Python 3.14)

```bash
sudo apt install sox
pip install pillow
```


All required packages except for Python 3 and pip can be installed by running the installation script provided with Rippy. However, you are free to install them manually as described above.

You may delete this README file once everything is installed and configured to your satisfaction.


## How to Run

1. Open a terminal in the project folder.
   (Right-click the folder and choose "Open terminal here" if available.)

2. Run the program using:

```bash
python3 Rippy.py
```

Or with overrides:

## Override Default Settings

You can override Rippy’s default behavior using command-line arguments in the form `--KEY=value`.

### Example

```bash
python3 Rippy.py --MATCHING_BYTES_INT=4 --CAPITALIZE_BOOL=True
```

### Available Overrides

| Key | Type | Allowed Values |
|-----|------|----------------|
| `--APOSTROPHE_BOOL` | bool | `True`, `False` |
| `--BONUS_BOOL` | bool | `True`, `False` |
| `--CAPITALIZE_BOOL` | bool | `True`, `False` |
| `--CUE_BOOL` | bool | `True`, `False` |
| `--DE_FACTO_LEVEL_STR` | str | `"E"`, `"F"`, `"G"`, `"H"` |
| `--DISCOGS_TOKEN_STR` | str | *(Discogs API token)* |
| `--EJECT_BOOL` | bool | `True`, `False` |
| `--ENABLE_TAGGING_BOOL` | bool | `True`, `False` |
| `--ERROR_CORRECTION_STR` | str | *(Any string)* |
| `--FILE_NAME_STANDARD_F_STR` | str | *(Any string)* |
| `--FOLDER_STANDARD_F_STR` | str | *(Any string)* |
| `--GAIN_BOOL` | bool | `True`, `False` |
| `--HTOA_BOOL` | bool | `True`, `False` |
| `--LEVEL_STR` | str | `"A"` to `"I"` |
| `--LINUX_BOOL` | bool | `True`, `False` |
| `--LOG_BOOL` | bool | `True`, `False` |
| `--MATCHING_BYTES_INT` | int | `2` to `32` |
| `--MUSICBRAINZ_BOOL` | bool | `True`, `False` |
| `--RETRY_INT` | int | `2` to `32` |
| `--SAVE_PATH` | str | *(Path to save files)* |
| `--SPEED_STR` | str | *(Any string)* |
| `--SPECTRO_BOOL` | bool | `True`, `False` |
| `--TEST_DRIVE_BOOL` | bool | `True`, `False` |
| `--V1_BOOL` | bool | `True`, `False` |
| `--VARIOUS_FILE_NAME_STANDARD_F_STR` | str | *(Any string)* |
| `--VARIOUS_FOLDER_STANDARD_F_STR` | str | *(Any string)* |
| `--VERBOSE_BOOL` | bool | `True`, `False` |
| `--WINDOWS_BOOL` | bool | `True`, `False` |

> **Note:** Boolean values are case-sensitive (`True`, `False`). Strings with spaces should be quoted.



## Acknowledgements & Thanks

Rippy uses or depends on the following external tools and libraries:

### System Tools & Libraries:
- **cdparanoia** - GPLv2 — Thank you to Monty and Xiph.Org for making this possible.
- **libcdio-utils** - GPL
- **flac** - Free and open under BSD-like terms
- **cdrdao** - GPLv2
- **normalize** - GPLv2
- **sox** - LGPL-2.1-or-later

### Python Libraries:
- **pytaglib** - GPLv3+
- **taglib** - LGPL / MPL
- **python3-discogs-client** - BSD-like
- **musicbrainzngs** - BSD-like
- **pillow** - MIT-CMU
- **pip** - MIT
- **Python 3** - PSF License
- **python-audio-tools** - Portions modified, originally GPLv2

### Development Tools (for AccurateRip compilation):
- **python3-dev** and **build-essential** — system packages under various permissive and copyleft licenses

All trademarks, logos, and brand names are the property of their respective owners.

Thank you to all open source developers whose work made this software possible.

I especially want to thank Millencolin for making Tiny Tunes, so I could use it as a my main test CD for this project. 
