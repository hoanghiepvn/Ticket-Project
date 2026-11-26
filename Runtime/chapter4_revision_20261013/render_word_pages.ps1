$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$chapterDirectory = Join-Path $env:TEMP 'ticketing_chapter4_revision_20261013'
$chapterPages = Join-Path $chapterDirectory 'native_pages'
New-Item -ItemType Directory -Path $chapterPages -Force | Out-Null
$chapterWord = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')
$chapterDocument = $chapterWord.Documents.Item('chapter4.docx')
if ($chapterDocument.FullName -ne (Join-Path $chapterDirectory 'chapter4.docx')) { throw 'Generated chapter path does not match.' }
$pageCount = $chapterDocument.ComputeStatistics(2)
for ($pageNumber = 1; $pageNumber -le $pageCount; $pageNumber++) {
    $pageStart = $chapterDocument.GoTo(1,1,$pageNumber).Start
    $pageEnd = $chapterDocument.Content.End
    if ($pageNumber -lt $pageCount) { $pageEnd = $chapterDocument.GoTo(1,1,($pageNumber+1)).Start }
    $pageRange = $chapterDocument.Range($pageStart,$pageEnd)
    [byte[]]$pageBits = $pageRange.EnhMetaFileBits
    $pageStream = [System.IO.MemoryStream]::new($pageBits)
    $pageMetafile = [System.Drawing.Imaging.Metafile]::new($pageStream)
    $pageImage = [System.Drawing.Bitmap]::new($pageMetafile.Width*2,$pageMetafile.Height*2)
    $pageGraphics = [System.Drawing.Graphics]::FromImage($pageImage)
    $pageGraphics.Clear([System.Drawing.Color]::White)
    $pageGraphics.DrawImage($pageMetafile,0,0,$pageImage.Width,$pageImage.Height)
    $pageImage.Save((Join-Path $chapterPages ('page-'+$pageNumber+'.png')),[System.Drawing.Imaging.ImageFormat]::Png)
    $pageGraphics.Dispose(); $pageImage.Dispose(); $pageMetafile.Dispose(); $pageStream.Dispose()
    Write-Output ('Rendered page ' + $pageNumber)
}
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($chapterWord) | Out-Null
