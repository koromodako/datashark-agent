# script parameters
## python related parameters
$python_vers = "3.9.7"
$python_digest = "cc3eabc1f9d6c703d1d2a4e7c041bc1d"
$python_scripts_dir = "$env:localappdata\Programs\Python\Python39\Scripts"
## datashark related parameters
$repo_url = "https://github.com/koromodako"
$core_vers = "0.1.1"
$agent_vers = "0.1.0"
$win_procs_vers = "0.1.0"
$indep_procs_vers = "0.1.0"
# computed variables
$tmpdir = "$env:localappdata\Temp"
## python related variables
$python_installer = "python-$python_vers-amd64.exe"
$python_installer_url = "https://www.python.org/ftp/python/$python_vers/$python_installer"
$python_installer_path = "$tmpdir\$python_installer"
# datashark related variables
$core = "datashark_core-$core_vers-py3-none-any.whl"
$core_url = "$repo_url/datashark-core/releases/download/$core_vers/$core"
$core_path = "$tmpdir\$core"
$agent = "datashark_agent-$agent_vers-py3-none-any.whl"
$agent_url = "$repo_url/datashark-agent/releases/download/$agent_vers/$agent"
$agent_path = "$tmpdir\$agent"
$win_procs = "datashark_processors_windows-$win_procs_vers-py3-none-any.whl"
$win_procs_url = "$repo_url/datashark-processors-windows/releases/download/$win_procs_vers/$win_procs"
$win_procs_path = "$tmpdir\$win_procs"
$indep_procs = "datashark_processors_independent-$indep_procs_vers-py3-none-any.whl"
$indep_procs_url = "$repo_url/datashark-processors-independent/releases/download/$indep_procs_vers/$indep_procs"
$indep_procs_path = "$tmpdir\$indep_procs"
$config_url = "https://github.com/koromodako/datashark-agent/releases/download/$agent_vers/datashark.dist.yml"
$config_path = "$env:appdata\Datashark\datashark.yml"
# download the installer from www.python.org
Write-Output "[INFO] downloading Python $python_vers installer..."
$webclient = New-Object System.Net.WebClient
$webclient.DownloadFile("$python_installer_url", "$python_installer_path")
# check installer hexdigest after download and just before run (warning: vulnerable to race condition on the file system)
Write-Output "[INFO] checking Python $python_vers installer MD5 digest..."
$digest = Get-FileHash "$python_installer_path" -Algorithm MD5
if(-Not $python_digest.Equals($digest.Hash.ToLower())){
    Write-Error "Hash digest mismatch!"
    Exit
}
# execute Python installer
Write-Output "[INFO] running Python $python_vers installer..."
$params = @{
    FilePath = "$python_installer_path"
    ArgumentList = "/passive","CompileAll=1","PrependPath=1","Shortcuts=0","Include_doc=0","Include_launcher=0","InstallLauncherAllUsers=0","Include_tcltk=0","Include_test=0"
    NoNewWindow = $true
    Wait = $true
}
Start-Process @params
# remove Python installer
Write-Output "[INFO] removing Python $python_vers installer..."
Remove-Item "$python_installer_path"
# refresh env
Write-Output "[INFO] refreshing environment..."
$env:path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ';' + [System.Environment]::GetEnvironmentVariable("Path","User")
# check python and pip
Write-Output "[INFO] checking python and pip..."
python.exe -V
pip.exe -V
# download Datashark packages
Write-Output "[INFO] downloading Datashark packages..."
$webclient.DownloadFile("$core_url", "$core_path")
$webclient.DownloadFile("$agent_url", "$agent_path")
$webclient.DownloadFile("$win_procs_url", "$win_procs_path")
$webclient.DownloadFile("$indep_procs_url", "$indep_procs_path")
# ensure pip is up-to-date
Write-Output "[INFO] ensuring pip is up-to-date..."
python.exe -m pip install -U pip
# setup Datashark packages
Write-Output "[INFO] installing Datashark packages..."
pip.exe install "$core_path"
pip.exe install "$agent_path"
pip.exe install "$win_procs_path"
pip.exe install "$indep_procs_path"
# remove Datashark packages
Write-Output "[INFO] removing Datashark packages..."
Remove-Item "$core_path"
Remove-Item "$agent_path"
Remove-Item "$win_procs_path"
Remove-Item "$indep_procs_path"
# create configuration and logs folders
Write-Output "[INFO] creating Datashark directories..."
mkdir -Force "$env:appdata\Datashark"
mkdir -Force "$env:appdata\Datashark\Logs"
# download template configuration file
Write-Output "[INFO] downloading configuration file template..."
$webclient.DownloadFile("$config_url", "$config_path")
# create startup file
Write-Output "[INFO] creating startup file..."
$content = "$python_scripts_dir\datashark-agent.exe --log-to %appdata%\Datashark\Logs\ %appdata%\Datashark\datashark.yml"
Set-Content -Path "$env:appdata\Microsoft\Windows\Start Menu\Programs\Startup\start-datashark-agent.cmd" -Value $content
# setup is complete
Write-Output "[INFO] setup complete!"
Write-Output "[INFO] 1. you should customize $config_path"
Write-Output "[INFO] 2. sign-out and sign-in again and datashark agent should start"
