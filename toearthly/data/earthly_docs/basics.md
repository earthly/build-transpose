# Earthly Tutorial

Below you'll find a simple example of an Earthfile. Existing Dockerfiles can easily be ported to Earthly by copying them to an Earthfile and tweaking them slightly.

```Dockerfile
VERSION 0.7
FROM golang:1.15-alpine3.13
WORKDIR /go-workdir

build:
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example AS LOCAL local-output/go-example

docker:
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:latest
```

## Creating Your First Earthfile

We'll slowly build up to the Earthfile we have above. Let's start with these first three lines.

`./tutorial/Earthfile`
```Dockerfile
VERSION 0.7
FROM golang:1.15-alpine3.13
WORKDIR /go-workdir
```
And some simple Hello World code in a `main.go`.

```go
package main

import "fmt"

func main() {
	fmt.Println("hello world")
}
```
Earthfiles are always named Earthfile, regardless of their location in the codebase. 

The Earthfile starts off with a version definition. This will tell Earthly which features to enable and which ones not to so that the build script maintains compatibility over time, even if Earthly itself is updated.

The first commands in the file are part of the `base` target and are implicitly inherited by all other targets. Targets are just sets of instructions we can call on from within the Earthfile, or when we run Earthly at the command line.


## Creating Your First Targets
Earthly aims to replace Dockerfile, makefile, bash scripts and more. We can take all the setup, configuration and build steps we'd normally define in those files and put them in our Earthfile in the form of `targets`.

Let's start by defining a target to build our simple Go app.

```Dockerfile
build:
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example
```

The first thing we do is copy our `main.go` from the **build context** (the directory where the Earthfile resides) to the **build environment** (the containerized environment where Earthly commands are run).

Next, we run a go build command against the previously copied `main.go` file.

Finally, we save the output of the build command as an artifact. The syntax for `SAVE ARTIFACT` defaults the destination path to `/` - so our artifact will be called `/example` (it can be later referenced as `+build/example`). If we wanted to save it at a different path, we could use `SAVE ARTIFACT output/example /some/path/to/example` and refer to it later as `+build/some/path/to/example`.

Now let's create a new target called `+docker`.

```Dockerfile
docker:
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:latest
```

You may notice the command `COPY +build/... ...`, which has an unfamiliar form if you're coming from Docker. This is a special type of `COPY`, which can be used to pass artifacts from one target to another.

Lastly, we save the current state as a docker image, which will have the docker tag `go-example:latest`. This image is only made available to the host's docker if the entire build succeeds.

## Target Environments

Notice how we already had Go installed for both our `+build` and `+docker` targets. This is because  targets inherit from the base target which for us was the `FROM golang:1.15-alpine3.13` that we set up at the top of the file. But it's worth noting that targets can define their own environments. For example:

```Dockerfile
VERSION 0.7
FROM golang:1.15-alpine3.13
WORKDIR /go-workdir

build:
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example AS LOCAL local-output/go-example

npm:
    FROM node:12-alpine3.12
    WORKDIR /src
    RUN npm install
    COPY assets/ .
    RUN npm test
```

In this example, the `+build` target does not have a `FROM`, so it inherits from the base target, `golang:1.15-alpine3.13`. 

The target `+npm`, on the other hand, specifies its own environment with the `FROM`command and so will run inside of a `node:12-alpine3.12` container.

## Not All Targets Produce Output
Targets have the ability to produce output outside of the build environment. You can save files and docker images to your local machine or push them to remote repositories. Targets can also run commands that affect the local environment outside of the build, such as running database migrations, but not all targets produce output. 

## Saving Files
We've already seen how the command SAVE ARTIFACT copies a file or directory from the build environment into the target's artifact environment.

This gives us the ability to copy files between targets, **but it does not allow us to save any files to our local machine.**

```Dockerfile
build:
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example

docker:
    #  COPY command copies files from the +build target
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:latest
```
In order to **save the file locally** , we need to add `AS LOCAL` to the command.

```Dockerfile
build:
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example AS LOCAL local-output/go-example
```

## Saving Docker Images
Saving Docker images to your local machine is easy with the `SAVE IMAGE` command.

```Dockerfile
build:
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example

docker:
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:latest
```

## The Push Flag

In addition to saving files and images locally, we can also push them to remote repositories.

```Dockerfile
docker:
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE --push go-example:latest
```
Note that adding the `--push` flag to `SAVE IMAGE` is not enough, we'll also need to invoke push when we run earthly. `earthly --push +docker`.

#### External Changes
You can also use `--push` as part of a `RUN` command to define commands that have an effect external to the build. These kinds of effects are only allowed to take place if the entire build succeeds.

This allows you to push to remote repositories. 

```Dockerfile
release:
    RUN --push --secret GITHUB_TOKEN=GH_TOKEN github-release upload
```
```bash
earthly --push +release
```
But also allows you to do things like run database migrations.

```Dockerfile
migrate:
    FROM +build
    RUN --push bundle exec rails db:migrate
```
```bash
earthly --push +migrate
```
Or apply terraform changes

