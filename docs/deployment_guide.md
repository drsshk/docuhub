# DocuHub Deployment Guide for DigitalOcean

This guide provides a step-by-step process for deploying the DocuHub Django application on a DigitalOcean Droplet.

## Prerequisites

Before you begin, you will need:

*   A DigitalOcean account.
*   A registered domain name that you can point to your new server.
*   A local machine with `git` and an SSH client installed.

### Generating SSH Keys (if you don't have them)

If you don't already have an SSH key pair, you can generate one on your local machine:

1.  **Open a terminal or Git Bash (on Windows).**

2.  **Generate the key pair:**
    ```bash
    ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    ```
    *   Press Enter to save the key in the default location (`~/.ssh/id_rsa`).
    *   Enter a strong passphrase when prompted (optional, but recommended for security).

3.  **Add your SSH private key to the SSH agent:**
    ```bash
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_rsa
    ```

4.  **Copy your public key to your DigitalOcean account:**
    *   Display your public key:
        ```bash
        cat ~/.ssh/id_rsa.pub
        ```
    *   Copy the entire output (it starts with `ssh-rsa` and ends with your email).
    *   In your DigitalOcean account, navigate to **Settings** > **Security** > **Add SSH Key** and paste your public key there. Give it a recognizable name.

### Adding SSH Key to an Existing Droplet

If your Droplet was created without your SSH key, you can add it manually:

1.  **Log in to your Droplet using password authentication (if SSH key is not set up yet) or an existing key:**
    ```bash
    ssh root@152.42.210.234
    ```

2.  **Create the `.ssh` directory if it doesn't exist:**
    ```bash
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    ```

3.  **Append your public key to the `authorized_keys` file:**
    ```bash
    echo "<your_public_key_content>" >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    ```
    *   Replace `<your_public_key_content>` with the actual content of your `id_rsa.pub` file (the one you copied to DigitalOcean).

4.  **Disable password authentication (optional, but recommended for security):**
    *   Edit the SSH daemon configuration:
        ```bash
        sudo nano /etc/ssh/sshd_config
        ```
    *   Find the line `PasswordAuthentication yes` and change it to `PasswordAuthentication no`.
    *   Restart the SSH service:
        ```bash
        sudo systemctl restart sshd
        ```

## Step 1: Configure the Existing Droplet

1.  **Initial Server Setup:**
    
    *   Log in to your server as the `root` user:
        ```bash
        ssh root@152.42.210.234
        ```
    *   Create a new non-root user:
        ```bash
        adduser <your_username>
        ```
    *   Add the new user to the `sudo` group:
        ```bash
        usermod -aG sudo <your_username>
        ```
    *   Log out of the `root` account and log back in as the new user:
        ```bash
        ssh <your_username>@152.42.210.234
        ```

3.  **Configure the Firewall:**
    *   Allow OpenSSH, HTTP, and HTTPS traffic:
        ```bash
        sudo ufw allow OpenSSH
        sudo ufw allow 'Nginx Full'
        sudo ufw enable
        ```

## Step 2: Install and Configure Nginx

1.  **Install Nginx:**
    ```bash
    sudo apt update
    sudo apt install nginx
    ```

2.  **Create an Nginx Server Block:**
    *   Create a new configuration file for your domain:
        ```bash
        sudo nano /etc/nginx/sites-available/your_domain
        ```
    *   Add the following configuration, replacing `your_domain` with your actual domain name:
        ```nginx
        server {
            listen 80;
            server_name 152.42.210.234;

            location = /favicon.ico { access_log off; log_not_found off; }
            location /static/ {
                root /home/drsshk/docuhub;
            }

            location / {
                include proxy_params;
                proxy_pass http://unix:/run/gunicorn.sock;
            }
        }
        ```
    *   Enable the new server block by creating a symbolic link:
        ```bash
        sudo ln -s /etc/nginx/sites-available/your_domain /etc/nginx/sites-enabled
        ```
    *   Test the Nginx configuration for syntax errors:
        ```bash
        sudo nginx -t
        ```
    *   Restart Nginx:
        ```bash
        sudo systemctl restart nginx
        ```

## Step 3: Install and Configure Gunicorn

1.  **Install Gunicorn:**
    *   Activate your virtual environment (you will create this in the next step).
    *   Install Gunicorn:
        ```bash
        pip install gunicorn
        ```

2.  **Create Gunicorn Systemd Service and Socket Files:**
    *   Create the service file (`/etc/systemd/system/gunicorn.service`):
        ```ini
        [Unit]
        Description=gunicorn daemon
        Requires=gunicorn.socket
        After=network.target

        [Service]
        User=drsshk
        Group=www-data
        WorkingDirectory=/home/drsshk/docuhub
        ExecStart=/home/drsshk/docuhub/venv/bin/gunicorn \
                  --access-logfile - \
                  --workers 3 \
                  --bind unix:/run/gunicorn.sock \
                  docuhub.wsgi:application

        [Install]
        WantedBy=multi-user.target
        ```
    *   Create the socket file (`/etc/systemd/system/gunicorn.socket`):
        ```ini
        [Unit]
        Description=gunicorn socket

        [Socket]
        ListenStream=/run/gunicorn.sock

        [Install]
        WantedBy=sockets.target
        ```

4.  **Start and Enable the Gunicorn Service:**
    ```bash
    sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket
    sudo systemctl daemon-reload
    sudo systemctl restart gunicorn
    sudo systemctl enable gunicorn
    ```

## Step 4: Set Up the Django Application

1.  **Clone the Repository:**
    *   Replace `<your_repository_url>` with the actual URL of your Git repository. For example:
    ```bash
    git clone https://github.com/drsshk/docuhub docuhub
    cd docuhub
    ```

2.  **Create a Virtual Environment:**
    *   First, install `python3-venv` if it's not already installed:
        ```bash
        sudo apt install python3-venv
        ```
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    sudo apt install -y default-libmysqlclient-dev pkg-config #for mysqclient issues
    pip install -r requirements.txt
    ```

6.  **Collect Static Files:**
    ```bash
    ./venv/bin/python manage.py collectstatic
    ```


## Step 7: Final Steps and Verification

1.  **Restart Services:**
    ```bash
    sudo systemctl restart nginx
    sudo systemctl restart gunicorn
    ```

2.  **Verify the Application:
    *   Open your web browser and navigate to `http://152.42.210.234`. You should see your DocuHub application.
    *   **Note:** Since you are using an IP address instead of a domain name, HTTPS will not be available unless you configure a reverse proxy with a self-signed certificate or use a service that provides SSL for IP addresses.

3.  **Troubleshooting:
    *   If you encounter errors, check the Nginx and Gunicorn logs:
        ```bash
        sudo journalctl -u nginx
        sudo journalctl -u gunicorn
        ```