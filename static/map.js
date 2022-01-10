window.onload = _ => {
    const map_divs = document.getElementsByClassName("map")
    for (const map_div of map_divs) {
        const map = L.map(map_div)
        const ACCESS_TOKEN = "pk.eyJ1IjoidGhlLWV4aWxlIiwiYSI6ImNreTM5dHpiaDAwMWIycGxnaHlyaHM0NG4ifQ.rQ0NPMwaTznNOKQxtROK1g"
        L.tileLayer(`https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=${ACCESS_TOKEN}`, {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: ACCESS_TOKEN
        }).addTo(map);      
        

        const coordinates = JSON.parse(map_div.getAttribute("coordinates"))
        const markers = []
        for (const coordinate of coordinates) {
            if (coordinate[0] !== -999 && coordinate[1] !== -999) {
                const marker = L.marker(coordinate).addTo(map)
                markers.push(marker)
            }
        }

        if (markers.length > 0) {
            const group = new L.featureGroup(markers);
            map.fitBounds(group.getBounds(), {maxZoom: 5});
        }
        else
        {
            map.setView([0, 0], 1)
        }
    }
}

