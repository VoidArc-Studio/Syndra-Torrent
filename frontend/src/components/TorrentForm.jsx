import { useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import { toast } from "react-toastify";

function TorrentForm({ setTorrents }) {
  const [url, setUrl] = useState("");

  const addTorrent = async () => {
    if (!url.match(/^magnet:|^http(s)?:\/\//)) {
      toast.error("Nieprawidłowy link magnet lub URL!");
      return;
    }
    try {
      await axios.post("http://localhost:8080/torrents", { url });
      setUrl("");
      const response = await axios.get("http://localhost:8080/torrents");
      setTorrents(response.data);
      toast.success("Torrent dodany pomyślnie!");
    } catch (error) {
      toast.error("Błąd dodawania torrenta: " + error.message);
    }
  };

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file.name.endsWith(".torrent")) {
      toast.error("Plik musi mieć rozszerzenie .torrent!");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post("http://localhost:8080/torrents/file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const response = await axios.get("http://localhost:8080/torrents");
      setTorrents(response.data);
      toast.success("Plik .torrent dodany pomyślnie!");
    } catch (error) {
      toast.error("Błąd przesyłania pliku: " + error.message);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div className="mb-6">
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Wklej link magnet lub URL pliku .torrent"
          className="flex-1 p-3 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:border-primary"
        />
        <button
          onClick={addTorrent}
          className="px-4 py-3 bg-primary text-white rounded hover:bg-secondary transition"
        >
          Dodaj
        </button>
      </div>
      <div
        {...getRootProps()}
        className={`p-6 border-2 border-dashed rounded text-center ${
          isDragActive ? "border-accent bg-gray-700 animate-pulse" : "border-gray-600 bg-gray-800"
        }`}
      >
        <input {...getInputProps()} />
        <p>Przeciągnij i upuść plik .torrent lub kliknij, aby wybrać</p>
      </div>
    </div>
  );
}

export default TorrentForm;
