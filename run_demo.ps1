# Add CUDA to PATH
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin;$env:PATH"
# Add MSVC Compiler to PATH
$env:PATH = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.42.34433\bin\Hostx64\x64;$env:PATH"

$venvPy = ".\venv\Scripts\python.exe"

# 1. Generate PCAP (Run once, wait to finish)
Write-Host "Generating PCAP file..."
& $venvPy pcap_gen.py

# 2. Start Destination (New Window)
Write-Host "Starting Destination..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Set-Location '$PWD'; `$host.UI.RawUI.WindowTitle = 'DESTINATION'; & '.\venv\Scripts\python.exe' destination.py }"

# 3. Start Decrypter (New Window)
Write-Host "Starting Decrypter..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Set-Location '$PWD'; `$host.UI.RawUI.WindowTitle = 'DECRYPTER'; & '.\venv\Scripts\python.exe' decrypter.py }"

# 4. Start Encrypter (New Window)
Start-Sleep -Seconds 1
Write-Host "Starting Encrypter..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Set-Location '$PWD'; `$host.UI.RawUI.WindowTitle = 'ENCRYPTER'; & '.\venv\Scripts\python.exe' encrypter.py }"

# 5. Start Injector (New Window)
Start-Sleep -Seconds 1
Write-Host "Starting Injector..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Set-Location '$PWD'; `$host.UI.RawUI.WindowTitle = 'INJECTOR'; & '.\venv\Scripts\python.exe' injector.py }"

Write-Host "All components started. Check the 4 terminal windows."
