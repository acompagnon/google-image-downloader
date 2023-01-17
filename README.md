# GoogleImageDownloader :camera:

Python script to **download Google images** from a given query string

## Install

### Docker

```bash
docker-compose build
docker-compose up -d && docker-compose logs -f
```

### Local

```bash
python3.7 -m pip install -r requirements.txt
python3.7 -m playwright install
```

## Use

```bash
python3.7 google_image_downloader.py -h
```

```bash
usage: google_image_downloader.py [-h] [--limit LIMIT] [--output OUTPUT] [--proxy-server PROXY_SERVER] [--headless HEADLESS]
                                  [--verbose]
                                  search_string

positional arguments:
  search_string         Google image query (ex: 'flag')

optional arguments:
  -h, --help            show this help message and exit
  --limit LIMIT, -l LIMIT
                        Images download limit, default None
  --output OUTPUT, -o OUTPUT
                        Ouptut directory
  --proxy-server PROXY_SERVER
                        Proxy server (ex: 'http://myproxy:3128')
  --headless HEADLESS   Display playwright window, this option does not work inside Docker
  --verbose, -v         Set logging level to DEBUG
```

## Example

```bash
python3.7 google-image-downloader.py "flag" --limit 42
```

![cli](https://user-images.githubusercontent.com/93054660/138571704-8d9a2701-05ed-4adb-acec-9b6fc827c4b1.gif)

## Result

![Screenshot from 2021-10-23 23-26-52](https://user-images.githubusercontent.com/93054660/138572109-35d66c67-61ee-4232-9ff2-ea4194c11ac8.png)
