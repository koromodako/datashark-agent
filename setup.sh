#!/usr/bin/env bash

home="/home/datashark"
repo_url="https://github.com/koromodako"
core_vers="0.1.1"
agent_vers="0.1.0"
win_procs_vers="0.1.0"
indep_procs_vers="0.1.0"
# computed variables
tmpdir="$(mktemp -d)"
# datashark related variables
core="datashark_core-${core_vers}-py3-none-any.whl"
core_url="${repo_url}/datashark-core/releases/download/${core_vers}/${core}"
core_path="${tmpdir}/${core}"
agent="datashark_agent-${agent_vers}-py3-none-any.whl"
agent_url="${repo_url}/datashark-agent/releases/download/${agent_vers}/${agent}"
agent_path="${tmpdir}/${agent}"
win_procs="datashark_processors_windows-${win_procs_vers}-py3-none-any.whl"
win_procs_url="${repo_url}/datashark-processors-windows/releases/download/${win_procs_vers}/${win_procs}"
win_procs_path="${tmpdir}/${win_procs}"
indep_procs="datashark_processors_independent-${indep_procs_vers}-py3-none-any.whl"
indep_procs_url="${repo_url}/datashark-processors-independent/releases/download/${indep_procs_vers}/${indep_procs}"
indep_procs_path="${tmpdir}/${indep_procs}"
config_url="https://github.com/koromodako/datashark-agent/releases/download/${agent_vers}/datashark.dist.yml"
config_path="/home/datashark/datashark.yml"
# setup python 3.x
sudo apt install python3 python3-dev python3-pip python3-venv
# ensure pip is up-to-date
python3 -m pip install -U pip
# create virtual environment
python3 -m venv "${home}/venv"
# source virtual environment
. "${home}/venv/bin/activate"
# download packages
curl -o "${core_path}" "${core_url}"
curl -o "${agent_path}" "${agent_url}"
curl -o "${win_procs_path}" "${win_procs_url}"
curl -o "${indep_procs_path}" "${indep_procs_url}"
# install packages
pip install "${core_path}"
pip install "${agent_path}"
pip install "${win_procs_path}"
pip install "${indep_procs_path}"
# remove temporary directory
rm -rf "${tmpdir}"
# download configuration file
curl -o "${config_path}" "${config_url}"
# create systemd service
cat << "EOF" > /etc/systemd/system/datashark.service
[Unit]
Description=Datashark Agent
After=network.target

[Service]
Type=simple
User=datashark
Group=datashark
WorkingDirectory=/home/datashark/
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=LC_LANG=en_US.UTF-8
ExecStart=/home/datashark/venv/bin/datashark-agent /home/datashark/datashark.yml
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF
# enable systemd service
systemctl enable datashark.service
