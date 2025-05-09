""" Defining functions to get album tags """

import os
from rippy_help_functions import *


def musicbrainz_function(rippy_class):
    ripping_lists = {"artist_list": [], "year_list": [], "title_list": [], "id_list": [], "track_lists": [], "various_list": []}
    ALBUM = ARTIST = YEAR = GENRE = COMMENT = ""
    tracklist = various = []

    import musicbrainzngs

    # Set user agent for MusicBrainz API
    musicbrainzngs.set_useragent("Rippy", f"{rippy_class.RIPPY_VERSION_STR}", "A CD ripping script in Python for Linux")
    
    # Fetch release information from MusicBrainz using CDID
    disc_info = musicbrainzngs.get_releases_by_discid(rippy_class.MBID_STR, includes="artists")['disc']['release-list']
    
    disc_number = 0
    if len(disc_info[0]["medium-list"]) > 1:
        disc_number = int(input("This album has more than one disc. Which disc is it you are ripping? Write here with a number: ")) - 1

    spaced_print("Fetching Musicbrainz data. This might take quite a long time, depending on how many versions Musicbrainz has for the album.\n")

    # Loop through each release in the disc info
    for i in disc_info:
        ripping_lists["id_list"].append(i["id"])
        ripping_lists["year_list"].append(i['date'][:4])

        # Handle artist credits
        if len(i["artist-credit"]) > 1:
            ripping_lists["artist_list"].append("Various Artists")
        else:
            ripping_lists["artist_list"].append(character_change(i['artist-credit-phrase'], rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL))
        
        ripping_lists["title_list"].append(character_change(i['title'], rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL))
        
    # Loop through each ID list and fetch track information
    for i in ripping_lists["id_list"]:
        various_append_list = []
        tracklist = musicbrainzngs.get_release_by_id(i, includes=["recordings"])["release"]["medium-list"][disc_number]["track-list"]
        
        for i in tracklist:
            artist_credit = musicbrainzngs.get_recording_by_id(i["recording"]["id"], includes="artist-credits")
            various_append_list.append(character_change(artist_credit["recording"]["artist-credit-phrase"].replace("\t",""), rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL))
        
        tracks = []
        for i in range(len(tracklist)):
            line = tracklist[i]
            tracks.append(character_change(line["recording"]["title"], rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL))
        
        ripping_lists["track_lists"].append(tracks)
        ripping_lists["various_list"].append(various_append_list)


    # If multiple artists are found, display them and allow user to choose
    if len(ripping_lists["artist_list"]) > 1:
        for count, i in enumerate(ripping_lists["artist_list"]):
            spaced_print(f"{count + 1}) {i} - {ripping_lists['year_list'][count]} - {ripping_lists['title_list'][count]}")
            string_of_tracklist = []
            current_tracklist = ripping_lists["track_lists"][count]
            tracknumber = 1
            
            if i == "Various Artists":
                for _ in range(0, len(current_tracklist)):
                    string_of_tracklist.append(f"{tracknumber}. {ripping_lists['various_list'][count][_]} - {current_tracklist[_]}")
                    tracknumber += 1
            else:
                for _ in current_tracklist:
                    string_of_tracklist.append(f"{tracknumber}. {_}")
                    tracknumber += 1
            
            spaced_print(' '.join(string_of_tracklist))

        spaced_print("This is the CD data from Musicbrainz. Is any of these your album? If not, press Enter. If yes, write the number before the album title and press Enter. If you want to choose artist, album title, year, and tracklist from different releases, write the number from each release corresponding to your choice in this order:")
        spaced_print("Artist,Year,Album,Tracklist")
        spaced_print(f"Example: '1,2,3,2' will choose artist from the first alternative, year and track list from the second alternative and album from the third. If you write anything else than available options, you will have to write information yourrippy_class. You can change anything you want in the temporary file called 'temp_data_{rippy_class.TEMP_STR}.py', after you've made your choice.")
        
        musicbrainz_info = special_input("Write your choice here: ")
        print()
    else:
        musicbrainz_info = "1"



    # If the user selects an option, assign the corresponding data
    if len(musicbrainz_info) == 1:
        if isinstance(int(musicbrainz_info), int) and (int(musicbrainz_info)-1) in list(range(0, len(ripping_lists["artist_list"]))):
            artist = ripping_lists["artist_list"][int(musicbrainz_info)-1]
            album = ripping_lists["title_list"][int(musicbrainz_info)-1]
            year = ripping_lists['year_list'][int(musicbrainz_info)-1]
            tracklist = ripping_lists["track_lists"][int(musicbrainz_info)-1]
            various = ripping_lists['various_list'][int(musicbrainz_info)-1]
            genre = special_input("What genre is this CD? Can be left empty by pressing enter. Write here: ")
            print()
            comment = special_input("Do you want a tag comment? Write here or just press Enter: ")


    # If the user selects more than one release option, assign from each chosen option
    elif len(musicbrainz_info) == 7:
        if isinstance(int(musicbrainz_info[0] + musicbrainz_info[2] + musicbrainz_info[4] + musicbrainz_info[6]), int) and \
           (int(musicbrainz_info[0])-1) in list(range(0, len(ripping_lists["artist_list"]))) and \
           (int(musicbrainz_info[2])-1) in list(range(0, len(ripping_lists["artist_list"]))) and \
           (int(musicbrainz_info[4])-1) in list(range(0, len(ripping_lists["artist_list"]))) and \
           (int(musicbrainz_info[6])-1) in list(range(0, len(ripping_lists["artist_list"]))):
            
            artist = ripping_lists['artist_list'][int(musicbrainz_info[0])-1]
            various = ripping_lists['various_list'][int(musicbrainz_info[0])-1]
            album = ripping_lists["title_list"][int(musicbrainz_info[4])-1]
            year = ripping_lists['year_list'][int(musicbrainz_info[2])-1]
            tracklist = ripping_lists["track_lists"][int(musicbrainz_info[6])-1]
            genre = special_input("What genre is this CD? Can be left empty by pressing enter. Write here: ")
            print()
            comment = special_input("Do you want a comment tag? Write your comment here or just press Enter: ")

    return album, artist, year, genre, comment, tracklist, various




