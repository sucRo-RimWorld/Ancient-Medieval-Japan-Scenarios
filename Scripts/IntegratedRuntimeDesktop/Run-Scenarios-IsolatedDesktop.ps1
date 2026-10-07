param(
 [int]$TimeoutSeconds = 1800,
 [string]$RimWorldRoot = 'D:\SteamLibrary\steamapps\common\RimWorld',
 [ValidateSet('all','vanilla','grains','mo','grains-mo')][string]$Profile = 'all',
 [string]$GrainsRepositoryRoot = ''
)
$ErrorActionPreference = 'Stop'
$env:PSModulePath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\Modules"
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.ComponentModel;
public static class AmjDesktop {
 [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
 public struct Startup {
  public int cb; public string reserved, desktop, title;
  public int x,y,cx,cy,xchars,ychars,fill,flags;
  public short show, reservedBytes; public IntPtr reservedPtr, input, output, error;
 }
 [StructLayout(LayoutKind.Sequential)]
 public struct ProcessInfo { public IntPtr process, thread; public uint pid, tid; }
 [DllImport("user32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
 public static extern IntPtr CreateDesktop(string name, IntPtr device, IntPtr mode, uint flags, uint access, IntPtr security);
 [DllImport("user32.dll")] public static extern bool CloseDesktop(IntPtr desktop);
 [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
 public static extern bool CreateProcess(string app, StringBuilder command, IntPtr psa, IntPtr tsa, bool inherit, uint flags, IntPtr env, string cwd, ref Startup startup, out ProcessInfo process);
 [DllImport("kernel32.dll")] public static extern uint WaitForSingleObject(IntPtr handle, uint millis);
 [DllImport("kernel32.dll")] public static extern bool GetExitCodeProcess(IntPtr process, out uint code);
 [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr handle);
 public delegate bool WindowCallback(IntPtr window, IntPtr parameter);
 [DllImport("user32.dll", SetLastError=true)] public static extern bool EnumDesktopWindows(IntPtr desktop, WindowCallback callback, IntPtr parameter);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr window, out uint pid);
 public static string WindowProcesses(IntPtr desktop) {
  var ids = new System.Collections.Generic.HashSet<uint>();
  WindowCallback callback = delegate(IntPtr window, IntPtr parameter) { uint pid; GetWindowThreadProcessId(window, out pid); ids.Add(pid); return true; };
  // EnumDesktopWindows may return false without an error when the desktop is empty.
  EnumDesktopWindows(desktop, callback, IntPtr.Zero);
  var names = new System.Collections.Generic.List<string>();
  foreach (uint pid in ids) { try { var p=System.Diagnostics.Process.GetProcessById((int)pid); names.Add(p.ProcessName+":"+pid); } catch(ArgumentException) {} }
  return String.Join(",", names.ToArray());
 }
}
'@
$desktopName = 'AMJ_Automated_' + [Guid]::NewGuid().ToString('N')
$desktop = [AmjDesktop]::CreateDesktop($desktopName, [IntPtr]::Zero, [IntPtr]::Zero, 0, 0x01FF, [IntPtr]::Zero)
if ($desktop -eq [IntPtr]::Zero) { throw (New-Object ComponentModel.Win32Exception) }
$info = New-Object AmjDesktop+ProcessInfo
$started = $false
$finished = $false
try {
 $startup = New-Object AmjDesktop+Startup
 $startup.cb = [Runtime.InteropServices.Marshal]::SizeOf($startup)
 $startup.desktop = 'WinSta0\' + $desktopName
 if ($RimWorldRoot -match '["%\r\n]' -or $GrainsRepositoryRoot -match '["%\r\n]') { throw 'Invalid path for the batch launcher.' }
 $batch = Join-Path $PSScriptRoot 'run-scenario-profiles.cmd'
 $reportRoot = Join-Path $PSScriptRoot '../../TestResults/Scenarios'
 New-Item -ItemType Directory -Force -Path $reportRoot | Out-Null
 $log = Join-Path $reportRoot 'automated-gates.log'
 $batchArgs = ' "' + $RimWorldRoot + '" "' + $Profile + '" "' + $GrainsRepositoryRoot + '"'
 $command = New-Object Text.StringBuilder
 [void]$command.Append('"' + $env:ComSpec + '" /d /s /c ""' + $batch + '"' + $batchArgs + ' > "' + $log + '" 2>&1"')
 $started = [AmjDesktop]::CreateProcess($env:ComSpec, $command, [IntPtr]::Zero, [IntPtr]::Zero, $false, 0x08000000, [IntPtr]::Zero, $PSScriptRoot, [ref]$startup, [ref]$info)
 if (-not $started) { throw (New-Object ComponentModel.Win32Exception) }
 Write-Output "[START] Desktop=$($startup.desktop); runner=$($info.pid); rendering enabled; desktop never switched."
 $seen = New-Object 'System.Collections.Generic.HashSet[string]'
 $timer = [Diagnostics.Stopwatch]::StartNew()
 while ($timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
  $state = [AmjDesktop]::WaitForSingleObject($info.process, 5000)
  if ($state -eq 0) { $finished=$true; break }
  if ($state -ne 258) { throw "Wait failed: $state" }
  $windows = [AmjDesktop]::WindowProcesses($desktop)
  if ($windows -and $seen.Add($windows)) { Write-Output "[WINDOWS] $desktopName : $windows" }
 }
 if (-not $finished) { throw "AMJ suite exceeded ${TimeoutSeconds}s. See $log" }
 [uint32]$result = 0
 if (-not [AmjDesktop]::GetExitCodeProcess($info.process, [ref]$result)) { throw (New-Object ComponentModel.Win32Exception) }
 Write-Output "[EXIT] $result; log=$log"
 exit $result
}
finally {
 if ($started -and -not $finished) { & taskkill /PID $info.pid /T /F | Out-Null }
 if ($info.thread -ne [IntPtr]::Zero) { [void][AmjDesktop]::CloseHandle($info.thread) }
 if ($info.process -ne [IntPtr]::Zero) { [void][AmjDesktop]::CloseHandle($info.process) }
 [void][AmjDesktop]::CloseDesktop($desktop)
}
