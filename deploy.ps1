# ScrapeMaster Intelligence - Enterprise Windows Deployment Script
# Advanced PowerShell deployment with bulletproof syntax and error handling

[CmdletBinding()]
param(
    [switch]$SkipPython,
    [switch]$Force
)

# Set strict error handling for enterprise deployment
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configure advanced PowerShell execution environment
$ProgressPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🚀 ScrapeMaster Intelligence - Enterprise Deployment" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue

# Advanced logging function with structured output
function Write-LogMessage {
    param(
        [string]$Message,
        [ValidateSet("Info", "Success", "Warning", "Error")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colorMap = @{
        "Info"    = "Cyan"
        "Success" = "Green" 
        "Warning" = "Yellow"
        "Error"   = "Red"
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $colorMap[$Level]
}

# Enterprise-grade dependency validation
function Test-SystemDependencies {
    Write-LogMessage "Validating system dependencies..." -Level Info
    
    # Validate PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-LogMessage "PowerShell 5.0+ required. Current: $($PSVersionTable.PSVersion)" -Level Error
        exit 1
    }
    
    # Test Python installation with advanced validation
    try {
        $pythonOutput = & python --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $pythonOutput -match "Python 3\.(\d+)\.(\d+)") {
            $majorVersion = [int]$Matches[1]
            $minorVersion = [int]$Matches[2]
            
            if ($majorVersion -ge 8 -or ($majorVersion -eq 7 -and $minorVersion -ge 6)) {
                Write-LogMessage "Python validation successful: $pythonOutput" -Level Success
            } else {
                Write-LogMessage "Python 3.7.6+ required. Found: $pythonOutput" -Level Error
                exit 1
            }
        } else {
            throw "Python validation failed"
        }
    } catch {
        Write-LogMessage "Python not found or invalid installation" -Level Error
        Write-LogMessage "Install Python 3.8+ from https://python.org" -Level Warning
        exit 1
    }
    
    # Validate pip with version checking
    try {
        $pipOutput = & pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Pip validation successful: $pipOutput" -Level Success
        } else {
            Write-LogMessage "Installing pip via ensurepip..." -Level Warning
            & python -m ensurepip --upgrade
        }
    } catch {
        Write-LogMessage "Pip installation failed" -Level Error
        exit 1
    }
}

# Advanced virtual environment management
function Initialize-VirtualEnvironment {
    Write-LogMessage "Configuring Python virtual environment..." -Level Info
    
    if (Test-Path "venv" -PathType Container) {
        if ($Force) {
            Write-LogMessage "Removing existing virtual environment..." -Level Warning
            Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
        } else {
            Write-LogMessage "Virtual environment exists. Use -Force to recreate." -Level Warning
            return
        }
    }
    
    # Create virtual environment with advanced configuration
    & python -m venv venv --upgrade-deps
    if ($LASTEXITCODE -ne 0) {
        Write-LogMessage "Virtual environment creation failed" -Level Error
        exit 1
    }
    
    Write-LogMessage "Virtual environment created successfully" -Level Success
    
    # Activate virtual environment with validation
    $activateScript = ".\venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        Write-LogMessage "Virtual environment activated" -Level Success
    } else {
        Write-LogMessage "Virtual environment activation failed" -Level Error
        exit 1
    }
}

# Enterprise dependency installation with retry logic
function Install-PythonDependencies {
    Write-LogMessage "Installing Python dependencies with retry logic..." -Level Info
    
    # Upgrade pip to latest version
    & python -m pip install --upgrade pip wheel setuptools
    
    $maxRetries = 3
    $retryCount = 0
    
    do {
        $retryCount++
        Write-LogMessage "Dependency installation attempt $retryCount of $maxRetries" -Level Info
        
        try {
            & pip install -r requirements.txt --no-cache-dir --timeout 300
            if ($LASTEXITCODE -eq 0) {
                Write-LogMessage "All dependencies installed successfully" -Level Success
                return
            }
        } catch {
            Write-LogMessage "Installation attempt $retryCount failed: $($_.Exception.Message)" -Level Warning
        }
        
        if ($retryCount -lt $maxRetries) {
            Write-LogMessage "Retrying in 10 seconds..." -Level Info
            Start-Sleep -Seconds 10
        }
    } while ($retryCount -lt $maxRetries)
    
    Write-LogMessage "Dependency installation failed after $maxRetries attempts" -Level Error
    exit 1
}

# Advanced directory structure initialization
function Initialize-ProjectStructure {
    Write-LogMessage "Initializing enterprise project structure..." -Level Info
    
    $directories = @("data", "logs", "backups", "config", "temp")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir -PathType Container)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-LogMessage "Created directory: $dir" -Level Info
        }
    }
    
    # Set appropriate permissions for security
    $dataAcl = Get-Acl "data"
    $dataAcl.SetAccessRuleProtection($true, $false)
    Set-Acl -Path "data" -AclObject $dataAcl -ErrorAction SilentlyContinue
    
    Write-LogMessage "Project structure initialized" -Level Success
}

