try:
    import gi
    import sub_gui.gtk_gui as gtk_gui
    gtk_gui.main()
except ImportError:
    print("unable to import gi (gtk 3). starting tk gui")
    import sub_gui.tk_gui as tk_gui
    tk_gui.main()