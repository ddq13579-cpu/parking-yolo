# Parking monitor

Docker Compose deployment for an x86_64 Debian host. The stack contains:

- `parking`: RTSP/YOLO parking-space monitor.
- `snapshot-web`: serves snapshots for Bark notification links.

No Synology paths or services are required. Snapshots are stored in the Docker
named volume `parking_snapshots` and are served at `/parking/parking_snapshot.jpg`.

## Deploy on Debian

1. Install Docker Engine and the Docker Compose plugin.
2. Clone this repository and enter it.
3. Create the private runtime configuration:

   ```sh
   cp .env.example .env
   editor .env
   ```

   Set `RTSP_URL`, `BARK_KEYS`, and `SNAPSHOT_URL`. `SNAPSHOT_URL` must use the
   Debian server's reachable hostname/IP (or a reverse-proxy domain), not the old
   NAS address. If the URL is accessed from outside the LAN, also configure the
   firewall/router or an HTTPS reverse proxy.

4. Start the stack:

   ```sh
   docker compose up -d --build
   docker compose logs -f parking
   ```

5. Verify the snapshot URL in a browser after the first parking-state change.

## Operations

```sh
git pull
docker compose build --pull
docker compose up -d
docker compose logs -f
docker compose down
```

`docker compose down` retains snapshots. `docker compose down -v` also deletes
the snapshot volume.
