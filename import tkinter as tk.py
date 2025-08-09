import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, ttk
from tkcalendar import Calendar
from datetime import datetime
import json
import os

ARCHIVO = "tareas.json"
PRIORIDADES = ["Alta", "Media", "Baja"]

class TaskManager:
    def __init__(self):
        self.tareas = []
        self.cargar()

    def guardar(self):
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(self.tareas, f, indent=4, ensure_ascii=False)

    def cargar(self):
        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                self.tareas = json.load(f)

    def agregar_tarea(self, titulo, fecha, prioridad):
        self.tareas.append({
            "titulo": titulo,
            "fecha": fecha,
            "prioridad": prioridad
        })
        self.guardar()

    def editar_tarea(self, index, titulo, fecha, prioridad):
        if 0 <= index < len(self.tareas):
            self.tareas[index] = {"titulo": titulo, "fecha": fecha, "prioridad": prioridad}
            self.guardar()

    def eliminar_tarea(self, index):
        if 0 <= index < len(self.tareas):
            self.tareas.pop(index)
            self.guardar()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tareas PRO")
        self.root.geometry("600x450")
        self.manager = TaskManager()

        # Filtro por prioridad
        filtro_frame = tk.Frame(root)
        filtro_frame.pack(pady=5)
        tk.Label(filtro_frame, text="Filtrar por prioridad:").pack(side=tk.LEFT)
        self.filtro_var = tk.StringVar(value="Todas")
        filtro_combo = ttk.Combobox(filtro_frame, textvariable=self.filtro_var,
                                    values=["Todas"] + PRIORIDADES, state="readonly")
        filtro_combo.pack(side=tk.LEFT, padx=5)
        filtro_combo.bind("<<ComboboxSelected>>", lambda e: self.actualizar_lista())

        # Lista de tareas
        self.lista = tk.Listbox(root, height=15, width=70)
        self.lista.pack(pady=10)

        # Botones
        frame_btn = tk.Frame(root)
        frame_btn.pack()

        tk.Button(frame_btn, text="Agregar", width=12, command=self.agregar).grid(row=0, column=0, padx=5)
        tk.Button(frame_btn, text="Editar", width=12, command=self.editar).grid(row=0, column=1, padx=5)
        tk.Button(frame_btn, text="Eliminar", width=12, command=self.eliminar).grid(row=0, column=2, padx=5)
        tk.Button(frame_btn, text="Salir", width=12, command=root.quit).grid(row=0, column=3, padx=5)

        self.actualizar_lista()

    def actualizar_lista(self):
        self.lista.delete(0, tk.END)
        filtro = self.filtro_var.get()
        for i, t in enumerate(self.manager.tareas):
            if filtro != "Todas" and t["prioridad"] != filtro:
                continue
            color = "red" if t["prioridad"] == "Alta" else "orange" if t["prioridad"] == "Media" else "green"
            texto = f"{t['titulo']} - {t['fecha']} ({t['prioridad']})"
            self.lista.insert(tk.END, texto)
            self.lista.itemconfig(tk.END, fg=color)

    def seleccionar_fecha(self, fecha_inicial=None):
        """Abre un calendario para seleccionar fecha."""
        top = Toplevel(self.root)
        top.title("Seleccionar Fecha")
        fecha_hoy = datetime.today().strftime("%Y-%m-%d")
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd",
                       year=int(fecha_hoy.split("-")[0]),
                       month=int(fecha_hoy.split("-")[1]),
                       day=int(fecha_hoy.split("-")[2]))
        if fecha_inicial:
            try:
                fecha_dt = datetime.strptime(fecha_inicial, "%Y-%m-%d")
                cal.selection_set(fecha_dt)
            except:
                pass
        cal.pack(pady=10)

        fecha_seleccionada = {"valor": None}

        def confirmar():
            fecha_seleccionada["valor"] = cal.get_date()
            top.destroy()

        tk.Button(top, text="Aceptar", command=confirmar).pack(pady=5)
        top.wait_window()
        return fecha_seleccionada["valor"]

    def agregar(self):
        titulo = simpledialog.askstring("Tarea", "Título de la tarea:")
        if not titulo:
            return
        fecha = self.seleccionar_fecha()
        if not fecha:
            return
        prioridad = simpledialog.askstring("Prioridad", f"Ingrese prioridad {PRIORIDADES}:")
        if prioridad not in PRIORIDADES:
            messagebox.showerror("Error", "Prioridad inválida.")
            return
        self.manager.agregar_tarea(titulo, fecha, prioridad)
        self.actualizar_lista()

    def editar(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione una tarea para editar.")
            return
        index = seleccion[0]
        tarea = self.manager.tareas[index]

        nuevo_titulo = simpledialog.askstring("Editar Tarea", "Nuevo título:", initialvalue=tarea["titulo"])
        if not nuevo_titulo:
            return
        nueva_fecha = self.seleccionar_fecha(fecha_inicial=tarea["fecha"])
        if not nueva_fecha:
            return
        nueva_prioridad = simpledialog.askstring("Prioridad", f"Ingrese prioridad {PRIORIDADES}:",
                                                 initialvalue=tarea["prioridad"])
        if nueva_prioridad not in PRIORIDADES:
            messagebox.showerror("Error", "Prioridad inválida.")
            return
        self.manager.editar_tarea(index, nuevo_titulo, nueva_fecha, nueva_prioridad)
        self.actualizar_lista()

    def eliminar(self):
        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione una tarea para eliminar.")
            return
        self.manager.eliminar_tarea(seleccion[0])
        self.actualizar_lista()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
