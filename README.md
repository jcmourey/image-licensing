## Google Cloud Setup

* [Create a Google Cloud project](https://console.cloud.google.com/projectcreate)
	* Make a note of the project id `GOOGLE_PROJECT_ID`
* [Enable the following APIs](https://console.cloud.google.com/apis):
	* Google Vision
	* Google Storage
	* Google Drive
	* Google Sheets
* [Create a Google Drive folder for the image reports](https://drive.google.com/drive)
	* Open the folder and make a note of the `GOOGLE_FOLDER_ID` displayed in the url: `https://drive.google.com/drive/folders/<GOOGLE_FOLDER_ID>`
* [Create a Google Storage Bucket](https://console.cloud.google.com/storage/browser)
	* Make a note of the `GOOGLE_BUCKET_NAME`
	* Allow public access (needed for Google Sheets to be able to display the images)
		* Stop public access prevention
		* Grant viewing access to all users: add Principal 
			* New Principals: AllUsers
			* Assign roles: Storage Object Viewer
* [Create Google Cloud credentials](https://console.cloud.google.com/apis/credentials)
	* download credentials json file to the project root as: `credentials.json`
* Install Chrome driver (needed to ger license information from sites that protect against bots)
	
```brew install chromedriver```

## Configuration File

Create a `config.json` file in the project root

### Template

```{
  "google": {
    "drive": {
      "folder_id": "GOOGLE_FOLDER_ID",
      "report_name": "image_report"
    },
    "storage": {
      "bucket": "GOOGLE_BUCKET_NAME"
    },
    "project": "GOOGLE_PROJECT_ID"
  }
}
```


