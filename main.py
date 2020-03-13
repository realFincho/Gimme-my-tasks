import datetime
import sqlite3 as sql
import tkinter as tk


class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.initDesign()
        self.initScrollSpace()
        self.database = DataBase()
        self.initTasks()

    def initDesign(self):
        self.title('Task Manager')
        self.iconbitmap(default='data\\icon.ico')

        _x = int((self.winfo_screenwidth() / 2) - 240)

        _y = int((self.winfo_screenheight() / 2) - 225)
        self.geometry("{}x{}+{}+{}".format(480, 450, _x, _y))
        self.resizable(False, False)

    def initScrollSpace(self):

        self.canvasFrame = tk.Frame(self, width=464, height=450, bg='green')
        self.canvasFrame.pack(side='left', fill='y')

        self.canvas = tk.Canvas(self.canvasFrame, bg='white', borderwidth=0)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=384, height=450)
        self.canvas.place(x=-2, y=-2)

        self.frameOnCanvas = tk.Frame(self.canvas, bg='grey92')
        self.canvas.create_window((0, 0), window=self.frameOnCanvas, anchor='nw')
        self.frameOnCanvas.bind("<Configure>", self.eFrameConfigure)

        self.scrlBar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrlBar.set)
        self.scrlBar.pack(side='right', fill='y')

    def eFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=464, height=450)

    def clearTasks(self):
        for i in self.frameOnCanvas.grid_slaves():
            i.destroy()

    def initTasks(self):
        self.clearTasks()

        with self.database.con:
            self.database.cursor.execute('select * from tasks')
            i = 0
            while True:
                record = self.database.cursor.fetchone()

                if record is None:
                    break

                Task(self.frameOnCanvas, record).grid(row=i, column=0, pady=1)
                i += 1

        self.newTask = NewTask(self.frameOnCanvas)
        self.newTask.grid(row=len(self.frameOnCanvas.grid_slaves()) + 1, column=0, pady=1)

        self.newTask.image.bind('<Double-Button-1>', self.eAddTask)
        self.newTask.lbName.bind('<Double-Button-1>', self.eAddTask)

    def eAddTask(self, event):
        with self.database.con:
            self.database.cursor.execute(
                "insert into tasks (name, category, date, repeat) values ('Новая задача', 'Новая категория', '', 'Не выбрано')")
        record = (self.database.cursor.lastrowid, 'Новая задача', 'Новая категория', '', 'Не выбрано')
        Task(self.frameOnCanvas, record).grid(row=len(self.frameOnCanvas.grid_slaves()), column=0, pady=1)
        self.newTask.grid(row=len(self.frameOnCanvas.grid_slaves()) + 1, column=0, pady=1)

    def checkTasks(self):
        self.cday = datetime.datetime.today()


