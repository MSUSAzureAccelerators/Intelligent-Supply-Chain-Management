## Step 10. Deploy and configure the Supply Chain Power App
1. Go to https://make.preview.powerapps.com/
2. In the right upper corner, make sure you select the correct environment where you want to deploy the Power App.
3. Click on `Apps - Import Canvas App`
4. Click upload and select the [Deployment/PowerApp/SupplyChainSA_20221117163532.zip](./Deployment/PowerApp/SupplyChainSA_20221117163532.zip) Zipfile.
5. Review the package content. You should see the details as the screenshot below

  ![Review Package Content](./Deployment/Images/ReviewPackageContent.jpg "Review Package Content")

6. Under the `Review Package Content`, click on the little wrench next to the Application Name `Complaint Manager`, to change the name of the Application. Make sure the name is unique for the environemnt.
7. Click Import and wait until you see the message `All package resources were successfully imported.`
8. Click on `Flows`. You will notice that all the flows are disabled. 

![Cloud Flows disabled](./Deployment/Images/CloudFlows.jpg "CloudFlows")

9. You need to turn them on before you can use them. Hover over each of the flows, select the button `More Commands` and click `Turn on`.

![Turn on Cloud Flows](./Deployment/Images/TurnonCloudFlows.png "TurnonCloudFlows")

10. For each flow (except ComplaintsManagement-GetSearchResults, see point 11), you need to change the HTTP component so that the URI points to your Azure Function App. Edit each flow, open the HTTP component and past the Azure Function Url before the first &.
Your URI should look similar like the screenshot below.

![HTTP](./Deployment/Images/HTTP.jpg "HTTP")

11. For the ComplaintsManagement-GetSearchResults flow, change the URI with your Azure Search Service URI. Replace the api-key with the primary admin key of your Search Service.
Your HTTP component should look similar like the screenshot below.

![Search Service HTTP Request](./Deployment/Images/SearchServiceHTTPRequest.jpg "Search Service HTTP Request.")
