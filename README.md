# An Alternative SBLAR Parser POC

This is a POC for a SBLAR file parser and validator that does not rely on data classes. More to come.

## Dev Container Setup

The code in this repository is developed and run inside of a dev container within Visual Studio Code. These instructions will not work if using an alternative editor such as Vim or Emacs. To build, run, and attach the container to VS Code you'll need to have Docker installed on your system, and the `Dev Containers` extension installed within VS Code.

Open this repository within VS Code and press `COMMAND + SHIFT + p` on your keyboard. This will open the command bar at the top of your window. Enter `Dev Containers: Rebuild and Reopen in Container`. VS Code will open a new window and you'll see a status message towards the bottom right of your screen that the container is building and attaching. This will take a few minutes the first time because Docker needs to build the container without a build cache. You may receive a notification that VS Code wants to perform a reload because some extensions could not load. Sometimes this happens because extensions are loaded in conflicting orders and dependencies are not satisfied. 

## Fixing the Code

There is a `hello_world.py` file at the root of the repository. It has some linting issues such as excessive line lengths and unused imports. We can rely on `make` and the Makefile VS Code extension to let us know what problems there are with this code. Towards the bottom left of your screen you should see `Makefile Tasks`. Click `lint` and it will tell you there are 6 linting errors. Now run `lint_and_fix` and 4 of these will be solved for us. You'll have to manually fix the formatting on the lines that are too long. Make the fix, save the file, and rerun `lint` and ruff will be happy with the file.