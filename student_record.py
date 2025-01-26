from PIL import Image
import ttkbootstrap as ttk
import pymongo
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import bcrypt

Image.CUBIC = Image.BICUBIC


class App(ttk.Window):
    def __init__(self) -> None:
        super().__init__(themename="superhero")
        self.minsize(800, 999)
        self.geometry("800x999")
        self.resizable(False, False)
        self.title("Logowanie")

        self.columnconfigure(0, weight=1, uniform="a")
        self.rowconfigure(0, weight=1, uniform="a")
        self.__frame_data = None
        self.__frame_login = LoginFrame(self)
        self.__frame_login.grid(column=0, row=0, sticky="news")

    def check_password(self, *args, **kwargs) -> None:
        col = pymongo.MongoClient("mongodb://localhost:27017/")["grades_db"]["login_data"]
        login_u = self.__frame_login.entry_login.get()
        password_u = self.__frame_login.entry_password.get()

        if login_u != "" and password_u != "":
            login_db = col.find_one({"Login": login_u})
            if login_db:
                if bcrypt.checkpw(password_u.encode("utf-8"), login_db["Password"].encode("utf-8")):
                    self.__frame_data = FrameData(self, str(login_db["_id"]))
                    self.__frame_login.destroy()
                    self.__frame_data.grid(row=0, column=0, sticky="news")
                    self.title(f"Oceny - {login_u}")
                else:
                    self.error_login()
            else:
                self.error_login()
        else:
            self.error_login()

    def error_login(self) -> None:
        self.__frame_login.label_error.configure(text="Podano zły login lub hasło")
        self.__frame_login.after(5000, lambda: self.__frame_login.label_error.configure(text=""))


class LoginFrame(ttk.Frame):
    def __init__(self, a) -> None:
        super().__init__()

        self.a = a

        sl = ttk.Style()
        sl.configure("TitleLabel.TLabel", font=("Century Gothic", 35))

        sle = ttk.Style()
        sle.configure("EL.TLabel", font=("Century Gothic", 20), foreground="red")

        sb = ttk.Style()
        sb.configure("B.TButton", font=("Century Gothic", 35))

        label_title_login = ttk.Label(self,
                                      text="Login",
                                      style="TitleLabel.TLabel")

        self.entry_login = ttk.Entry(self,
                                     width=45,
                                     font=("Century Gothic", 15))

        label_title_password = ttk.Label(self,
                                         text="Hasło:",
                                         style="TitleLabel.TLabel")

        self.entry_password = ttk.Entry(self,
                                        width=45,
                                        font=("Century Gothic", 15),
                                        show="⬛")

        button_check = ttk.Button(self,
                                  text="Zaloguj",
                                  style="B.TButton",
                                  command=self.a.check_password)

        self.label_error = ttk.Label(self,
                                     text="",
                                     style="EL.TLabel")

        label_title_login.grid(column=0, row=0)
        self.entry_login.grid(column=0, row=1, sticky="n")
        label_title_password.grid(column=0, row=2)
        self.entry_password.grid(column=0, row=3, sticky="n")
        button_check.grid(column=0, row=4, sticky="n")
        self.label_error.grid(column=0, row=5, sticky="n")

        self.entry_password.bind("<Return>", self.a.check_password)

        self.columnconfigure(0, weight=1, uniform="lf")
        self.rowconfigure(0, weight=1, uniform="lf")
        self.rowconfigure(1, weight=1, uniform="lf")
        self.rowconfigure(2, weight=1, uniform="lf")
        self.rowconfigure(3, weight=1, uniform="lf")
        self.rowconfigure(4, weight=1, uniform="lf")
        self.rowconfigure(5, weight=1, uniform="lf")