```Dockerfile
apply:
    RUN --push terraform apply -auto-approve
```
```bash
earthly --push +apply
```

## Dependencies
Now let's imagine that we want to add some dependencies to our app. In Go, that means adding `go.mod` and `go.sum`. 

`./go.mod`

```go.mod
module github.com/earthly/earthly/examples/go

go 1.13

require github.com/sirupsen/logrus v1.5.0
```

`./go.sum` (empty)

```go.sum
```

Now we can update our Earthfile to copy in the `go.mod` and `go.sum`.

`./Earthfile`

```Dockerfile
VERSION 0.7
FROM golang:1.15-alpine3.13
WORKDIR /go-workdir

build:
    COPY go.mod go.sum .
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example AS LOCAL local-output/go-example

docker:
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:latest
```
This works, but it is inefficient because we have not made proper use of caching. In the current setup, when a file changes, the corresponding `COPY` command is re-executed without cache, causing all commands after it to also re-execute without cache.

### Caching

If, however, we could first download the dependencies and only afterwards copy and build the code, then the cache would be reused every time we changed the code.

`./Earthfile`

```Dockerfile
VERSION 0.7
FROM golang:1.15-alpine3.13
WORKDIR /go-workdir

build:
    # Download deps before copying code.
    COPY go.mod go.sum .
    RUN go mod download
    # Copy and build code.
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example AS LOCAL local-output/go-example

docker:
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:latest
```

## Reusing Dependencies

In some cases, the dependencies might be used in more than one build target. For this use case, we might want to separate dependency downloading and reuse it. For this reason, let's consider breaking this out into a separate target called `+deps`. We can then inherit from `+deps` by using the command `FROM +deps`.

`./Earthfile`

```Dockerfile
VERSION 0.7
FROM golang:1.15-alpine3.13
WORKDIR /go-workdir

deps:
    COPY go.mod go.sum ./
    RUN go mod download
    # Output these back in case go mod download changes them.
    SAVE ARTIFACT go.mod AS LOCAL go.mod
    SAVE ARTIFACT go.sum AS LOCAL go.sum

build:
    FROM +deps
    COPY main.go .
    RUN go build -o output/example main.go
    SAVE ARTIFACT output/example AS LOCAL local-output/go-example

docker:
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:latest
```

## Just Like Docker...Mostly

`ARG`s in Earthly work similar to `ARG`s in Dockerfiles, however there are a few differences when it comes to scope. Also, Earthly has a number of [built in `ARG`s](../earthfile/builtin-args.md) that are available to use.

Let's say we wanted to have the option to pass in a tag for our Docker image when we run `earthly +docker`.

```Dockerfile
docker:
    ARG tag='latest'
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:$tag
```
In our `+docker` target we can create an `ARG` called tag. In this case, we give it a default value of `latest`. If we do not provide a default value the default will be an empty string.

Then, down in our `SAVE IMAGE` command, we are able to reference the `ARG` with `$` followed by the `ARG` name.

Now we can take advantage of this when we run Earthly.

```bash
earthly +docker --tag='my-new-image-tag'
```

### Passing ARGs in FROM, BUILD, and COPY
We can also pass `ARG`s when referencing a target inside an Earthfile. Using the `FROM` and `BUILD` commands, this looks pretty similar to what we did above on the command line.

```Dockerfile
docker:
    ARG tag='latest'
    COPY +build/example .
    ENTRYPOINT ["/go-workdir/example"]
    SAVE IMAGE go-example:$tag

with-build:
    BUILD +docker --tag='my-new-image-tag'

with-from:
    FROM +docker --tag='my-new-image-tag'
```
We can also pass `ARG`s when using the `COPY` command, though the syntax is a little different.

```Dockerfile
build:
    ARG version
    COPY main.go .
    RUN go build -o output/example-$version main.go
    SAVE ARTIFACT output/example-$version AS LOCAL local-output/go-example

with-copy:
    COPY (+build/example --version='1.0') .
```
## The `WITH DOCKER` Command

You may find that you need to run Docker commands inside of a target. For those cases Earthly offers `WITH DOCKER`. `WITH DOCKER` will initialize a Docker daemon that can be used in the context of a `RUN` command.

Whenever you need to use `WITH DOCKER` we recommend (though it is not required) that you use Earthly's own Docker in Docker (dind) image: `earthly/dind:alpine`.

Notice `WITH DOCKER` creates a block of code that has an `END` keyword. Everything that happens within this block is going to take place within our `earthly/dind:alpine` container.

### Pulling an Image
```Dockerfile
hello:
    FROM earthly/dind:alpine
    WITH DOCKER --pull hello-world
        RUN docker run hello-world
    END

```
You can see in the command above that we can pass a flag to `WITH DOCKER` telling it to pull an image from Docker Hub. We can pass other flags to [load in artifacts built by other targets](#loading-an-image) `--load` or even images defined by [docker-compose](#a-real-world-example) `--compose`. These images will be available within the context of `WITH DOCKER`'s docker daemon.
