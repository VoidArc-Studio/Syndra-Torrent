import { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";

function TorrentDetailsModal({ torrent, onClose }) {
  const [details, setDetails] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:8080/torrents/${torrent.id}/details`);
        setDetails(response.data);
      } catch (error) {
        toast.error("Błąd pobierania szczegółów: " + error.message);
      }
    };
    fetchDetails();
  }, [torrent.id]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-gray-800 rounded p-6 max-w-lg w-full">
        <h2 className="text-2xl font-bold mb-4">{torrent.name}</h2>
        {details ? (
          <div>
            <p><strong>Postęp:</strong> {torrent.progress}%</p>
            <p><strong>Prędkość:</strong> {torrent.speed} KB/s</p>
            <p><strong>Seeders:</strong> {details.seeders}</p>
            <p><strong>Peers:</strong> {details.peers}</p>
            <p><strong>Pliki:</strong></p>
            <ul className="list-disc pl-5">
              {details.files.map((file, index) => (
                <li key={index}>{file}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p>Ładowanie szczegółów...</p>
        )}
        <button
          onClick={onClose}
          className="mt-4 px-4 py-2 bg-primary text-white rounded hover:bg-secondary transition"
        >
          Zamknij
        </button>
      </div>
    </div>
  );
}

export default TorrentDetailsModal;
