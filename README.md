# SnapBox v2

SnapBox is software working in Single Board Computer (SBC) for pilot digital camera and some features like lite GUI.

# Dependencies

```bash
$ apt update
$ apt install python3-pip python3-pkgconfig python3-setuptools libgphoto2-dev
```

# Quickstart

How to install :

```
$ cd /<folders>/snapbox-server
$ python3 setup.py
```

Generate secret token :

```bash
$ snapbox-server --generate-tokens
ou
$ python3 server.py --generate-tokens
```

Set admin password :

```
$ snapbox-server --password-admin
ou
$ python3 server.py --password-admin
```
