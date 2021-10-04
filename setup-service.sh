#!/usr/bin/env bash

cat << "EOF" > /etc/systemd/system/datashark.service
[Unit]
Description=Datashark Agent
After=network.target

[Service]
Type=simple
User=datashark
Group=datashark
WorkingDirectory=/opt/datashark/
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=LC_LANG=en_US.UTF-8
ExecStart=/opt/datashark/venv/bin/datashark-agent /opt/datashark/config/datashark.yml
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable datashark.service
