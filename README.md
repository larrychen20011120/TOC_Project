# TOC Project 2020

## Setup

### Prerequisite
* Python 3.9
* Pipenv
* Linebot API
* HTTPS Server
* Fast-Style-Transfer github package
* Imgur
* Sqlite
* BeautifulSoup

#### Install Dependency
```sh
pip install -r requirements.txt
```

#### Secret Data
`config.py` => Config fill in your own token of linebot and imgur

#### run locally

**`ngrok` would be used in the following instruction**

```sh
ngrok http 8000
```

After that, `ngrok` would generate a https URL.

#### Run the sever

* linebot server
```sh
python3 app.py
```
* spider and computing server
```sh
python3 server.py
```

## Finite State Machine
![fsm](./static/fsm.png)


## Reference
