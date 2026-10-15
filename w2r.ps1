<#
.SYNOPSIS
  Point d'entrée unique de word2robot (Windows). Tout s'exécute dans un conteneur Podman.

.DESCRIPTION
  .\w2r.ps1 build            construit l'image (puis à chaque changement de Containerfile / requirements)
  .\w2r.ps1 stop             arrête le conteneur (il redémarre tout seul à la commande suivante)
  .\w2r.ps1 <commande>       exécute la commande dans le conteneur : voir « .\w2r.ps1 aide »

  Le conteneur reste allumé entre deux commandes (podman exec : rapide). Il est recréé après
  « build » ou « stop » ; relancer « stop » après une modification de .env.
  W2R_MOTEUR=docker permet d'utiliser Docker à la place de Podman (même ligne de commande).
  Compatible Windows PowerShell 5.1 et PowerShell 7.
#>
$ErrorActionPreference = 'Stop'
# Entrée standard : celle du processus passe directement au conteneur (hook Claude, serveurs MCP en flux
# continu). Ne PAS lire $input ici : avec « powershell -File », il attendrait la fin du flux et bloquerait
# les serveurs MCP. Conséquence : « texte | .\w2r.ps1 … » depuis PowerShell ne transmet pas le texte.
$Racine = $PSScriptRoot
$Moteur = if ($env:W2R_MOTEUR) { $env:W2R_MOTEUR } else { 'podman' }
$Image = 'localhost/word2robot:local'
$Conteneur = 'word2robot-' + ((Split-Path $Racine -Leaf).ToLower() -replace '[^a-z0-9_.-]', '-')

if (-not (Get-Command $Moteur -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine("$Moteur introuvable : installer Podman (winget install -e --id RedHat.Podman), puis « podman machine init --rootful ».")
    exit 127
}

function Get-EtatConteneur {
    $etat = & $Moteur ps -a --filter "name=^$Conteneur$" --format '{{.Status}}' 2>$null
    if ($LASTEXITCODE -and $Moteur -eq 'podman') {
        # Machine Podman arrêtée (après un redémarrage du PC) : la démarrer, sans rien écrire sur la sortie
        # standard (elle sert au protocole des serveurs MCP).
        [Console]::Error.WriteLine('Démarrage de la machine Podman…')
        & podman machine start *> $null
        $etat = & $Moteur ps -a --filter "name=^$Conteneur$" --format '{{.Status}}' 2>$null
    }
    if (-not $etat) { return 'absent' }
    if ("$etat" -like 'Up*') { return 'actif' }
    return 'arrete'
}

function Start-Conteneur {
    switch (Get-EtatConteneur) {
        'actif' { return }
        'arrete' { & $Moteur start $Conteneur | Out-Null }
        'absent' {
            $options = @('run', '-d', '--name', $Conteneur, '--init', '--shm-size', '1g',
                '-v', "${Racine}:/work", '-w', '/work')
            if (Test-Path (Join-Path $Racine '.env')) { $options += @('--env-file', (Join-Path $Racine '.env')) }
            & $Moteur @options $Image sleep infinity | Out-Null
        }
    }
    if ($LASTEXITCODE) {
        [Console]::Error.WriteLine("Impossible de démarrer le conteneur : l'image est-elle construite (.\w2r.ps1 build) ? La machine Podman est-elle en mode rootful (voir README) ?")
        exit $LASTEXITCODE
    }
}

$commande = if ($args.Count) { $args[0] } else { 'aide' }
switch ($commande) {
    'build' {
        $null = Get-EtatConteneur   # démarre la machine Podman si besoin
        & $Moteur rm -f $Conteneur 2>$null | Out-Null
        & $Moteur build -t $Image -f (Join-Path $Racine 'Containerfile') $Racine
        exit $LASTEXITCODE
    }
    'stop' {
        & $Moteur rm -f $Conteneur | Out-Null
        exit 0
    }
    default {
        Start-Conteneur
        $exec = @('exec', '-i', '-e', "W2R_HOTE=$Racine", '-w', '/work', $Conteneur, 'python', 'tools/cli.py') + $args
        & $Moteur @exec
        exit $LASTEXITCODE
    }
}
