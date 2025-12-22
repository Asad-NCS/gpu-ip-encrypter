param([string]$File = "C:\Users\asada\Videos\10 Minutes Of Beautiful Nature Scenes 4K HD Short Video (2021) Relax Video.mp4")#change this to your test file

# --- CLEANUP PREVIOUS RUNS ---
Write-Host "Cleaning up previous sessions..." -ForegroundColor Cyan
$titles = @("ENCRYPTER*", "DECRYPTER*", "FILE SENDER*", "FILE RECEIVER*")
foreach ($title in $titles) {
    Get-Process | Where-Object { $_.MainWindowTitle -like $title } | Stop-Process -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Milliseconds 500

# --- FILENAME SETUP ---
$targetFileName = [System.IO.Path]::GetFileName($File)
if (-not $targetFileName) { $targetFileName = "received_file.bin" } # fallback

# if you have different versions of cuda/msvc, change these paths
# otherwise just comment them out if your env vars are already set
$env:PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin;$env:PATH"
$env:PATH = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.42.34433\bin\Hostx64\x64;$env:PATH"

# Python Interpreter
$venvPy = ".\venv\Scripts\python.exe"


Write-Host "Select Operation Mode:"
Write-Host "1. SENDER Device   (Run this on the source computer)"
Write-Host "2. RECEIVER Device (Run this on the destination computer)"
Write-Host "3. LOCAL Test      (Run everything on this computer)"
Write-Host "Q. Quit"
Write-Host ""

$choice = Read-Host "Enter your choice (1/2/3/Q)"

switch ($choice) {
    "1" {
        Write-Host "`n[SENDER MODE SELECTED]"
        Write-Host "Target File: $File"
        Write-Host "Make sure config.py has the right Receiver IP!"
        
        # start encrypter
        Write-Host "Launching Encrypter..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'ENCRYPTER (GPU)'; & '$venvPy' encrypter.py }"
        
        Start-Sleep -Seconds 2
        
        # start sender
        Write-Host "Launching File Sender..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'FILE SENDER'; & '$venvPy' file_sender.py '$File' }"
    }
    "2" {
        Write-Host "`n[RECEIVER MODE SELECTED]"
        Write-Host "Output goes to 'decrypted_output/' folder."
        
        # start receiver
        Write-Host "Launching File Receiver..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'FILE RECEIVER'; & '$venvPy' file_receiver.py '$targetFileName' }"
        
        # start decrypter
        Write-Host "Launching Decrypter..."
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'DECRYPTER (GPU)'; & '$venvPy' decrypter.py }"
    }
    "3" {
        Write-Host "`n[LOCAL TEST MODE SELECTED]"
        Write-Host "Running everything locally..."
        
        # receiver stuff
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'FILE RECEIVER'; & '$venvPy' file_receiver.py '$targetFileName' }"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'DECRYPTER'; & '$venvPy' decrypter.py }"
        
        Start-Sleep -Seconds 2
        
        # sender stuff
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'ENCRYPTER'; & '$venvPy' encrypter.py }"
        Start-Sleep -Seconds 2
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'FILE SENDER'; & '$venvPy' file_sender.py '$File' }"
    }
    "Q" {
        Write-Host "Exiting."
        exit
    }
    Default {
        Write-Host "Invalid selection. Run it again."
    }
}

Write-Host "`nDone. Check the new windows."
