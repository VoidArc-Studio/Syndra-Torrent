use libtorrent::{Session, TorrentHandle, TorrentInfo};
use std::path::Path;
use tokio::sync::mpsc;
use serde::{Serialize, Deserialize};
use crate::Config;

#[derive(Serialize, Deserialize)]
pub struct TorrentManager {
    session: Session,
    torrents: Vec<TorrentHandle>,
    config: Config,
    #[serde(skip)]
    notification_tx: mpsc::Sender<String>,
}

impl TorrentManager {
    pub fn new(config: Config, notification_tx: mpsc::Sender<String>) -> Self {
        let mut session = Session::new().expect("Failed to create session");
        if config.max_download_speed > 0 {
            session.set_max_download_speed(config.max_download_speed as i64);
        }
        if config.max_upload_speed > 0 {
            session.set_max_upload_speed(config.max_upload_speed as i64);
        }
        TorrentManager {
            session,
            torrents: Vec::new(),
            config,
            notification_tx,
        }
    }

    pub fn add_torrent(&mut self, magnet_link: &str) -> Result<String, String> {
        let torrent_info = TorrentInfo::from_magnet_link(magnet_link)
            .map_err(|e| format!("Invalid magnet link: {}", e))?;
        let handle = self.session.add_torrent(torrent_info, Path::new(&self.config.download_dir))
            .map_err(|e| format!("Failed to add torrent: {}", e))?;
        let torrent_id = handle.id().to_string();
        self.torrents.push(handle);
        self.notification_tx
            .try_send(format!("Added torrent: {}", torrent_id))
            .unwrap_or_default();
        Ok(torrent_id)
    }

    pub fn pause_torrent(&mut self, torrent_id: &str) -> Result<(), String> {
        if let Some(handle) = self.torrents.iter().find(|t| t.id().to_string() == torrent_id) {
            handle.pause().map_err(|e| format!("Failed to pause torrent: {}", e))?;
            self.notification_tx
                .try_send(format!("Paused torrent: {}", torrent_id))
                .unwrap_or_default();
            Ok(())
        } else {
            Err("Torrent not found".to_string())
        }
    }

    pub fn resume_torrent(&mut self, torrent_id: &str) -> Result<(), String> {
        if let Some(handle) = self.torrents.iter().find(|t| t.id().to_string() == torrent_id) {
            handle.resume().map_err(|e| format!("Failed to resume torrent: {}", e))?;
            self.notification_tx
                .try_send(format!("Resumed torrent: {}", torrent_id))
                .unwrap_or_default();
            Ok(())
        } else {
            Err("Torrent not found".to_string())
        }
    }

    pub fn remove_torrent(&mut self, torrent_id: &str) -> Result<(), String> {
        if let Some(index) = self.torrents.iter().position(|t| t.id().to_string() == torrent_id) {
            let handle = self.torrents.remove(index);
            self.session.remove_torrent(&handle, false)
                .map_err(|e| format!("Failed to remove torrent: {}", e))?;
            self.notification_tx
                .try_send(format!("Removed torrent: {}", torrent_id))
                .unwrap_or_default();
            Ok(())
        } else {
            Err("Torrent not found".to_string())
        }
    }

    pub fn get_status(&self) -> Vec<crate::grpc::TorrentStatus> {
        self.torrents.iter().map(|t| crate::grpc::TorrentStatus {
            torrent_id: t.id().to_string(),
            name: t.name().unwrap_or_default(),
            progress: t.progress() as f32,
            download_speed: t.download_rate() as i32,
            upload_speed: t.upload_rate() as i32,
            eta: t.eta().unwrap_or(0) as i32,
            status: t.state().to_string(),
            files: t.files().unwrap_or_default().iter().map(|f| f.path().to_string_lossy().to_string()).collect(),
            peers: t.peers().unwrap_or_default().len() as i32,
        }).collect()
    }
}
