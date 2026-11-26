$ErrorActionPreference = 'Stop'
$chapterDirectory = Join-Path $env:TEMP 'ticketing_chapter4_revision_20261013'
$chapterWord = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
$chapterDocument = $null
try {
    Write-Output 'Connected to running Word for document export.'
    $missing = [System.Type]::Missing
    $chapterDocument = $chapterWord.Documents.Open((Join-Path $chapterDirectory 'chapter4.docx'), $false, $false, $false, $missing, $missing, $false, $missing, $missing, $missing, $missing, $false)
    Write-Output 'Opened generated chapter only.'
    $chapterDocument.Fields.Update() | Out-Null
    $chapterDocument.Repaginate()
    $chapterDocument.Save()
    $chapterDocument.ExportAsFixedFormat((Join-Path $chapterDirectory 'chapter4.pdf'),17)
    Write-Output ('Pages: ' + $chapterDocument.ComputeStatistics(2))
} finally {
    if ($null -ne $chapterDocument) { $chapterDocument.Close(0) }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($chapterWord) | Out-Null
}
