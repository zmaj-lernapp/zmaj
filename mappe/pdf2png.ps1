# Wandelt ein PDF seitenweise in PNG-Bilder - mit dem PDF-Renderer, der in
# Windows steckt. Damit laesst sich ein erzeugtes Word-Dokument auch ohne
# LibreOffice oder Poppler wirklich ansehen, nicht nur im Text pruefen.
#
# Aufruf:  powershell -File pdf2png.ps1 <datei.pdf> <zielordner> [breite]

param(
  [Parameter(Mandatory = $true)][string]$Pdf,
  [Parameter(Mandatory = $true)][string]$Ziel,
  [int]$Breite = 1000
)

Add-Type -AssemblyName System.Runtime.WindowsRuntime

# WinRT arbeitet mit IAsyncOperation. PowerShell kann damit nichts anfangen,
# deshalb der Umweg ueber AsTask und .Wait().
$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() |
  Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
  } | Select-Object -First 1

# Zweite Fassung fuer IAsyncAction - das ist etwas anderes als
# IAsyncOperation<T>: ein Vorgang OHNE Rueckgabewert. RenderToStreamAsync
# gehoert dazu, deshalb scheiterte der erste Versuch.
$asTaskOhne = [System.WindowsRuntimeSystemExtensions].GetMethods() |
  Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction'
  } | Select-Object -First 1

function Warte($op, $typ) {
  $m = $asTask.MakeGenericMethod($typ)
  $t = $m.Invoke($null, @($op))
  $t.Wait(120000) | Out-Null
  return $t.Result
}

function WarteOhne($op) {
  $t = $asTaskOhne.Invoke($null, @($op))
  $t.Wait(120000) | Out-Null
}

$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Storage.FileIO, Windows.Storage, ContentType = WindowsRuntime]

if (-not (Test-Path $Ziel)) { New-Item -ItemType Directory -Path $Ziel | Out-Null }

# GetFileFromPathAsync verlangt einen vollen Pfad. Mit einem relativen Ziel
# scheitert jede Seite still: der Vorgang bricht ab, $out bleibt leer, und
# es entstehen elf Dateien mit 0 Bytes. Deshalb hier einmal aufloesen.
$Ziel = (Resolve-Path $Ziel).Path

$datei = Warte ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $Pdf).Path)) ([Windows.Storage.StorageFile])
$doc = Warte ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($datei)) ([Windows.Data.Pdf.PdfDocument])

Write-Output "Seiten: $($doc.PageCount)"

for ($i = 0; $i -lt $doc.PageCount; $i++) {
  $seite = $doc.GetPage($i)
  $name = Join-Path $Ziel ("seite-{0:d2}.png" -f ($i + 1))

  # Eine Datei zum Hineinschreiben anlegen und als Stream oeffnen
  Set-Content -Path $name -Value $null -Encoding Byte -ErrorAction SilentlyContinue
  $out = Warte ([Windows.Storage.StorageFile]::GetFileFromPathAsync($name)) ([Windows.Storage.StorageFile])
  $stream = Warte ($out.OpenAsync(1)) ([Windows.Storage.Streams.IRandomAccessStream])   # 1 = ReadWrite

  $opt = New-Object Windows.Data.Pdf.PdfPageRenderOptions
  $opt.DestinationWidth = $Breite

  WarteOhne ($seite.RenderToStreamAsync($stream, $opt))

  $stream.Dispose()
  Write-Output ("  {0}  ({1:n0} Bytes)" -f $name, (Get-Item $name).Length)
}
