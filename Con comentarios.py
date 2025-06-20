# ==============================================================================
# --- IMPORTACIONES DE BIBLIOTECAS ---
# ==============================================================================
import tkinter as tk  # Biblioteca estándar de Python para crear interfaces gráficas (GUI).
from tkinter import font, messagebox  # Componentes específicos de tkinter para fuentes y ventanas de mensajes.
from PIL import Image, ImageTk       # Biblioteca Pillow (PIL) para manipular imágenes. Se usa para mostrar el árbol.
import graphviz                     # Biblioteca para crear visualizaciones de grafos, usada para dibujar el árbol.
import os                           # Biblioteca para interactuar con el sistema operativo (aunque no se usa activamente aquí).

# ==============================================================================
# --- LÓGICA DE ÁRBOLES (Nodo y Funciones de Conteo) ---
# ==============================================================================

class Nodo:
    """
    Representa un único nodo en un árbol. Cada nodo contiene un valor (clave),
    referencias a sus hijos izquierdo y derecho, y su altura.
    La altura es crucial para el balanceo en los árboles AVL.
    """
    def __init__(self, clave):
        self.clave = clave          # El valor almacenado en el nodo.
        self.izquierdo = None       # Referencia al nodo hijo izquierdo (None si no tiene).
        self.derecho = None         # Referencia al nodo hijo derecho (None si no tiene).
        self.altura = 1             # Altura del nodo. Un nodo nuevo (hoja) siempre tiene altura 1.

def construir_arbol_perfecto(claves):
    """
    Construye un árbol binario de búsqueda lo más balanceado posible a partir de una lista de claves.
    No es un AVL, sino que se genera una única vez de forma óptima.
    """
    if not claves: return None
    # Elimina duplicados y ordena las claves para facilitar la construcción.
    claves_ordenadas = sorted(list(set(claves)))

    def construir_recursivo(sub_claves):
        # Caso base: si no hay claves en la sublista, no hay subárbol.
        if not sub_claves: return None
        # Se elige el elemento del medio como raíz del subárbol.
        # Esto garantiza que el árbol esté balanceado.
        indice_medio = len(sub_claves) // 2
        raiz = Nodo(sub_claves[indice_medio])
        # Se construye recursivamente el subárbol izquierdo con la mitad inferior de las claves.
        raiz.izquierdo = construir_recursivo(sub_claves[:indice_medio])
        # Se construye recursivamente el subárbol derecho con la mitad superior.
        raiz.derecho = construir_recursivo(sub_claves[indice_medio + 1:])
        return raiz
    
    return construir_recursivo(claves_ordenadas)

# --- Funciones para calcular estadísticas del árbol ---

def contar_nodos(nodo):
    """Cuenta el número total de nodos en un árbol de forma recursiva."""
    if not nodo: return 0
    return 1 + contar_nodos(nodo.izquierdo) + contar_nodos(nodo.derecho)

def contar_hojas(nodo):
    """Cuenta el número de nodos hoja (nodos sin hijos) de forma recursiva."""
    if not nodo: return 0
    # Caso base: un nodo es una hoja si no tiene hijo izquierdo ni derecho.
    if not nodo.izquierdo and not nodo.derecho: return 1
    # Suma las hojas de los subárboles izquierdo y derecho.
    return contar_hojas(nodo.izquierdo) + contar_hojas(nodo.derecho)

def calcular_altura_arbol(nodo):
    """Calcula la altura de un árbol (la longitud del camino más largo desde la raíz a una hoja)."""
    if not nodo: return 0
    # La altura es 1 (el nodo actual) más la altura del subárbol más alto.
    return 1 + max(calcular_altura_arbol(nodo.izquierdo), calcular_altura_arbol(nodo.derecho))

