$rg = "opti-rg009"
$location = "East US"
$templateFilePath = ".\main.bicep"
New-AzResourceGroup -Name $rg -Location $location
New-AzResourceGroupDeployment -ResourceGroupName $rg -TemplateFile $templateFilePath 
