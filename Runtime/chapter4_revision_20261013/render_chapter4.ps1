$ErrorActionPreference = 'Stop'
$chapterDirectory = Join-Path $env:TEMP 'ticketing_chapter4_revision_20261013'
$chapterWord = New-Object -ComObject Word.Application
$chapterWord.Visible = $false
$chapterWord.DisplayAlerts = 0
$chapterDocument = $null
try {
    $chapterDocument = $chapterWord.Documents.Open((Join-Path $chapterDirectory 'chapter4.docx'), $false, $false)
    $chapterDocument.Fields.Update() | Out-Null
    $chapterDocument.Repaginate()
    $chapterDocument.Save()
    $chapterDocument.ExportAsFixedFormat((Join-Path $chapterDirectory 'chapter4.pdf'),17)
    Write-Output ('Pages: ' + $chapterDocument.ComputeStatistics(2))
} finally {
    if ($null -ne $chapterDocument) { $chapterDocument.Close(0) }
    $chapterWord.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($chapterWord) | Out-Null
}
