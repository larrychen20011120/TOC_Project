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
ngrok http 5000
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

## Example
![image](https://user-images.githubusercontent.com/38965858/209559978-105d279b-940d-4e4b-8ca4-465b15a4247e.png)

## Reference
* https://github.com/lengstrom/fast-style-transfer
* https://ithelp.ithome.com.tw/users/20144761/ironman/5735
