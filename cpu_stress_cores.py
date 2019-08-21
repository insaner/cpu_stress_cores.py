#!/usr/bin/env python

# ORIG: http://danielflannery.ie/simulate-cpu-load-with-python/
# https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python
# https://wiki.gnome.org/Projects/PyGObject/Threading

import time
import signal

import sys # for cli args

import multiprocessing
from multiprocessing import Pool
from multiprocessing import Process

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, GLib, Gtk

cpu_cores = multiprocessing.cpu_count() # includes hyperthreads
core_is_stressed = [0]*cpu_cores

stressed_cores = []
unstressed_cores = []

stop_loop = 0

#################
# config:
show_timestamp = 0
show_debug_msgs = 0 # can override this here or with the command line arg "-m"
#################

def d_print(msg):
    if show_debug_msgs:
        print(msg) 


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN) # https://noswap.com/blog/python-multiprocessing-keyboardinterrupt


class StressTestWindow(Gtk.Window):

    ########## 
    def __init__(self):
        super(StressTestWindow, self).__init__( default_width=500, default_height=400, title="CPU stress test")

        self.cancellable = Gio.Cancellable()
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, border_width=12)

        self.stress_button = [None]*cpu_cores

        for x in range(cpu_cores):
                self.stress_button[x] = Gtk.Button(label="stress core #" + str(x))
                self.stress_button[x].connect("clicked", self.on_stress_clicked)
                self.stress_button[x].core_num = x
                self.stress_button[x].core_id = str(x)
                self.stress_button[x].stress_state = 0
                
                # https://docs.python.org/release/3.1.3/library/multiprocessing.html
                self.stress_button[x].proc =  Process(target=self.proc_func, args=(self.stress_button[x],))
                
                box.pack_start(self.stress_button[x], False, True, 0)

        self.stress_all_button = Gtk.Button(label="Stress all " + str(cpu_cores) + " cores")
        self.stress_all_button.connect("clicked", self.on_stress_all_clicked)

        self.cancel_button = Gtk.Button(label="Quit")
        self.cancel_button.connect("clicked", self.on_quit_clicked)

        textview = Gtk.TextView()
        self.textbuffer = textview.get_buffer()
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.add(textview)

        box.pack_start(self.stress_all_button, False, True, 0)
        box.pack_start(self.cancel_button, False, True, 0)
        box.pack_start(self.scrolled, True, True, 0)

        self.add(box)
        



    ########## 
    def proc_func(self, core_button):
        self.stressor_func(core_button)
        #self.test_proc_func(core_button) # comment the stressor_func line above and uncomment this one to debug the multiproc functionality
        
    ########## 
    def stressor_func(self, core_button):
        x=2
        d_print ("stressor_func: core[" + str(core_button.core_num) +"]"  +" begin stress" )
        while not stop_loop:
            x*x
        d_print ("stressor_func: core[" + str(core_button.core_num) +"]"  +" STOP LOOP" )


    ########## 
    def test_proc_func(self, core_button):
        self.append_text("test_proc_func: core[" + str(core_button.core_num) +"]"  )
        for x in range(cpu_cores):
            if stop_loop:
                d_print ("test_proc_func: core[" + str(core_button.core_num) +"]"  +" STOP LOOP" )
                self.set_stress_state(core_button, 0)
                return
            d_print ("test_proc_func: core[" + str(core_button.core_num) +"]"  +" [" + str(x) +"]" )
            time.sleep(1)


    ########## 
    def begin_stress(self, core_button_h):
        global stop_loop
        stop_loop = 0
        
        msg = "Stressing core: " + core_button_h.core_id        
        self.append_text(msg)
        d_print (msg)
        self.set_stress_all_state(self.stress_all_button, 0)
        
        if not core_button_h.proc:
            #print ("begin_stress(): " + str(core_button_h.core_id) )
            core_button_h.proc = Process(target=self.proc_func, args=(core_button_h,))
        core_is_stressed[core_button_h.core_num]=1
        core_button_h.proc.start()
        #core_button_h.proc.join() # causes the button to block


    ########## 
    def stop_stress(self, core_button_h):
        msg = "Unstressing core: " + core_button_h.core_id
        self.append_text(msg)
        d_print (msg)
        core_button_h.proc.terminate()
        core_button_h.proc = None
        core_is_stressed[core_button_h.core_num]=0
        
        if not self.any_stressed():
            self.set_stress_all_state(self.stress_all_button, 1)
            

    ########## 
    def append_text(self, text):
        iter_ = self.textbuffer.get_end_iter()
        if show_timestamp:
           self.textbuffer.insert(iter_, "[%s] %s\n" % (str(time.time()), text))
        else:
           self.textbuffer.insert(iter_, " %s\n" % (text))

        adj = self.scrolled.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())


    ########## 
    def set_stress_state(self, button, set_to_state):
        if set_to_state == 0:
            button.set_label ("stress core #" + button.core_id)
        else:
            button.set_label ("stop stressing core #" + button.core_id)
        button.stress_state = set_to_state


    ########## 
    def set_stress_all_state(self, button, set_to_state):
        if set_to_state == 1:
            button.set_label ("Stress all " + str(cpu_cores) + " cores")
        else:
            button.set_label ("Stop stressing cores")


    ########## 
    def any_stressed(self):
        global stressed_cores
        global unstressed_cores
        stressed_cores = []
        unstressed_cores = []
        
        any_stressed = 0
        
        for i,v in enumerate(core_is_stressed):
            if v:
                #print (" core[" + str(i) +"] is STRESSED" )
                any_stressed = 1
                stressed_cores.append(i)
            else:
                #print (" core[" + str(i) +"] is NOT STRESSED" )
                unstressed_cores.append(i)
        return any_stressed


    ########## 
    def on_stress_clicked(self, button):
        if button.stress_state == 0:
            self.set_stress_state(button, 1)
            self.begin_stress(button)
        else:
            self.set_stress_state(button, 0)
            self.stop_stress(button)

    ########## 
    def on_stress_all_clicked(self, button):
        any_stressed = self.any_stressed() # must run any_stressed() before "stressed_cores" is correct
        self.set_stress_all_state(button,any_stressed)
        if any_stressed:
            self.append_text("Stop stressing cores...")
            for x in stressed_cores:
                # d_print (" stressed_cores[" + str(x) +"] " )
                self.set_stress_state(self.stress_button[x], 0)
                self.stop_stress(self.stress_button[x])
        else:
            self.append_text("Stressing all " + str(cpu_cores) + " cores...")
            for x in range(cpu_cores):
                self.set_stress_state(self.stress_button[x], 1)
                self.begin_stress(self.stress_button[x])


    ########## 
    def on_quit_clicked(self, button):
        self.append_text("Cancel clicked...")
        
        d_print ("Unstressing cores before quit...")
        any_stressed = self.any_stressed() # must run any_stressed() before "stressed_cores" is correct
        if any_stressed:
            for x in stressed_cores:
                #print (" unstressing core[" + str(x) +"] " )
                self.stop_stress(self.stress_button[x])
                
        self.cancellable.cancel()
        d_print ("quitting...")
        quit()

    ########## 
    def quit():
        d_print ("exiting...")
        exit()


