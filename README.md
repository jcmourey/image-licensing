# Objective

Given a series of images, attempt to find what websites the images came from and look up any available licensing information.

Works with full or partial images.

# User notes
### Google Cloud Setup
* [Create a Google Cloud project](https://console.cloud.google.com/projectcreate)
	* Make a note of the project id `GOOGLE_PROJECT_ID`
* [Enable the following APIs](https://console.cloud.google.com/apis):
	* Google Vision
	* Google Storage
	* Google Drive
	* Google Sheets
* [Create a Google Storage Bucket](https://console.cloud.google.com/storage/browser)
	* Make a note of the `GOOGLE_BUCKET_NAME`
	* Upload the images to the bucket
	* Allow public access (needed for Google Sheets to be able to display the images)
		* Stop public access prevention
		* Grant viewing access to all users: add Principal 
			* New Principals: AllUsers
			* Assign roles: Storage Object Viewer
* [Create Google Cloud credentials](https://console.cloud.google.com/apis/credentials)
	* download credentials json file to the project root to: `internals/credentials.json`
* [Create a Google Drive folder for the image reports](https://drive.google.com/drive)
	* Open the folder and make a note of the `GOOGLE_FOLDER_ID` displayed in the url: `https://drive.google.com/drive/folders/<GOOGLE_FOLDER_ID>`

### Configuration File
Copy the `config_template.json` to `config.json`:

```zsh 
  cp config_template.json config.json
```
 and enter the `<GOOGLE_XXX>` values in `config.json`.

### Install
> Required to download license information from websites that protect against bots:

 [Download Google Chrome](https://www.google.com/chrome/)


# Developer notes

### Configuration
> When changing the structure of `config.json`:

Update the `config_template.json` and regenerate the`pydantic` config model with:

```zsh
  jq '.spreadsheet.folder_id = "<GOOGLE_FOLDER_ID>" | .images.bucket = "<GOOGLE_BUCKET_NAME>" | .images.project = "<GOOGLE_PROJECT_NAME>"' config.json > config_template.json
  datamodel-codegen --input config.json --input-file-type json --output licensing/config_model.py
```
