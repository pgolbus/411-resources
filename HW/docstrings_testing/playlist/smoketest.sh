#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Song Management
#
##########################################################

create_song() {
  artist=$1
  title=$2
  year=$3
  genre=$4
  duration=$5

  echo "Adding song ($artist - $title, $year) to the playlist..."
  curl -s -X POST "$BASE_URL/create-song" -H "Content-Type: application/json" \
    -d "{\"artist\":\"$artist\", \"title\":\"$title\", \"year\":$year, \"genre\":\"$genre\", \"duration\":$duration}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Song added successfully."
  else
    echo "Failed to add song."
    exit 1
  fi
}

delete_song_by_id() {
  song_id=$1

  echo "Deleting song by ID ($song_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-song/$song_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song deleted successfully by ID ($song_id)."
  else
    echo "Failed to delete song by ID ($song_id)."
    exit 1
  fi
}

get_all_songs() {
  echo "Getting all songs in the playlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-songs-from-catalog")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All songs retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Songs JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get songs."
    exit 1
  fi
}

get_song_by_id() {
  song_id=$1

  echo "Getting song by ID ($song_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-song-from-catalog-by-id/$song_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song retrieved successfully by ID ($song_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON (ID $song_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get song by ID ($song_id)."
    exit 1
  fi
}

get_song_by_compound_key() {
  artist=$1
  title=$2
  year=$3

  echo "Getting song by compound key (Artist: '$artist', Title: '$title', Year: $year)..."
  response=$(curl -s -X GET "$BASE_URL/get-song-from-catalog-by-compound-key?artist=$(echo $artist | sed 's/ /%20/g')&title=$(echo $title | sed 's/ /%20/g')&year=$year")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song retrieved successfully by compound key."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON (by compound key):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get song by compound key."
    exit 1
  fi
}

get_random_song() {
  echo "Getting a random song from the catalog..."
  response=$(curl -s -X GET "$BASE_URL/get-random-song")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random song retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get a random song."
    exit 1
  fi
}


############################################################
#
# Playlist Management
#
############################################################

add_song_to_playlist() {
  artist=$1
  title=$2
  year=$3

  echo "Adding song to playlist: $artist - $title ($year)..."
  response=$(curl -s -X POST "$BASE_URL/add-song-to-playlist" \
    -H "Content-Type: application/json" \
    -d "{\"artist\":\"$artist\", \"title\":\"$title\", \"year\":$year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song added to playlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add song to playlist."
    exit 1
  fi
}

remove_song_from_playlist() {
  artist=$1
  title=$2
  year=$3

  echo "Removing song from playlist: $artist - $title ($year)..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-song-from-playlist" \
    -H "Content-Type: application/json" \
    -d "{\"artist\":\"$artist\", \"title\":\"$title\", \"year\":$year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song removed from playlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to remove song from playlist."
    exit 1
  fi
}

remove_song_by_track_number() {
  track_number=$1

  echo "Removing song by track number: $track_number..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-song-from-playlist-by-track-number/$track_number")

  if echo "$response" | grep -q '"status":'; then
    echo "Song removed from playlist by track number ($track_number) successfully."
  else
    echo "Failed to remove song from playlist by track number."
    exit 1
  fi
}