def discogs_or_manual(rippy_class):
    """ Creates a folder with a random folder name and changes directory into that folder """
    
    # Initialize default metadata values
    artist = "Unknown Artist"
    various = ["Unknown Artist"] * rippy_class.TRACK_AMOUNT_INT
    album = "Unknown Album"
    year = ""
    genre = "Unknown Genre"
    comment = ""
    tracklist = ["Track " + str(i).zfill(2) for i in range(1, int(rippy_class.TRACK_AMOUNT_INT) + 1)]

    # Check if internet access is enabled
    if rippy_class.DISCOGS_TOKEN_STR != "":
        spaced_print("Do you have a Discogs link, want to write metadata yourself, or use default (Artist: Unknown Artist, year: (blank), album: Unknown Album, genre: Unknown Genre, track: Track ##)?")
        meta = special_input("Enter d for Discogs, s to write album data manually, or leave empty to use default data: ")
    else:
        spaced_print("Do you want to write metadata yourself or use default (Artist: Unknown Artist, year: (blank), album: Unknown Album, genre: Unknown Genre, track: Track ##)?")
        meta = special_input("Enter s to write album data manually or leave empty to use default data: ")

    # If Discogs metadata is selected and Discogs ID is available
    if rippy_class.DISCOGS_TOKEN_STR and meta == "d":
        tracklist = []

        import discogs_client  # Import Discogs client

        # Initialize the Discogs client
        discogs_data = discogs_client.Client('Rippy', user_token = rippy_class.DISCOGS_TOKEN_STR)

        print()

        # Ask user for a Discogs URL or search query
        search_artist = input("Enter artist or album release link (should include 'release' like in 'https://www.discogs.com/release/'): ")

        if "release" in search_artist:
            release = search_artist.split("release/")[-1].split("-")[0]
            release = discogs_data.release(release)
        else:
            search_album = input("Which album? Write here: ")
            results = discogs_data.search(search_artist, type='artist')
            start_title_discogs = ""
            list_discogs = []

            # Loop through search results
            for start_number_discogs, result in enumerate(results):
                start_number_discogs += 1
                if search_artist in result.name:
                    for discogs_item in result.releases.page(1):
                        if search_album in discogs_item.title:
                            if str(type(discogs_item)).split(".")[-1][0] == "R":
                                if "CD" in discogs_item.formats[0]["name"]:
                                    start_title_discogs = discogs_item.id
                            else:
                                discogs_number_two = 0
                                for discogs_item_three in discogs_item.versions.page(1):
                                    if "CD" in discogs_item_three.formats[0]["name"]:
                                        discogs_number_two += 1
                                        print(f"{discogs_number_two}) {discogs_item_three.artists[0].name} - {discogs_item_three.year} - {discogs_item_three.title}")
                                        discogs_list_two = []
                                        discogs_number_three = 0
                                        for discogs_item_two in discogs_item_three.tracklist:
                                            if discogs_item_two.position != "":    
                                                discogs_number_three += 1
                                                discogs_list_two.append(str(discogs_number_three) + ". " + discogs_item_two.title.replace("\t",""))
                                        print(" ".join(discogs_list_two))
                                        list_discogs.append(discogs_item_three.id)
                                        print()

                if start_number_discogs == 6:
                    break

            # Handle Discogs search results
            if len(list_discogs) > 1:
                print()
                discogs_input_result = special_input("Which release do you want to use? Write the number: ")
                start_title_discogs = list_discogs[int(discogs_input_result)-1]
            elif len(list_discogs) == 1:
                start_title_discogs = list_discogs[0]

            # Fetch release from Discogs
            if start_title_discogs != "":
                release = discogs_data.release(start_title_discogs)
            else:
                release = discogs_data.release(special_input("Paste your Discogs link here: ").split("/")[-1])

        print()

        # Extract year and album title
        year = str(release.year)
        album = character_change(str(release.title), rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL)

        # Check for "Various Artists" if applicable
        if len(release.artists) > 1:
            various = []
            artist = "Various Artists"
        elif "Various" in str(release.artists[0].name):
            various = []
            artist = "Various Artists"
        else:
            artist = character_change(str(release.artists[0].name), rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL)
            if artist.find(" (") != -1:
                artist = str(artist[:artist.find(" (")])

            various = [character_change(artist, rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL)] * rippy_class.TRACK_AMOUNT_INT

        if artist.find(" (") != -1:
            artist = str(artist[:artist.find(" (")])

        start_track = 0
        filtered_tracklist = []

        # Filter tracks
        for track in release.tracklist:
            if track.position != "":
                filtered_tracklist.append(track)

        if len(filtered_tracklist) > rippy_class.TRACK_AMOUNT_INT:
            start_track = int(input("The number of tracks on Discogs are more than the number of tracks on the CD. From which track do you want to start? Write here: ")) - 1

        # Loop through tracks and append to tracklist
        for idx, filtered_tracklist_track in enumerate(filtered_tracklist):
            if idx < start_track:
                continue
            if filtered_tracklist_track.position != "":
                if "Various" in artist:
                    if filtered_tracklist_track.data["artists"][0]["name"].find(" (") != -1:
                        various.append(character_change(filtered_tracklist_track.data["artists"][0]["name"].replace("\t",""), rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL)[:filtered_tracklist_track.data["artists"][0]["name"].find(" (")])
                    else:
                        various.append(character_change(filtered_tracklist_track.data["artists"][0]["name"].replace("\t",""), rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL))
                tracklist.append(character_change(filtered_tracklist_track.title, rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL).replace("\t",""))

        # Ask for genre and comment
        genre = special_input("What genre is this CD? Can be left empty by pressing enter. Write here: ")
        print()
        comment = special_input("Do you want a comment tag? Write your comment here or just press Enter: ")

    # Manual metadata entry if Discogs is not used
    elif meta == "s" or (meta == "d" and rippy_class.DISCOGS_TOKEN_STR == ""):
        tracklist = []
        artist = special_input("Which artist: ")
        album = special_input("Which album: ")
        year = special_input("Which year: ")
        genre = special_input("What genre is this CD? Can be left empty by pressing enter. Write here: ")
        if "Various" in artist:
            various = []
            for i in range(1, int(rippy_class.TRACK_AMOUNT_INT) + 1):
                print(f"{i}/{rippy_class.TRACK_AMOUNT_INT}")
                various.append(special_input(f"Artist name: "))
                tracklist.append(special_input(f"Track name: "))
        else:
            various = [character_change(artist, rippy_class.CAPITALIZE_BOOL, rippy_class.APOSTROPHE_BOOL)] * rippy_class.TRACK_AMOUNT_INT

        print()
        comment = special_input("Do you want a comment tag? Write your comment here or just press Enter: ")

    return album, artist, year, genre, comment, tracklist, various


