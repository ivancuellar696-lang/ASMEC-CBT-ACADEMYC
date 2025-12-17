# build_apk.ps1
Write-Host "=== CONSTRUYENDO APK DE ASMET CON DOCKER ===" -ForegroundColor Green

# Verificar que estamos en el directorio correcto
$projectDir = Get-Location
Write-Host "Directorio del proyecto: $projectDir"

# Verificar que Docker esté en ejecución
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker no está en ejecución. Inicia Docker Desktop y vuelve a intentar." -ForegroundColor Red
    exit 1
}

# Ejecutar el contenedor de Buildozer
Write-Host "`n🚀 Iniciando construcción en Docker..." -ForegroundColor Cyan

docker run --rm -it `
  -v "${projectDir}:/home/user/hostcwd" `
  -v "${env:USERPROFILE}\.buildozer:/home/user/.buildozer" `
  mkdocs/buildozer bash -c "
    cd /home/user/hostcwd &&
    echo '=== ACTUALIZANDO BUILDOCER ===' &&
    pip install --upgrade buildozer &&
    echo '=== CONSTRUYENDO APK ===' &&
    buildozer -v android debug 2>&1
  "

# Verificar si se creó el APK
if (Test-Path "${projectDir}\bin\*.apk") {
    Write-Host "`n🎉 ¡APK CONSTRUIDO EXITOSAMENTE!" -ForegroundColor Green
    Write-Host "APK en: ${projectDir}\bin\" -ForegroundColor Yellow
    Get-ChildItem "${projectDir}\bin\*.apk" | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor White
    }
} else {
    Write-Host "`n❌ Error en la construcción. Revisa los mensajes de error." -ForegroundColor Red
}