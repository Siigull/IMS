import osmium, folium
from shapely.geometry import LineString

bbox = (16.462276, 49.265380, 16.718942, 49.104087)

class SimpleExtract(osmium.SimpleHandler):
    def __init__(self, bbox):
        super().__init__()
        self.minlon, self.minlat, self.maxlon, self.maxlat = bbox
        self.ways = []

    def way(self, w):
        coords = [(n.location.lat, n.location.lon) for n in w.nodes if n.location.valid()]
        if not coords:
            return

        # Compute bounding box manually
        lats = [lat for lat, lon in coords]
        lons = [lon for lat, lon in coords]
        if (min(lons) > self.maxlon or max(lons) < self.minlon or
            min(lats) > self.maxlat or max(lats) < self.minlat):
            return  # way is completely outside

        self.ways.append(coords)

# Load file and extract
extractor = SimpleExtract(bbox)
extractor.apply_file("maps_czechia/250901.osm.pbf", locations=True, idx='flex_mem')

# Create simple folium map
m = folium.Map(location=[(bbox[1]+bbox[3])/2, (bbox[0]+bbox[2])/2], zoom_start=13)

# Draw lines
for coords in extractor.ways[:500]:  # limit to avoid overload
    folium.PolyLine(coords, color="blue", weight=1).add_to(m)

m.save("osm_area.html")
# print("✅ Saved as osm_area.html")