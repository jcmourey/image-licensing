# Objective
# Image Management Project

## Type Synchronization

This project uses a type-driven development approach to ensure consistency between the frontend and backend. The TypeScript interfaces in the frontend and the Python Pydantic models in the backend are kept in sync using the following approaches:

### Manual Synchronization

Currently, the types are defined in:
- Frontend: `web-ui/src/components/types.ts`
- Backend: `backend/models/types.py`

When modifying these types, be sure to update both files to maintain consistency.

### Automated Synchronization (Optional)

For automatic type synchronization, we've included a script that generates TypeScript interfaces from Python Pydantic models:
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
  cp backend/config_template.json backend/config.json
```
 and enter the `<GOOGLE_XXX>` values in `config.json`.

### Install

 [Download Google Chrome](https://www.google.com/chrome/)
 
* Required to download license information from websites that protect against bots



# Developer notes

### Configuration

After changing the structure of `config.json`:

* update `config_template.json`, and
* regenerate the`pydantic` config model, with:

```zsh
  jq -f backend/tools/make_json_template.jq backend/config.json > backend/config_template.json
  datamodel-codegen --input backend/config.json --input-file-type json --output backend/config/generated_config_model.py
```
