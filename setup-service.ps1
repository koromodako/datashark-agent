$params = @{
  Name = "DatasharkAgent"
  BinaryPathName = '"C:\Users\user\AppData\Local\Python\Python39\Scripts\datashark-agent.exe --log-to C:\Users\user\AppData\Roaming\Datashark\Logs\ C:\Users\user\AppData\Roaming\Datashark\datashark.yml"'
  Credential = ".\user"
  DisplayName = "Datashark Agent"
  StartupType = "Automatic"
  Description = "Datashak agent service."
}
New-Service @params
