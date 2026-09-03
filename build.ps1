param(
    [string]$Python = "python",
    [string]$IndexUrl = ""
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceRoot = Join-Path $ProjectRoot "src"
$EntryPoint = Join-Path $ProjectRoot "launcher.py"
$DataFile = Join-Path $SourceRoot "bannerlord_assistant\data\commands.json"
$EntityDataFile = Join-Path $SourceRoot "bannerlord_assistant\data\entities.json"
$OutputDir = Join-Path $ProjectRoot "outputs"
$WorkDir = Join-Path $ProjectRoot "work\pyinstaller"
$SpecDir = Join-Path $ProjectRoot "work"
$VenvDir = Join-Path $ProjectRoot "work\build-venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    & $Python -m venv $VenvDir
}

$PipArguments = @("-m", "pip", "install", "-r", (Join-Path $ProjectRoot "requirements.txt"))
if ($IndexUrl) {
    $PipArguments += @("-i", $IndexUrl)
}
& $VenvPython @PipArguments

& $VenvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "BannerlordConsoleAssistant" `
    --paths $SourceRoot `
    --add-data "$DataFile;bannerlord_assistant/data" `
    --add-data "$EntityDataFile;bannerlord_assistant/data" `
    --distpath $OutputDir `
    --workpath $WorkDir `
    --specpath $SpecDir `
    $EntryPoint

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

Write-Host "Build complete: $OutputDir\BannerlordConsoleAssistant.exe"
