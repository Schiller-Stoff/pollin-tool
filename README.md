# Poll-In tool

Tool polls / pulls-in ("poll-in") digital objects from a GAMS5 project and performs static site rendering. 

Informatics: polling-concept


## Basic usage

1. Clone or init project files
2. Rye setup (https://rye.astral.sh/)
    - Set the correct Python version (recommended: 3.12): `rye pin 3.12`
    - Install packages: `rye sync`
3. Create a `project.toml` with your project metadata, e.g. for the "Memo" project:
```toml
projectAbbr = "memo" 
projectTitle = "MEMO" 
projectSubTitle = "Digitales Memobuch der Stadt Graz" 
projectDesc = "Das digitale Memobuch der Stadt Graz erinnert an Opfer des Nationalsozialismus"
```
4. Run the static site rendering


```sh
# Setup project files
pollin "memo" "C:\Users\sebas\Desktop\testme" init


# Example GAMS-SSR startup 
#   Default host:port of the GAMS-API is http://localhost:18085/ 
#   and localhost:18090 of the GAMS-SSR)
pollin "memo" "C:\Users\sebas\Desktop\testme" start

# alternatively set a custom host and port of the GAMS-API and custom port for the GAMS-SSR
pollin -h "http://localhost:18085/" "memo" "C:\Users\sebas\Desktop\testme" start 8080

```