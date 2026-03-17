param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root
try {
    & python -m self_actualize.runtime.command_membrane @Args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
