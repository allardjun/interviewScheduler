import tkinter as tk

def show_entry_fields():
    print("Folder name: %s" % folderName.get())

master = tk.Tk()
tk.Label(master,
         text="Folder name:").grid(row=0)


folderName = tk.Entry(master)

folderName.grid(row=0, column=1)

tk.Button(master,
          text='Quit',
          command=master.quit).grid(row=3,
                                    column=0,
                                    sticky=tk.W,
                                    pady=4)
tk.Button(master,
          text='Show', command=show_entry_fields).grid(row=3,
                                                       column=1,
                                                       sticky=tk.W,
                                                       pady=4)

tk.mainloop()
tk.quit()
