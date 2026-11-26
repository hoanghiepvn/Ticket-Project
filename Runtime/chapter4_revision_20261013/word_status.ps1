$ErrorActionPreference = 'Stop'
$chapterWord = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
Write-Output ('Printer: ' + $chapterWord.ActivePrinter)
Write-Output ('Background printing: ' + $chapterWord.Options.PrintBackground)
Write-Output ('Background saving: ' + $chapterWord.BackgroundSavingStatus)
$chapterDocument = $chapterWord.Documents.Item('chapter4.docx')
Write-Output ('Pages: ' + $chapterDocument.ComputeStatistics(2))
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($chapterWord) | Out-Null