def calcular_grado_arbol(nodo):
    """Calcula el grado del árbol (el número máximo de hijos que tiene cualquier nodo)."""
    if not nodo: return 0
    grado_actual = 0
    if nodo.izquierdo: grado_actual += 1
    if nodo.derecho: grado_actual += 1
    # Si un nodo ya tiene grado 2, el grado del árbol será 2 (el máximo en un árbol binario).
    if grado_actual == 2: return 2
    # El grado del árbol es el máximo entre el grado del nodo actual y el de sus subárboles.
    return max(grado_actual, calcular_grado_arbol(nodo.izquierdo), calcular_grado_arbol(nodo.derecho))

# ==============================================================================
# --- CLASE ArbolAVL ---
# ==============================================================================
class ArbolAVL:
    """Implementa la lógica completa de un Árbol AVL, incluyendo inserción,
    eliminación y las rotaciones necesarias para el auto-balanceo."""

    def obtener_altura(self, raiz):
        """Devuelve de forma segura la altura de un nodo, manejando el caso de que sea None."""
        if not raiz: return 0
        return raiz.altura

    def obtener_balance(self, raiz):
        """Calcula el factor de balance de un nodo (diferencia de alturas de subárboles)."""
        if not raiz: return 0
        return self.obtener_altura(raiz.izquierdo) - self.obtener_altura(raiz.derecho)

    def rotacion_derecha(self, z):
        """Realiza una rotación simple a la derecha sobre el nodo z."""
        y = z.izquierdo      # El hijo izquierdo de z se convertirá en la nueva raíz.
        T3 = y.derecho        # Guardamos el subárbol derecho de y.

        # Realizar la rotación
        y.derecho = z       # z se convierte en el hijo derecho de y.
        z.izquierdo = T3    # El antiguo subárbol derecho de y se convierte en el hijo izquierdo de z.

        # Actualizar alturas (importante hacerlo en este orden: primero el nodo que bajó, luego el que subió).
        z.altura = 1 + max(self.obtener_altura(z.izquierdo), self.obtener_altura(z.derecho))
        y.altura = 1 + max(self.obtener_altura(y.izquierdo), self.obtener_altura(y.derecho))

        return y  # Devolvemos la nueva raíz del subárbol.

    def rotacion_izquierda(self, z):
        """Realiza una rotación simple a la izquierda sobre el nodo z."""
        y = z.derecho         # El hijo derecho de z se convertirá en la nueva raíz.
        T2 = y.izquierdo      # Guardamos el subárbol izquierdo de y.

        # Realizar la rotación
        y.izquierdo = z       # z se convierte en el hijo izquierdo de y.
        z.derecho = T2        # El antiguo subárbol izquierdo de y se convierte en el hijo derecho de z.

        # Actualizar alturas
        z.altura = 1 + max(self.obtener_altura(z.izquierdo), self.obtener_altura(z.derecho))
        y.altura = 1 + max(self.obtener_altura(y.izquierdo), self.obtener_altura(y.derecho))

        return y  # Devolvemos la nueva raíz del subárbol.
        
    def insertar(self, raiz, clave):
        """Inserta una clave en el árbol y realiza el balanceo si es necesario."""
        # 1. Inserción estándar de un Árbol Binario de Búsqueda (BST)
        if not raiz: return Nodo(clave)
        elif clave < raiz.clave: raiz.izquierdo = self.insertar(raiz.izquierdo, clave)
        else: raiz.derecho = self.insertar(raiz.derecho, clave)

        # 2. Actualizar la altura del nodo ancestro actual
        raiz.altura = 1 + max(self.obtener_altura(raiz.izquierdo), self.obtener_altura(raiz.derecho))

        # 3. Obtener el factor de balance para ver si el nodo se ha desbalanceado
        balance = self.obtener_balance(raiz)

        # 4. Si hay desbalance, aplicar una de las 4 rotaciones posibles
        # Caso Izquierda-Izquierda (LL) -> Rotación Derecha Simple
        if balance > 1 and clave < raiz.izquierdo.clave:
            return self.rotacion_derecha(raiz)
        # Caso Derecha-Derecha (RR) -> Rotación Izquierda Simple
        if balance < -1 and clave > raiz.derecho.clave:
            return self.rotacion_izquierda(raiz)
        # Caso Izquierda-Derecha (LR) -> Rotación Izquierda y luego Derecha
        if balance > 1 and clave > raiz.izquierdo.clave:
            raiz.izquierdo = self.rotacion_izquierda(raiz.izquierdo)
            return self.rotacion_derecha(raiz)
        # Caso Derecha-Izquierda (RL) -> Rotación Derecha y luego Izquierda
        if balance < -1 and clave < raiz.derecho.clave:
            raiz.derecho = self.rotacion_derecha(raiz.derecho)
            return self.rotacion_izquierda(raiz)
        
        return raiz

    def obtener_minimo(self, raiz):
        """Encuentra el nodo con el valor mínimo en un subárbol (el que está más a la izquierda)."""
        if raiz is None or raiz.izquierdo is None: return raiz
        return self.obtener_minimo(raiz.izquierdo)

    def eliminar(self, raiz, clave):
        """Elimina una clave del árbol y realiza el balanceo si es necesario."""
        # 1. Eliminación estándar de un BST
        if not raiz: return raiz
        if clave < raiz.clave: raiz.izquierdo = self.eliminar(raiz.izquierdo, clave)
        elif clave > raiz.clave: raiz.derecho = self.eliminar(raiz.derecho, clave)
        else:
            # Nodo con uno o cero hijos
            if raiz.izquierdo is None: return raiz.derecho
            elif raiz.derecho is None: return raiz.izquierdo
            # Nodo con dos hijos: obtener el sucesor inorden (el más pequeño del subárbol derecho)
            sucesor = self.obtener_minimo(raiz.derecho)
            raiz.clave = sucesor.clave
            raiz.derecho = self.eliminar(raiz.derecho, sucesor.clave) # Eliminar el sucesor

        if raiz is None: return raiz

        # 2. Actualizar altura y balancear (similar a la inserción)
        raiz.altura = 1 + max(self.obtener_altura(raiz.izquierdo), self.obtener_altura(raiz.derecho))
        balance = self.obtener_balance(raiz)

        # 3. Lógica de balanceo post-eliminación
        # Caso Izquierda-Izquierda (LL)
        if balance > 1 and self.obtener_balance(raiz.izquierdo) >= 0:
            return self.rotacion_derecha(raiz)
        # Caso Izquierda-Derecha (LR)
        if balance > 1 and self.obtener_balance(raiz.izquierdo) < 0:
            raiz.izquierdo = self.rotacion_izquierda(raiz.izquierdo)
            return self.rotacion_derecha(raiz)
        # Caso Derecha-Derecha (RR)
        if balance < -1 and self.obtener_balance(raiz.derecho) <= 0:
            return self.rotacion_izquierda(raiz)
        # Caso Derecha-Izquierda (RL)
        if balance < -1 and self.obtener_balance(raiz.derecho) > 0:
            raiz.derecho = self.rotacion_derecha(raiz.derecho)
            return self.rotacion_izquierda(raiz)

        return raiz

