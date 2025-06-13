# Get-InstalledSoftware.ps1
# Description: This script retrieves a list of all installed software, including additional properties like InstallLocation, EstimatedSize, and URLs, and exports it to a CSV file.

# Function to retrieve installed software
function Get-InstalledSoftware {
    Write-Host "Retrieving installed software. This may take a few moments..." -ForegroundColor Cyan

    # Collect installed software from the registry
    $registryPaths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )

    $softwareList = @()

    foreach ($path in $registryPaths) {
        try {
            $items = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue
            foreach ($item in $items) {
                # Construct the software entry with additional properties
                $installDate = $null
                if ($item.InstallDate -match '^\d{8}$') {
                    $installDate = ([datetime]::ParseExact($item.InstallDate, 'yyyyMMdd', $null)).ToString('yyyy-MM-dd')
                }

                $softwareList += [PSCustomObject]@{
                    Name            = $item.DisplayName
                    Version         = $item.DisplayVersion
                    Publisher       = $item.Publisher
                    InstallDate     = $installDate
                    InstallLocation = $item.InstallLocation
                    EstimatedSize   = if ($item.EstimatedSize) { 
                                         "{0:N0} KB" -f $item.EstimatedSize 
                                     } else { $null }
                    URLInfoAbout    = $item.URLInfoAbout
                    URLUpdateInfo   = $item.URLUpdateInfo
                }
            }
        } catch {
            Write-Host "Error reading from registry path: $path" -ForegroundColor Red
        }
    }

    # Filter out entries without a name
    $softwareList = $softwareList | Where-Object { $_.Name -ne $null }
    return $softwareList
}

# Main script execution
$dumpFolder = "J:\Ennead Applied Computing\DUMP\installed_software"

# Check if J: drive exists
if (-not (Test-Path "J:")) {
    Write-Host "J: drive is not accessible. Exiting." -ForegroundColor Yellow
    exit 0
}

# Check if dump folder exists
if (-not (Test-Path $dumpFolder)) {
    try {
        New-Item -ItemType Directory -Path $dumpFolder -Force | Out-Null
        Write-Host "Created dump folder: $dumpFolder" -ForegroundColor Yellow
    } catch {
        Write-Host "Failed to create dump folder: $dumpFolder" -ForegroundColor Red
        exit 1
    }
}

$computerName = $env:COMPUTERNAME
$outputFile = Join-Path $dumpFolder "EnneadTabAuto_InstalledSoftware_${computerName}.csv"

try {
    $installedSoftware = Get-InstalledSoftware
    if ($installedSoftware.Count -gt 0) {
        $installedSoftware | Sort-Object Name | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8
        Write-Host "Installed software list exported to $outputFile" -ForegroundColor Green
    } else {
        Write-Host "No installed software found." -ForegroundColor Yellow
    }
} catch {
    Write-Host "An error occurred while exporting the software list: $_" -ForegroundColor Red
}
