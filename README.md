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
	* Stop public access prevention
	* Add Principal
		* New Principals: AllUsers
		* Assign roles: Storage Object Viewer
* [Create Google Cloud credentials](https://console.cloud.google.com/apis/credentials)
	* download credentials json to the project root as: `credentials.json`

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


