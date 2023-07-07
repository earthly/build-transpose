FROM alpine:3.15 AS base
RUN echo "word" > ./a-file

FROM busybox as another
COPY --from=build ./a-file ./
