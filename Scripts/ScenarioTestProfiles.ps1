# MIT-derived from Grains Scripts/GrainsTestProfiles.ps1 at faa2ced; separate test owner.
function Get-ScenarioTestProfile([string]$Name) {
    if ($Name -notin @('vanilla','grains','mo','grains-mo')) { throw "Unknown Scenario profile: $Name" }
    $useMO = $Name -in @('mo','grains-mo')
    $useGrains = $Name -in @('grains','grains-mo')
    $providers = @()
    if ($useMO) { $providers += 'dankpyon.medieval.overhaul' }
    if ($useGrains) { $providers += 'sucro.ancientmedievaljapan.core.scenariose2etarget' }
    [pscustomobject]@{ Name=$Name; UseMO=$useMO; UseGrains=$useGrains; Providers=$providers;
        Feature="scenarios-$Name.feature";
        Scenarios=@("Scenarios $Name requested providers", "Scenarios $Name loaded village definition", "Scenarios $Name actual village start") }
}

# Resolve only declared hard dependencies, then order active loadAfter edges.
# Never reuse the player's active mod list or activate all installed mods.
function Get-ScenarioActiveMods([object]$Profile, [hashtable]$Installed) {
    $ordered = New-Object 'System.Collections.Generic.List[string]'
    $visiting = @{}
    $visited = @{}
    function Visit([string]$Id) {
        $Id = $Id.ToLowerInvariant()
        if ($visited.ContainsKey($Id)) { return }
        if ($visiting.ContainsKey($Id)) { throw "Mod dependency cycle at $Id" }
        if (-not $Installed.ContainsKey($Id)) { throw "Required installed mod missing: $Id" }
        if ($Id -like '*fixture*' -or $Id -in @('sucro.ancientmedievaljapan.core','sucro.ancientmedievaljapan.scenarios')) {
            throw "Production package or API fixture cannot participate in a Scenario profile: $Id"
        }
        if ((-not $Profile.UseMO -and $Id -eq 'dankpyon.medieval.overhaul') -or
            ($Id -eq 'sucro.cropcoldtoleranceoverhaul')) {
            throw "Profile $($Profile.Name) forbids dependency $Id"
        }
        $visiting[$Id] = $true
        foreach ($dependency in @($Installed[$Id].Xml.ModMetaData.modDependencies.li)) {
            $depId = ([string]$dependency.packageId).Trim()
            if ($depId) { Visit $depId }
        }
        $visiting.Remove($Id)
        $visited[$Id] = $true
        $ordered.Add($Id)
    }
    foreach ($id in @('brrainz.harmony', 'ludeon.rimworld') + @($Profile.Providers) + @(
        'sucro.ancientmedievaljapan.scenarios.e2etarget', 'rimworks.rimlogging',
        'rimworks.pickle', 'rimworks.quickstarts', 'sucro.ancientmedievaljapan.scenarios.e2e')) { Visit $id }

    $result = New-Object 'System.Collections.Generic.List[string]'
    $pending = @($ordered)
    while ($pending.Count -gt 0) {
        $ready = @($pending | Where-Object {
            $id = $_
            $before = @($Installed[$id].Xml.ModMetaData.modDependencies.li | ForEach-Object { [string]$_.packageId }) +
                @($Installed[$id].Xml.ModMetaData.loadAfter.li) + @($Installed[$id].Xml.ModMetaData.forceLoadAfter.li)
            @($before | Where-Object { $_ -and $pending -contains ([string]$_).ToLowerInvariant() }).Count -eq 0
        })
        if ($ready.Count -eq 0) { throw "Active load-order cycle: $($pending -join ', ')" }
        foreach ($id in $ready) { $result.Add($id) }
        $pending = @($pending | Where-Object { $ready -notcontains $_ })
    }
    return $result.ToArray()
}
