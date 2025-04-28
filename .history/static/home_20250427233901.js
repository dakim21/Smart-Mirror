/*
Clock and Weather Modules
1. Displays current time updated every second
2. Fetches current temperature and weather code from Open-Meteo API
3. Maps weather codes to readable text descriptions
4. Updates weather information automatically every 30 minutes
*/

//CLOCK MODULE
function clock() {
  //get current system time from rpi
  const now = new Date();

  //format time as XX:XX using 2 digit padding
  const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  //update clock element with formatted time
  document.getElementById('clock').textContent = time;
}

//initialize clock
clock();

//update clock every second
setInterval(clock, 1000);

// WEATHER MODULE
async function weather() {
  //coords for Burlington, VT
  const latitude = 44.4759;
  const longitude = -73.2121;

  //construct Open-Meteo API URL with current temp and weather code
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,weather_code&timezone=auto`;

  //fetch weather data
  const res = await fetch(url);
  const data = await res.json();

  //extract temp and weather code
  const temp = data.current.temperature_2m;
  const code = data.current.weather_code;

  //map weather codes to forecast strings (ex: 0 to "Clear")
  const codes = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime Fog", 51: "Light Drizzle", 53: "Drizzle",
    55: "Heavy Drizzle", 61: "Light Rain", 63: "Rain", 65: "Heavy Rain"
  };

  //update weather elemtn with current temp and desc
  document.getElementById('weather').textContent = `${temp}°C, ${codes[code] || "Unknown"}`;
}

//initialize weather
weather();

//update weather every 30 min
setInterval(weather, 1800000);
