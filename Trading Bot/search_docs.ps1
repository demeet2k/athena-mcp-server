param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$SearchArgs
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[docs-search] $Message" -ForegroundColor Cyan
}

function Get-SystemPython {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }
    throw "Python is not installed or not on PATH."
}

function Find-OAuthClientJson {
    param([string]$Folder)

    if (-not (Test-Path $Folder)) {
        return $null
    }

    $preferred = Get-ChildItem -Path $Folder -File -Filter "client_secret*.json" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($preferred) {
        return $preferred
    }

    $jsonFiles = Get-ChildItem -Path $Folder -File -Filter "*.json" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 50

    foreach ($file in $jsonFiles) {
        try {
            $obj = Get-Content -Path $file.FullName -Raw | ConvertFrom-Json -ErrorAction Stop
        } catch {
            continue
        }

        $hasInstalled = $obj.PSObject.Properties.Name -contains "installed"
        $hasWeb = $obj.PSObject.Properties.Name -contains "web"
        if (-not $hasInstalled -and -not $hasWeb) {
            continue
        }

        $node = if ($hasInstalled) { $obj.installed } else { $obj.web }
        if ($node.client_id -and $node.auth_uri -and $node.token_uri) {
            return $file
        }
    }

    return $null
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot

if (-not $SearchArgs -or $SearchArgs.Count -eq 0) {
    # User's default query from this thread.
    $SearchArgs = @("manuscript", "holographic", "time")
}

$venvPython = Join-Path $scriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Step "Creating virtual environment..."
    $systemPython = Get-SystemPython
    if ($systemPython.Count -eq 2) {
        & $systemPython[0] $systemPython[1] -m venv .venv
    } else {
        & $systemPython[0] -m venv .venv
    }
}

$venvPython = Join-Path $scriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Failed to create .venv (missing .venv\Scripts\python.exe)."
}

$requirementsFile = Join-Path $scriptRoot "requirements.txt"
$depsStamp = Join-Path $scriptRoot ".venv\.deps_installed"
$needsInstall = -not (Test-Path $depsStamp)
if (-not $needsInstall) {
    $needsInstall = (Get-Item $requirementsFile).LastWriteTimeUtc -gt (Get-Item $depsStamp).LastWriteTimeUtc
}

if ($needsInstall) {
    Write-Step "Installing/updating Python dependencies..."
    & $venvPython -m pip install -r $requirementsFile --disable-pip-version-check
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    New-Item -Path $depsStamp -ItemType File -Force | Out-Null
}

if ($SearchArgs -contains "-h" -or $SearchArgs -contains "--help") {
    & $venvPython "docs_search.py" @SearchArgs
    exit $LASTEXITCODE
}

$credentialsPath = Join-Path $scriptRoot "credentials.json"
if (-not (Test-Path $credentialsPath)) {
    $downloads = Join-Path $HOME "Downloads"
    if (Test-Path $downloads) {
        $candidate = Find-OAuthClientJson -Folder $downloads
        if ($candidate) {
            Copy-Item $candidate.FullName $credentialsPath -Force
            Write-Step "Imported OAuth credentials from Downloads ($($candidate.Name))."
        }
    }
}

if (-not (Test-Path $credentialsPath) -and $env:GOOGLE_OAUTH_CLIENT_JSON) {
    if (Test-Path $env:GOOGLE_OAUTH_CLIENT_JSON) {
        Copy-Item $env:GOOGLE_OAUTH_CLIENT_JSON $credentialsPath -Force
        Write-Step "Imported OAuth credentials from GOOGLE_OAUTH_CLIENT_JSON."
    }
}

if (-not (Test-Path $credentialsPath)) {
    Write-Warning "Missing credentials.json. Opening Google Cloud pages to generate OAuth Desktop credentials."
    Start-Process "https://console.cloud.google.com/apis/library/drive.googleapis.com"
    Start-Process "https://console.cloud.google.com/apis/credentials"

    $downloads = Join-Path $HOME "Downloads"
    if (-not (Test-Path $downloads)) {
        Write-Host ""
        Write-Host "Could not find Downloads folder; place OAuth JSON here and run again:"
        Write-Host "  $credentialsPath"
        exit 1
    }

    Write-Step "Waiting up to 10 minutes for OAuth JSON download..."
    $found = $false
    $deadline = (Get-Date).AddMinutes(10)
    while ((Get-Date) -lt $deadline) {
        $candidate = Find-OAuthClientJson -Folder $downloads

        if ($candidate) {
            Copy-Item $candidate.FullName $credentialsPath -Force
            Write-Step "Imported OAuth credentials from Downloads ($($candidate.Name))."
            $found = $true
            break
        }

        Start-Sleep -Seconds 5
    }

    if (-not $found) {
        Write-Host ""
        Write-Host "Timed out waiting for OAuth JSON download."
        Write-Host "Save it here, then rerun:"
        Write-Host "  $credentialsPath"
        Write-Host "  .\search_docs.cmd $($SearchArgs -join ' ')"
        exit 1
    }
}

Write-Step "Running Google Docs search..."
& $venvPython "docs_search.py" @SearchArgs
exit $LASTEXITCODE
