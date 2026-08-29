<# 
.SYNOPSIS
    Knowledge Layer PowerShell Wrapper for Project Discovery System
.DESCRIPTION
    Provides basic knowledge management operations without Python dependency.
    For full validation and schema enforcement, use the Python CLI (knowledge.py).
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("add-source", "add-entity", "add-evidence", "add-fact", "add-relationship", "add-question", "add-conflict", "add-run",
                 "query-sources", "query-entities", "query-evidence", "query-facts", "query-relationships", "query-questions", "query-conflicts", "query-runs",
                 "snapshot", "stats", "validate")]
    [string]$Command,

    [string]$KnowledgeBase = ".ai/knowledge",

    [string]$Id,
    [string]$Data,
    [string]$File,
    [string]$RunId,
    [string[]]$Filters,
    [string]$Primary,
    [string[]]$Duplicates,
    [string]$Type
)

$KBRoot = Resolve-Path $KnowledgeBase
$Current = Join-Path $KBRoot "current"
$History = Join-Path $KBRoot "history"
$Schemas = Join-Path $KBRoot "schemas"

function Get-NextId {
    param([string]$Prefix, [string]$File)
    $existing = @()
    if (Test-Path $File) {
        $content = Get-Content $File -Raw
        $docs = $content -split "`n---`n"
        foreach ($doc in $docs) {
            if ($doc.Trim()) {
                $obj = $doc | ConvertFrom-Yaml
                if ($obj.id -and $obj.id -like "$Prefix-*") {
                    $num = [int]($obj.id -replace "$Prefix-", "")
                    $existing += $num
                }
            }
        }
    }
    $next = if ($existing) { ($existing | Measure-Object -Maximum).Maximum + 1 } else { 1 }
    return "$Prefix-{0:D6}" -f $next
}

function Append-Yaml {
    param([string]$File, [object]$Object)
    $yaml = $Object | ConvertTo-Yaml -Depth 10
    Add-Content -Path $File -Value $yaml
    Add-Content -Path $File -Value "---"
}

function Read-AllYaml {
    param([string]$File)
    if (-not (Test-Path $File)) { return @() }
    $content = Get-Content $File -Raw
    $docs = $content -split "`n---`n"
    $results = @()
    foreach ($doc in $docs) {
        if ($doc.Trim()) {
            $results += $doc | ConvertFrom-Yaml
        }
    }
    return $results
}

function Write-AllYaml {
    param([string]$File, [object[]]$Objects)
    Set-Content -Path $File -Value ""
    foreach ($obj in $Objects) {
        Append-Yaml -File $File -Object $obj
    }
}

$files = @{
    sources = Join-Path $Current "sources.yaml"
    entities = Join-Path $Current "entities.yaml"
    evidence = Join-Path $Current "evidence.yaml"
    facts = Join-Path $Current "facts.yaml"
    relationships = Join-Path $Current "relationships.yaml"
    questions = Join-Path $Current "questions.yaml"
    conflicts = Join-Path $Current "conflicts.yaml"
    runs = Join-Path $Current "runs.yaml"
}

switch ($Command) {
    "add-source" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "SRC" $files.sources)
        $data.timestamps = @{ observed_at = (Get-Date).ToString("o") }
        Append-Yaml $files.sources $data
        Write-Host $data.id
    }
    "add-entity" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "ENT" $files.entities)
        $data.timestamps = @{ discovered_at = (Get-Date).ToString("o") }
        Append-Yaml $files.entities $data
        Write-Host $data.id
    }
    "add-evidence" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "EVD" $files.evidence)
        Append-Yaml $files.evidence $data
        Write-Host $data.id
    }
    "add-fact" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "FACT" $files.facts)
        $data.timestamps = @{ observed_at = (Get-Date).ToString("o") }
        Append-Yaml $files.facts $data
        Write-Host $data.id
    }
    "add-relationship" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "REL" $files.relationships)
        $data.timestamps = @{ created_at = (Get-Date).ToString("o") }
        Append-Yaml $files.relationships $data
        Write-Host $data.id
    }
    "add-question" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "Q" $files.questions)
        $data.timestamps = @{ created_at = (Get-Date).ToString("o") }
        Append-Yaml $files.questions $data
        Write-Host $data.id
    }
    "add-conflict" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "CON" $files.conflicts)
        $data.timestamps = @{ created_at = (Get-Date).ToString("o") }
        Append-Yaml $files.conflicts $data
        Write-Host $data.id
    }
    "add-run" {
        $data = if ($File) { Get-Content $File -Raw | ConvertFrom-Yaml } else { $Data | ConvertFrom-Yaml }
        $data.id = $data.id ?? (Get-NextId "RUN" $files.runs)
        Append-Yaml $files.runs $data
        Write-Host $data.id
    }
    "query-*" {
        $objType = $Command -replace "query-", ""
        $file = $files.$objType
        $objects = Read-AllYaml $file
        
        if ($Id) {
            $objects = $objects | Where-Object { $_.id -eq $Id }
        }
        
        foreach ($f in $Filters) {
            $parts = $f -split "=", 2
            $key = $parts[0]
            $value = $parts[1]
            $objects = $objects | Where-Object { $_.$key -eq $value }
        }
        
        $objects | ConvertTo-Yaml -Depth 10 | Write-Host
    }
    "snapshot" {
        $runDir = Join-Path $History $RunId
        New-Item -ItemType Directory -Path $runDir -Force | Out-Null
        foreach ($key in $files.Keys) {
            $src = $files.$key
            $dst = Join-Path $runDir "$key.yaml"
            if (Test-Path $src) {
                Copy-Item $src $dst -Force
            }
        }
        Write-Host "Snapshot created at $runDir"
    }
    "stats" {
        foreach ($key in $files.Keys) {
            $count = (Read-AllYaml $files.$key).Count
            Write-Host "$key: $count"
        }
    }
    "validate" {
        Write-Warning "Full validation requires Python CLI (knowledge.py). Install Python and run: python knowledge.py validate"
    }
    default {
        Write-Error "Unknown command: $Command"
        exit 1
    }
}