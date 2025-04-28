async function loadSports() {
    console.log("🔵 loadSports() started");
    try {
        const res = await fetch('/sports_data');
        const data = await res.json();
        console.log("🟢 JSON parsed:", data);

        const gamesDiv = document.getElementById('games');
        const standingsDiv = document.getElementById('standings');

        gamesDiv.innerHTML = '';
        standingsDiv.innerHTML = '';

        // Games list
        if (data.games.length === 0) {
            gamesDiv.innerHTML = "<p style='text-align:center;'>No games today.</p>";
        } else {
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

        // Standings table
        if (data.divisions.length === 0) {
            standingsDiv.innerHTML = "<p style='text-align:center;'>No standings available.</p>";
        } else {
            let teamIndex = 1;

            data.divisions.forEach(division => {
                const divisionHeader = document.createElement('div');
                divisionHeader.style.fontWeight = 'bold';
                divisionHeader.style.margin = '20px 0 10px';
                divisionHeader.textContent = division.division_name;
                standingsDiv.appendChild(divisionHeader);

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
        console.error("Unable to load sports data", err);
    }
}

window.onload = loadSports;

// Optional: refresh every 5 minutes
// setInterval(loadSports, 300000);