# Enterprise startup script generation
function New-StartupScripts {
    Write-LogMessage "Generating enterprise startup scripts..." -Level Info
    
    # Create advanced PowerShell startup script
    $psScript = @'
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

Write-StartupLog "🚀 ScrapeMaster Intelligence Platform" -Level Success
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
Write-StartupLog "🌐 Starting web application..." -Level Info
Write-StartupLog "📊 Dashboard: http://localhost:8501" -Level Success
Write-StartupLog "🎯 Revenue Target: $15,000 MRR by Month 3" -Level Warning
Write-StartupLog "💡 Quick Start: Add monitoring targets via dashboard" -Level Info
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
'@

    $psScript | Out-File -FilePath "start_scrapemaster.ps1" -Encoding UTF8 -Force
    
    # Create batch file for Windows compatibility
    $batchScript = @'
@echo off
setlocal enabledelayedexpansion

echo.
echo 🚀 ScrapeMaster Intelligence Platform
echo =====================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found. Run deploy.ps1 first.
    pause & exit /b 1
)

if not exist "src\app.py" (
    echo ❌ Application not found. Check installation.
    pause & exit /b 1
)

call venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo ❌ Virtual environment activation failed
    pause & exit /b 1
)

if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo 🌐 Starting ScrapeMaster Intelligence...
echo 📊 Dashboard: http://localhost:8501
echo 💰 Revenue Target: $15,000 MRR by Month 3
echo.

streamlit run src\app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false

if !errorlevel! neq 0 (
    echo ❌ Application startup failed
    pause & exit /b 1
)
'@

    $batchScript | Out-File -FilePath "start_scrapemaster.bat" -Encoding ASCII -Force
    
    Write-LogMessage "Startup scripts generated successfully" -Level Success
}

# Advanced testing and validation
function Test-Installation {
    Write-LogMessage "Executing comprehensive installation validation..." -Level Info
    
    # Test Python module imports
    $testModules = @("streamlit", "pandas", "plotly", "requests", "bs4")
    $importTest = $testModules | ForEach-Object { "import $_" } | Join-String -Separator "; "
    
    try {
        & python -c "$importTest; print('✅ All core modules validated')"
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Module validation successful" -Level Success
        } else {
            throw "Module import test failed"
        }
    } catch {
        Write-LogMessage "Module validation failed: $($_.Exception.Message)" -Level Error
        return $false
    }
    
    # Test Streamlit availability
    try {
        $streamlitVersion = & streamlit --version 2>&1
        Write-LogMessage "Streamlit validation: $streamlitVersion" -Level Success
    } catch {
        Write-LogMessage "Streamlit validation failed" -Level Warning
    }
    
    return $true
}

# Main deployment orchestration
function Start-Deployment {
    try {
        Write-LogMessage "Initiating enterprise deployment sequence..." -Level Info
        
        Test-SystemDependencies
        Initialize-VirtualEnvironment  
        Install-PythonDependencies
        Initialize-ProjectStructure
        New-StartupScripts
        
        if (Test-Installation) {
            Write-LogMessage "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY" -Level Success
            Show-CompletionSummary
        } else {
            Write-LogMessage "Deployment completed with warnings" -Level Warning
        }
        
    } catch {
        Write-LogMessage "Deployment failed: $($_.Exception.Message)" -Level Error
        Write-LogMessage "Stack trace: $($_.ScriptStackTrace)" -Level Error
        exit 1
    }
}

# Enterprise completion summary
function Show-CompletionSummary {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host "🎉 SCRAPEMASTER INTELLIGENCE - DEPLOYMENT COMPLETE" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "📋 QUICK START GUIDE:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. 🚀 LAUNCH APPLICATION:" -ForegroundColor White
    Write-Host "   → PowerShell: .\start_scrapemaster.ps1" -ForegroundColor Cyan
    Write-Host "   → Batch File: .\start_scrapemaster.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. 🌐 ACCESS DASHBOARD:" -ForegroundColor White  
    Write-Host "   → URL: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "   → Dashboard loads automatically" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. 💰 REVENUE GENERATION:" -ForegroundColor White
    Write-Host "   → Configure monitoring targets" -ForegroundColor Cyan
    Write-Host "   → Pricing: $99-499/month per client" -ForegroundColor Cyan
    Write-Host "   → Target: $15,000 MRR by Month 3" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📈 REVENUE PROJECTIONS:" -ForegroundColor Green
    Write-Host "   → Month 1: $3,000 MRR (15 clients)" -ForegroundColor White
    Write-Host "   → Month 3: $15,000 MRR (75 clients)" -ForegroundColor White
    Write-Host "   → Month 6: $25,000 MRR (125 clients)" -ForegroundColor White
    Write-Host "   → Year 1: $50,000 MRR (250 clients)" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 IMMEDIATE NEXT STEPS:" -ForegroundColor Magenta
    Write-Host "   1. Launch platform: .\start_scrapemaster.ps1" -ForegroundColor White
    Write-Host "   2. Create demo targets for testing" -ForegroundColor White
    Write-Host "   3. Begin client outreach campaigns" -ForegroundColor White
    Write-Host "   4. Set up payment processing (Stripe)" -ForegroundColor White
    Write-Host ""
    Write-LogMessage "🚀 Ready to generate revenue! Execute: .\start_scrapemaster.ps1" -Level Success
}

# Execute main deployment
Start-Deployment