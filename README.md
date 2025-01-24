# permanens

Clinical Decisions Support System (CDSS) of PERMANENS project


## Install

A docker container (https://www.docker.com/), fully configured can be downloaded from DockerHub and installed using:

```bash
docker run -d -p 5000:5000 acabrera809/permanens:latest
```
Then, the Permanens GUI will be accesible from a web browser at address http://localhost:5000

Please note that the port of this address is defined in the command line above and can be easily customized.

It is also possible to use an existing local folder for storing the RAs. Let's assume you wish to use 'c:\data' as the local PERMANENS repository. Start by creating a folder inside named 'permanens'. Then, run the following command: 

```bash
docker run -d -p 5000:5000 -v c:\permanens:/data acabrera809/permanens:latest
```
Then, as in the previous example, you can acces the permanens GUI from a web broser at http://localhost:5000


Permanens can be used in most Windows, Linux or macOS configurations, provided that a suitable execution environment is set up. We recommend, as a fist step, installing the Conda package and environment manager. Download a suitable Conda or Anaconda distribution for your operative system from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#)


Download the repository:

```bash
git clone https://github.com/phi-grib/permanens.git
```

Go to the repository directory 

```bash
cd permanens
```

and create the **conda environment** with all the dependencies and extra packages (numpy, RDKit...):

```bash
conda env create -f environment.yml
```

Once the environment is created type:

```bash
source activate permanens_app
```

to activate the environment.

Conda environments can be easily updated using a new version of the environment definition

```bash
conda env update -f new_environment.yml
```

Permanens must be installed as a regular Python package. From the permanens directory type (note the dot at the end):

```bash
pip install . 
```

or

```bash
python setup.py install
```

For development, use pip with the -e flag or setup with `develop` instead of `install`. This will made accesible the latest changes to other components

```bash
pip install -e .
```
or 

```bash
python setup.py develop
```

## Configuration

After installation is completed, you must run the configuration command to configure the directory where permanens will place the consults. If permanens has not been configured previously the following command

```bash
permanenns -c config
```

will suggest a default directory structure following the XDG specification in GNU/Linux, %APPDATA% in windows.

To specify a custom path use the `-d` parameter to enter the root folder where the risk assessments will be placed:

```bash
permanens -c config -d /my/custom/path
```

will set up the risk assessments repository to `/my/custom/path/consults`

Once it has been configured, the current setting can be displayed using again the command 

```bash
permanens -c config
```

As a fallback, permanens can also be configured using the following command

```bash
permanens -c config -a silent
```

This option sets up the consult repository within the permanens installation directory (`permanens\permanens\consults`). Unlike other options, this command does not ask permision to the end-user to create the directories or set up the repositories and is used internally by automatic installers and for software development. 



## Acknowledgments

Permanens has been developed for the project Permanens (https://www.permanens.eu/)

The PERMANENS project is supported by Instituto de Salud Carlos III (ISCIII) and by the European Union NextGenerationEU, Mecanismo para la Recuperación y la Resiliencia (AC22/00006; AC22/00045), the Swedish Innovation Agency (no. 2022-00549), the Research Council of Norway (project no. 342386) and the Health Research Board Ireland (ERAPERMED2022) under the frame of ERA PerMed.

