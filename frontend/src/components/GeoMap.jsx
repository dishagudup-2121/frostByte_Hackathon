import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";

export default function GeoMap({ locations }) {

  const defaultCenter = [20.5937, 78.9629]; // India center

  return (
    <MapContainer
      center={defaultCenter}
      zoom={5}
      style={{ height: "400px", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {locations?.map((loc, i) => (
        <Marker key={i} position={[loc.lat, loc.lon]}>
          <Popup>
            {loc.region} <br />
            Sentiment: {loc.sentiment}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