#signal.signal(signal.SIGINT, signal.SIG_DFL)
#signal.signal(signal.SIGINT, exit_chld)
#signal.signal(signal.SIGINT, signal.SIG_IGN) # https://stackoverflow.com/a/6191991/2758435

if __name__ == "__main__":
    # https://stackoverflow.com/questions/16410852/keyboard-interrupt-with-with-python-gtk
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    if len(sys.argv) > 2 :
        print ('ERROR: only one argument supported at a time.')
        print ('usage:')
        print ('-h  display this help message')
        print ('-m  show debug messages')
        exit()

    if len(sys.argv) > 1 and sys.argv[1] == "-h":
        print ('usage:')
        print ('-h  display this help message')
        print ('-m  show debug messages')
        exit()

    if len(sys.argv) > 1 and sys.argv[1] == "-m":
        show_debug_msgs = 1
        
    d_print ('-' * 20)
    d_print("* "+ str(cpu_cores) + " * cpu cores to test")    
    
    num_cpus = multiprocessing.cpu_count()
    pool = Pool(num_cpus, init_worker)
    # pool = Pool(num_cpus)
    # pool.map(f, range(num_cpus))
    
    win = StressTestWindow()
    
    # https://stackoverflow.com/a/5753472/2758435
    # https://lazka.github.io/pgi-docs/Gtk-3.0/constants.html
    # https://developer.gnome.org/pygtk/stable/gtk-stock-items.html
    # https://valadoc.org/gtk+-3.0/Gtk.IconSize.html
    #  other options: STOCK_INFO, STOCK_DIALOG_WARNING, STOCK_CONVERT
    windowicon = win.render_icon(Gtk.STOCK_EXECUTE, Gtk.IconSize.DIALOG)
    win.set_icon(windowicon)
    
    win.show_all()
    win.connect("delete-event", Gtk.main_quit)
    
    Gtk.main()


    
