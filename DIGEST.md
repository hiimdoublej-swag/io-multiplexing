- What are some different IO methods ?
    1. blocking IO
    2. non-blocking IO
    3. IO multiplexing
- When do you need IO multiplexing?
- What are some methods of IO multiplexing ?
    1. select
    2. poll
    3. epoll
- Performance comparisons.
- How can IO multiplexing benefit us (SWAG) ?
- Conclusion

---

Blocking IO
- The socket waits for incoming data to be ready for receive.
- Therefore it blocks the process until it has data for the process to ready.

Non-blocking IO
- Instead of waiting for data to be ready, it throws an error if there is no data ready.
- The process have to act accordingly. If the process just keeps on asking the socket for data, it's essentially the same as blocking.

IO multiplexing
- Instead of trying to directly receive data from the socket, we look for events on those sockets from the kernel.
- Each socket read is still blocking IO underneath, just that it should not wait since the process knows the socket is already ready for read.

---

`select`
- The process keeps 3 sets of fds (read,write,errors) themself, as `fdset` objects. 
```
int select(int nfds, fd_set *readfds, fd_set *writefds, fd_set *errorfds, struct timeval *timeout);
```
- The process at the time of calling `select()` is blocked until one fd is ready or a timeout.
- The call will return a list of status result for each traversed fd by `select()`, the process has to traverse through all of them to find a ready fd.
- Supported universally.
- The number of fds to watch is hard capped by `fdset`.

`poll`
- The process keeps 1 set of FDs, but this time in a specific structure `pollfd`.
```
int poll(struct pollfd *fds, nfds_t nfds, int timeout);
```
- The call returns a list similar with `select()`
- After the call returns, also has to traverse all the fds to find a ready fd.
- Support is OS-dependent.
- The number of fds to watch is technically unlimited as the `pollfd` array can be dynamically allocated.

`epoll`
- The application creates one epoll object to let the process keep track of interested fds.
- Once we set the epoll object up correctly with our fds, the application can call `epoll_wait` to wait for events until a timeout.
```
epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);
```
- The said call will give you a list of `(fd, event)` sets.
- After the call returns, the process can just directly interact with the fd since the process knows which fd is ready to do what.
- Support is added after linux kernel 2.5.44.
- The number of fds for an `epoll()` object to watch also technically unlimited as it will try to allocate as much memory as needed on construction.

---

Scenario 1 - High number of fds, 95% of them are active.
- `epoll` will give you the fds for the active ones, which in this case is 95% of all fds, and it can directly read.
- `select`, `poll` forces the application to iterate through all the fds in the structure, find the fds that are ready for read, then read.
- For this case, all the methods require you to do a high amount of traversing, there's not much performance difference.

---

Scenario 2 - High number of fds, only 1% are active.
- `epoll` will give you just the active fds, which is just 1% of all fds.
- `select`, `poll` will go through the same steps as decribed last time.
- In this situation, `epoll` is clearly better since it avoided 99% of traversing to find the intrested fds.