class Task(tk.Frame):

    def __init__(self, master, record):
        super().__init__(master, width=464, height=54, bg='white')
        self.data = list(record)
        self.updateDate()
        self.initWidgets()

    def initWidgets(self):
        self.image = tk.Label(self, width=36, height=54, bg='white')
        try:
            if datetime.datetime.strptime(self.data[3], '%d.%m.%Y') <= datetime.datetime.today():
                self.photoImage = tk.PhotoImage(file='data\\inactive.png')
            else:
                self.photoImage = tk.PhotoImage(file='data\\active.png')
        except:
            self.photoImage = tk.PhotoImage(file='data\\active.png')

        self.image.configure(image=self.photoImage)
        self.image.place(x=-2, y=-2)

        self.lbName = tk.Label(self, font=('Tahoma', 12), anchor='sw', text=self.data[1], bg='white')
        self.lbName.place(x=38, y=-2, width=240, height=34)

        self.lbDate = tk.Label(self, font=('Tahoma', 10, 'bold'), anchor='w', fg='grey40', bg='white')
        if self.data[3] != '' and self.data[3] is not None:
            self.lbDate.configure(text='Срок: ' + self.data[3])

        self.lbDate.place(x=38, y=32, width=150, height=22)

        self.lbCategory = tk.Label(self, font=('Tahoma', 12), anchor='sw', text=self.data[2], bg='white')
        self.lbCategory.place(x=278, y=-2, width=188, height=34)

        self.lbRepeat = tk.Label(self, font=('Tahoma', 10, 'bold'), anchor='w', borderwidth=0, fg='grey40', bg='white')
        if self.data[4] != 'Не выбрано' and self.data[4] is not None:
            self.lbRepeat.configure(text='Повтор: ' + self.data[4])

        self.lbRepeat.place(x=188, y=32, width=278, height=22)

        self.bind('<Enter>', self.eWidgetEnter)
        self.bind('<Leave>', self.eWidgetLeave)

        self.image.bind('<Double-Button-1>', self.eOpenTaskEditor)
        self.lbName.bind('<Double-Button-1>', self.eOpenTaskEditor)
        self.lbCategory.bind('<Double-Button-1>', self.eOpenTaskEditor)
        self.lbDate.bind('<Double-Button-1>', self.eOpenTaskEditor)
        self.lbRepeat.bind('<Double-Button-1>', self.eOpenTaskEditor)

    def eOpenTaskEditor(self, event):
        self.te = TaskEditor(self, self.data)
        self.te.btnDelete.configure(command=self.eDeleteTask)
        self.te.btnApply.configure(command=self.eApply)

    def eApply(self):
        # ----
        dName = self.te.entryName.get()
        dCategory = self.te.entryCategory.get()
        try:
            dDate = datetime.datetime.strptime(self.te.entryData.get(), '%d.%m.%Y')
            dDate = datetime.datetime.strftime(dDate, '%d.%m.%Y')
            dRepeat = self.te.repeatvar.get()
        except:
            dDate = ''
            dRepeat = 'Не выбрано'

        self.data = [self.data[0], dName, dCategory, dDate, dRepeat]

        self.updateDate()

        con = sql.connect('TM.db')
        cursor = con.cursor()
        cursor.execute("update tasks set name = ? , category = ? , date = ? , repeat = ? where id = ?",
                       tuple(self.data[1:] + [self.data[0]]))
        con.commit()
        # ----
        self.te.destroy()
        self.updateData()

    def updateData(self):
        try:
            if datetime.datetime.strptime(self.data[3], '%d.%m.%Y') <= datetime.datetime.today():
                self.photoImage = tk.PhotoImage(file='data\\inactive.png')
            else:
                self.photoImage = tk.PhotoImage(file='data\\active.png')
        except:
            self.photoImage = tk.PhotoImage(file='data\\active.png')
        self.image.configure(image=self.photoImage)

        self.lbName.configure(text=self.data[1])
        self.lbCategory.configure(text=self.data[2])
        if self.data[3] != '':
            self.lbDate.configure(text='Срок: ' + self.data[3])
        else:
            self.lbDate.configure(text='')
        if self.data[4] != 'Не выбрано':
            self.lbRepeat.configure(text='Повтор: ' + self.data[4])
        else:
            self.lbRepeat.configure(text='')

    def eDeleteTask(self):
        # ----
        con = sql.connect('TM.db')
        cursor = con.cursor()
        cursor.execute('delete from tasks where id = ?', (self.data[0],))
        con.commit()
        # ----
        self.te.destroy()
        self.destroy()

    def eWidgetEnter(self, event):
        self.image.configure(bg='gray96')
        self.lbName.configure(bg='gray96')
        self.lbCategory.configure(bg='gray96')
        try:
            self.lbDate.configure(bg='gray96')
            self.lbRepeat.configure(bg='gray96')
        except:
            self.configure(bg='gray96')

    def eWidgetLeave(self, event):
        self.image.configure(bg='white')
        self.lbName.configure(bg='white')
        self.lbCategory.configure(bg='white')
        try:
            self.lbDate.configure(bg='white')
            self.lbRepeat.configure(bg='white')
        except:
            self.configure(bg='white')

    def updateDate(self):
        if self.data[3] != '' and self.data[4] != 'Не выбрано':
            date = datetime.datetime.strptime(self.data[3], '%d.%m.%Y')
            span = {"Ежедневно": datetime.timedelta(days=1), "Еженедельно": datetime.timedelta(weeks=1),
                    "Ежемесячно": datetime.timedelta(days=30)}[self.data[4]]
            while date <= datetime.datetime.today():
                date += span
            self.data[3] = datetime.datetime.strftime(date, '%d.%m.%Y')
        return None


