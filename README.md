## DNS-Server

Простой итеративный сервер, работает по UDP, умеет находить A записи.

Критерии:

1) Ручное формирование пакетов (20 баллов)
2) Одновременное обслуживание нескольких пользователей (многопоточность) (+3 балла)
3) Кеширование ответов с учетом ttl (+3 балла) (Кеширование происходит не только по итоговым записям, но и по зонам)

Usage:

1) Запустите сервер:

```shell
python dns.py --bind {server bind host} --port {server port} --timeout {timeout in seconds} --retry_count {retry count answer dns servers} --max_hops {max hops for ask dns servers}
```

Все параметры необязательны. По умолчанию сервер будет слушать 0.0.0.0:53

2) Отправьте DNS запрос:

```shell
dig @127.0.0.1 domain.com
```

or (windows)

```shell
nslookup
> server 127.0.0.1
> set type=A
> domain.com
```