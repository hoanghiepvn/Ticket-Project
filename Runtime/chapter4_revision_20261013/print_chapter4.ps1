$ErrorActionPreference = 'Stop'
$chapterDirectory = Join-Path $env:TEMP 'ticketing_chapter4_revision_20261013'
$chapterWord = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
$chapterDocument = $chapterWord.Documents.Item('chapter4.docx')
if ($chapterDocument.FullName -ne (Join-Path $chapterDirectory 'chapter4.docx')) { throw 'Generated chapter path does not match.' }
$missing = [System.Type]::Missing
Write-Output 'Printing generated chapter to local PDF.'
$chapterDocument.PrintOut($false,$false,0,(Join-Path $chapterDirectory 'chapter4_print.pdf'),$missing,$missing,0,1,$missing,0,$true,$false,$missing,$missing,$missing,$missing,$missing,$missing)
Write-Output 'Printed generated chapter.'
