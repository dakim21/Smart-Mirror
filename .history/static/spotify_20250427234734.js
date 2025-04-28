/*
Spotify Module
1. Fetches currently playing song information from Flask backend (/spotify_data)
2. Updates song name, artist name, album name, and playback device dynamically on the page
3. Updates the album cover image if available
4. Automatically fetches and updates song information every 15 seconds
*/

async function getSong() {
  //send get request to Flask /spotify_data route
  const res = await fetch("/spotify_data");
  const data = await res.json();

  //update DOM elements with current song info
  updateSong(data);
}

function updateSong(song) {
//update each text field with their respective song details
  document.getElementById('spotify-track').textContent = `Song: ${song.name || 'N/A'}`;
  document.getElementById('spotify-artist').textContent = `Artist: ${song.artist || 'N/A'}`;
  document.getElementById('spotify-album').textContent = `Album: ${song.album || 'N/A'}`;
  document.getElementById('spotify-device').textContent = `Device: ${song.device || 'N/A'}`;

  //update album cover image (if there is one)
  const albumCover = document.getElementById('spotify-album-cover');
  if (song.album_cover) {
    albumCover.src = song.album_cover;
    albumCover.alt = `${song.album} album cover`;
  } else {
    albumCover.src = '';
    albumCover.alt = 'No album cover';
  }
}

//initial fetch when page loads
getSong();

//refresh song info every 10 seconds
setInterval(getSong, 10000);