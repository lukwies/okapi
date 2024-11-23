# Okapi

Okapi is a tool to speed up and simplify your API development.<br>

## Features
- Create API documentations
- Test APIs
- Generate server/client code
- Export API documentation

## Run
<pre>
$ python -m venv venv
$ source venv/bin/activate
$ pip install -R requirements.txt
$ python okapi/main.py
</pre>

## Export

* **Documentation**
	- HTML
	- Textfile
	- Markdown<br>

* **Server Code**
	- Flask
	- Esp32
	- Esp8266

* **Client Code**
	- Python
	- Esp32
	- curl

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
