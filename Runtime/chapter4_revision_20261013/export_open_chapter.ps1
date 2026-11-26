$ErrorActionPreference = 'Stop'
$chapterDirectory = Join-Path $env:TEMP 'ticketing_chapter4_revision_20261013'
$chapterWord = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
Write-Output 'Accessing generated chapter for direct export.'
$chapterDocument = $chapterWord.Documents.Item('chapter4.docx')
if ($chapterDocument.FullName -ne (Join-Path $chapterDirectory 'chapter4.docx')) { throw 'Generated chapter path does not match.' }
Write-Output 'Exporting generated chapter PDF.'
$chapterDocument.ExportAsFixedFormat((Join-Path $chapterDirectory 'chapter4.pdf'),17)
Write-Output 'Export complete.'