clear_playlist() {
  echo "Clearing playlist..."
  response=$(curl -s -X POST "$BASE_URL/clear-playlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Playlist cleared successfully."
  else
    echo "Failed to clear playlist."
    exit 1
  fi
}


############################################################
#
# Play Playlist
#
############################################################

play_current_song() {
  echo "Playing current song..."
  response=$(curl -s -X POST "$BASE_URL/play-current-song")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current song is now playing."
  else
    echo "Failed to play current song."
    exit 1
  fi
}

rewind_playlist() {
  echo "Rewinding playlist..."
  response=$(curl -s -X POST "$BASE_URL/rewind-playlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Playlist rewound successfully."
  else
    echo "Failed to rewind playlist."
    exit 1
  fi
}

get_all_songs_from_playlist() {
  echo "Retrieving all songs from playlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-songs-from-playlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All songs retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Songs JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all songs from playlist."
    exit 1
  fi
}

get_song_from_playlist_by_track_number() {
  track_number=$1
  echo "Retrieving song by track number ($track_number)..."
  response=$(curl -s -X GET "$BASE_URL/get-song-from-playlist-by-track-number/$track_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song retrieved successfully by track number."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve song by track number."
    exit 1
  fi
}

get_current_song() {
  echo "Retrieving current song..."
  response=$(curl -s -X GET "$BASE_URL/get-current-song")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current song retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Current Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve current song."
    exit 1
  fi
}

get_playlist_length_duration() {
  echo "Retrieving playlist length and duration..."
  response=$(curl -s -X GET "$BASE_URL/get-playlist-length-duration")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Playlist length and duration retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Playlist Info JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve playlist length and duration."
    exit 1
  fi
}

go_to_track_number() {
  track_number=$1
  echo "Going to track number ($track_number)..."
  response=$(curl -s -X POST "$BASE_URL/go-to-track-number/$track_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Moved to track number ($track_number) successfully."
  else
    echo "Failed to move to track number ($track_number)."
    exit 1
  fi
}

play_entire_playlist() {
  echo "Playing entire playlist..."
  curl -s -X POST "$BASE_URL/play-entire-playlist" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Entire playlist played successfully."
  else
    echo "Failed to play entire playlist."
    exit 1
  fi
}

# Function to play the rest of the playlist
play_rest_of_playlist() {
  echo "Playing rest of the playlist..."
  curl -s -X POST "$BASE_URL/play-rest-of-playlist" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Rest of playlist played successfully."
  else
    echo "Failed to play rest of playlist."
    exit 1
  fi
}

############################################################
#
# Arrange Playlist
#
############################################################

move_song_to_beginning() {
  artist=$1
  title=$2
  year=$3

  echo "Moving song ($artist - $title, $year) to the beginning of the playlist..."
  response=$(curl -s -X POST "$BASE_URL/move-song-to-beginning" \
    -H "Content-Type: application/json" \
    -d "{\"artist\": \"$artist\", \"title\": \"$title\", \"year\": $year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song moved to the beginning successfully."
  else
    echo "Failed to move song to the beginning."
    exit 1
  fi
}

move_song_to_end() {
  artist=$1
  title=$2
  year=$3

  echo "Moving song ($artist - $title, $year) to the end of the playlist..."
  response=$(curl -s -X POST "$BASE_URL/move-song-to-end" \
    -H "Content-Type: application/json" \
    -d "{\"artist\": \"$artist\", \"title\": \"$title\", \"year\": $year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song moved to the end successfully."
  else
    echo "Failed to move song to the end."
    exit 1
  fi
}

move_song_to_track_number() {
  artist=$1
  title=$2
  year=$3
  track_number=$4

  echo "Moving song ($artist - $title, $year) to track number ($track_number)..."
  response=$(curl -s -X POST "$BASE_URL/move-song-to-track-number" \
    -H "Content-Type: application/json" \
    -d "{\"artist\": \"$artist\", \"title\": \"$title\", \"year\": $year, \"track_number\": $track_number}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song moved to track number ($track_number) successfully."
  else
    echo "Failed to move song to track number ($track_number)."
    exit 1
  fi
}

swap_songs_in_playlist() {
  track_number1=$1
  track_number2=$2

  echo "Swapping songs at track numbers ($track_number1) and ($track_number2)..."
  response=$(curl -s -X POST "$BASE_URL/swap-songs-in-playlist" \
    -H "Content-Type: application/json" \
    -d "{\"track_number_1\": $track_number1, \"track_number_2\": $track_number2}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Songs swapped successfully between track numbers ($track_number1) and ($track_number2)."
  else
    echo "Failed to swap songs."
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Function to get the song leaderboard sorted by play count
get_song_leaderboard() {
  echo "Getting song leaderboard sorted by play count..."
  response=$(curl -s -X GET "$BASE_URL/song-leaderboard?sort=play_count")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by play count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get song leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Create songs
create_song "The Beatles" "Hey Jude" 1968 "Rock" 180
create_song "The Rolling Stones" "Paint It Black" 1966 "Rock" 180
create_song "The Beatles" "Let It Be" 1970 "Rock" 180
create_song "Queen" "Bohemian Rhapsody" 1975 "Rock" 180
create_song "Led Zeppelin" "Stairway to Heaven" 1971 "Rock" 180

delete_song_by_id 1
get_all_songs

get_song_by_id 2
get_song_by_compound_key "The Beatles" "Let It Be" 1970
get_random_song

add_song_to_playlist "The Rolling Stones" "Paint It Black" 1966
add_song_to_playlist "Queen" "Bohemian Rhapsody" 1975
add_song_to_playlist "Led Zeppelin" "Stairway to Heaven" 1971
add_song_to_playlist "The Beatles" "Let It Be" 1970

remove_song_from_playlist "The Beatles" "Let It Be" 1970
remove_song_by_track_number 2

get_all_songs_from_playlist

add_song_to_playlist "Queen" "Bohemian Rhapsody" 1975
add_song_to_playlist "The Beatles" "Let It Be" 1970

move_song_to_beginning "The Beatles" "Let It Be" 1970
move_song_to_end "Queen" "Bohemian Rhapsody" 1975
move_song_to_track_number "Led Zeppelin" "Stairway to Heaven" 1971 2
swap_songs_in_playlist 1 2

get_all_songs_from_playlist
get_song_from_playlist_by_track_number 1

get_playlist_length_duration

play_current_song
rewind_playlist

play_entire_playlist
play_current_song
play_rest_of_playlist

get_song_leaderboard

echo "All tests passed successfully!"
