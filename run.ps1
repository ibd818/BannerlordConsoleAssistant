param(
    [string]$Python = "python"
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $ProjectRoot "src"
& $Python -m bannerlord_assistant

