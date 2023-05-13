$rg = "opti-rg009"
$location = "East US"
New-AzResourceGroup -Name $rg -Location $location
New-AzResourceGroupDeployment -ResourceGroupName $rg -TemplateFile .\main.bicep 
