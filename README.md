# IIM submission

### - _BiTZ_

#### This project is a **Prototype**

##### Folder sctructure

```
|
|= /code-files/
|= /demo-vid/
|= /Verification-documents/
|- README.md [Which you are reading.]
```

#### _`/code-files/`_

##### File sctructure

```
|
|- API_links.json
|- districts.json
|- process.py
|- requirements.txt
|- simulated_data.py
|- training_data.json
```

##### Files and brief descriptions

- **`/API_links.json`** - contains all the simulated APi links live monitor will use to compute the pridiction

- **`/districts.json`** - list of all the districts that can be used in _`simulated_data.py`_ and _`main.processor.py`_

- **`/training_data.json`** - demo training datasetv

- **`/requirements.txt`** - List of all the python packages needed

- **`/simulated_data.py`** - helper script to generate simulated datasets for testing (Demo ports no real data is provided).

- **`/process.py`** - main processing script for main.process.py (Returns pridictions depending upon given / simulated data)

- **`/main.processor.py`** - pulls data from the APis and formats them for process.py and read pridictions and show them on Ui
