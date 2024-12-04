# Poll-In tool

Tool polls / pulls-in ("poll-in") digital objects from a GAMS5 project and performs static site rendering. 

Informatics: polling-concept


## Basic usage

0. Rye setup (rye sync / rye pin)
1. Clone or init project files (zimlab under projects)
2. Run the static site rendering


```sh
# Setup project files
pollin "memo" "C:\Users\sebas\Desktop\testme" init


# Example GAMS-SSR startup
pollin "memo" "C:\Users\sebas\Desktop\testme" start

# alternatively set a custom host and port 
pollin -h "http://localhost:18085/" "memo" "C:\Users\sebas\Desktop\testme" start 8080

```