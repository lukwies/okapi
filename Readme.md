# Okapi

Okapi is a tool to speed up and simplify your API development.<br>
It can be used for documentation, interaction with APIs and code generation.<br>

## Features
- Create API documentations
- Test APIs
- Generate server/client code
- Export API documentation

## Run
<pre>
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python okapi/main.py
</pre>

## Export

* **Documentation**
	- HTML
	- Textfile
	- Markdown (**TODO**)

* **Server Code**
	- Esp32
	- Flask (**TODO**)

* **Client Code**
	- Esp32
	- curl script (**TODO**)
	- Python client (**TODO**)

## Files
<pre>
~/.okapi                    # Configs directory
  |__ apidoc/               # Holds apidocs
  |__ uris.txt              # List with stored urls
  |__ user_agents.txt       # List with default HTTP useragents
</pre>

## Screenshots
<img src="https://raw.githubusercontent.com/lukwies/okapi/refs/heads/main/screenshots/models.png" width=700 float="left">
<img src="https://raw.githubusercontent.com/lukwies/okapi/refs/heads/main/screenshots/endpoints.png" width=700 float="left">
<img src="https://raw.githubusercontent.com/lukwies/okapi/refs/heads/main/screenshots/request.png" width=700 float="left">
