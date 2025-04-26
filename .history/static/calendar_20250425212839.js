async function fetchCalendar() {
  const res = await fetch("/calendar_data");
  const data = await res.json();

  const todayContainer = document.getElementById("today-events");
  const upcomingContainer = document.getElementById("upcoming-events");

  todayContainer.innerHTML = "";
  upcomingContainer.innerHTML = "";

  data.today.forEach(event => {
    const p = document.createElement("p");
    p.classList.add("event");
    p.textContent = ${event.start} – ${event.summary};
    todayContainer.appendChild(p);
  });

  data.upcoming.forEach(event => {
    const p = document.createElement("p");
    p.classList.add("event");
    p.textContent = ${event.date} ${event.start} – ${event.summary};
    upcomingContainer.appendChild(p);
  });
}

fetchCalendar();
setInterval(fetchCalendar, 60000);