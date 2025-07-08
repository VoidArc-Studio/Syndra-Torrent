import { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import TorrentDetailsModal from "./TorrentDetailsModal";

function TorrentList({ torrents, filter, setTorrents }) {
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");
  const [selectedTorrent, setSelectedTorrent] = useState(null);

  const toggleTorrent = async (id, paused) => {
    try {
      await axios.post(`http://localhost:8080/torrents/${id}/${paused ? "resume" : "pause"}`);
      const response = await axios.get("http://localhost:8080/torrents");
      setTorrents(response.data);
      toast.success(`Torrent ${paused ? "wznowiony" : "wstrzymany"}!`);
    } catch (error) {
      toast.error("Błąd zmiany statusu torrenta: " + error.message);
    }
  };

  const deleteTorrent = async (id) => {
    try {
      await axios.delete(`http://localhost:8080/torrents/${id}`);
      const response = await axios.get("http://localhost:8080/torrents");
      setTorrents(response.data);
      toast.success("Torrent usunięty pomyślnie!");
    } catch (error) {
      toast.error("Błąd usuwania torrenta: " + error.message);
    }
  };

  const filteredTorrents = torrents
    .filter((torrent) => {
      if (filter === "active") return !torrent.paused && torrent.progress < 100;
      if (filter === "paused") return torrent.paused;
      if (filter === "completed") return torrent.progress === 100;
      return true;
    })
    .sort((a, b) => {
      const order = sortOrder === "asc" ? 1 : -1;
      return a[sortBy] > b[sortBy] ? order : -order;
    });

  return (
    <div className="bg-gray-800 rounded shadow overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="bg-gray-700">
            <th
              className="p-3 text-left cursor-pointer"
              onClick={() => {
                setSortBy("name");
                setSortOrder(sortBy === "name" && sortOrder === "asc" ? "desc" : "asc");
              }}
            >
              Nazwa {sortBy === "name" && (sortOrder === "asc" ? "↑" : "↓")}
            </th>
            <th
              className="p-3 text-left cursor-pointer"
              onClick={() => {
                setSortBy("progress");
                setSortOrder(sortBy === "progress" && sortOrder === "asc" ? "desc" : "asc");
              }}
            >
              Postęp {sortBy === "progress" && (sortOrder === "asc" ? "↑" : "↓")}
            </th>
            <th
              className="p-3 text-left cursor-pointer"
              onClick={() => {
                setSortBy("speed");
                setSortOrder(sortBy === "speed" && sortOrder === "asc" ? "desc" : "asc");
              }}
            >
              Prędkość {sortBy === "speed" && (sortOrder === "asc" ? "↑" : "↓")}
            </th>
            <th className="p-3 text-left">Akcje</th>
          </tr>
        </thead>
        <tbody>
          {filteredTorrents.map((torrent) => (
            <tr
              key={torrent.id}
              className="border-t border-gray-700 hover:bg-gray-600 transition cursor-pointer"
              onClick={() => setSelectedTorrent(torrent)}
            >
              <td className="p-3">{torrent.name}</td>
              <td className="p-3">
                <div className="w-full bg-gray-600 rounded h-2">
                  <div
                    className="bg-gradient-to-r from-primary to-secondary h-2 rounded"
                    style={{ width: `${torrent.progress}%` }}
                  ></div>
                </div>
              </td>
              <td className="p-3">{torrent.speed} KB/s</td>
              <td className="p-3 flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleTorrent(torrent.id, torrent.paused);
                  }}
                  className="px-2 py-1 bg-secondary text-white rounded hover:bg-primary transition"
                >
                  {torrent.paused ? "Wznów" : "Wstrzymaj"}
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteTorrent(torrent.id);
                  }}
                  className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition"
                >
                  Usuń
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {selectedTorrent && (
        <TorrentDetailsModal
          torrent={selectedTorrent}
          onClose={() => setSelectedTorrent(null)}
        />
      )}
    </div>
  );
}

export default TorrentList;