def defining_tags(rippy_class):
    artist = rippy_class.ARTIST_STR
    album = rippy_class.ALBUM_STR
    genre = rippy_class.GENRE_STR
    comment = rippy_class.COMMENT_STR
    year = rippy_class.YEAR_STR
    various = rippy_class.various_list
    tracklist = rippy_class.track_list

    # Write the metadata to a temporary Python file
    with open(f"temp_data_{rippy_class.TEMP_STR}.py", "w") as temp_data_write:
        # Placeholding the values
        album_temp = placeholding(album)
        artist_temp = placeholding(artist)
        genre_temp = placeholding(genre)
        comment_temp = placeholding(comment)

        # Write album metadata
        temp_data_write.write(f"album = '{album_temp}'\n")
        temp_data_write.write(f"artist = '{artist_temp}'\n")
        temp_data_write.write(f"year = '{year}'\n")
        temp_data_write.write(f"genre = '{genre_temp}'\n")
        temp_data_write.write(f"comment = '{comment_temp}'\n")

        # Check if the track amount matches the tracklist length
        if rippy_class.TRACK_AMOUNT_INT != len(tracklist):
            if rippy_class.TRACK_AMOUNT_INT > len(tracklist):
                choice = special_input(f"Do you want to add the extra track(s) manually (man), in temp_data_{rippy_class.TEMP_STR}.py later (temp), or exit (leave empty)?\nEnter: ")

                if choice == "man":
                    amount_of_tracks = int(rippy_class.TRACK_AMOUNT_INT)
                    tracklist_number_now = len(tracklist)

                    # Add missing tracks manually
                    for bonus_number in range(tracklist_number_now + 1, amount_of_tracks + 1):
                        various.append(special_input(f"Artist for track number {bonus_number}: "))
                        tracklist.append(special_input(f"Track for track number {bonus_number}: "))
                elif choice == "temp":
                    needed_tracks = int(rippy_class.TRACK_AMOUNT_INT) - len(tracklist)
                    spaced_print(f"Open temp_data_{rippy_class.TEMP_STR}.py and remove the track(s) that should not be there. There are {needed_tracks} track{'s' if  needed_tracks > 1 else ''} that has to be added.")
                else:
                    rippy_class.abort()  # Exit if user chooses not to continue
            else:
                # If there are too many tracks, save the tracklist to a file
                with open(f"tracklist_edit_{rippy_class.TEMP_STR}.py", "w") as my_tracklist:
                    my_tracklist.write(f"tracklist = {str(tracklist)}")
                superfluous_int = len(tracklist) - int(rippy_class.TRACK_AMOUNT_INT)
                input(f"Open the tracklist_edit_{rippy_class.TEMP_STR}.py and remove the track{'s' if superfluos > 1 else ''} that should not be there. There {'is' if superfluous == 1 else 'are'} superfluous track{'s' if superfluous > 1 else ''}. Then press Enter.")

                # Read the corrected tracklist from file
                from tracklist_edit import album, artist, year, genre, comment, tracklist, various
                os.remove("tracklist_edit.py")  # Remove the file after reading


        track_str = '", "'.join([placeholding(tracklist[i]) for i in range(rippy_class.TRACK_AMOUNT_INT)])
        temp_data_write.write(f'track_list = ["{track_str}"]\n\n')
        various_str = '", "'.join([placeholding(various[i]) for i in range(rippy_class.TRACK_AMOUNT_INT)])
        temp_data_write.write(f'various_list = ["{various_str}"]\n\n')


        # Display the user input
        print(f"\nYour choice:\nArtist: {artist}\nYear: {year}\nAlbum: {album}\nGenre: {genre}\nComment: {comment}")
        string_of_tracklist = []

        # Format the tracklist for output
        string_of_tracklist = [f"{i + 1}. {various[i]} - {tracklist[i]}" for i in range(0, rippy_class.TRACK_AMOUNT_INT)] if artist == "Various Artists" else [f"{i + 1}. {tracklist[i]}" for i in range(0, rippy_class.TRACK_AMOUNT_INT)]


        print(f"Tracklist (should be {rippy_class.TRACK_AMOUNT_INT} tracks, is {len(string_of_tracklist)}):")
        spaced_print(' '.join([str(elem) for elem in string_of_tracklist]))

    # Ask for confirmation from the user
    special_input(f"If you are not happy with this, open the file called temp_data_{rippy_class.TEMP_STR}.py and change anything you want before continuing. Then press Enter. Otherwise, just press Enter.")
