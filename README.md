# An Alternative SBLAR Parser POC

This is a POC for a SBLAR file parser and validator that does not rely on data classes. More to come.

## Dev Container Setup

The code in this repository is developed and run inside of a dev container within Visual Studio Code. These instructions will not work if using an alternative editor such as Vim or Emacs. To build, run, and attach the container to VS Code you'll need to have Docker installed on your system, and the `Dev Containers` extension installed within VS Code.

Open this repository within VS Code and press `COMMAND + SHIFT + p` on your keyboard. This will open the command bar at the top of your window. Enter `Dev Containers: Rebuild and Reopen in Container`. VS Code will open a new window and you'll see a status message towards the bottom right of your screen that the container is building and attaching. This will take a few minutes the first time because Docker needs to build the container without a build cache. You may receive a notification that VS Code wants to perform a reload because some extensions could not load. Sometimes this happens because extensions are loaded in conflicting orders and dependencies are not satisfied.

## Running the Demo

If using VS Code, setup is completed by simply running the code within a Dev Container. If you're not making use of VS Code, make your life easier and use VS Code :sunglasses:. See the instructions above for setting up the Dev Container. There is a single Jupyter Notebook of interest called `validating_example_sblar.ipynb`. Double click this file and it will open. The default base interpreter is fine beucase we are working in a container. Take a look at `custom_checks.py` and `schema.py`. Feel free to make changes to the code in a different branch. If you make changes to the check functions or Pandera schema, you'll need to restart the Jupyter kernel in order for the import to be reloaded.
