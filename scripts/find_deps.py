#!/usr/bin/env python
import click
import os
import build
import subprocess
import tempfile
import glob
import tomli_w
import tomli
import sys


@click.command()
@click.argument("package")
@click.option("--skeleton", is_flag=True)
def find_deps(package, skeleton):
    "Finds the build dependencies."

    skel_data = {
        "project": {"package": "example", "versions": []},
        "dependencies": {"default": []},
        "debian11": {},
    }
    if package.find("==") != -1:
        # means we have to split
        package, version = package.split("==")
    else:
        print("Please provide a package with proper version.")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        output = tmpdir
        cmd = [
            "python3",
            "-m",
            "pip",
            "download",
        ]
        cmd.append("--no-binary")
        cmd.append(package)

        cmd.append("--no-deps")
        cmd.extend(["--dest", output, package])
        # now download first
        print(cmd)
        subprocess.check_call(cmd)

        # Now find extract the source.
        tarsources = glob.glob(f"{output}/*.tar.gz")
        zipsources = glob.glob(f"{output}/*.zip")

        with tempfile.TemporaryDirectory() as WHEEL_BUILD_DIR:
            # Now let us extract in a different directory
            for source in tarsources:
                cmd = ["tar", "-xvf", source, "-C", WHEEL_BUILD_DIR]
                subprocess.check_call(cmd)

            for source in zipsources:
                cmd = ["unzip", source, "-d", WHEEL_BUILD_DIR]
                subprocess.check_call(cmd)

            project_names = os.listdir(WHEEL_BUILD_DIR)
            for project_name in project_names:
                build_requires = []
                pb = build.ProjectBuilder(os.path.join(WHEEL_BUILD_DIR, project_name))
                build_requires.extend(list(pb.build_system_requires))
                try:
                    res = pb.get_requires_for_build("wheel")
                except:
                    print(
                        f"\n\nPlease install {build_requires=} in the virtual environment to get the full build dependency list."
                    )
                    return
                build_requires.extend(res)
                result = set()
                for name in build_requires:
                    name = name.replace(" ", "")
                    result.add(name)
                click.echo(
                    click.style(
                        f"\n\n{package} build requirements:\n", fg="green", bold=True
                    )
                )
                print(f"{list(result)}\n\n")

                if not skeleton:
                    click.echo(
                        click.style(
                            f"Not creating/updating the build file.\n", fg="red", bold=True
                        )
                    )
                    sys.exit(0)

                # Now if we have to build the skeleton
                # First check if it already exists or not.
                build_file = os.path.join(
                    f"./packages/{package}/build-dependencies.toml"
                )
                if os.path.exists(build_file):
                    with open(build_file, "rb") as fobj:
                        existing_data = tomli.load(fobj)
                    # First add version
                    versions = existing_data["project"].get("versions")
                    if version not in versions:
                        versions.append(version)
                        versions.sort()
                        existing_data["project"]["versions"] = versions
                    else:
                        print(f"{version=} is already there for {package=}.")
                    # Now build dependencies
                    old = len(result)
                    result.update(existing_data["dependencies"].get("default", []))
                    new = len(result)
                    if old != new:
                        # Means we have new dependencies.
                        # So we have the file and tell the user.
                        existing_data["dependencies"]["default"] = list(result)
                        with open(build_file, "wb") as fobj:
                            tomli_w.dump(existing_data, fobj)
                            print(f"Updated {build_file=}")
                else:
                    # Create a new project directory and build file.
                    os.mkdir(f"./packages/{package}")
                    skel_data["project"]["package"] = package
                    skel_data["project"]["versions"].append(version)
                    skel_data["dependencies"]["default"].extend(list(result))
                    with open(build_file, "wb") as fobj:
                        tomli_w.dump(skel_data, fobj)
                        print(f"Created {build_file=}")


if __name__ == "__main__":
    find_deps()
