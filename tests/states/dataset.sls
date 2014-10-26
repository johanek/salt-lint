/etc/sensu/conf.d/redis.json:
  file:
    - serialize
    - user: sensu
    - group: sensu
    - formatter: json
    - dataset:
        redis:
            host: localhost
            port: 6379
    - mode: '0644'
