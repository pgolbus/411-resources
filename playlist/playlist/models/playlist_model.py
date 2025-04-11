import logging
from typing import List

from playlist.models.song_model import Song, update_play_count
from playlist.utils.api_utils import get_random
from playlist.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class PlaylistModel:
    """
    A class to manage a playlist of songs.

    Attributes:
        current_track_number (int): The current track number being played.
                                    Track number starts at 1
        playlist (List[Song]): The list of songs in the playlist.

    """

    def __init__(self):
        """Initializes the PlaylistModel with an empty playlist and the current track set to 1.

        """
        self.current_track_number = 1
        self.playlist: List[Song] = []


    ##################################################
    # Song Management Functions
    ##################################################


    def add_song_to_playlist(self, song: Song) -> None:
        """Adds a song to the playlist.

        Args:
            song (Song): The song to add to the playlist.

        Raises:
            TypeError: If the song is not a valid Song instance.
            ValueError: If a song with the same 'id' already exists.

        """
        logger.info("Received request to add a song to the playlist")

        if not isinstance(song, Song):
            logger.error("Invalid type: Song is not a valid Song instance")
            raise TypeError("Song is not a valid Song instance")

        song_id = self.validate_song_id(song.id, check_in_playlist=False)
        if song_id in [s.id for s in self.playlist]:
            logger.error(f"Song with ID {song.id} already exists in the playlist")
            raise ValueError(f"Song with ID {song.id} already exists in the playlist")

        self.playlist.append(song)
        logger.info(f"Successfully added song to playlist: {song.artist} - {song.title} ({song.year})")

    def remove_song_by_song_id(self, song_id: int) -> None:
        """Removes a song from the playlist by its song ID.

        Args:
            song_id (int): The ID of the song to remove from the playlist.

        Raises:
            ValueError: If the playlist is empty or the song ID is invalid.

        """
        logger.info(f"Received request to remove song with ID {song_id}")

        self.check_if_empty()
        song_id = self.validate_song_id(song_id)

        if song_id not in [s.id for s in self.playlist]:
            logger.warning(f"Song with ID {song_id} not found in the playlist")
            raise ValueError(f"Song with ID {song_id} not found in the playlist")

        self.playlist = [s for s in self.playlist if s.id != song_id]
        logger.info(f"Successfully removed song with ID {song_id} from the playlist")

    def remove_song_by_track_number(self, track_number: int) -> None:
        """Removes a song from the playlist by its track number (1-indexed).

        Args:
            track_number (int): The track number of the song to remove.

        Raises:
            ValueError: If the playlist is empty or the track number is invalid.

        """
        logger.info(f"Received request to remove song at track number {track_number}")

        self.check_if_empty()
        track_number = self.validate_track_number(track_number)
        playlist_index = track_number - 1

        logger.info(f"Successfully removed song: {self.playlist[playlist_index].artist} - {self.playlist[playlist_index].title} ({self.playlist[playlist_index].year})")
        del self.playlist[playlist_index]

    def clear_playlist(self) -> None:
        """Clears all songs from the playlist.

        Clears all songs from the playlist. If the playlist is already empty, logs a warning.

        """
        logger.info("Received request to clear the playlist")

        try:
            if self.check_if_empty():
                pass
        except ValueError:
            logger.warning("Clearing an empty playlist")

        self.playlist.clear()
        logger.info("Successfully cleared the playlist")


    ##################################################
    # Playlist Retrieval Functions
    ##################################################


    def get_all_songs(self) -> List[Song]:
        """Returns a list of all songs in the playlist.

        Returns:
            List[Song]: A list of all songs in the playlist.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()
        logger.info("Retrieving all songs in the playlist")
        return self.playlist

    def get_song_by_song_id(self, song_id: int) -> Song:
        """Retrieves a song from the playlist by its song ID.

        Args:
            song_id (int): The ID of the song to retrieve.

        Returns:
            Song: The song with the specified ID.

        Raises:
            ValueError: If the playlist is empty or the song is not found.

        """
        self.check_if_empty()
        song_id = self.validate_song_id(song_id)
        logger.info(f"Retrieving song with ID {song_id} from the playlist")

        song = next((s for s in self.playlist if s.id == song_id), None)
        if not song:
            logger.warning(f"Song with ID {song_id} not found in the playlist")
            raise ValueError(f"Song with ID {song_id} not found in the playlist")

        logger.info(f"Successfully retrieved song: {song.artist} - {song.title} ({song.year})")
        return song

    def get_song_by_track_number(self, track_number: int) -> Song:
        """Retrieves a song from the playlist by its track number (1-indexed).

        Args:
            track_number (int): The track number of the song to retrieve.

        Returns:
            Song: The song at the specified track number.

        Raises:
            ValueError: If the playlist is empty or the track number is invalid.

        """
        self.check_if_empty()
        track_number = self.validate_track_number(track_number)
        playlist_index = track_number - 1

        logger.info(f"Retrieving song at track number {track_number} from playlist")
        song = self.playlist[playlist_index]
        logger.info(f"Successfully retrieved song: {song.artist} - {song.title} ({song.year})")
        return song

    def get_current_song(self) -> Song:
        """Returns the current song being played.

        Returns:
            Song: The currently playing song.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()
        logger.info("Retrieving the current song being played")
        return self.get_song_by_track_number(self.current_track_number)

    def get_playlist_length(self) -> int:
        """Returns the number of songs in the playlist.

        Returns:
            int: The total number of songs in the playlist.

        """
        length = len(self.playlist)
        logger.info(f"Retrieving playlist length: {length} songs")
        return length

    def get_playlist_duration(self) -> int:
        """Returns the total duration of the playlist in seconds.

        Returns:
            int: The total duration of all songs in the playlist in seconds.

        """
        total_duration = sum(song.duration for song in self.playlist)
        logger.info(f"Retrieving total playlist duration: {total_duration} seconds")
        return total_duration


    ##################################################
    # Playlist Movement Functions
    ##################################################


    def go_to_track_number(self, track_number: int) -> None:
        """Sets the current track number to the specified track number.

        Args:
            track_number (int): The track number to set as the current track.

        Raises:
            ValueError: If the playlist is empty or the track number is invalid.

        """
        self.check_if_empty()
        track_number = self.validate_track_number(track_number)
        logger.info(f"Setting current track number to {track_number}")
        self.current_track_number = track_number

    def go_to_random_track(self) -> None:
        """Sets the current track number to a randomly selected track.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()

        # Get a random index using the random.org API
        random_track = get_random(self.get_playlist_length())

        logger.info(f"Setting current track number to random track: {random_track}")
        self.current_track_number = random_track

    def move_song_to_beginning(self, song_id: int) -> None:
        """Moves a song to the beginning of the playlist.

        Args:
            song_id (int): The ID of the song to move.

        Raises:
            ValueError: If the playlist is empty or the song ID is invalid.

        """
        logger.info(f"Moving song with ID {song_id} to the beginning of the playlist")
        self.check_if_empty()
        song_id = self.validate_song_id(song_id)
        song = self.get_song_by_song_id(song_id)

        self.playlist.remove(song)
        self.playlist.insert(0, song)

        logger.info(f"Successfully moved song with ID {song_id} to the beginning")

    def move_song_to_end(self, song_id: int) -> None:
        """Moves a song to the end of the playlist.

        Args:
            song_id (int): The ID of the song to move.

        Raises:
            ValueError: If the playlist is empty or the song ID is invalid.

        """
        logger.info(f"Moving song with ID {song_id} to the end of the playlist")
        self.check_if_empty()
        song_id = self.validate_song_id(song_id)
        song = self.get_song_by_song_id(song_id)

        self.playlist.remove(song)
        self.playlist.append(song)

        logger.info(f"Successfully moved song with ID {song_id} to the end")

    def move_song_to_track_number(self, song_id: int, track_number: int) -> None:
        """Moves a song to a specific track number in the playlist.

        Args:
            song_id (int): The ID of the song to move.
            track_number (int): The track number to move the song to (1-indexed).

        Raises:
            ValueError: If the playlist is empty, the song ID is invalid, or the track number is out of range.

        """
        logger.info(f"Moving song with ID {song_id} to track number {track_number}")
        self.check_if_empty()
        song_id = self.validate_song_id(song_id)
        track_number = self.validate_track_number(track_number)

        playlist_index = track_number - 1
        song = self.get_song_by_song_id(song_id)

        self.playlist.remove(song)
        self.playlist.insert(playlist_index, song)

        logger.info(f"Successfully moved song with ID {song_id} to track number {track_number}")

    def swap_songs_in_playlist(self, song1_id: int, song2_id: int) -> None:
        """Swaps the positions of two songs in the playlist.

        Args:
            song1_id (int): The ID of the first song to swap.
            song2_id (int): The ID of the second song to swap.

        Raises:
            ValueError: If the playlist is empty, either song ID is invalid, or attempting to swap the same song.

        """
        logger.info(f"Swapping songs with IDs {song1_id} and {song2_id}")
        self.check_if_empty()
        song1_id = self.validate_song_id(song1_id)
        song2_id = self.validate_song_id(song2_id)

        if song1_id == song2_id:
            logger.error(f"Cannot swap a song with itself: {song1_id}")
            raise ValueError(f"Cannot swap a song with itself: {song1_id}")

        song1 = self.get_song_by_song_id(song1_id)
        song2 = self.get_song_by_song_id(song2_id)
        index1, index2 = self.playlist.index(song1), self.playlist.index(song2)

        self.playlist[index1], self.playlist[index2] = self.playlist[index2], self.playlist[index1]

        logger.info(f"Successfully swapped songs with IDs {song1_id} and {song2_id}")


    ##################################################
    # Playlist Playback Functions
    ##################################################


    def play_current_song(self) -> None:
        """Plays the current song and advances the playlist.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()
        current_song = self.get_song_by_track_number(self.current_track_number)

        logger.info(f"Playing song: {current_song.title} (ID: {current_song.id}) at track number: {self.current_track_number}")
        update_play_count(current_song.id)
        logger.info(f"Updated play count for song: {current_song.title} (ID: {current_song.id})")

        self.current_track_number = (self.current_track_number % self.get_playlist_length()) + 1
        logger.info(f"Advanced to track number: {self.current_track_number}")

    def play_entire_playlist(self) -> None:
        """Plays all songs in the playlist from the beginning.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()
        logger.info("Starting to play the entire playlist.")

        self.current_track_number = 1
        for _ in range(self.get_playlist_length()):
            self.play_current_song()

        logger.info("Finished playing the entire playlist.")

    def play_rest_of_playlist(self) -> None:
        """Plays the remaining songs in the playlist from the current track onward.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()
        logger.info(f"Playing the rest of the playlist from track number: {self.current_track_number}")

        for _ in range(self.get_playlist_length() - self.current_track_number + 1):
            self.play_current_song()

        logger.info("Finished playing the rest of the playlist.")

    def rewind_playlist(self) -> None:
        """Resets the playlist to the first track.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()
        self.current_track_number = 1
        logger.info("Rewound playlist to the first track.")


    ##################################################
    # Utility Functions
    ##################################################


    ####################################################################################################
    #
    # Note: I am only testing these things once. EG I am not testing that everything rejects an empty
    # list as they all do so by calling this helper
    #
    ####################################################################################################

    def validate_song_id(self, song_id: int, check_in_playlist: bool = True) -> int:
        """
        Validates the given song ID, ensuring it is a non-negative integer.

        Args:
            song_id (int): The song ID to validate.
            check_in_playlist (bool, optional): If True, checks if the song ID exists in the playlist.
                                                If False, skips the check. Defaults to True.

        Returns:
            int: The validated song ID.

        Raises:
            ValueError: If the song ID is not a valid non-negative integer or not found in the playlist.

        """
        try:
            song_id = int(song_id)
            if song_id < 0:
                raise ValueError(f"Invalid song id: {song_id}")
        except ValueError as e:
            logger.error(f"Invalid song id: {song_id}")
            raise ValueError(f"Invalid song id: {song_id}") from e

        if check_in_playlist:
            song_ids = {song.id for song in self.playlist}  # Convert to set for O(1) lookup
            if song_id not in song_ids:
                logger.error(f"Song with id {song_id} not found in playlist")
                raise ValueError(f"Song with id {song_id} not found in playlist")

        return song_id

    def validate_track_number(self, track_number: int) -> int:
        """
        Validates the given track number, ensuring it is within the playlist's range.

        Args:
            track_number (int): The track number to validate.

        Returns:
            int: The validated track number.

        Raises:
            ValueError: If the track number is not a valid positive integer or is out of range.

        """
        try:
            track_number = int(track_number)
            if not (1 <= track_number <= self.get_playlist_length()):
                raise ValueError(f"Invalid track number: {track_number}")
        except ValueError as e:
            logger.error(f"Invalid track number: {track_number}")
            raise ValueError(f"Invalid track number: {track_number}") from e

        return track_number

    def check_if_empty(self) -> None:
        """
        Checks if the playlist is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the playlist is empty.

        """
        if not self.playlist:
            logger.error("Playlist is empty")
            raise ValueError("Playlist is empty")
