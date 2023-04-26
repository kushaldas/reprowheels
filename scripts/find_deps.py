#!/usr/bin/env python
import click
import os
import build
import subprocess
import tempfile
import glob

@click.command()
@click.argument('package')
@click.option('--skeleton', is_flag=True)
def find_deps(package, skeleton):
    "Finds the build dependencies."
    if package.find("==") != -1:
        # means we have to split
        package, version = package.split("==")

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
        cmd.extend(
            [
                "--dest",
                output,
                package])
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
                    print(f"\n\nPlease install {build_requires=} in the virtual environment to get the full build dependency list.")
                    return
                build_requires.extend(res)
                result = set()
                for name in build_requires:
                    name = name.replace(" ", "")
                    result.add(name)
                click.echo(click.style(f"\n\n{package} build requirements:\n", fg='green', bold=True))
                print(f"{list(result)}")

                print(f"{skeleton=}")


if __name__ == "__main__":
    find_deps()
