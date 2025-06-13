param(
    [string]$Format = "BOTH",
    [int]$BatchSize = 1000,
    [switch]$DebugMode = $false
)

# Bypass execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Get computer info
$computerName = $env:COMPUTERNAME
$scanTimestamp = Get-Date

Write-Host "Starting file scan for $computerName..." -ForegroundColor Green
Write-Host "This may take several minutes to complete." -ForegroundColor Yellow

# Enhanced logging function
function Write-DebugLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    if ($global:logFile) {
        try { $logMessage | Out-File -FilePath $global:logFile -Append -Encoding UTF8 } catch {}
    }
}

# Function to test drive access
function Test-DriveAccess {
    param([string]$DrivePath)
    try {
        Write-DebugLog "Testing access to drive: $DrivePath"
        
        # Test basic path existence
        if (-not (Test-Path $DrivePath)) {
            Write-DebugLog "Drive path does not exist: $DrivePath" "ERROR"
            return $false
        }
        
        # Test read permissions
        try {
            $testItems = Get-ChildItem -Path $DrivePath -ErrorAction Stop | Select-Object -First 5
            Write-DebugLog "Successfully accessed drive root, found $($testItems.Count) items"
        } catch {
            Write-DebugLog "Cannot list drive contents: $($_.Exception.Message)" "ERROR"
            return $false
        }
        
        # Test if it's a system drive and check available space
        try {
            $driveInfo = Get-PSDrive -Name $DrivePath.Substring(0,1) -ErrorAction SilentlyContinue
            if ($driveInfo) {
                $freeSpace = [Math]::Round($driveInfo.Free / 1GB, 2)
                $usedSpace = [Math]::Round($driveInfo.Used / 1GB, 2)
                Write-DebugLog "Drive space - Free: $freeSpace GB, Used: $usedSpace GB"
            }
        } catch {
            Write-DebugLog "Could not get drive space info: $($_.Exception.Message)" "WARNING"
        }
        
        return $true
    } catch {
        Write-DebugLog "Drive access test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Function to get detailed WMI drive info
function Get-DriveDetails {
    param([object]$Drive)
    try {
        $details = @{
            DeviceID = $Drive.DeviceID
            FileSystem = $Drive.FileSystem
            Size = if($Drive.Size) { [Math]::Round($Drive.Size / 1GB, 2) } else { "Unknown" }
            FreeSpace = if($Drive.FreeSpace) { [Math]::Round($Drive.FreeSpace / 1GB, 2) } else { "Unknown" }
            DriveType = switch($Drive.DriveType) {
                1 { "No Root Directory" }
                2 { "Removable Disk" }
                3 { "Local Disk" }
                4 { "Network Drive" }
                5 { "Compact Disc" }
                6 { "RAM Disk" }
                default { "Unknown ($($Drive.DriveType))" }
            }
            MediaType = $Drive.MediaType
            VolumeName = $Drive.VolumeName
        }
        return $details
    } catch {
        Write-DebugLog "Could not get drive details: $($_.Exception.Message)" "WARNING"
        return @{ DeviceID = $Drive.DeviceID; Status = "Details unavailable" }
    }
}

# Output paths
$jDrivePath = "J:\Ennead Applied Computing\DUMP\my_computer_log"
$envDumpPath = Join-Path $env:USERPROFILE "Documents\EnneadTab Ecosystem\Dump\my_computer_log"

# Create directories if they don't exist
$validPaths = @()

# Check J: drive
try {
    if (Test-Path "J:\") {
        if (-not (Test-Path $jDrivePath)) {
            New-Item -Path $jDrivePath -ItemType Directory -Force | Out-Null
        }
        $validPaths += $jDrivePath
        Write-DebugLog "J: drive dump path available: $jDrivePath"
    } else {
        Write-Host "WARNING: J: drive not available" -ForegroundColor Yellow
        Write-DebugLog "J: drive not available" "WARNING"
    }
} catch {
    Write-Host "WARNING: Could not create dump directory on J: drive: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-DebugLog "Could not create J: drive dump directory: $($_.Exception.Message)" "WARNING"
}

# Check Environment dump folder
try {
    if (-not (Test-Path $envDumpPath)) {
        New-Item -Path $envDumpPath -ItemType Directory -Force | Out-Null
    }
    $validPaths += $envDumpPath
    Write-DebugLog "Environment dump path available: $envDumpPath"
} catch {
    Write-Host "WARNING: Could not create environment dump directory: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-DebugLog "Could not create environment dump directory: $($_.Exception.Message)" "WARNING"
}

# Exit if no valid paths available
if ($validPaths.Count -eq 0) {
    Write-Host "ERROR: No valid output paths available. Cannot proceed." -ForegroundColor Red
    Write-DebugLog "No valid output paths available, exiting script" "ERROR"
    exit 1
}

Write-DebugLog "Valid output paths: $($validPaths.Count)"
foreach ($path in $validPaths) {
    Write-DebugLog "  - $path"
}

# Initialize log file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$global:logFile = Join-Path $validPaths[0] "$computerName`_FileScan_Debug_$timestamp.log"
Write-DebugLog "=== File Scanner Debug Log Started ==="
Write-DebugLog "Computer: $computerName"
Write-DebugLog "User: $env:USERNAME"

# Check admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
Write-DebugLog "Admin Rights: $isAdmin"

if (-not $isAdmin) {
    Write-Host "WARNING: Running without administrator privileges. Some system files may be inaccessible." -ForegroundColor Red
    Write-DebugLog "Running without administrator privileges" "WARNING"
}

# Function to get file information safely
function Get-SafeFileInfo {
    param([System.IO.FileInfo]$File)
    try {
        $fileInfo = [PSCustomObject]@{
            ComputerName = $computerName
            ScanDateTime = $scanTimestamp.ToString("yyyy-MM-dd HH:mm:ss")
            FilePath = $File.FullName
            FileName = $File.Name
            Directory = $File.DirectoryName
            Extension = $File.Extension
            SizeBytes = $File.Length
            SizeMB = [Math]::Round($File.Length / 1MB, 2)
            DateCreated = $File.CreationTime.ToString("yyyy-MM-dd HH:mm:ss")
            DateModified = $File.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            DateAccessed = $File.LastAccessTime.ToString("yyyy-MM-dd HH:mm:ss")
            IsReadOnly = $File.IsReadOnly
            IsHidden = ($File.Attributes -band [System.IO.FileAttributes]::Hidden) -ne 0
            IsSystem = ($File.Attributes -band [System.IO.FileAttributes]::System) -ne 0
        }
        return $fileInfo
    } catch { 
        Write-DebugLog "Error getting file info for $($File.FullName): $($_.Exception.Message)" "WARNING"
        return $null 
    }
}

# Function to save data in batches
function Save-DataBatch {
    param([array]$Data, [string]$FilePath, [string]$Format, [bool]$IsFirstBatch)
    try {
        if ($Format -eq "JSON") {
            if ($IsFirstBatch) { "[" | Out-File -FilePath $FilePath -Encoding UTF8 }
            if (-not $IsFirstBatch) { "," | Out-File -FilePath $FilePath -Append -Encoding UTF8 }
            $jsonData = ($Data | ConvertTo-Json -Depth 3) -replace '^\[|\]$'
            $jsonData | Out-File -FilePath $FilePath -Append -Encoding UTF8
        } elseif ($Format -eq "CSV") {
            if ($IsFirstBatch) { $Data | Export-Csv -Path $FilePath -NoTypeInformation -Encoding UTF8 }
            else { $Data | Export-Csv -Path $FilePath -NoTypeInformation -Append -Encoding UTF8 }
        }
    } catch {
        Write-DebugLog "Error saving batch to $FilePath ($Format): $($_.Exception.Message)" "ERROR"
    }
}

# Function to finalize JSON file
function Complete-JsonFile { 
    param([string]$FilePath)
    try { 
        "]" | Out-File -FilePath $FilePath -Append -Encoding UTF8 
        Write-DebugLog "JSON file finalized: $FilePath"
    } catch {
        Write-DebugLog "Error finalizing JSON file $FilePath - $($_.Exception.Message)" "ERROR"
    }
}

# Main execution
Write-Host "Scanning files on $computerName..." -ForegroundColor Cyan
Write-DebugLog "Starting file scan process"
$totalFiles = 0; $processedFiles = 0; $batchCount = 0; $startTime = Get-Date

# Prepare output files for all valid paths
$outputFiles = @()
foreach ($path in $validPaths) {
    $outputFiles += @{
        Path = $path
        CSV = Join-Path $path "$computerName`_AllFiles_$timestamp.csv"
        JSON = Join-Path $path "$computerName`_AllFiles_$timestamp.json"
    }
}

Write-DebugLog "Output files prepared for $($outputFiles.Count) locations:"
foreach ($output in $outputFiles) {
    Write-DebugLog "  Location: $($output.Path)"
    Write-DebugLog "    CSV: $($output.CSV)"
    Write-DebugLog "    JSON: $($output.JSON)"
}

# Get all drives (only fixed drives)
Write-DebugLog "Discovering drives..."
try { 
    $drives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
    Write-DebugLog "WMI method successful, found $($drives.Count) fixed drives"
} catch { 
    Write-DebugLog "WMI method failed: $($_.Exception.Message), trying alternative method" "WARNING"
    $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Root -like "*:\" }
    Write-DebugLog "Alternative method found $($drives.Count) drives"
}

Write-Host "Found $($drives.Count) drives to scan" -ForegroundColor Green
Write-DebugLog "=== Drive Analysis ==="

# Analyze each drive first
foreach ($drive in $drives) {
    $driveDetails = Get-DriveDetails -Drive $drive
    $drivePath = if ($drive.DeviceID) { "$($drive.DeviceID)\" } else { $drive.Root }
    
    Write-DebugLog "Drive: $drivePath"
    Write-DebugLog "  Type: $($driveDetails.DriveType)"
    Write-DebugLog "  File System: $($driveDetails.FileSystem)"
    Write-DebugLog "  Size: $($driveDetails.Size) GB"
    Write-DebugLog "  Free Space: $($driveDetails.FreeSpace) GB"
    Write-DebugLog "  Volume Name: $($driveDetails.VolumeName)"
}

Write-DebugLog "=== Starting Drive Scanning ==="
# Process each drive
foreach ($drive in $drives) {
    $driveStartTime = Get-Date
    $drivePath = if ($drive.DeviceID) { "$($drive.DeviceID)\" } else { $drive.Root }
    Write-Host "Scanning $drivePath..." -ForegroundColor Cyan
    Write-DebugLog "--- Processing Drive: $drivePath ---"
    
    try {
        # Test drive access first
        if (-not (Test-DriveAccess -DrivePath $drivePath)) {
            Write-DebugLog "Skipping drive $drivePath due to access issues" "ERROR"
            continue
        }
        
        Write-DebugLog "Starting file enumeration for $drivePath"
        
        # Get all files recursively, skip system and protected directories
        $files = Get-ChildItem -Path $drivePath -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
            $_.FullName -notlike "*\Windows\System32\*" -and
            $_.FullName -notlike "*\Windows\SysWOW64\*" -and
            $_.FullName -notlike "*\`$Recycle.Bin\*" -and
            $_.FullName -notlike "*\System Volume Information\*" -and
            $_.FullName -notlike "*\Windows\WinSxS\*" -and
            $_.FullName -notlike "*\hiberfil.sys" -and
            $_.FullName -notlike "*\pagefile.sys" -and
            $_.FullName -notlike "*\swapfile.sys"
        }

        $driveFileCount = ($files | Measure-Object).Count
        $totalFiles += $driveFileCount
        Write-Host "   Found $driveFileCount files" -ForegroundColor Green
        Write-DebugLog "Found $driveFileCount files on $drivePath"

        if ($driveFileCount -eq 0) {
            Write-DebugLog "No accessible files found on $drivePath, checking if drive is empty or access is restricted"
            try {
                $allItems = Get-ChildItem -Path $drivePath -ErrorAction SilentlyContinue
                Write-DebugLog "Drive has $($allItems.Count) total items (including folders)"
            } catch {
                Write-DebugLog "Cannot enumerate drive contents: $($_.Exception.Message)" "ERROR"
            }
        }

        # Process files in batches
        $currentBatch = @()
        $driveProcessedFiles = 0
        foreach ($file in $files) {
            $fileInfo = Get-SafeFileInfo -File $file
            if ($fileInfo) {
                $currentBatch += $fileInfo
                $processedFiles++
                $driveProcessedFiles++
                
                if ($currentBatch.Count -ge $BatchSize) {
                    $batchCount++
                    Write-Host "   Processing batch $batchCount ($processedFiles files total)..." -ForegroundColor Yellow
                    Write-DebugLog "Processing batch $batchCount with $($currentBatch.Count) files"
                    
                    if ($Format -eq "JSON" -or $Format -eq "BOTH") {
                        foreach ($output in $outputFiles) {
                            Save-DataBatch -Data $currentBatch -FilePath $output.JSON -Format "JSON" -IsFirstBatch ($batchCount -eq 1)
                        }
                    }
                    if ($Format -eq "CSV" -or $Format -eq "BOTH") {
                        foreach ($output in $outputFiles) {
                            Save-DataBatch -Data $currentBatch -FilePath $output.CSV -Format "CSV" -IsFirstBatch ($batchCount -eq 1)
                        }
                    }
                    $currentBatch = @()
                }
            }
        }
        
        # Process remaining files
        if ($currentBatch.Count -gt 0) {
            $batchCount++
            Write-Host "   Processing final batch $batchCount ($processedFiles files total)..." -ForegroundColor Yellow
            Write-DebugLog "Processing final batch $batchCount with $($currentBatch.Count) files"
            
            if ($Format -eq "JSON" -or $Format -eq "BOTH") {
                foreach ($output in $outputFiles) {
                    Save-DataBatch -Data $currentBatch -FilePath $output.JSON -Format "JSON" -IsFirstBatch ($batchCount -eq 1)
                }
            }
            if ($Format -eq "CSV" -or $Format -eq "BOTH") {
                foreach ($output in $outputFiles) {
                    Save-DataBatch -Data $currentBatch -FilePath $output.CSV -Format "CSV" -IsFirstBatch ($batchCount -eq 1)
                }
            }
        }
        
        $driveEndTime = Get-Date
        $driveTime = $driveEndTime - $driveStartTime
        Write-DebugLog "Drive $drivePath completed: $driveProcessedFiles files in $($driveTime.TotalSeconds) seconds"
        
    } catch { 
        $errorDetails = @{
            Exception = $_.Exception.GetType().Name
            Message = $_.Exception.Message
            StackTrace = $_.Exception.StackTrace
            TargetSite = $_.TargetSite
        }
        Write-Host "   Error scanning $drivePath, continuing..." -ForegroundColor Red
        Write-DebugLog "DETAILED ERROR scanning $drivePath" "ERROR"
        Write-DebugLog "  Exception Type: $($errorDetails.Exception)" "ERROR"
        Write-DebugLog "  Message: $($errorDetails.Message)" "ERROR"
        Write-DebugLog "  Target Site: $($errorDetails.TargetSite)" "ERROR"
        if ($DebugMode) {
            Write-DebugLog "  Stack Trace: $($errorDetails.StackTrace)" "ERROR"
        }
    }
}

# Finalize JSON files
if ($Format -eq "JSON" -or $Format -eq "BOTH") {
    foreach ($output in $outputFiles) {
        Complete-JsonFile -FilePath $output.JSON
    }
}

$endTime = Get-Date; $totalTime = $endTime - $startTime
Write-DebugLog "=== File Scan Completed ==="
Write-DebugLog "Total processing time: $($totalTime.TotalSeconds) seconds"
Write-DebugLog "Files processed: $processedFiles"
Write-DebugLog "Batches created: $batchCount"

# Create summary
$summaryText = @"
File Scan Summary for Computer: $computerName
Scan completed on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Total files processed: $processedFiles
Total batches: $batchCount
Time elapsed: $($totalTime.Hours):$('{0:D2}' -f $totalTime.Minutes):$('{0:D2}' -f $totalTime.Seconds)
Average rate: $(if ($totalTime.TotalSeconds -gt 0) { [Math]::Round($processedFiles / $totalTime.TotalSeconds, 0) } else { 0 }) files/second

Output files saved to:
$(foreach ($path in $validPaths) { "- $path`n" })

Debug log saved to: $global:logFile
"@

try {
    foreach ($path in $validPaths) {
        $summaryText | Out-File -FilePath (Join-Path $path "$computerName`_ScanSummary_$timestamp.txt") -Encoding UTF8
    }
    Write-DebugLog "Summary files created successfully in $($validPaths.Count) locations"
} catch {
    Write-DebugLog "Error creating summary file: $($_.Exception.Message)" "ERROR"
}

Write-Host "`nFile scan completed for $computerName!" -ForegroundColor Green
Write-Host "Files saved to $($validPaths.Count) location(s):" -ForegroundColor Cyan
foreach ($path in $validPaths) {
    Write-Host "  - $path" -ForegroundColor Cyan
}
Write-Host "Debug log available at: $global:logFile" -ForegroundColor Yellow

# Pause equivalent for PowerShell
Write-Host "`nPress any key to continue..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 