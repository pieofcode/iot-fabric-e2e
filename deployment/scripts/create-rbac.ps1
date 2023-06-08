param (
    [string]$sub
)

$token = "/subscriptions/{0}" -f $sub
# az ad sp create-for-rbac --role="Contributor" --scopes=$token
$output = New-AzADServicePrincipal -Role "Contributor" -Scope $token -Tenant
# $output = (az ad sp create-for-rbac --role="Contributor" --scopes=$token)
Write-Host $output