class NewTask(tk.Frame):

    def __init__(self, master):
        super().__init__(master, width=464, height=54, bg='green')
        self.initWidgets()

    def initWidgets(self):
        self.image = tk.Label(self, width=36, height=54, bg='white')
        self.photoImage = tk.PhotoImage(file='data\\add.png')
        self.image.configure(image=self.photoImage)
        self.image.place(x=-2, y=-2)

        self.lbName = tk.Label(self, font=('Tahoma', 12), anchor='w', text='Добавить задачу', fg='blue', bg='white')
        self.lbName.place(x=38, y=-2, width=426, height=56)

        self.bind('<Enter>', self.eWidgetEnter)
        self.bind('<Leave>', self.eWidgetLeave)

    def eWidgetEnter(self, event):
        self.image.configure(bg='gray96')
        self.lbName.configure(bg='gray96')

    def eWidgetLeave(self, event):
        self.image.configure(bg='white')
        self.lbName.configure(bg='white')

    # data = [id, name, category, date, repeat]


class TaskEditor(tk.Toplevel):

    def __init__(self, master, record):
        super().__init__(master)
        self.data = record
        self.initDesign()
        self.initWidgets()

        self.grab_set()
        self.focus_set()

    def initDesign(self):
        self.title('Редактор задач')
        self.configure(bg='grey96')
        _x = int((self.winfo_screenwidth() / 2) - 200)
        _y = int((self.winfo_screenheight() / 2) - 200)
        self.geometry("{}x{}+{}+{}".format(400, 400, _x, _y))

        self.resizable(False, False)

    def initWidgets(self):
        self.labelName = tk.Label(self, font=('Tahoma', 12), bg='grey96', anchor='w', text='Название задачи:')
        self.labelName.place(x=20, y=20, width=140, height=30)

        self.entryName = tk.Entry(self, borderwidth=1, relief='solid', font=('TrueType', 12))
        self.entryName.insert(0, self.data[1])
        self.entryName.place(x=20, y=50, width=240, height=34)

        self.labelCategory = tk.Label(self, font=('Tahoma', 12), bg='grey96', anchor='w', text='Название категории:')
        self.labelCategory.place(x=20, y=84, width=188, height=34)

        self.entryCategory = tk.Entry(self, borderwidth=1, relief='solid', font=('Tahoma', 12))
        self.entryCategory.insert(0, self.data[2])
        self.entryCategory.place(x=20, y=114, width=188, height=34)

        # -
        self.btnDelete = tk.Button(self, width=64, height=64, bg='grey96')
        self.photoImage = tk.PhotoImage(file='data\\trash.png')
        self.btnDelete.configure(image=self.photoImage)
        self.btnDelete.place(x=310, y=20)
        # -
        self.btnApply = tk.Button(self, font=('Tahoma', 12), text='Применить')
        self.btnApply.place(x=280, y=350, width=100, height=30)
        # -
        self.labelDataMenu = tk.Label(self, font=('Tahoma', 12), bg='grey96', text='Дата выполнения:')
        self.labelDataMenu.place(x=20, y=164, width=148, height=34)

        self.entryData = tk.Entry(self, borderwidth=1, relief='solid', font=('Tahoma', 12))
        self.entryData.insert(0, self.data[3])
        self.entryData.place(x=20, y=198, width=160, height=34)
        # -
        self.repeatvar = tk.StringVar()
        self.repeatvar.set(self.data[4])

        self.labelDataMenu = tk.Label(self, font=('Tahoma', 12), bg='grey96', anchor='w', text='Повтор:')
        self.labelDataMenu.place(x=220, y=164, width=148, height=34)

        self.repeatMenu = tk.OptionMenu(self, self.repeatvar, 'Не выбрано', "Ежедневно", "Еженедельно", "Ежемесячно")
        self.repeatMenu.configure(bg="white", font=('Tahoma', 12), anchor='w')
        self.repeatMenu.place(x=220, y=198, height=38, width=160)


class DataBase:

    def __init__(self):
        self.con = sql.connect('TM.db')
        self.cursor = self.con.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS tasks (
            id integer not null primary key autoincrement,
            name text,
            category text,
            date text,
            repeat text)''')
        self.con.commit()


mainWindow = MainWindow()
mainWindow.mainloop()
