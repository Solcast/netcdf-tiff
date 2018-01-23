$a = Get-Date
$d = $a.ToUniversalTime()
$year = $d.Year
$day = $d.DayOfYear.ToString().PadLeft(3,'0')
$hour = $d.Hour

Write-Host "aws s3 sync s3://noaa-goes16/ABI-L2-CMIPF/$year/$day/$hour ."
