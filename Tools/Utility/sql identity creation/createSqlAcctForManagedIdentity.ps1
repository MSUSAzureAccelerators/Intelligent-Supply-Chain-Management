Param(
  [Parameter(Mandatory = $true)][string]$ServerName,
  [Parameter(Mandatory = $true)][string]$ResourceGroupName,
  [Parameter(Mandatory = $true)][string]$ServerUri,
  [Parameter(Mandatory = $true)][string]$CatalogName,
  [Parameter(Mandatory = $true)][string]$ApplicationId,
  [Parameter(Mandatory = $true)][string]$ManagedIdentityName,
  [Parameter(Mandatory = $true)][string]$SqlAdminLogin,
  [Parameter(Mandatory = $true)][string]$SqlAdminPwd,
  [Parameter(Mandatory = $true)][bool]$IsProd
)

# Assumes the service principal that will connect to SQL has been set as the Azure AD Admin
# This was handled by the bicep templates
# see https://docs.microsoft.com/en-us/azure/azure-sql/database/authentication-aad-configure?view=azuresql&tabs=azure-powershell#azure-portal

# Make Invoke-Sqlcmd available
Install-Module -Name SqlServer -Force
Import-Module -Name SqlServer

# translate applicationId into SID
[guid]$guid = [System.Guid]::Parse($ApplicationId)

foreach ($byte in $guid.ToByteArray()) {
  $byteGuid += [System.String]::Format("{0:X2}", $byte)
}
$Sid = "0x" + $byteGuid

# Prepare SQL cmd to CREATE USER
$CreateUserSQL = "IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = N'$ManagedIdentityName') create user [$ManagedIdentityName] with sid = $Sid, type = E;"

# Connect as SQL Admin acct and execute SQL cmd
Invoke-Sqlcmd -ServerInstance $ServerUri -database $CatalogName -Username $SqlAdminLogin -Password $SqlAdminPwd -Query $CreateUserSQL