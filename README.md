OCS Botnet - Agent
==================

Agent that run commands sent from the OCS Botnet shell.

OCS Botnet Shell
----------------

- https://github.com/moul/ocs-botnet

Run
---

```bash
docker run --privileged -v /var/run/docker.sock:/var/run/docker.sock -it --rm moul/armhf-ocs-botnet-worker:latest
```

LICENSE
-------

MIT
