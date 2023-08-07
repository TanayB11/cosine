# cosine

First clone this repository, then

```bash
cd cosine
git clone https://github.com/chroma-core/chroma.git
```

Then modify `chroma/docker-compose.yml` to reflect the following:
```yaml
environment:
  - IS_PERSISTENT=TRUE
  - ALLOW_RESET=TRUE
ports:
  - 8080:8000
```

