# cpu_stress_cores.py
Simple python script to bring your cpu usage to 100% on every cpu core

A tool for computer enthusiasts who want to test the stability of their system under full load, or how hot their CPU and other components get at 100% usage. Especially useful when you are installing a new cpu, heatsink or have had to reapply thermal paste, or have in some way affected airflow inside your computer case.

This script will count how many cpu cores your system has (or hyperthreads on some systems), and creates a gtk3 window with buttons to trigger 100% cpu usage processes for that number of processor cores (8 cores = 8 buttons). Especially useful is an extra button to trigger all cpu cores to be sent to 100% cpu usage at once.

*NOTE*: Unfortunately, though the GUI says it is going to stress a particular cpu core (eg, core #4) this is not actually possible (yet?), and is instead just an id for each process that will be launched.

I have kept useful comments and links within the code for python newbies like myself.

Tested only on Linux. Requires GTK 3. **Use at your own risk!**



    Usage:
    -h  display help message
    -m  show debug messages on the terminal

