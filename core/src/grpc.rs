use tonic::{Request, Response, Status};
use crate::torrent::TorrentManager;

pub mod torrent_proto {
    tonic::include_proto!("syndra");
}

use torrent_proto::torrent_service_server::TorrentService;
use torrent_proto::{
    AddTorrentRequest, AddTorrentResponse, GetStatusRequest, GetStatusResponse,
    PauseTorrentRequest, PauseTorrentResponse, ResumeTorrentRequest, ResumeTorrentResponse,
    RemoveTorrentRequest, RemoveTorrentResponse, TorrentStatus,
};

#[tonic::async_trait]
impl TorrentService for TorrentManager {
    async fn add_torrent(
        &self,
        request: Request<AddTorrentRequest>,
    ) -> Result<Response<AddTorrentResponse>, Status> {
        let magnet_link = request.into_inner().magnet_link;
        match self.add_torrent(&magnet_link) {
            Ok(torrent_id) => Ok(Response::new(AddTorrentResponse {
                success: true,
                error: String::new(),
                torrent_id,
            })),
            Err(e) => Ok(Response::new(AddTorrentResponse {
                success: false,
                error: e,
                torrent_id: String::new(),
            })),
        }
    }

    async fn get_status(
        &self,
        _request: Request<GetStatusRequest>,
    ) -> Result<Response<GetStatusResponse>, Status> {
        let torrents = self.get_status();
        Ok(Response::new(GetStatusResponse { torrents }))
    }

    async fn pause_torrent(
        &self,
        request: Request<PauseTorrentRequest>,
    ) -> Result<Response<PauseTorrentResponse>, Status> {
        let torrent_id = request.into_inner().torrent_id;
        match self.pause_torrent(&torrent_id) {
            Ok(_) => Ok(Response::new(PauseTorrentResponse {
                success: true,
                error: String::new(),
            })),
            Err(e) => Ok(Response::new(PauseTorrentResponse {
                success: false,
                error: e,
            })),
        }
    }

    async fn resume_torrent(
        &self,
        request: Request<ResumeTorrentRequest>,
    ) -> Result<Response<ResumeTorrentResponse>, Status> {
        let torrent_id = request.into_inner().torrent_id;
        match self.resume_torrent(&torrent_id) {
            Ok(_) => Ok(Response::new(ResumeTorrentResponse {
                success: true,
                error: String::new(),
            })),
            Err(e) => Ok(Response::new(ResumeTorrentResponse {
                success: false,
                error: e,
            })),
        }
    }

    async fn remove_torrent(
        &self,
        request: Request<RemoveTorrentRequest>,
    ) -> Result<Response<RemoveTorrentResponse>, Status> {
        let torrent_id = request.into_inner().torrent_id;
        match self.remove_torrent(&torrent_id) {
            Ok(_) => Ok(Response::new(RemoveTorrentResponse {
                success: true,
                error: String::new(),
            })),
            Err(e) => Ok(Response::new(RemoveTorrentResponse {
                success: false,
                error: e,
            })),
        }
    }
}
