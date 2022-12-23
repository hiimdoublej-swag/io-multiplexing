## Test Epoll server
```sh
docker-compose down && docker-compose up vegeta-epoll
```
## Test Blocking server
```sh
docker-compose down && docker-compose up vegeta-blocking
```

## References
1. https://docs.python.org/3/library/socket.html
2. https://docs.python.org/3/library/select.html
3. https://harveyqing.gitbooks.io/python-read-and-write/content/python_advance/how_to_use_linux_epoll.html 
4. http://scotdoyle.com/python-epoll-howto.html
