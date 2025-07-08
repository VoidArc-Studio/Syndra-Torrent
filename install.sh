#!/bin/bash

# Kolory dla lepszej czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Rozpoczynanie instalacji backendu Syndra Torrent...${NC}"

# Sprawdzanie i instalacja Go
GO_VERSION="1.21.5"
if ! command -v go &> /dev/null; then
    echo "Go nie jest zainstalowane. Instalowanie Go $GO_VERSION..."
    curl -L -o go.tar.gz "https://go.dev/dl/go$GO_VERSION.linux-amd64.tar.gz"
    sudo tar -C /usr/local -xzf go.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin
    rm go.tar.gz
else
    echo "Go jest już zainstalowane: $(go version)"
fi

# Sprawdzanie i instalacja git
if ! command -v git &> /dev/null; then
    echo "Git nie jest zainstalowany. Instalowanie git..."
    sudo apt-get update
    sudo apt-get install -y git
else
    echo "Git jest już zainstalowany: $(git version)"
fi

# Klonowanie repozytorium (zakładam, że kod jest w repozytorium git, np. na GitHub)
REPO_URL="https://github.com/username/syndra-torrent.git" # Zastąp odpowiednim URL repozytorium
if [ ! -d "syndra-torrent" ]; then
    echo "Klonowanie repozytorium Syndra Torrent..."
    git clone "$REPO_URL" syndra-torrent
else
    echo "Repozytorium już istnieje, aktualizowanie..."
    cd syndra-torrent
    git pull
    cd ..
fi

# Przejście do folderu backendu
cd syndra-torrent/backend

# Instalacja zależności Go
echo "Instalowanie zależności backendu..."
go mod tidy
if [ $? -ne 0 ]; then
    echo -e "${RED}Błąd podczas instalacji zależności Go${NC}"
    exit 1
fi

# Tworzenie folderu downloads, jeśli nie istnieje
mkdir -p downloads

# Tworzenie pliku konfiguracyjnego, jeśli nie istnieje
if [ ! -f "config.json" ]; then
    echo '{"downloadDir": "./downloads"}' > config.json
fi

# Budowanie backendu
echo "Budowanie backendu..."
go build -o syndra-torrent-backend main.go
if [ $? -ne 0 ]; then
    echo -e "${RED}Błąd podczas budowania backendu${NC}"
    exit 1
fi

echo -e "${GREEN}Backend Syndra Torrent zainstalowany pomyślnie!${NC}"
echo "Aby uruchomić backend, wykonaj: cd syndra-torrent/backend && ./syndra-torrent-backend"
