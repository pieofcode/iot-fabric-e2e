param (
    [string]$gateway,
    [string]$device
    
)

$IoTHub = Get-AzIotHub | Where-Object { $_.Name -eq $gateway }
if (!$IoTHub || [string]::IsNullOrEmpty($IoTHub.Name)) {
    "Invalid IoT Hub reference: {0}" -f $gateway | Write-Output 
    exit
}
"Registering device on: {0}" -f $IoTHub.Name | Write-Output

$IotDevice = Add-AzIotHubDevice -ResourceGroupName $IoTHub.Resourcegroup -IotHubName $IoTHub.Name -DeviceId $device

$IotDeviceConStr = Get-AzIotHubDeviceConnectionString -ResourceGroupName $IoTHub.Resourcegroup -IotHubName $IoTHub.Name -DeviceId $device

$path = ".\Devices\{0}\{1}.txt" -f $gateway, $IotDeviceConStr.DeviceId

$folderName = ".\Devices\{0}\" -f $gateway

if (Test-Path $folderName) {
   
    Write-Host "Folder Exists"
    # Perform Delete file from folder operation
}
else {
    #PowerShell Create directory if not exists
    New-Item $FolderName -ItemType Directory
    Write-Host "Folder Created successfully"
}

$IotDeviceConStr.ConnectionString | Out-File -FilePath $path
"{0}" -f $IotDeviceConStr.ConnectionString | Write-Debug

"{0} Successfully created!" -f $IotDeviceConStr.DeviceId | Write-Output

