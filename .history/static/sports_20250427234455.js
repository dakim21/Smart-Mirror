/*
Sports Module
1. Fetches today's MLB games and current standings from Flask backend (/sports_data)
2. Clears and updates games list
3. Clears and updates standings table
4. Displays fallback messages if no games or standings are available
5. Automatically loads sports data when the page finishes loading
*/

async function loadSports() {
    try {
        //send GET request to flask /sports_data route
        const res = await fetch('/sports_data');
        const data = await res.json();

        //get references to DOM element
        const gamesDiv = document.getElementById('games');
        const standingsDiv = document.getElementById('standings');

        //clear exisiting content
        gamesDiv.innerHTML = '';
        standingsDiv.innerHTML = '';

        //games list
        if (data.games.length === 0) {
            //if no games today display "no games today"
            gamesDiv.innerHTML = "<p style='text-align:center;'>No games today.</p>";
        } else {
            //if games detected today, render each game
            data.games.forEach(game => {
                const row = document.createElement('div');
                row.className = 'game-row';
                row.innerHTML = `
                    <div class="team-name">
                        ${game.away}<br><span style="opacity: 0.8;">vs ${game.home}</span>
                    </div>
                    <div style="white-space: nowrap;">${game.time}</div>
                `;
                gamesDiv.appendChild(row);
            });
        }

        //standings table
        if (data.divisions.length === 0) {
            standingsDiv.innerHTML = "<p style='text-align:center;'>No standings available.</p>";
        } else {
            let teamIndex = 1;

            data.divisions.forEach(division => {
                //render division header
                const divisionHeader = document.createElement('div');
                divisionHeader.style.fontWeight = 'bold';
                divisionHeader.style.margin = '20px 0 10px';
                divisionHeader.textContent = division.division_name;
                standingsDiv.appendChild(divisionHeader);
                
                //render each team inside the division
                division.teams.forEach(team => {
                    const row = document.createElement('div');
                    row.className = 'standing-row';
                    row.innerHTML = `
                        <div class="team-name">${team.name}</div>
                        <div style="width: 32px; text-align: right;">${team.wins}</div>
                        <div style="width: 32px; text-align: right;">${team.losses}</div>
                        <div style="width: 60px; text-align: right;">${team.win_p}</div>
                        <div style="width: 40px; text-align: right;">${team.games_back}</div>
                        <div style="width: 48px; text-align: right;">${team.last_10}</div>
                    `;
                    standingsDiv.appendChild(row);
                    teamIndex++;
                });
            });
        }

    } catch (err) {
        //catch any errors
        console.error("Unable to load sports data", err);
    }
}

//run loadSports once the frame finishes loading
window.onload = loadSports;