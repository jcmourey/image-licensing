## Configuration

Add the following json files to the project root:

`config.json`:

### Template

```{
  "google": {
    "drive": {
      "folder_id": "GOOGLE FOLDER ID TO STORE THE SPREADSHEET REPORT",
      "report_name": "image_report"
    },
    "storage": {
      "bucket": "GOOGLE CLOUD STORAGE BUCKET NAME CONTAINING THE IMAGES"
    },
    "project": "GOOGLE CLOUD PROJECT NAME CONTAINING THE BUCKET"
  }
}
```

## Public Bucket Access

The bucket must provide public access to the images for Google Sheets to be able to display them.

* [Google Cloud Storage Console](https://console.cloud.google.com/storage/browser)
* Stop public access prevention
* Add Principal
	* New Principals: AllUsers
	* Assign roles: Storage Object Viewer

## Google Credentials
Create credentials with [Google Cloud credentials](https://console.cloud.google.com/apis/credentials) and download json to the project root as:

`credentials.json`


