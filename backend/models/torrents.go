package handlers

import (
    "encoding/json"
    "io"
    "net/http"
    "os"
    "github.com/anacrolix/torrent"
    "github.com/gorilla/mux"
    "syndra-torrent/models"
)

var (
    torrents = make(map[string]*torrent.Torrent)
    mu       sync.RWMutex
    client   *torrent.Client
)

func SetClient(c *torrent.Client) {
    client = c
}

func GetTorrents(w http.ResponseWriter, r *http.Request) {
    mu.RLock()
    defer mu.RUnlock()
    var torrentList []models.Torrent
    for id, t := range torrents {
        stats := t.Stats()
        files := []string{}
        for _, f := range t.Files() {
            files = append(files, f.Path())
        }
        torrentList = append(torrentList, models.Torrent{
            ID:       id,
            Name:     t.Name(),
            Progress: float64(t.BytesCompleted()) / float64(t.Length()) * 100,
            Speed:    float64(stats.BytesReadData.Int64()) / 1024, // KB/s
            Paused:   !t.IsSeeding() && t.BytesMissing() > 0 && stats.ActivePeers == 0,
            Seeders:  stats.ActivePeers,
            Peers:    stats.TotalPeers,
            Files:    files,
        })
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(torrentList)
}

func AddTorrent(w http.ResponseWriter, r *http.Request) {
    var input struct {
        URL string `json:"url"`
    }
    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        http.Error(w, "Invalid request", http.StatusBadRequest)
        return
    }
    if !strings.HasPrefix(input.URL, "magnet:") && !strings.HasPrefix(input.URL, "http") {
        http.Error(w, "Invalid URL or magnet link", http.StatusBadRequest)
        return
    }

    mu.Lock()
    defer mu.Unlock()
    if len(torrents) >= 50 { // Limit torrentów
        http.Error(w, "Too many torrents", http.StatusTooManyRequests)
        return
    }

    t, err := client.AddMagnet(input.URL)
    if err != nil {
        http.Error(w, "Error adding torrent: "+err.Error(), http.StatusInternalServerError)
        return
    }
    <-t.GotInfo()
    t.DownloadAll()
    torrents[t.InfoHash().String()] = t

    w.WriteHeader(http.StatusOK)
}

func AddTorrentFile(w http.ResponseWriter, r *http.Request) {
    r.ParseMultipartForm(10 << 20) // 10 MB limit
    file, _, err := r.FormFile("file")
    if err != nil {
        http.Error(w, "Error reading file: "+err.Error(), http.StatusBadRequest)
        return
    }
    defer file.Close()

    tempFile, err := os.CreateTemp("", "torrent-*.torrent")
    if err != nil {
        http.Error(w, "Error creating temp file: "+err.Error(), http.StatusInternalServerError)
        return
    }
    defer tempFile.Close()
    defer os.Remove(tempFile.Name())

    _, err = io.Copy(tempFile, file)
    if err != nil {
        http.Error(w, "Error saving file: "+err.Error(), http.StatusInternalServerError)
        return
    }

    mu.Lock()
    defer mu.Unlock()
    if len(torrents) >= 50 {
        http.Error(w, "Too many torrents", http.StatusTooManyRequests)
        return
    }

    t, err := client.AddTorrentFromFile(tempFile.Name())
    if err != nil {
        http.Error(w, "Error adding torrent: "+err.Error(), http.StatusInternalServerError)
        return
    }
    <-t.GotInfo()
    t.DownloadAll()
    torrents[t.InfoHash().String()] = t

    w.WriteHeader(http.StatusOK)
}

func PauseTorrent(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    mu.RLock()
    t, ok := torrents[id]
    mu.RUnlock()
    if !ok {
        http.Error(w, "Torrent not found", http.StatusNotFound)
        return
    }
    t.Close()
    w.WriteHeader(http.StatusOK)
}

func ResumeTorrent(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    mu.RLock()
    t, ok := torrents[id]
    mu.RUnlock()
    if !ok {
        http.Error(w, "Torrent not found", http.StatusNotFound)
        return
    }
    t.DownloadAll()
    w.WriteHeader(http.StatusOK)
}

func DeleteTorrent(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    mu.Lock()
    defer mu.Unlock()
    t, ok := torrents[id]
    if !ok {
        http.Error(w, "Torrent not found", http.StatusNotFound)
        return
    }
    t.Close()
    t.Drop()
    delete(torrents, id)
    w.WriteHeader(http.StatusOK)
}

func GetTorrentDetails(w http.ResponseWriter, r *http.Request) {
    id := mux.Vars(r)["id"]
    mu.RLock()
    defer mu.RUnlock()
    t, ok := torrents[id]
    if !ok {
        http.Error(w, "Torrent not found", http.StatusNotFound)
        return
    }
    stats := t.Stats()
    files := []string{}
    for _, f := range t.Files() {
        files = append(files, f.Path())
    }
    details := models.Torrent{
        ID:       id,
        Name:     t.Name(),
        Progress: float64(t.BytesCompleted()) / float64(t.Length()) * 100,
        Speed:    float64(stats.BytesReadData.Int64()) / 1024,
        Paused:   !t.IsSeeding() && t.BytesMissing() > 0 && stats.ActivePeers == 0,
        Seeders:  stats.ActivePeers,
        Peers:    stats.TotalPeers,
        Files:    files,
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(details)
}
