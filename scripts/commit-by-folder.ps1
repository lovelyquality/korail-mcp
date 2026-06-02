<#
.SYNOPSIS
  변경된 m-* 서버 폴더를 각각 "이모지 + 이름" 라벨로 개별 커밋합니다.

.DESCRIPTION
  여러 서버 폴더를 한 번에 커밋하면 GitHub 폴더 뷰의 라벨(마지막 커밋 메시지)이
  하나로 덮입니다. 이 스크립트는 변경된 서버 폴더마다 고정 라벨로 따로 커밋하여
  각 폴더의 라벨이 항상 유지되도록 합니다.

  - m-* 폴더 변경분: 아래 $labels 맵의 라벨로 폴더별 개별 커밋
  - 그 외 변경분(루트 README, setup.bat, proxy-worker 등): -OtherMessage 지정 시 한 커밋으로,
    미지정 시 건드리지 않고 그대로 둠

.PARAMETER OtherMessage
  m-* 폴더가 아닌 나머지 변경분을 커밋할 메시지. 생략하면 나머지는 커밋하지 않음.

.PARAMETER Push
  커밋 후 origin main 으로 push.

.EXAMPLE
  .\scripts\commit-by-folder.ps1
  .\scripts\commit-by-folder.ps1 -Push
  .\scripts\commit-by-folder.ps1 -OtherMessage "📖 docs: 루트 README 갱신" -Push
#>
param(
  [string]$OtherMessage,
  [switch]$Push
)

$ErrorActionPreference = "Stop"

# 폴더 → 라벨 (단일 진실 공급원). 새 서버 추가 시 여기만 갱신.
$labels = [ordered]@{
  "m-codebook"      = "📖 역코드·노선 코드북"
  "m-convenience"   = "🏢 역 편의시설·접근성 조회"
  "m-freight"       = "📦 화물·위험물·물류 조회"
  "m-internal-svc"  = "🏠 사내 서비스 조회"
  "m-network"       = "🗺️ 선로망·운임·운행거리 조회"
  "m-procurement"   = "🛒 조달·자재 정보 조회"
  "m-rolling-stock" = "🚅 철도차량 현황·제원 조회"
  "m-stats"         = "📊 여객·화물 수송 통계"
  "m-train-ops"     = "🚆 열차 운행 계획·이력 조회"
  "m-urban-rail"    = "🚇 도시철도 역사 시설 조회"
  "m-voc-cs"        = "📋 VOC·고객만족도·정보공개"
}

# 레포 루트로 이동 (이 스크립트는 scripts\ 하위에 있음)
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot

# PS 5.1에서 이모지가 인자로 깨지는 문제를 피하려고 메시지를 UTF-8 파일로 써서 -F 사용
function Commit-WithMessage([string]$message) {
  $tmp = [System.IO.Path]::GetTempFileName()
  [System.IO.File]::WriteAllText($tmp, $message, (New-Object System.Text.UTF8Encoding($false)))
  git commit -F $tmp | Out-Null
  Remove-Item $tmp -Force
}

# 변경된 경로 수집 (staged/unstaged/untracked). porcelain 3글자 상태코드 제거 + 따옴표 정리
$changedPaths = git status --porcelain |
  Where-Object { $_ -ne "" } |
  ForEach-Object { ($_.Substring(3)).Trim('"') }

if (-not $changedPaths) {
  Write-Host "변경된 파일이 없습니다."
  return
}

# 최상위 폴더 기준으로 그룹화
$topDirs = $changedPaths | ForEach-Object { ($_ -replace '\\','/').Split('/')[0] } | Select-Object -Unique

$committed = 0

# 1) m-* 서버 폴더: 폴더별 개별 커밋
foreach ($dir in $topDirs) {
  if ($labels.Contains($dir)) {
    git add -- $dir
    Commit-WithMessage $labels[$dir]
    Write-Host ("[{0}] {1}" -f $dir, $labels[$dir])
    $committed++
  }
}

# 2) 나머지 변경분
$others = $topDirs | Where-Object { -not $labels.Contains($_) }
if ($others) {
  if ($OtherMessage) {
    foreach ($o in $others) { git add -- $o }
    Commit-WithMessage $OtherMessage
    Write-Host ("[기타: {0}] {1}" -f ($others -join ', '), $OtherMessage)
    $committed++
  } else {
    Write-Host ""
    Write-Host ("⚠ m-* 외 변경분은 커밋하지 않았습니다: {0}" -f ($others -join ', '))
    Write-Host "   → 커밋하려면 -OtherMessage ""메시지"" 옵션을 추가하세요."
  }
}

Write-Host ""
Write-Host ("총 {0}개 커밋 생성." -f $committed)

if ($Push -and $committed -gt 0) {
  git push origin main
  Write-Host "push 완료."
}
