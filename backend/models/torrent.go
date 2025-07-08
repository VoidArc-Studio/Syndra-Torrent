package models

type Torrent struct {
    ID       string   `json:"id"`
    Name     string   `json:"name"`
    Progress float64  `json:"progress"`
    Speed    float64  `json:"speed"`
    Paused   bool     `json:"paused"`
    Seeders  int      `json:"seeders"`
    Peers    int      `json:"peers"`
    Files    []string `json:"files"`
}
