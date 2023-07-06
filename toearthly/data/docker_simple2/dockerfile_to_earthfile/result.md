Sure, here is the Earthfile:

```Earthfile
VERSION 0.7
WORKDIR /bash
FROM alpine:latest

docker:
  ARG date=$(date +%s)
  COPY ./hello.md .
  CMD ["/bin/sh"]
  SAVE IMAGE --push my-xyz7:$date

all:
  BUILD +docker
```
