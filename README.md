# Response page with Huntflow API integration 

Simple project for demonstrating of responses page for collecting and passing them to Huntflow via API

## Run locally

```bash
docker build -t api_reponse .
docker run -p 9990:9990 -t api_reponse --host=0.0.0.0
```

or you need Python 3.7+

```
python3.7 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 main.py
```

Now go to http://127.0.0.1:9990


## Configuration parameters

Name | Type  | Default | Description
---- | ----- | ------- | -----------
`--debug` | `bool` | `False` | Run service in debug mode (should be True for development) 
`--port` | `int` | `9990` | Port to run on
`--host` | `string` | `127.0.0.1` | Host to run on
`--base_path` | `string` |  | If you need to have relative path for response page on your career site you can set it here. See production usage section.
`--api_endpoint` | `string` | `https://api.huntflow.ru` | URL of API endpoint. Change it if you have dedicated or on-premise Huntflow installation 
`--api_key` | `string` |  | API token (aka personal token). You can gain it at support@huntflow.ru 
`--api_account_id` | `int` |  | Your Huntflow account identifier (could be received via [/accounts API request](https://github.com/huntflow/api/blob/master/en/user.md#getting-information-about-available-organizations))  
`--source_id` | `int` |  | Huntflow applicant source identifier to be set to the response. Available sources could be received via [list of available sources request](https://github.com/huntflow/api/blob/master/en/dicts.md#applicant_sources)
`--vacancy_id` | `int` |  | Huntflow vacancy identifier to add applicants to. Available vacancies could be received via [list of available vacancies request](https://github.com/huntflow/api/blob/master/en/vacancies.md#vacancies)
`--status_id` | `int` |  | Huntflow vacancy stage identifier to put applicant on. Available stages could be received via [list of available stages request](https://github.com/huntflow/api/blob/master/en/dicts.md#stages-of-headhunting)
`--vacancy_og` | `string` |  | Path to the vacancy image in `og` directory for Open Graph
`--vacancy_name` | `string` | `Моя вакансия` | Human readable vacancy name for page and Open Graph 
`--vacancy_url` | `string` | `https://example.com/career/my-vacancy` | URL to vacancy description page 
`--privacy_url` | `string` | `https://example.com/privacy-policy` | URL to privacy policy page 


## Production usage

Example docker-compose.yml

```
version: '3.4'
services:

  api_response:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: api_response
    command: ["--base_path=/career/my-vacancy/response", "--vacancy_id=1", "--status_id=10", "--source_id=20", "--log_filename=/var/log/api-response.log", "--api_key=<API KEY>"]
    restart: always
    ports:
     - 9990:9990
    volumes:
     - /etc/localtime:/etc/localtime:ro
     - logs-datavolume:/var/log
    network_mode: "host"
    logging:
      options:
        max-size: "512m"
    cap_add:
     - sys_ptrace

volumes:
  logs-datavolume:
    driver: local
    driver_opts:
      type: none
      device: /var/log
      o: bind
```

Example Nginx config:

```
location /career/my-vacancy/response {
    # limit body size
    client_max_body_size 6m;

    proxy_set_header    Host $http_host;
    proxy_redirect      off;
    # for rate limiting
    proxy_set_header    X-Real-IP $remote_addr;
    proxy_pass          http://127.0.0.1:9990;
}
```
