document.addEventListener('DOMContentLoaded', () => {
    const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
    const tilesUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

    let el = document.getElementById('cldf_map');

    // Only execute on table, query and row pages
    if (el) {
        let tds = document.querySelectorAll('table.rows-and-columns td');

        let lat = document.getElementsByClassName('cldf_latitude');
        let lon = document.getElementsByClassName('cldf_longitude');

        if (lat) {
            let map = L.map(el, {layers: [L.tileLayer(tilesUrl, {
                    maxZoom: 19,
                    detectRetina: true,
                    attribution: attribution
                })]});
            let layer = L.geoJSON({
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [
        parseFloat(lon[0].textContent),
        parseFloat(lat[0].textContent)
    ]
  }
});
            layer.addTo(map);
            map.fitBounds(layer.getBounds(), {
                maxZoom: 2
            });

        }
    }
});