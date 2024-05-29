// custom.js

// Initialize the map
var map = L.map('map').setView([37.8, -96], 4);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Sample TMY3 locations with names, coordinates, state, and ASHRAE climate type
var tmy3Locations = [
    {lat: 38.9445, lng: -77.4558, name: 'Sterling-Washington', state: 'VA', climate: 'Mixed-Humid'},
    {lat: 33.4342, lng: -112.0116, name: 'Phoenix-Sky Harbor', state: 'AZ', climate: 'Hot-Dry'},
    {lat: 36.7762, lng: -119.7181, name: 'Fresno', state: 'CA', climate: 'Hot-Dry'},
    {lat: 39.9088, lng: -105.1165, name: 'Boulder', state: 'CO', climate: 'Cold'},
    {lat: 25.7959, lng: -80.2870, name: 'Miami', state: 'FL', climate: 'Hot-Humid'}
];

// Function to download the EPW file
function downloadEPW(location) {
    fetch('/download_epw', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `location=${encodeURIComponent(location.name)}`
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('selected-location').innerText = location.name + ', ' + location.state;
            document.getElementById('selected-climate').innerText = location.climate;
            alert('File downloaded and saved successfully');
        } else {
            alert('Failed to download file');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred: ' + error);
    });
}

// Add markers to the map
tmy3Locations.forEach(function(location) {
    var marker = L.marker([location.lat, location.lng]).addTo(map);
    marker.bindPopup('<b>' + location.name + ', ' + location.state + '</b><br><button onclick=\'downloadEPW(' + JSON.stringify(location) + ')\'>Select</button>');
});
