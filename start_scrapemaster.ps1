# ScrapeMaster Intelligence - Production Startup Script
[CmdletBinding()]
param([switch]$Debug)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-StartupLog {
    param([string]$Message, [string]$Level = "Info")
    $colors = @{"Info"="Cyan"; "Success"="Green"; "Warning"="Yellow"; "Error"="Red"}
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [$Level] $Message" -ForegroundColor $colors[$Level]
}

Write-StartupLog "ðŸš€ ScrapeMaster Intelligence Platform" -Level Success
Write-StartupLog "=====================================" -Level Info

# Change to script directory with validation
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not (Test-Path $scriptPath)) {
    Write-StartupLog "Script directory not found: $scriptPath" -Level Error
    exit 1
}
Set-Location $scriptPath

# Validate environment
$requiredFiles = @("venv\Scripts\Activate.ps1", "src\app.py", "requirements.txt")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-StartupLog "Required file missing: $file" -Level Error
        exit 1
    }
}

# Activate virtual environment
Write-StartupLog "Activating virtual environment..." -Level Info
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-StartupLog "Virtual environment activated" -Level Success
} catch {
    Write-StartupLog "Virtual environment activation failed" -Level Error
    exit 1
}

# Initialize directories
@("data", "logs") | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
}

# Display startup information
Write-StartupLog "ðŸŒ Starting web application..." -Level Info
Write-StartupLog "ðŸ“Š Dashboard: http://localhost:8501" -Level Success
Write-StartupLog "ðŸŽ¯ Revenue Target: $15,000 MRR by Month 3" -Level Warning
Write-StartupLog "ðŸ’¡ Quick Start: Add monitoring targets via dashboard" -Level Info
Write-Host ""

# Launch application with production settings
$streamlitArgs = @(
    "run", "src\app.py",
    "--server.port=8501",
    "--server.address=0.0.0.0", 
    "--server.headless=true",
    "--browser.gatherUsageStats=false",
    "--server.enableCORS=false",
    "--server.enableXsrfProtection=true"
)

if ($Debug) {
    $streamlitArgs += "--logger.level=debug"
}

try {
    & streamlit @streamlitArgs
} catch {
    Write-StartupLog "Application startup failed: $($_.Exception.Message)" -Level Error
    Read-Host "Press Enter to exit"
    exit 1
}
