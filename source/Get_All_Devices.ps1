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
  "Device - {0}" -f $id | Write-Output
  
}

