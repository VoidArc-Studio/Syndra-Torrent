package handlers

import (
    "encoding/json"
    "os"
)

type Config struct {
    DownloadDir string `json:"downloadDir"`
}

func LoadConfig() (*Config, error) {
    config := &Config{DownloadDir: "./downloads"}
    data, err := os.ReadFile("config.json")
    if err != nil {
        if os.IsNotExist(err) {
            return config, nil
        }
        return nil, err
    }
    if err := json.Unmarshal(data, config); err != nil {
        return nil, err
    }
    return config, nil
}

func SaveConfig(config *Config) error {
    data, err := json.MarshalIndent(config, "", "  ")
    if err != nil {
        return err
    }
    return os.WriteFile("config.json", data, 0644)
}