class FrameData(ttk.Frame):
    def __init__(self, a, id) -> None:
        super().__init__()
        self.a = a
        self.id = id

        self.col = pymongo.MongoClient("mongodb://localhost:27017/")["grades_db"]["lesson_journal"]

        self.plot = True

        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.fig.patch.set_facecolor('#2b3e50')

        self.frame = self.avg_widget()

        self.draw()

        self.button_change = ttk.Button(self,
                                        text="⮂ Średnia na tle klasy ⮂",
                                        width=25,
                                        command=self.change_plot)

        self.treeview = ttk.Treeview(self,
                                     columns=("subject", "grade", "weight", "description", "date"),
                                     show="headings")
        self.treeview.heading("subject", text="Przedmiot")
        self.treeview.heading("grade", text="Ocena")
        self.treeview.heading("weight", text="Waga")
        self.treeview.heading("description", text="Opis")
        self.treeview.heading("date", text="Data")

        self.treeview.column("subject", anchor="center", minwidth=50, width=150)
        self.treeview.column("grade", anchor="center", minwidth=50, width=100)
        self.treeview.column("weight", anchor="center", minwidth=50, width=100)
        self.treeview.column("description", anchor="center", minwidth=50, width=200)
        self.treeview.column("date", anchor="center", minwidth=50, width=150)

        self.combobox_var = ttk.StringVar()

        combobox_subjects = ttk.Combobox(self,
                                         textvariable=self.combobox_var,
                                         state="readonly",
                                         values=("Matematyka",
                                                 "Biologia",
                                                 "Język angielski",
                                                 "Język polski",
                                                 "Język niemiecki",
                                                 "Język francuski",
                                                 "Język łaciński",
                                                 "Informatyka",
                                                 "WF",
                                                 "Chemia",
                                                 "Historia",
                                                 "Fizyka",
                                                 "Religia",
                                                 "Geografia",
                                                 "WOS"))

        self.columnconfigure(0, weight=10, uniform="fd")
        self.columnconfigure(1, weight=4, uniform="fd")

        self.rowconfigure(0, weight=2, uniform="fd")
        self.rowconfigure(1, weight=8, uniform="fd")
        self.rowconfigure(2, weight=2, uniform="fd")
        self.rowconfigure(3, weight=8, uniform="fd")

        combobox_subjects.grid(row=0, column=1)
        self.treeview.grid(row=1, column=0, columnspan=2, sticky="news")
        self.button_change.grid(row=2, column=1)
        self.canvas_widget.grid(row=3, column=0, columnspan=2, sticky="news")

        combobox_subjects.bind("<<ComboboxSelected>>", lambda x: self.treeview_fill())
        self.bind("<Configure>", lambda x: self.fig.tight_layout())
        self.bind("<Map>", lambda x: self.a.geometry("800x1000"))

    def treeview_fill(self) -> None:
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        data = self.col.find({"Przedmiot": self.combobox_var.get(), "uid": self.id})
        for i in data:
            self.treeview.insert("", "end", values=list(i.values())[2:])

    def draw(self) -> None:
        if self.plot:
            self.draw_avg()

        self.after(10_000, self.draw)

    def draw_avg(self) -> None:
        self.fig.clear()
        subjects = {"Matematyka": 0,
                    "Biologia": 0,
                    "Język angielski": 0,
                    "Język polski": 0,
                    "Język niemiecki": 0,
                    "Język francuski": 0,
                    "Język łaciński": 0,
                    "Informatyka": 0,
                    "WF": 0,
                    "Chemia": 0,
                    "Historia": 0,
                    "Fizyka": 0,
                    "Religia": 0,
                    "Geografia": 0,
                    "WOS": 0}

        lista = []
        for i in subjects.keys():
            lista.append(self.col.find({"Przedmiot": i, "uid": self.id}))

        tmp_list = []
        for i in lista:
            l = 0
            m = 0
            for j in i:
                ocena = j["Ocena"]
                waga = j["Waga"]

                if ocena in ('-6', '-5', '-4', '-3', '-2'):
                    l += (float(ocena[1:]) - 0.25) * waga
                    m += waga
                elif ocena in ('+5', '+4', '+3', '+2', '+1'):
                    l += (float(ocena[1:]) + 0.5) * waga
                    m += waga
                else:
                    l += float(ocena) * waga
                    m += waga

            if m > 0:
                tmp_list.append(l / m)
            else:
                tmp_list.append(0)

        for i in range(len(subjects.keys())):
            subjects[list(subjects.keys())[i]] = tmp_list[i]

        ax = self.fig.add_subplot(111)
        bars_colors = ["red" if values < 1.5 else "skyblue" for values in subjects.values()]
        bars = ax.barh(tuple(subjects.keys()), tuple(subjects.values()), color=bars_colors)

        ax.set_title("Średnia ważona z ocen", color="white")
        ax.set_xlabel("Średnie ważone", color="white")
        ax.set_ylabel("Przedmioty", color="white")
        ax.set_facecolor('#2b3e50')
        ax.tick_params(axis='y', labelsize=10, color="white", labelcolor="white")
        ax.tick_params(axis='x', color="white", labelcolor="white")

        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.text(width - 0.2, bar.get_y() + bar.get_height() / 2, f'{width:.2f}',
                        ha='center', va='center', color='black', fontsize=10)

        self.fig.tight_layout()
        self.canvas.draw()

    def change_plot(self) -> None:
        if self.plot:
            self.canvas_widget.grid_remove()
            self.fig.clear()
            self.frame.grid(row=3, column=0, columnspan=2, sticky="news")
            self.button_change.configure(text="⮂ Wykres ocen własnych ⮂")
            self.plot = False
        else:
            self.frame.grid_remove()
            self.canvas_widget.grid(row=3, column=0, columnspan=2, sticky="news")
            self.button_change.configure(text="⮂ Średnia na tle klasy ⮂")
            self.draw()
            self.plot = True

    def avg_widget(self) -> ttk.Frame:
        frame = ttk.Frame(self)
        frame.rowconfigure(0, weight=1, uniform="aw")
        frame.columnconfigure(0, weight=1, uniform="aw")
        frame.columnconfigure(1, weight=1, uniform="aw")

        ttk.Style().configure("L.TLabel", font=("Century Gothic", 20))

        oceny = []
        wagi = []
        for i in self.col.find({"uid": self.id}):
            oceny.append(i["Ocena"])
            wagi.append(i["Waga"])

        for i in range(len(oceny)):
            if oceny[i] in ('-6', '-5', '-4', '-3', '-2'):
                oceny[i] = float(oceny[i][1:]) - 0.25
            if oceny[i] in ('+5', '+4', '+3', '+2', '+1'):
                oceny[i] = float(oceny[i][1:]) + 0.5
            else:
                oceny[i] = int(oceny[i])

        licznik = sum(i * j for i, j in zip(oceny, wagi))
        mianownik = sum(wagi)

        if mianownik > 0:
            user_avg = licznik / mianownik
        else:
            user_avg = 0.0

        ttk.Label(frame,
                  text=f"Twoja średnia: \n {user_avg:.2f}",
                  style="L.TLabel").grid(row=0, column=0)

        oceny = []
        wagi = []
        for i in self.col.find({"uid": {"$ne": self.id}}):
            oceny.append(i["Ocena"])
            wagi.append(i["Waga"])

        for i in range(len(oceny)):
            if oceny[i] in ('-6', '-5', '-4', '-3', '-2'):
                oceny[i] = float(oceny[i][1:]) - 0.25
            if oceny[i] in ('+5', '+4', '+3', '+2', "+1"):
                oceny[i] = float(oceny[i][1:]) + 0.5
            else:
                oceny[i] = int(oceny[i])

        licznik = sum(i * j for i, j in zip(oceny, wagi))
        mianownik = sum(wagi)

        if mianownik > 0:
            user_avg = licznik / mianownik
        else:
            user_avg = 0.0

        ttk.Label(frame,
                  text=f"Średnia klasy: \n {user_avg:.2f}",
                  style="L.TLabel").grid(row=0, column=1)

        return frame


if __name__ == '__main__':
    app = App()
    app.mainloop()
