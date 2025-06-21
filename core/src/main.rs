use std::fs;
use tokio::sync::mpsc;
use tonic::transport::Server;
use serde::{Serialize, Deserialize};
use notify_rust::Notification;

mod torrent;
mod grpc;
use grpc::torrent_service_server::TorrentServiceServer;
use torrent::TorrentManager;

#[derive(Serialize, Deserialize, Default)]
struct Config {
    download_dir: String,
    theme: String,
    max_download_speed: u64,
    max_upload_speed: u64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load configuration
    let config: Config = fs::read_to_string("config.json")
        .map(|s| serde_json::from_str(&s).unwrap_or_default())
        .unwrap_or_else(|_| {
            let default_config = Config {
                download_dir: "~/Downloads".to_string(),
                theme: "light".to_string(),
                max_download_speed: 0,
                max_upload_speed: 0,
            };
            fs::write("config.json", serde_json::to_string(&default_config).unwrap()).unwrap();
            default_config
        });

    // Initialize torrent manager
    let (tx, rx) = mpsc::channel(32);
    let manager = TorrentManager::new(config, tx);
    
    // Start notification handler
    tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            Notification::new()
                .summary("Syndra Torrent")
                .body(&msg)
                .show()
                .unwrap();
        }
    });

    // Start gRPC server
    let addr = "[::1]:50051".parse()?;
    Server::builder()
        .add_service(TorrentServiceServer::new(manager))
        .serve(addr)
        .await?;

    Ok(())
}
