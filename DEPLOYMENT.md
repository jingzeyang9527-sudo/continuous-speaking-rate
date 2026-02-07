# DSAL Deployment Guide

This guide explains how to deploy the DSAL toolkit as a public web application.

## Prerequisites

- Python 3.9+
- Access to a server with public IP or domain
- SSH access to the server

## Step 1: Batch Process PPA Dataset

Before deploying, process your PPA dataset to generate features:

```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features.csv
```

This will create a CSV file with all extracted features from your PPA audio files.

**Note**: Processing 3634 files may take several hours. You can test with a subset first:

```bash
# Test with 100 files first
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features_test.csv --max-files 100
```

## Step 2: Configure Streamlit for Public Access

The configuration file `.streamlit/config.toml` is already set up for public access:
- Server listens on `0.0.0.0` (all interfaces)
- Port: `8502`
- CORS and XSRF protection enabled

## Step 3: Start Streamlit Server

### Option A: Direct Run (Development)

```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
streamlit run app/main.py --server.port 8502 --server.address 0.0.0.0
```

### Option B: Using systemd Service (Production)

Create a systemd service file `/etc/systemd/system/dsal-streamlit.service`:

```ini
[Unit]
Description=DSAL Streamlit Application
After=network.target

[Service]
Type=simple
User=jingzeyang
WorkingDirectory=/data/jingzeyang/dsal_toolkit
Environment="PATH=/data/jingzeyang/dsal_toolkit/.venv/bin"
ExecStart=/data/jingzeyang/dsal_toolkit/.venv/bin/streamlit run app/main.py --server.port 8502 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable dsal-streamlit
sudo systemctl start dsal-streamlit
sudo systemctl status dsal-streamlit
```

### Option C: Using screen/tmux (Simple)

```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
screen -S dsal
streamlit run app/main.py --server.port 8502 --server.address 0.0.0.0
# Press Ctrl+A then D to detach
```

## Step 4: Configure Firewall

Allow incoming connections on port 8502:

```bash
# UFW (Ubuntu)
sudo ufw allow 8502/tcp

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8502/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 8502 -j ACCEPT
```

## Step 5: Access the Application

### Direct IP Access

If your server has a public IP, access via:
```
http://YOUR_SERVER_IP:8502
```

### Domain Name (Recommended)

1. Point your domain to the server IP (A record)
2. Configure reverse proxy with Nginx:

```nginx
# /etc/nginx/sites-available/dsal
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/dsal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Then access via: `http://your-domain.com`

## Step 6: Add Authentication (Optional but Recommended)

For public access, consider adding authentication. You can use:

1. **Streamlit's built-in authentication** (Streamlit 1.10+):
   Create `.streamlit/secrets.toml`:

```toml
[general]
password = "your-secure-password-hash"
```

2. **Nginx Basic Auth**:
```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd username
```

Then add to Nginx config:
```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

3. **Third-party authentication** (OAuth, SAML, etc.) via Nginx or a reverse proxy.

## Monitoring and Logs

### Streamlit Logs

```bash
# If using systemd
sudo journalctl -u dsal-streamlit -f

# If running directly
# Logs appear in terminal
```

### Check if service is running

```bash
# Check port
netstat -tuln | grep 8502
# or
ss -tuln | grep 8502

# Check process
ps aux | grep streamlit
```

## Troubleshooting

### Port already in use

```bash
# Find process using port 8502
sudo lsof -i :8502
# Kill it
sudo kill -9 <PID>
```

### Permission denied

```bash
# Make sure user has permissions
chmod +x /data/jingzeyang/dsal_toolkit/.venv/bin/streamlit
```

### Connection refused

- Check firewall rules
- Verify server is listening on `0.0.0.0` not `127.0.0.1`
- Check server logs for errors

## Performance Tips

1. **Enable caching**: Already enabled in the app
2. **Use CDN**: For static assets if needed
3. **Load balancing**: For high traffic, use multiple instances behind a load balancer
4. **Database**: For large datasets, consider storing results in a database instead of CSV

## Security Considerations

1. **Use HTTPS**: Set up SSL/TLS certificate (Let's Encrypt)
2. **Authentication**: Add user authentication
3. **Rate limiting**: Configure rate limits in Nginx
4. **Input validation**: The app validates file uploads, but consider additional checks
5. **Regular updates**: Keep dependencies updated

## Backup

Regularly backup:
- `ppa_features.csv` (processed features)
- Configuration files
- Any custom modifications

```bash
# Example backup script
tar -czf dsal_backup_$(date +%Y%m%d).tar.gz \
    /data/jingzeyang/dsal_toolkit/ppa_features.csv \
    /data/jingzeyang/dsal_toolkit/.streamlit/
```
