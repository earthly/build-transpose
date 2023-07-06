Earthfiles are similar to Dockerfiles but are comprised of a series of target declarations and recipe definitions. They provide a rough structure that includes base-recipes, target-names, and command-names. Each recipe contains a series of commands.

## FROM

* `FROM <image-name>`
* `FROM [--platform <platform>] [--allow-privileged] <target-ref> [--<build-arg-key>=<build-arg-value>...]`

The FROM command in an Earthfile works like the FROM instruction in Dockerfile, but with added ability to use another target's image as the base image. The FROM ... AS ... form available in Dockerfile syntax is not supported in Earthfiles. Instead, developers can define a new Earthly target.

## RUN

* `RUN [--push] [--entrypoint] [--privileged] [--secret <env-var>=<secret-ref>] [--ssh] [--mount <mount-spec>] [--] <command>`

The RUN command is used in the Earthfile (analogous to Dockerfile) to execute commands in the build environment of the current target. It can be used in two forms, the exec form (without shell) and the shell form (with shell).

The command has several flags/options that allow for enhanced functionality such as --push (executes command only if all other instructions succeed), --entrypoint (uses current image entrypoint to prepend the command), --privileged (allows the command to use privileged capabilities), --secret (provides a secret to the command), --ssh (allows command to access the ssh authentication client), --mount (mounts a file or directory in the build environment), and --interactive (opens an interactive prompt during the target build).

## COPY

* `COPY dir1 dir1`
* `COPY (+target1/artifact --arg1=foo --arg2=bar) ./dest/path`
* `COPY +dummy-target/encoded-data .`

Contextual Copying: The COPY command in Earthfiles allows the copying of files and directories from one context to another. It can operate in a classical form, copying from the build context into the build environment, or in an artifact form, copying artifacts from the environments of other build targets into the current one.

Differences from Dockerfile: COPY in Earthfiles differs from Dockerfiles in a few key aspects. For instance, URL sources and absolute paths are not supported, and instead of the --from option, you can use a combination of SAVE ARTIFACT and COPY in the artifact form. Also, an .earthlyignore file can be used to exclude file patterns from the build context.

## ARG

* `ARG [--required] <name>[=<default-value>]` 
* `ARG [--required] <name>=$(<default-value-expr>)` 

ARG declares a variable with a name and an optional default value. If no default value is provided, an empty string is used. The scope of the variable is limited to the recipe of the current target or command and only from the point it is declared onward.

The value of an ARG can be overridden either from the earthly command or from another target, when implicitly or explicitly invoking the target containing the ARG.

An ARG can be marked as required with --required flag. A required ARG must be provided at build time and cannot have a default value. This can help eliminate cases where an ARG is unexpectedly set to "".

## SAVE ARTIFACT

* `SAVE ARTIFACT [--keep-ts] [--keep-own] [--if-exists] [--force] <src> [<artifact-dest-path>] [AS LOCAL <local-path>]`

Copying Artifacts: The SAVE ARTIFACT command copies files, directories, or series of files and directories from the build environment into the artifact environment. If AS LOCAL is also specified, the artifact will also be copied to the host at the specified location upon successful build completion.

## SAVE IMAGE

* `SAVE IMAGE [--cache-from=<cache-image>] [--push] <image-name>...` 
* `SAVE IMAGE --cache-hint`

Image Saving and Naming: The SAVE IMAGE command in Earthly is used to mark the current build environment as an image of the target and assign it one or more output image names. This command can be used multiple times to assign different image names to the same build.

Pushing and Caching: The command supports options like --push and --cache-from, enabling the developer to push the image to an external registry or add additional cache sources. The --push option also allows the image to be used as a cache source if inline caching is enabled.

## BUILD

* `BUILD [--platform <platform>] [--allow-privileged] <target-ref> [--<build-arg-name>=<build-arg-value>...]`

The BUILD command is used in Earthly to initiate the construction of a target specified by <target-ref>. This could involve building images, saving artifacts for local output, or issuing push commands, depending on the settings enabled.

The command allows for customization through various options such as --platform to specify the build platform, --allow-privileged for privileged operations, and --<build-arg-key>=<build-arg-value> to set override values for build arguments. Note that build arguments can be constant strings, expressions involving other build args, or dynamic expressions based on the output of a command executed in the context of the build environment.
