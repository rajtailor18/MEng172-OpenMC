
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
## Setup micromamba
```python
python setupmicromamba.py
```


## Enable OpenMC
Open the codespace and in the terminal type these two commands
The first one will take a few mins since its 3gb
```python
micromamba activate openmc
```
And then test to see if it works by running this command
```python
python test_openmc.py
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
- 'git add . ':!endfb80-lowtemp/'' to add all your changes
- 'git commit -m "YOUR NOTES"'
- 'git push' to push your changes

## OpenMC Notes
- Sometimes, OpenMC puts limits on how long it should follow a neutron — like if it’s bouncing too much or has too little energy then it will stop tracking it.
- OpenMC alone does not do time-dependent simulations -> Take a look at OpenMOC or Serpent transient mode 

## Visualizations Notes
Dependencies 
- pip install plotly

To see 3D Model 
- python -m http.server 8000
- You'll see something like 'Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...'
- Click on http://0.0.0.0:8000/
- Then click on the .html file in the data folder


## Notes
- The `openmc-data` package installs an HDF5 nuclear data library and `cross_sections.xml`.
- Everyone on the team will get the exact same environment when launching a Codespace.

