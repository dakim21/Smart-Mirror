/*
Calendar Events Fetcher
1. Fetches calendar event data from the Flask backend at /calendar_data
2. Clears and updates today's events section dynamically
3. Clears and updates upcoming events section dynamically
4. Refreshes event data automatically every 30 seconds
*/

async function fetchCalendar() {
  //send GET request to flask /calendar_data route
  const res = await fetch("/calendar_data");
  const data = await res.json();

  //get references to the DOM containers for events
  const todayContainer = document.getElementById("today-events");
  const upcomingContainer = document.getElementById("upcoming-events");

  //clear current events before updating
  todayContainer.innerHTML = "";
  upcomingContainer.innerHTML = "";

  //render today's events
  data.today.forEach(event => {
    const p = document.createElement("p");
    p.classList.add("event");
    p.textContent = `${event.start} - ${event.summary}`;
    todayContainer.appendChild(p);
  });

  //render upcoming events
  data.upcoming.forEach(event => {
    const p = document.createElement("p");
    p.classList.add("event");
    p.textContent = `${event.date} ${event.start} - ${event.summary}`;
    upcomingContainer.appendChild(p);
  });
}

//initial fetcch on page load
fetchCalendar();

//refresh events every 30 seconds to stay updated
setInterval(fetchCalendar, 300000);
