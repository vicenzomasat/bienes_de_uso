import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from utils.validators import Validators

class GestionIndices:
    def __init__(self, gestor_indices, parent_window=None, on_change=None):
        self.gestor_indices = gestor_indices
        self.parent_window = parent_window
        self.on_change = on_change
        
        self.window = None
        self.tree = None
        self.fecha_var = None
        self.indice_var = None
        self.obs_var = None
        
        self.create_window()
        self.refresh_table()

    def _changed(self):
        if callable(self.on_change):
            try:
                self.on_change()
            except Exception:
                # La vista principal no debería fallar si el callback da error
                pass
    
    def create_window(self):
        """Crea la ventana de gestión de índices"""
        self.window = tk.Toplevel()
        self.window.title("Gestión de Índices FACPCE")
        self.window.geometry("800x600")
        
        if self.parent_window:
            self.window.transient(self.parent_window)
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="Gestión de Índices FACPCE", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame superior - formulario
        form_frame = ttk.LabelFrame(main_frame, text="Agregar/Editar Índice", padding="10")
        form_frame.pack(fill='x', pady=(0, 10))
        
        self.setup_form(form_frame)
        
        # Frame medio - botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        self.setup_buttons(button_frame)
        
        # Frame inferior - tabla
        table_frame = ttk.LabelFrame(main_frame, text="Índices Cargados", padding="10")
        table_frame.pack(fill='both', expand=True)
        
        self.setup_table(table_frame)
        
        # Instrucciones para decimales
        instrucciones_frame = ttk.Frame(main_frame)
        instrucciones_frame.pack(fill='x', pady=(10, 0))
        
        instrucciones_label = ttk.Label(instrucciones_frame, 
                                      text="💡 Use coma para decimales (ej: 1234,567890) - Link oficial:", 
                                      font=('Arial', 9))
        instrucciones_label.pack(side='left')
        
        link_button = ttk.Button(instrucciones_frame, text="FACPCE - Índices Oficiales", 
                               command=self.abrir_link_facpce)
        link_button.pack(side='left', padx=(10, 0))
    
    def setup_form(self, parent):
        """Configura el formulario de entrada"""
        # Variables
        self.fecha_var = tk.StringVar()
        self.indice_var = tk.StringVar()
        self.obs_var = tk.StringVar()
        
        # Grid
        ttk.Label(parent, text="Fecha (DD/MM/AAAA):").grid(row=0, column=0, sticky='w', padx=(0, 10))
        fecha_entry = ttk.Entry(parent, textvariable=self.fecha_var, width=15)
        fecha_entry.grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        ttk.Label(parent, text="Índice (use , para decimales):").grid(row=0, column=2, sticky='w', padx=(0, 10))
        indice_entry = ttk.Entry(parent, textvariable=self.indice_var, width=20)
        indice_entry.grid(row=0, column=3, sticky='w', padx=(0, 20))
        
        ttk.Label(parent, text="Observaciones:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        obs_entry = ttk.Entry(parent, textvariable=self.obs_var, width=50)
        obs_entry.grid(row=1, column=1, columnspan=3, sticky='ew', pady=(10, 0))
        
        parent.columnconfigure(1, weight=1)
    
    def setup_buttons(self, parent):
        """Configura los botones"""
        ttk.Button(parent, text="➕ Agregar Índice", 
                  command=self.agregar_indice).pack(side='left', padx=(0, 10))
        
        ttk.Button(parent, text="📁 Importar CSV", 
                  command=self.importar_csv).pack(side='left', padx=(0, 10))
        
        ttk.Button(parent, text="💾 Exportar CSV", 
                  command=self.exportar_csv).pack(side='left', padx=(0, 10))
        
        ttk.Button(parent, text="📋 Crear Template", 
                  command=self.crear_template).pack(side='left', padx=(0, 10))
        
        ttk.Button(parent, text="🗑 Eliminar Seleccionado", 
                  command=self.eliminar_indice).pack(side='left', padx=(0, 10))
        
        ttk.Button(parent, text="🔄 Actualizar", 
                  command=self.refresh_table).pack(side='right')
    
    def setup_table(self, parent):
        """Configura la tabla de índices"""
        # Treeview
        columns = ('Fecha', 'Índice', 'Observaciones', 'Fecha Carga')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('Fecha', text='Fecha')
        self.tree.heading('Índice', text='Índice')
        self.tree.heading('Observaciones', text='Observaciones')
        self.tree.heading('Fecha Carga', text='Fecha Carga')
        
        self.tree.column('Fecha', width=100)
        self.tree.column('Índice', width=150)
        self.tree.column('Observaciones', width=200)
        self.tree.column('Fecha Carga', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
    
    def agregar_indice(self):
        """Agrega un nuevo índice"""
        fecha = self.fecha_var.get().strip()
        indice = self.indice_var.get().strip()
        observaciones = self.obs_var.get().strip()
        
        # Validaciones
        if not fecha:
            messagebox.showerror("Error", "Ingrese la fecha")
            return
        
        if not Validators.validar_fecha(fecha):
            messagebox.showerror("Error", "Fecha debe tener formato DD/MM/AAAA")
            return
        
        if not indice:
            messagebox.showerror("Error", "Ingrese el índice")
            return
        
        es_valido, mensaje = Validators.validar_indice_facpce(indice)
        if not es_valido:
            messagebox.showerror("Error", mensaje)
            return
        
        # Convertir índice con parser argentino
        indice_float = Validators.parse_decimal_argentino(indice)
        
        # Agregar al gestor
        if self.gestor_indices.agregar_indice(fecha, indice_float, observaciones):
            self.refresh_table()
            # Limpiar formulario
            self.fecha_var.set("")
            self.indice_var.set("")
            self.obs_var.set("")
            messagebox.showinfo("Éxito", f"Índice agregado correctamente\nValor: {Validators.format_decimal_argentino(indice_float, 6)}")
            self._changed()
        else:
            messagebox.showerror("Error", "Error agregando el índice")
    
    def eliminar_indice(self):
        """Elimina el índice seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un índice para eliminar")
            return
        
        item = selection[0]
        fecha = self.tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar índice del {fecha}?"):
            # Buscar clave
            from datetime import datetime
            try:
                fecha_obj = datetime.strptime(fecha, '%d/%m/%Y')
                key = f"{fecha_obj.month:02d}/{fecha_obj.year}"
                
                if key in self.gestor_indices.indices:
                    del self.gestor_indices.indices[key]
                    self.refresh_table()
                    messagebox.showinfo("Éxito", "Índice eliminado")
                    self._changed()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el índice")
            except ValueError:
                messagebox.showerror("Error", "Error procesando la fecha")
    
    def on_item_double_click(self, event):
        """Maneja doble click en la tabla"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            
            # Cargar datos en formulario
            self.fecha_var.set(values[0])
            # Convertir índice de formato argentino a entrada
            indice_valor = values[1].replace('.', '').replace(',', '.')  # Normalizar primero
            try:
                indice_float = float(indice_valor)
                self.indice_var.set(Validators.format_decimal_argentino(indice_float, 6))
            except:
                self.indice_var.set(values[1])
            self.obs_var.set(values[2])
    
    def importar_csv(self):
        """Importa índices desde CSV"""
        file_path = filedialog.askopenfilename(
            title="Importar Índices CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        count, error = self.gestor_indices.cargar_desde_csv(file_path)
        
        if error:
            messagebox.showerror("Error", f"Error importando CSV: {error}")
        else:
            self.refresh_table()
            messagebox.showinfo("Éxito", f"{count} índices importados correctamente\n\nFormato detectado automáticamente (CSV con ; o ,)")
            if count:
                self._changed()
    
    def exportar_csv(self):
        """Exporta índices a CSV"""
        file_path = filedialog.asksaveasfilename(
            title="Exportar Índices CSV",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        success, error = self.gestor_indices.exportar_a_csv(file_path)
        
        if error:
            messagebox.showerror("Error", f"Error exportando CSV: {error}")
        else:
            messagebox.showinfo("Éxito", f"Índices exportados a {file_path}\n\nFormato: CSV con punto y coma (;) y decimales argentinos")
    
    def crear_template(self):
        """Crea un template CSV de ejemplo"""
        file_path = filedialog.asksaveasfilename(
            title="Crear Template de Índices",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file, delimiter=';')
                csv_writer.writerow(['Fecha', 'Indice', 'Observaciones'])
                
                # Ejemplos con formato argentino
                csv_writer.writerow(['31/12/2023', '1.234.567,890123', 'Diciembre 2023'])
                csv_writer.writerow(['31/01/2024', '1.267.890,123456', 'Enero 2024'])
                csv_writer.writerow(['29/02/2024', '1.301.234,567890', 'Febrero 2024'])
                csv_writer.writerow(['31/03/2024', '1.335.678,901234', 'Marzo 2024'])
            
            messagebox.showinfo("Éxito", f"Template creado en {file_path}\n\nEditelo con los índices reales de FACPCE")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando template: {str(e)}")
    
    def refresh_table(self):
        """Actualiza la tabla de índices"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar índices ordenados
        indices = self.gestor_indices.get_todos_indices()
        
        for indice in indices:
            self.tree.insert('', 'end', values=(
                indice.fecha,
                Validators.format_decimal_argentino(indice.indice, 6),
                indice.observaciones,
                indice.fecha_carga
            ))
    
    def abrir_link_facpce(self):
        """Abre el link de FACPCE en el navegador"""
        webbrowser.open('https://www.facpce.org.ar/indices-facpce/')
