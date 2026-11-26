$ErrorActionPreference = 'Stop'
$reportPath = 'C:\Users\zicza\AppData\Local\Temp\ticket_report_de_20261006\report.docx'
$pdfPath = 'C:\Users\zicza\AppData\Local\Temp\ticket_report_de_20261006\report.pdf'
$wordApp = New-Object -ComObject Word.Application
$wordApp.Visible = $false
$wordApp.DisplayAlerts = 0
$reportDocument = $null
try {
    $reportDocument = $wordApp.Documents.Open($reportPath, $false, $false)
    $reportDocument.Fields.Update() | Out-Null
    foreach ($tocItem in $reportDocument.TablesOfContents) { $tocItem.Update() }
    $reportDocument.Repaginate()
    foreach ($tocItem in $reportDocument.TablesOfContents) { $tocItem.UpdatePageNumbers() }
    $reportDocument.Save()
    $reportDocument.ExportAsFixedFormat($pdfPath,17)
    Write-Output ('Pages: ' + $reportDocument.ComputeStatistics(2))
    Write-Output ('Contents fields: ' + $reportDocument.TablesOfContents.Count)
} finally {
    if ($null -ne $reportDocument) { $reportDocument.Close(0) }
    $wordApp.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) | Out-Null
}
