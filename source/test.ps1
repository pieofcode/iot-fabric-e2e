

$list = Get-ChildItem -Path . -Recurse | `
        Where-Object { $_.PSIsContainer -eq $false -and $_.Extension -eq '.txt' }

"Total Files: {0}" -f $list.Length | Write-Output

foreach ($n in $list) 
{
    "File Name: {0}, Base Name: {1}, Full Name: {2}" -f $n.Name,$n.BaseName,$n.FullName | Write-Output

    $test = "{0}{1}" -f $n.BaseName,$n.Extension
    Write-Output $test

    Write-Output $n.Directory
}




