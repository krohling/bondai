# WINDOWS INSTALL

Example setup with: Windows 11 + WSL, Visual Studio Code, Docker Desktop

### SOFTWARE PREREQUISITES

- Windows 11
- WSL (Windows Subsystem for Linux)
- Ubuntu 22.04 
- Visual Studio Code (vsCode)
- Docker Extension for vsCode
- Docker Desktop

> Install WSL and Ubuntu 22.04 from the Microsoft Store (Start > Microsoft Store)
> Add Docker Extension from within vsCode (Click the Extensions Menu)
> Docker Desktop: https://www.docker.com/products/docker-desktop/
> vsCode: https://code.visualstudio.com/

### FRESH INSTALLATION

Make sure you have all of the software programs installed and open vsCode and Docker Desktop.

1. From inside vsCode, press `CTRL+SHIFT+P` to open the command palette and search for **WSL**

2. Click on **WSL: Connect to WSL using Distro..** and select Ubuntu 22.04

> Next up we need to clone the Bondai Github Repo to your localhost and because we're connected to WSL, save it to a folder in your home directory, rather than a regular windows folder such as My Documents. It will load correctly and be faster keeping it all inside of the Linux environment.

3. `` CTRL + SHIFT + ` `` to open a Terminal window and create a new directory in your home; something like `apps` or `websites` or `repos`.

```bash
cd ~
mkdir apps
```

4. Assuming you dont have an existing project open in vsCode; When you open the left menu (Explorer Panel) you should see some blue buttons, select **Clone Repository**. 

5. From the drop down menu that appears, copy/paste the Bondai Github Repo URL: https://github.com/krohling/bondai and hit enter.

6. After its finished cloning you should see all the files in the left menu under "explorer".

7. Open the Docker folder and right click `docker-compose.yml` and select `Compose Up`

8. In the terminal that opens, you should see Docker building the Image and Container, when it has finished, go to Docker Desktop (and all being well), you will see the Bondai Docker Container running on port 8000 - the green icon symbolizes that is has started up successfully. Orange means something has gone wrong.

9. Click on the docker-bondai container and you will see the a sub menu with:

Logs, Inspect, Bind Mounts, Terminal, Files, Stats

10. Click on Terminal and in the command line type **bondai**, this will start **Bondai** ... you should see something like:

```bash
Loading BondAI...
Skipping Alpaca Markets tools because ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables are not set.
Skipping Gmail tools because gmail-token.pickle file is not present.
Loading LangChain tools...
Done loading LangChain tools
Dangerous Tools are enabled.

Welcome to BondAI!
I have been trained to help you with a variety of tasks.
To get started, just tell me what task you would like me to help you with. The more descriptive you are, the better I can help you.
If you would like to exit, just type 'exit'.

What can I help you with today?
```
