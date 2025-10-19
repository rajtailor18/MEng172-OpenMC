
# OpenMC Codespaces Starter

This repo gives you a reproducible OpenMC setup in GitHub Codespaces with Jupyter.

## One-time: Create Codespace
1. Push these files to a GitHub repo (or create the repo from this folder).
2. Click **Code → Codespaces → MEng-172**.
3. Wait for the container to build. When done, you'll have the space ready.

## Setup Cross sectional data OpenMC
Open the codespace and in the terminal type these two commands
The first one will take a few mins since its 3gb
```python
python setup.py
source ~/.bashrc
```

If cross sections aren't set, run in the terminal:
```bash
source ~/.bashrc
```

## Project layout
```
.devcontainer  - DO NOT TOUCH
models - will host all of our models, please place your respected openmc python script in the correct folder
environment.yml - DO NOT TOUCH
README.md - feel free to edit
setup.py is the setup file that needs to be run everytime you set up the codebase
test_openmc.py is the file to test to see if OpenMC is running correctly on your setup
```

## Publishing your work
- 'git status' to see all the code you added
- VERY IMPORTANT - delete the cross sectional files the .tar file and the folder it creates endfb80-lowtemp
- 'git add .' to add all your changes
- 'git commit -m "YOUR NOTES"'
- 'git push' to push your changes

## Notes
- The `openmc-data` package installs an HDF5 nuclear data library and `cross_sections.xml`.
- Everyone on the team will get the exact same environment when launching a Codespace.
```

