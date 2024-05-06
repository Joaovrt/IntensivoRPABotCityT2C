$exclude = @("venv", "intesivoBotCity.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "intesivoBotCity.zip" -Force