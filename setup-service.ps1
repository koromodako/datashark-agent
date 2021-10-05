$python = "Programs\Python\Python39\Scripts"
$content = "%localappdata%\$python\datashark-agent.exe --log-to %appdata%\Datashark\Logs\ %appdata%\Datashark\datashark.yml"
Set-Content -Path "$env:appdata\Microsoft\Windows\Start Menu\Programs\Startup\start-datashark-agent.cmd" -Value $content
