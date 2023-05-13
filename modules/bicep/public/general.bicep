@description('Additional prefix for the resource name. Default: random 3 characters if not passed as parameter')
param prefix string = substring(newGuid(),0,3)

@description('Additional postfix for the resource name. Default: "opti" if not passed as parameter')
param postfix string = 'opti'
