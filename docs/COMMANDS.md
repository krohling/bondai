# BONDAI COMMANDS

Basic commands:

### `bondai`

Start BondAI with default settings.

```bash
bondai
```

### `exit`

To get back to the terminal.

```bash
exit
```


The following arguments can be passed on the command line to change how the **BondAI** CLI tool works.

### `--enable-prompt-logging`

Turns on prompt logging which will write all prompt inputs into the default log directory `/logs`

```bash
bondai --enable-prompt-logging
```

Save log files to a custom directory

```bash
bondai --enable-prompt-logging my-log-files
```

### `--enable-dangerous`

Allows potentially dangerous Tools to be loaded (i.e. ShellTool and PythonREPLTool)

```bash
bondai --enable-dangerous
```

### `--quiet` 

Suppress agent output. Prevent the agent from printing detailed information about each step it's taking.

```bash
bondai --quiet
```

### `--load-tools my_tools.py`

If this option is specified no tools will be loaded by default. Instead **BondAI** will load the specified Python file and look for a function named **get_tools()**. This function should return a list of Tools.

```bash
bondai --load-tools my_tools.py
```
