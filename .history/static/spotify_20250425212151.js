async function getSong() {
    const res = await fetch("/spotify_data");
    const data = await res.json();
    updateSong(data);
  }
  
  function updateSong(song) {
    document.getElementById('spotify-track').textContent = `Song: ${song.name || 'N/A'}`;
    document.getElementById('spotify-artist').textContent = `Artist: ${song.artist || 'N/A'}`;
    document.getElementById('spotify-album').textContent = `Album: ${song.album || 'N/A'}`;
    document.getElementById('spotify-device').textContent = `Device: ${song.device || 'N/A'}`;
  
    const albumCover = document.getElementById('spotify-album-cover');
    if (song.album_cover) {
      albumCover.src = song.album_cover;
      albumCover.alt = `${song.album} album cover`;
    } else {
      albumCover.src = '';
      albumCover.alt = 'No album cover';
    }
  }
  getSong();
  setInterval(getSong, 15000);
  