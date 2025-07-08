package main

import (
    "encoding/json"
    "log"
    "net/http"
    "sync"
    "github.com/anacrolix/torrent"
    "github.com/gorilla/mux"
    "github.com/rs/cors"
)

var (
    torrents = make(map[string]*torrent.Torrent)
    mu       sync.RWMutex
    client   *torrent.Client
)

func main() {
    // Inicjalizacja klienta BitTorrent
    config := torrent.NewDefaultClientConfig()
    config.DataDir = "./downloads"
    var err error
    client, err = torrent.NewClient(config)
    if err != nil {
        log.Fatalf("Error creating torrent client: %v", err)
    }
    defer client.Close()

    // Inicjalizacja routera
    router := mux.NewRouter()
    router.HandleFunc("/torrents", getTorrents).Methods("GET")
    router.HandleFunc("/torrents", addTorrent).Methods("POST")
    router.HandleFunc("/torrents/file", addTorrentFile).Methods("POST")
    router.HandleFunc("/torrents/{id}/pause", pauseTorrent).Methods("POST")
    router.HandleFunc("/torrents/{id}/resume", resumeTorrent).Methods("POST")
    router.HandleFunc("/torrents/{id}", deleteTorrent).Methods("DELETE")
    router.HandleFunc("/torrents/{id}/details", getTorrentDetails).Methods("GET")

    // CORS
    c := cors.New(cors.Options{
        AllowedOrigins:   []string{"http://localhost:5173"},
        AllowedMethods:   []string{"GET", "POST", "DELETE"},
        AllowedHeaders:   []string{"Content-Type"},
        AllowCredentials: true,
    })

    // Uruchomienie serwera
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", c.Handler(router)))
}
