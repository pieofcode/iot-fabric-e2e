param (
    [string]$gateway,
    [string]$device,
    [string]$datamodel,
    [string]$properties
)


Write-Output "################################################"
"Starting device emulator for: {0}" -f $device | Write-Output
Write-Output "################################################"

Set-Location .\Emulator
dotnet run $gateway $device $datamodel $properties
# dotnet run edge-hub factory-a paint_defect "type:a|frequency:10"
# dotnet run edge-hub sensor-1 location_sensor frequency:5

Set-Location ..
