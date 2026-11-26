$ErrorActionPreference = 'Stop'
$reportPath = 'C:\Users\zicza\AppData\Local\Temp\ticket_report_20261004\report.docx'
$pdfPath = 'C:\Users\zicza\AppData\Local\Temp\ticket_report_20261004\report.pdf'
$wordApp = New-Object -ComObject Word.Application
$wordApp.Visible = $false
$wordApp.DisplayAlerts = 0
$reportDocument = $null
try {
    $reportDocument = $wordApp.Documents.Open($reportPath, $false, $false)
    Write-Output 'Opened local document'
    $reportDocument.Fields.Update() | Out-Null
    foreach ($tocItem in $reportDocument.TablesOfContents) { $tocItem.Update() }
    $reportDocument.Repaginate()
    foreach ($tocItem in $reportDocument.TablesOfContents) { $tocItem.UpdatePageNumbers() }
    $reportDocument.Save()
    Write-Output 'Saved fields'
    $reportDocument.ExportAsFixedFormat($pdfPath,17)
    Write-Output ('Pages: ' + $reportDocument.ComputeStatistics(2))
} finally {
    if ($null -ne $reportDocument) { $reportDocument.Close(0) }
    $wordApp.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) | Out-Null
}
