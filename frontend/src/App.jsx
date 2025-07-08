import { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import TorrentList from "./components/TorrentList";
import TorrentForm from "./components/TorrentForm";
import Filters from "./components/Filters";
import "./App.css";

function App() {
  const [torrents, setTorrents] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const fetchTorrents = async () => {
      try {
        const response = await axios.get("http://localhost:8080/torrents");
        setTorrents(response.data);
      } catch (error) {
        toast.error("Błąd pobierania listy torrentów: " + error.message);
      }
    };
    fetchTorrents();
    const interval = setInterval(fetchTorrents, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-dark text-white p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-primary animate-fadeIn">
          Syndra Torrent
        </h1>
        <TorrentForm setTorrents={setTorrents} />
        <Filters setFilter={setFilter} />
        <TorrentList torrents={torrents} filter={filter} setTorrents={setTorrents} />
      </div>
      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}

export default App;
