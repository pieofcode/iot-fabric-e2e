param (
  [string]$gateway
)

$IoTHub = Get-AzIotHub | Where-Object { $_.Name -eq $gateway }
if (!$IoTHub || [string]::IsNullOrEmpty($IoTHub.Name)) {
  "Invalid IoT Hub reference: {0}" -f $gateway | Write-Output 
  exit
}

$devices = Get-AzIotHubDevice -ResourceGroupName $IoTHub.Resourcegroup -IotHubName $IoTHub.Name | Format-List -Property Id | Out-String
# $option = [System.StringSplitOptions]::TrimEntries
$lines = ($devices -split "`r?`n")
# Write-Output $lines

Foreach ($device in $lines) {
  if ([string]::IsNullOrEmpty($device)) {
    continue
  }
  # $option = [System.StringSplitOptions]::TrimEntries
  
  $id = $device.Replace("Id : ", "").Trim()
  "Deleting - {0}, Resource group - {1}, Iot hub name - {2}" -f $id, $IoTHub.Resourcegroup, $IoTHub.Name | Write-Output
  Remove-AzIotHubDevice -ResourceGroupName $IoTHub.Resourcegroup -IotHubName $IoTHub.Name -DeviceId $id
  # az iot hub device-identity delete --device-id $id --hub-name $IoTHub.Name
  
  # Remove the credential files from the disk
  $path = "./Devices/{0}/{1}.txt" -f $gateway, $id
  "Deleting credential file: {0}" -f $path | Write-Output
  Remove-Item  -Force $path

}

Write-Output "############################################"
Write-Output "All the devices are deleted successfully!"
Write-Output "############################################"
