## Tip: COPY and FROM

In Earthly, the FROM command in an Earthfile sets the base environment for a target. This environment includes all the artifacts and images created and saved in the target that the FROM command is pointing to.

So, if you have target1 and you're creating artifacts in it using SAVE ARTIFACT, and then you have target2 where you're saying FROM target1, the build environment of target2 automatically inherits all the artifacts from target1. You don't need to use the COPY command to transfer those artifacts from target1 to target2 - it's done automatically by the FROM command.

However, if you change the base image in target1, this can affect the artifacts saved in target1. If you still want to use these artifacts in target2 even after changing the base image in target1, that's when you would use the SAVE ARTIFACT command in target1 and the COPY command in target2.

In essence, SAVE ARTIFACT and COPY together provide a way to persist and transfer artifacts across targets when the base image changes. If the base image isn't changing, then simply using FROM is sufficient.

## Tip: COPY Directories

Use COPY --dir to copy multiple directories
The classical Dockerfile COPY command differs from the unix cp in that it will copy directory contents, not the directories themselves. This requires that copying multiple directories to be split across multiple lines:
```
# Avoid: too verbose
COPY dir-1 dir-1
COPY dir-2 dir-2
COPY dir-3 dir-3
```
This is repetitive and uses more cache layers than should be necessary.
Earthly introduces a setting, COPY --dir, which makes COPY behave more like cp and less like the Dockerfile COPY. The --dir flag can be used therefore to copy multiple directories in a single command:
```
# Good
COPY --dir dir-1 dir-2 dir-3 ./
```

## Tip: COPY consilidation

Don't write code like this:
```
  COPY package.json .
  COPY tsconfig.json .
  COPY tsconfig.node.json .
  COPY postcss.config.cjs .
  COPY tailwind.config.cjs .
  COPY vite.config.ts .
  COPY public/ ./public
  COPY index.html .
  COPY src/ ./src
`Snippet 2``:`

Instead, it is better to translate it to this form:
```
  COPY index.html package.json tsconfig.json tsconfig.node.json postcss.config.cjs tailwind.config.cjs vite.config.ts .
  COPY --dir public src .
```

In the first snippet, each COPY command copies a single file or directory, which results in 9 separate COPY commands.

In the second snippet, the first COPY command copies multiple individual files at once, and the second COPY command copies the entire 'public' and 'src' directories, effectively reducing the number of COPY commands to just 2.

The second version is a best practice.

Depending on the context, it could also be further condensed to use glob wildcards:

```
  COPY index.html *.json *.config.cjs vite.config.ts .
  COPY --dir public src .
```

If all files are needed this may be more stable in the future when more files are added.
