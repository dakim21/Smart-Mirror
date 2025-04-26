// CLOCK MODULE
function clock() {
  const now = new Date();
  const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  document.getElementById('clock').textContent = time;
}
clock();
setInterval(clock, 1000);

// WEATHER MODULE
async function weather() {
  const latitude = 44.4759;
  const longitude = -73.2121;
  const url = https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,weather_code&timezone=auto;
  const res = await fetch(url);
  const data = await res.json();
  const temp = data.current.temperature_2m;
  const code = data.current.weather_code;
  const codes = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime Fog", 51: "Light Drizzle", 53: "Drizzle",
    55: "Heavy Drizzle", 61: "Light Rain", 63: "Rain", 65: "Heavy Rain"
  };
  document.getElementById('weather').textContent = ${temp}°C, ${codes[code] || "Unknown"};
}
weather();
setInterval(weather, 1800000);