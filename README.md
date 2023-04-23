Test repository to try out build files for wheels.


## Specification

Every package must have a `build-dependencies.toml` file. The file will have the following sections inside.

### project

In the `project` section we mention the name of the project using `package` key, this is the same name 
we have in the upstream `https://pypi.org/project/{package}`.

Next, we have a list of versions to be build for this project.

```toml
package="test-package"
versions = ["0.8.0", "0.78.2", "0.87.0"]
```

### dependencies

This section explains the build time Python dependencies of the project using a
list. Use the key `latest` to list down all the build dependencies for the
latest(aka default) package, we can also mention any version specific details
by adding the same in a list with the version as key.

```toml
[dependencies] 
latest = [
    "wheel==0.40.0",
    "pip"]

"0.78.0" = ["wheel==0.37.2", "pip"]
```

### osname

Next, we have different operating systems for which we are building and also
the details about any required system package, say via `apt` or via `dnf`.

```toml
[debian11]
packages = ["libxyz-dev",
"libpcsc-lite-dev"]

[fedora38]
packages = ["libxyz-devel",
"pcsc-devel"]
```