# ==============================================================================
# --- CLASE App (Interfaz con Layout Izquierda/Derecha) ---
# ==============================================================================
class App:
    """Clase principal que gestiona la interfaz gráfica y la interacción con los árboles."""
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Árboles")
        self.root.geometry("1200x800")

        # --- Variables de estado de la aplicación ---
        self.arbol_avl_obj = ArbolAVL()         # Instancia de la lógica AVL.
        self.raiz_avl, self.claves_avl = None, [] # Datos del árbol AVL.
        self.raiz_perfecto, self.claves_perfecto = None, [] # Datos del árbol perfecto.
        self.raiz_actual, self.claves_ingresadas = None, [] # Punteros al árbol actualmente seleccionado.
        self.tipo_arbol_seleccionado = None     # Flag para saber qué modo está activo ('AVL' o 'PERFECTO').
        self.photo_img = None                   # Variable para mantener una referencia a la imagen del árbol.

        # --- Definición de fuentes para la UI ---
        self.font_label = font.Font(family="Helvetica", size=12)
        self.font_button = font.Font(family="Helvetica", size=11, weight="bold")
        self.font_info = font.Font(family="Consolas", size=11)
        
        # --- CREACIÓN DE PANELES PRINCIPALES ---
        # Panel Izquierdo para Controles e Información
        self.panel_izquierdo = tk.Frame(root, width=380, relief=tk.RIDGE, bd=2)
        self.panel_izquierdo.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.panel_izquierdo.pack_propagate(False) # Evita que el panel se encoja para ajustarse a su contenido.

        # Panel Derecho para la Visualización del Árbol
        self.panel_derecho = tk.Frame(root)
        self.panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        # --- WIDGETS DEL PANEL IZQUIERDO ---
        # Frame de selección de modo de árbol
        self.frame_seleccion = tk.LabelFrame(self.panel_izquierdo, text="1. Modo de Árbol", font=self.font_label, padx=10, pady=10)
        self.frame_seleccion.pack(fill='x', padx=10, pady=10)
        
        self.frame_botones_sel = tk.Frame(self.frame_seleccion)
        self.frame_botones_sel.pack(pady=5)
        self.btn_seleccionar_avl = tk.Button(self.frame_botones_sel, text="Árbol AVL", font=self.font_button, command=self.seleccionar_modo_avl)
        self.btn_seleccionar_avl.pack(side='left', padx=10)
        self.btn_seleccionar_perfecto = tk.Button(self.frame_botones_sel, text="Árbol Perfecto", font=self.font_button, command=self.seleccionar_modo_perfecto)
        self.btn_seleccionar_perfecto.pack(side='left', padx=10)
        
        # Frame de acciones (insertar, eliminar, etc.)
        self.frame_accion = tk.LabelFrame(self.panel_izquierdo, text="2. Acciones", font=self.font_label, padx=10, pady=10)
        self.frame_accion.pack(fill='x', padx=10, pady=(0, 10))

        self.label_entrada = tk.Label(self.frame_accion, text="Ingrese los datos:", font=self.font_label)
        self.label_entrada.pack(pady=(0, 5))
        self.entry_claves = tk.Entry(self.frame_accion, font=self.font_label, width=40)
        self.entry_claves.pack(pady=5, ipady=3)
        self.frame_botones_acc = tk.Frame(self.frame_accion)
        self.frame_botones_acc.pack(pady=10)
        
        self.btn_accion_principal = tk.Button(self.frame_botones_acc, text="Insertar", font=self.font_button, bg="#007BFF", fg="white", command=self.accion_insertar_avl)
        self.btn_accion_principal.pack(side='left', padx=5)
        self.btn_eliminar = tk.Button(self.frame_botones_acc, text="Eliminar", font=self.font_button, bg="#E74C3C", fg="white", command=self.accion_eliminar_nodo)
        self.btn_eliminar.pack(side='left', padx=5)
        self.btn_reiniciar_actual = tk.Button(self.frame_botones_acc, text="Reiniciar Actual", font=self.font_button, bg="#FFC107", fg="black", command=self.accion_reiniciar_actual)
        self.btn_reiniciar_actual.pack(side='left', padx=5)
        
        # Frame para mostrar las estadísticas del árbol
        self.frame_info = tk.LabelFrame(self.panel_izquierdo, text="3. Estadísticas", font=self.font_label, padx=10, pady=10)
        self.frame_info.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.label_info = tk.Label(self.frame_info, font=self.font_info, justify='left', anchor='nw', wraplength=340)
        self.label_info.pack(fill='both', expand=True)

        # Botón de reinicio global
        tk.Button(self.panel_izquierdo, text="REINICIAR TODO", font=self.font_button, bg="#DC3545", fg="white", command=self.reiniciar_app).pack(side=tk.BOTTOM, fill='x', padx=10, pady=10)

        # --- WIDGETS DEL PANEL DERECHO ---
        self.label_imagen = tk.Label(self.panel_derecho) # Etiqueta donde se mostrará la imagen del árbol.
        self.label_imagen.pack(fill='both', expand=True)

        # Configura la interfaz a su estado inicial.
        self.configurar_ui_inicial()

    def configurar_ui_inicial(self):
        """Establece el estado inicial de la GUI al arrancar o reiniciar."""
        for btn in [self.btn_seleccionar_avl, self.btn_seleccionar_perfecto]: btn.config(state=tk.NORMAL)
        for widget in [self.label_entrada, self.entry_claves, self.btn_accion_principal, self.btn_eliminar, self.btn_reiniciar_actual]: widget.config(state=tk.DISABLED)
        self.entry_claves.delete(0, tk.END)
        self.label_info.config(text="Bienvenido.\n\nPor favor, elija un tipo de árbol para empezar.")
        self.label_imagen.config(image='')
        self.photo_img = None

    def reiniciar_app(self):
        """Reinicia la aplicación por completo, borrando ambos árboles."""
        if not messagebox.askyesno("Confirmar Reinicio Total", "Esto borrará TODOS los árboles (AVL y Perfecto).\n¿Está seguro?"): return
        self.raiz_avl, self.claves_avl = None, []
        self.raiz_perfecto, self.claves_perfecto = None, []
        self.raiz_actual, self.claves_ingresadas = None, []
        self.tipo_arbol_seleccionado = None
        self.configurar_ui_inicial()

    def seleccionar_modo_avl(self):
        """Configura la UI para operar en el modo Árbol AVL."""
        self.tipo_arbol_seleccionado = 'AVL'
        # Apunta las variables "actuales" a los datos del árbol AVL.
        self.raiz_actual, self.claves_ingresadas = self.raiz_avl, self.claves_avl
        # Actualiza el estado de los botones y textos.
        self.btn_seleccionar_avl.config(state=tk.DISABLED)
        self.btn_seleccionar_perfecto.config(state=tk.NORMAL)
        self.label_entrada.config(text="Ingrese número(s) separados por espacio:", state=tk.NORMAL)
        self.entry_claves.config(state=tk.NORMAL)
        self.btn_accion_principal.config(text="Insertar", command=self.accion_insertar_avl, state=tk.NORMAL)
        self.btn_eliminar.config(state=tk.NORMAL, command=self.accion_eliminar_nodo)
        self.btn_reiniciar_actual.config(state=tk.NORMAL)
        self.actualizar_ui("Modo Árbol AVL activado.")

    def seleccionar_modo_perfecto(self):
        """Configura la UI para operar en el modo Árbol Perfecto."""
        self.tipo_arbol_seleccionado = 'PERFECTO'
        # Apunta las variables "actuales" a los datos del árbol Perfecto.
        self.raiz_actual, self.claves_ingresadas = self.raiz_perfecto, self.claves_perfecto
        # Reconfigura los botones para las acciones del árbol perfecto.
        self.btn_seleccionar_avl.config(state=tk.NORMAL)
        self.btn_seleccionar_perfecto.config(state=tk.DISABLED)
        self.label_entrada.config(text="Ingrese números separados por espacios:", state=tk.NORMAL)
        self.entry_claves.config(state=tk.NORMAL)
        self.btn_accion_principal.config(text="Generar Árbol", command=self.accion_generar_perfecto, state=tk.NORMAL)
        self.btn_eliminar.config(state=tk.NORMAL, command=self.accion_eliminar_no_disponible) # Deshabilita la eliminación lógica.
        self.btn_reiniciar_actual.config(state=tk.NORMAL)
        self.actualizar_ui("Modo Árbol Perfecto activado.")

    def accion_eliminar_no_disponible(self):
        """Muestra un mensaje informativo indicando por qué la eliminación no está disponible."""
        messagebox.showinfo("Función no disponible","La eliminación de nodos no está habilitada para el modo 'Árbol Perfecto'.\n\nEste tipo de árbol se genera una sola vez. Eliminar nodos individualmente rompe su estructura 'perfecta'.")

    def accion_reiniciar_actual(self):
        """Borra los datos del árbol actualmente seleccionado."""
        if not self.tipo_arbol_seleccionado: return
        if not self.claves_ingresadas:
            messagebox.showinfo("Información", f"El Árbol {self.tipo_arbol_seleccionado} ya está vacío.")
            return
        if not messagebox.askyesno("Confirmar Reinicio Local", f"¿Desea reiniciar el Árbol {self.tipo_arbol_seleccionado} actual?"): return
        
        # Borra los datos del árbol correspondiente al modo actual.
        if self.tipo_arbol_seleccionado == 'AVL': self.raiz_avl, self.claves_avl = None, []
        elif self.tipo_arbol_seleccionado == 'PERFECTO': self.raiz_perfecto, self.claves_perfecto = None, []
        self.raiz_actual, self.claves_ingresadas = None, []
        self.actualizar_ui(f"Árbol {self.tipo_arbol_seleccionado} reiniciado.")

    def accion_insertar_avl(self):
        """Procesa la entrada del usuario para insertar nodos en el Árbol AVL."""
        try:
            claves_str = self.entry_claves.get().split()
            if not claves_str: return
            claves_nuevas = [int(item) for item in claves_str]
            nodos_insertados_count = 0
            for clave in claves_nuevas:
                if clave not in self.claves_ingresadas:
                    self.claves_ingresadas.append(clave)
                    # Llama al método de inserción de la clase ArbolAVL.
                    self.raiz_actual = self.arbol_avl_obj.insertar(self.raiz_actual, clave)
                    nodos_insertados_count += 1
            if nodos_insertados_count > 0:
                # Guarda el estado del árbol actual en las variables del modo AVL.
                self.raiz_avl, self.claves_avl = self.raiz_actual, self.claves_ingresadas
                self.actualizar_ui(f"Insertados {nodos_insertados_count} nodo(s).")
            else: messagebox.showinfo("Sin Cambios", "No se insertaron nodos (posiblemente ya existían).")
        except (ValueError, TypeError): messagebox.showerror("Error", "Ingrese solo números enteros separados por espacios.")
        finally: self.entry_claves.delete(0, tk.END) # Limpia el campo de entrada.

    def accion_eliminar_nodo(self):
        """Procesa la entrada del usuario para eliminar un nodo del Árbol AVL."""
        try:
            clave_str = self.entry_claves.get()
            if not clave_str.strip():
                messagebox.showwarning("Entrada vacía", "Por favor ingrese un número para eliminar.")
                return
            clave = int(clave_str)
            if clave not in self.claves_ingresadas:
                messagebox.showwarning("No Encontrado", f"El nodo {clave} no existe.")
                return
            self.claves_ingresadas.remove(clave)
            # Llama al método de eliminación de la clase ArbolAVL.
            self.raiz_actual = self.arbol_avl_obj.eliminar(self.raiz_actual, clave)
            # Guarda el estado actualizado.
            self.raiz_avl, self.claves_avl = self.raiz_actual, self.claves_ingresadas
            self.actualizar_ui(f"Nodo {clave} eliminado")
        except (ValueError, TypeError): messagebox.showerror("Error", "Para eliminar, ingrese un único número entero.")
        finally: self.entry_claves.delete(0, tk.END)

    def accion_generar_perfecto(self):
        """Procesa la entrada para generar un nuevo Árbol Perfecto."""
        try:
            claves = [int(item) for item in self.entry_claves.get().split()]
            if not claves:
                messagebox.showwarning("Entrada vacía", "Por favor ingrese números para generar el árbol.")
                return
            # Llama a la función de construcción del árbol perfecto.
            self.claves_ingresadas = sorted(list(set(claves)))
            self.raiz_actual = construir_arbol_perfecto(self.claves_ingresadas)
            # Guarda el estado.
            self.raiz_perfecto, self.claves_perfecto = self.raiz_actual, self.claves_ingresadas
            self.actualizar_ui("Árbol Perfecto generado")
        except (ValueError, TypeError): messagebox.showerror("Error", "Ingrese solo números enteros separados por espacios.")
        finally: self.entry_claves.delete(0, tk.END)

    def actualizar_ui(self, titulo_info):
        """Refresca toda la información visual (estadísticas y gráfico del árbol)."""
        if not self.claves_ingresadas or self.tipo_arbol_seleccionado is None:
            self.label_info.config(text=f"--- {titulo_info} ---\n\nEl árbol para el modo '{self.tipo_arbol_seleccionado}' está vacío.")
            self.label_imagen.config(image='')
            self.photo_img = None
            return

        # 1. Calcular todas las estadísticas usando las funciones auxiliares.
        orden, peso = len(self.claves_ingresadas), len(self.claves_ingresadas)
        hojas = contar_hojas(self.raiz_actual)
        nodos_internos, conexiones = orden - hojas, max(0, orden - 1)
        altura, grado = calcular_altura_arbol(self.raiz_actual), calcular_grado_arbol(self.raiz_actual)

        # 2. Formatear el texto de las estadísticas y mostrarlo.
        texto_info = (f"--- {titulo_info} ---\n\n"
                      f"Estadísticas del Árbol ({self.tipo_arbol_seleccionado}):\n"
                      f"------------------------\n"
                      f"Peso (Total Nodos) : {peso}\n"
                      f"Altura             : {altura}\n"
                      f"Grado              : {grado}\n"
                      f"Conexiones (Ramas) : {conexiones}\n"
                      f"Hojas (Terminales) : {hojas}\n"
                      f"Nodos Internos     : {nodos_internos}\n\n"
                      f"Claves del Árbol:\n{sorted(self.claves_ingresadas)}")
        self.label_info.config(text=texto_info)
        
        # 3. Generar la imagen del árbol usando Graphviz.
        g = graphviz.Digraph('Arbol')
        g.attr('node', shape='circle', style='filled', fillcolor='skyblue')
        
        def construir_grafo(nodo):
            """Función recursiva interna para añadir nodos y aristas al grafo."""
            if nodo:
                g.node(str(nodo.clave))
                if nodo.izquierdo: g.edge(str(nodo.clave), str(nodo.izquierdo.clave)); construir_grafo(nodo.izquierdo)
                if nodo.derecho: g.edge(str(nodo.clave), str(nodo.derecho.clave)); construir_grafo(nodo.derecho)
        
        construir_grafo(self.raiz_actual)
        
        try:
            # Renderiza el grafo en un archivo PNG temporal y lo limpia después.
            nombre_archivo = "arbol_temp"
            g.render(nombre_archivo, format='png', cleanup=True)
            
            # 4. Abrir la imagen con Pillow y mostrarla en la etiqueta de Tkinter.
            img = Image.open(f"{nombre_archivo}.png")
            # Ajusta el tamaño para que quepa en el panel, manteniendo la proporción.
            img.thumbnail((self.panel_derecho.winfo_width(), self.panel_derecho.winfo_height()), Image.Resampling.LANCZOS)
            self.photo_img = ImageTk.PhotoImage(img) # Convierte la imagen de PIL a un formato que Tkinter entiende.
            self.label_imagen.config(image=self.photo_img)
            self.label_imagen.image = self.photo_img # Mantiene una referencia para evitar que el recolector de basura la borre.
        except Exception as e:
            messagebox.showerror("Error de Graphviz", f"No se pudo generar el gráfico.\nAsegúrese de que Graphviz esté instalado y en el PATH.\n\nError: {e}")
            self.label_imagen.config(image='', text="Error al generar gráfico.")

# ==============================================================================
# --- PUNTO DE ENTRADA DE LA APLICACIÓN ---
# ==============================================================================
if __name__ == "__main__":
    # Crea la ventana principal de Tkinter.
    ventana = tk.Tk()
    # Crea una instancia de nuestra clase App, pasándole la ventana principal.
    app = App(ventana)
    # Inicia el bucle de eventos de la aplicación, que la mantiene corriendo y esperando interacciones.
    ventana.mainloop()