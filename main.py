import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path
from datetime import datetime

# Importar todos los módulos
from models.bien import Bien
from models.empresa import EmpresaData
from models.indice_facpce import GestorIndicesFACPCE
from utils.validators import Validators
from utils.csv_handler import CsvHandler
from modules.amortizaciones import AmortizacionCalculator
from modules.filtros import FiltroEjercicio
from modules.inflacion_calculator import InflacionCalculator
from views.vista_ajustada import VistaAjustada
from views.gestion_indices import GestionIndices
from db.duck import connect as duck_connect, init_schema as duck_init, save_company_state, load_by_cuit

class AmortizacionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Amortización con Ajuste por Inflación FACPCE + Decimales Argentinos")
        self.root.geometry("1800x900")
        
        # Datos principales
        self.empresa = EmpresaData()
        self.tipos_bienes = []
        self.bienes = {}
        self.next_id = 1
        self.tipos_configurados = False
        
        # Gestores e calculadoras
        self.csv_handler = CsvHandler()
        self.amort_calculator = AmortizacionCalculator()
        self.filtro_ejercicio = FiltroEjercicio()
        self.gestor_indices = GestorIndicesFACPCE()
        self.inflacion_calculator = InflacionCalculator(self.gestor_indices)
        
        # Variables de UI
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self.on_filter_change)
        
        self.ejercicio_liquidacion_var = tk.StringVar()
        self.ejercicio_liquidacion_var.trace('w', self.on_ejercicio_change)
        
        # Ventanas adicionales
        self.vista_ajustada_window = None
        self.db_con = None
        self.db_path = "data/cartera.duckdb"
        self._dirty = False
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_welcome()
        
    def setup_ui(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Panel izquierdo para datos de empresa
        self.empresa_frame = ttk.LabelFrame(self.main_frame, text="Datos de la Empresa", 
                                          padding="10")
        self.empresa_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.N, tk.S), 
                               padx=(0, 10))
        
        # Panel derecho para contenido principal
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=0, column=1, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(2, weight=1)
        
        self.setup_empresa_panel()
        self.setup_main_content()
        self.toggle_main_content(False)
        self.root.after(150, self.focus_cuit_entry)
    
    def setup_empresa_panel(self):
        # Variables para datos de empresa
        self.razon_var = tk.StringVar()
        self.cuit_var = tk.StringVar()
        self.inicio_var = tk.StringVar()
        self.cierre_var = tk.StringVar()
        self.ejercicio_anterior_var = tk.StringVar()
        
        self.empresa_frame.columnconfigure(0, weight=1)
        self.empresa_frame.columnconfigure(1, weight=0)

        row = 0
        ttk.Label(self.empresa_frame, text="Razón Social:").grid(row=row, column=0, 
                                                                sticky='w', pady=2)
        self.razon_entry = ttk.Entry(self.empresa_frame, textvariable=self.razon_var, 
                                    width=25)
        self.razon_entry.grid(row=row+1, column=0, sticky='ew', pady=(0, 10))
        
        row += 2
        ttk.Label(self.empresa_frame, text="C.U.I.T.:").grid(row=row, column=0, 
                                                            sticky='w', pady=2)
        self.cuit_entry = ttk.Entry(self.empresa_frame, textvariable=self.cuit_var, 
                                   width=25)
        self.cuit_entry.grid(row=row+1, column=0, sticky='ew', pady=(0, 10))
        self.lookup_btn = ttk.Button(self.empresa_frame, text="🔎 Consultar bienes", 
                                     command=self.lookup_by_cuit)
        self.lookup_btn.grid(row=row+1, column=1, padx=(8, 0), sticky='e')
        
        row += 2
        ttk.Label(self.empresa_frame, text="Fecha Inicio Ejercicio:").grid(row=row, column=0, 
                                                                          sticky='w', pady=2)
        self.inicio_entry = ttk.Entry(self.empresa_frame, textvariable=self.inicio_var, 
                                     width=25)
        self.inicio_entry.grid(row=row+1, column=0, sticky='ew', pady=(0, 10))
        
        row += 2
        ttk.Label(self.empresa_frame, text="Fecha Cierre Ejercicio:").grid(row=row, column=0, 
                                                                          sticky='w', pady=2)
        self.cierre_entry = ttk.Entry(self.empresa_frame, textvariable=self.cierre_var, 
                                     width=25)
        self.cierre_entry.grid(row=row+1, column=0, sticky='ew', pady=(0, 10))
        
        # Ejercicio Anterior
        row += 2
        ttk.Label(self.empresa_frame, text="Ejercicio Anterior:").grid(row=row, column=0, 
                                                                      sticky='w', pady=2)
        self.ejercicio_anterior_entry = ttk.Entry(self.empresa_frame, 
                                                 textvariable=self.ejercicio_anterior_var, 
                                                 width=25)
        self.ejercicio_anterior_entry.grid(row=row+1, column=0, sticky='ew', pady=(0, 10))
        
        self.confirm_empresa_btn = ttk.Button(self.empresa_frame, 
                                            text="✅ Confirmar Datos", 
                                            command=self.confirm_empresa_data)
        self.confirm_empresa_btn.grid(row=row+2, column=0, pady=10, sticky='ew')
        
        self.config_tipos_btn = ttk.Button(self.empresa_frame, 
                                         text="⚙️ Configurar Tipos de Bienes", 
                                         command=self.show_tipos_config)
        self.config_tipos_btn.grid(row=row+3, column=0, pady=5, sticky='ew')
        
        # Botón gestión de índices
        self.indices_btn = ttk.Button(self.empresa_frame, 
                                     text="📈 Gestionar Índices FACPCE", 
                                     command=self.abrir_gestion_indices)
        self.indices_btn.grid(row=row+4, column=0, pady=5, sticky='ew')
        
        # Botón crear template CSV
        self.template_btn = ttk.Button(self.empresa_frame, 
                                     text="📋 Crear Template CSV", 
                                     command=self.crear_template_csv)
        self.template_btn.grid(row=row+5, column=0, pady=5, sticky='ew')
        
        self.estado_frame = ttk.LabelFrame(self.empresa_frame, text="Estado", padding="5")
        self.estado_frame.grid(row=row+6, column=0, pady=10, sticky='ew')
        
        self.estado_empresa = ttk.Label(self.estado_frame, text="❌ Pendiente", 
                                      foreground='red')
        self.estado_empresa.grid(row=0, column=0, sticky='w')
        
        self.estado_tipos = ttk.Label(self.estado_frame, text="❌ Pendiente", 
                                    foreground='red')
        self.estado_tipos.grid(row=1, column=0, sticky='w')
        
        # Trace para validación en tiempo real
        for var in [self.razon_var, self.cuit_var, self.inicio_var, 
                   self.cierre_var, self.ejercicio_anterior_var]:
            var.trace('w', self.validate_empresa_data)

        self.confirm_empresa_btn.config(state='disabled')
    
    def setup_main_content(self):
        self.title_label = ttk.Label(
            self.content_frame,
            text="Sistema de Ajuste por Inflación FACPCE",
            font=('Arial', 16, 'bold')
        )
        self.title_label.grid(row=0, column=0, pady=(0, 10), sticky='w')

        self.toolbar_frame = ttk.Frame(self.content_frame)
        self.toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.toolbar_frame.columnconfigure(13, weight=1)

        # Botones existentes
        self.new_btn = ttk.Button(self.toolbar_frame, text="➕ Nuevo Bien", command=self.new_bien)
        self.new_btn.grid(row=0, column=0, padx=(0, 5))

        self.import_btn = ttk.Button(self.toolbar_frame, text="📁 Importar CSV", command=self.import_csv)
        self.import_btn.grid(row=0, column=1, padx=5)

        self.export_btn = ttk.Button(self.toolbar_frame, text="💾 Exportar Básico", command=self.export_csv_basico)
        self.export_btn.grid(row=0, column=2, padx=5)

        self.export_full_btn = ttk.Button(
            self.toolbar_frame,
            text="📊 Exportar Completo",
            command=self.export_csv_completo
        )
        self.export_full_btn.grid(row=0, column=3, padx=5)

        self.save_db_btn = ttk.Button(self.toolbar_frame, text="🗄 Guardar DuckDB", command=self.save_to_duckdb)
        self.save_db_btn.grid(row=0, column=4, padx=5)

        self.backup_btn = ttk.Button(self.toolbar_frame, text="🛟 Backup", command=self.backup_duckdb)
        self.backup_btn.grid(row=0, column=5, padx=5)

        self.load_db_btn = ttk.Button(self.toolbar_frame, text="📂 Cargar DuckDB", command=self.load_from_duckdb)
        self.load_db_btn.grid(row=0, column=6, padx=5)

        # Botón Vista Ajustada
        self.vista_ajustada_btn = ttk.Button(
            self.toolbar_frame,
            text="🔥 Vista Ajustada",
            command=self.abrir_vista_ajustada
        )
        self.vista_ajustada_btn.grid(row=0, column=7, padx=5)

        ttk.Separator(self.toolbar_frame, orient='vertical').grid(row=0, column=8, sticky='ns', padx=10)

        ttk.Label(self.toolbar_frame, text="Ejercicio a liquidar:").grid(row=0, column=9, padx=(0, 5))
        self.ejercicio_entry = ttk.Entry(
            self.toolbar_frame,
            textvariable=self.ejercicio_liquidacion_var,
            width=12
        )
        self.ejercicio_entry.grid(row=0, column=10, padx=5)

        ttk.Separator(self.toolbar_frame, orient='vertical').grid(row=0, column=11, sticky='ns', padx=10)

        ttk.Label(self.toolbar_frame, text="Filtrar:").grid(row=0, column=12, sticky='e', padx=(0, 5))
        self.filter_entry = ttk.Entry(self.toolbar_frame, textvariable=self.filter_var, width=20)
        self.filter_entry.grid(row=0, column=13, sticky='e')

        # Tabla HISTÓRICA con formato argentino
        self.table_container = ttk.Frame(self.content_frame)
        self.table_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.table_container.columnconfigure(0, weight=1)
        self.table_container.rowconfigure(0, weight=1)

        # Título de la vista
        vista_label = ttk.Label(
            self.table_container,
            text="Vista Histórica (Valores sin ajustar - Formato: 1.234.567,89)",
            font=('Arial', 12, 'bold')
        )
        vista_label.grid(row=0, column=0, pady=(0, 10), sticky='w')

        # Columnas de la vista histórica
        columns = (
            'ID', 'Descripción', 'Tipo de Bien', 'Amortizable', 'Años',
            'Ejercicio', 'F.Ingreso', 'F.Baja', 'Valor Origen',
            'Amort. Inicio', 'Amort. Ejercicio', 'Amort. Acumulada', 'Valor Residual'
        )

        self.tree = ttk.Treeview(self.table_container, columns=columns, show='headings', height=20)
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar columnas
        column_widths = {
            'ID': 50,
            'Descripción': 180,
            'Tipo de Bien': 130,
            'Amortizable': 80,
            'Años': 50,
            'Ejercicio': 70,
            'F.Ingreso': 90,
            'F.Baja': 90,
            'Valor Origen': 120,
            'Amort. Inicio': 120,
            'Amort. Ejercicio': 120,
            'Amort. Acumulada': 130,
            'Valor Residual': 120,
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.table_container, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.table_container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))

        # Configurar grid weights
        self.table_container.rowconfigure(1, weight=1)

        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)
        
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏ Editar", command=self.edit_selected)
        self.context_menu.add_command(label="🗑 Eliminar", command=self.delete_selected)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Configure primero los datos de la empresa")
        self.status_bar = ttk.Label(self.content_frame, textvariable=self.status_var, 
                                  relief='sunken', anchor='w')
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def show_welcome(self):
        """Muestra mensaje de bienvenida con funcionalidades"""
        messagebox.showinfo("Sistema Iniciado", 
                          """Sistema de Amortización con Decimales Argentinos iniciado correctamente.

Funcionalidades incluidas:
✅ Decimales argentinos (1.234.567,89)
✅ CSV con separador punto y coma (;)
✅ Ajuste por inflación FACPCE
✅ Vista histórica y ajustada

Configure primero los datos de empresa en el panel izquierdo.""")
    
    def toggle_main_content(self, enabled):
        state = 'normal' if enabled else 'disabled'
        
        self.new_btn.config(state=state)
        self.import_btn.config(state=state)
        self.export_btn.config(state=state)
        self.export_full_btn.config(state=state)
        self.vista_ajustada_btn.config(state=state)
        self.save_db_btn.config(state=state)
        self.backup_btn.config(state=state)
        self.load_db_btn.config(state='normal')
        self.filter_entry.config(state=state)
        self.ejercicio_entry.config(state=state)
        
        if enabled:
            self.tree.configure(selectmode='extended')
        else:
            self.tree.configure(selectmode='none')

    def focus_cuit_entry(self):
        if getattr(self, 'cuit_entry', None):
            self.cuit_entry.focus_set()
            self.cuit_entry.select_range(0, tk.END)
    
    def validate_empresa_data(self, *args):
        all_filled = (self.razon_var.get().strip() and 
                     self.cuit_var.get().strip() and 
                     self.inicio_var.get().strip() and 
                     self.cierre_var.get().strip() and
                     self.ejercicio_anterior_var.get().strip())
        
        if all_filled:
            self.confirm_empresa_btn.config(state='normal')
        else:
            self.confirm_empresa_btn.config(state='disabled')
    
    def confirm_empresa_data(self):
        try:
            # Validaciones existentes
            if not Validators.validar_fecha(self.inicio_var.get().strip()):
                messagebox.showerror("Error", 
                                   "Fecha de inicio debe tener formato DD/MM/AAAA")
                return
            
            if not Validators.validar_fecha(self.cierre_var.get().strip()):
                messagebox.showerror("Error", 
                                   "Fecha de cierre debe tener formato DD/MM/AAAA")
                return
            
            # Validación ejercicio anterior
            ejercicio_anterior = self.ejercicio_anterior_var.get().strip()
            ejercicio_actual = self.cierre_var.get().strip()
            
            es_valido, mensaje = Validators.validar_ejercicio_anterior(ejercicio_anterior, ejercicio_actual)
            if not es_valido:
                messagebox.showerror("Error", mensaje)
                return
            
            if not Validators.validar_cuit(self.cuit_var.get().strip()):
                messagebox.showerror("Error", 
                                   "C.U.I.T. inválido. Verifique los 11 dígitos y el dígito verificador")
                return
            
            fecha_inicio = self.inicio_var.get().strip()
            fecha_cierre = self.cierre_var.get().strip()

            try:
                inicio_dt = datetime.strptime(fecha_inicio, '%d/%m/%Y')
                cierre_dt = datetime.strptime(fecha_cierre, '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Error", "Fechas de ejercicio inválidas")
                return

            if inicio_dt > cierre_dt:
                messagebox.showerror(
                    "Error",
                    "La fecha de inicio debe ser anterior o igual a la fecha de cierre del ejercicio"
                )
                return

            # Guardar datos
            self.empresa.razon_social = self.razon_var.get().strip()
            self.empresa.cuit = self.cuit_var.get().strip()
            self.empresa.fecha_inicio = fecha_inicio
            self.empresa.fecha_cierre = fecha_cierre
            self.empresa.ejercicio_liquidacion = self.cierre_var.get().strip()
            self.empresa.ejercicio_anterior = ejercicio_anterior
            self.empresa.configurada = True
            self._dirty = True
            
            self.ejercicio_liquidacion_var.set(self.empresa.fecha_cierre)
            
            self.estado_empresa.config(text="✅ Configurado", foreground='green')
            self.config_tipos_btn.config(state='normal')
            
            # Deshabilitar edición de empresa
            for entry in [self.razon_entry, self.cuit_entry, self.inicio_entry, 
                         self.cierre_entry, self.ejercicio_anterior_entry]:
                entry.config(state='readonly')
            
            self.confirm_empresa_btn.config(state='disabled')
            
            self.status_var.set("Empresa configurada. Configure los tipos de bienes.")
            
            messagebox.showinfo("Éxito", 
                              "Datos de empresa confirmados. Configure los tipos de bienes.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al confirmar datos: {str(e)}")
    
    def show_tipos_config(self):
        """Configuración de tipos de bienes"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Tipos de Bienes")
        config_window.geometry("600x400")
        config_window.transient(self.root)
        
        main_frame = ttk.Frame(config_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Configurar Tipos de Bienes", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Frame para entrada
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(input_frame, text="Nuevo tipo:").pack(side='left', padx=(0, 10))
        tipo_var = tk.StringVar()
        tipo_entry = ttk.Entry(input_frame, textvariable=tipo_var, width=30)
        tipo_entry.pack(side='left', padx=(0, 10))
        
        add_btn = ttk.Button(input_frame, text="➕ Agregar", 
                           command=lambda: self.add_tipo(tipo_var, tipos_listbox))
        add_btn.pack(side='left')
        
        # Listbox para tipos
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        tipos_listbox = tk.Listbox(list_frame, height=10)
        tipos_listbox.pack(side='left', fill='both', expand=True)
        
        scroll = ttk.Scrollbar(list_frame, orient='vertical', command=tipos_listbox.yview)
        tipos_listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="🗑 Eliminar Seleccionado", 
                  command=lambda: self.remove_tipo(tipos_listbox)).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="✅ Confirmar Configuración", 
                  command=lambda: self.confirm_tipos_config(config_window)).pack(side='right')
        
        # Cargar tipos existentes
        for tipo in self.tipos_bienes:
            tipos_listbox.insert('end', tipo)
        
        # Si no hay tipos, agregar algunos predeterminados
        if not self.tipos_bienes:
            tipos_default = ["Maquinaria", "Muebles y Útiles", "Rodados", "Inmuebles", "Herramientas"]
            for tipo in tipos_default:
                tipos_listbox.insert('end', tipo)
        
        self.tipos_listbox_ref = tipos_listbox
        
        # Bind Enter para agregar
        tipo_entry.bind('<Return>', lambda e: self.add_tipo(tipo_var, tipos_listbox))
        
        config_window.focus()
        tipo_entry.focus()
    
    def add_tipo(self, tipo_var, listbox):
        tipo = tipo_var.get().strip()
        if tipo and tipo not in [listbox.get(i) for i in range(listbox.size())]:
            listbox.insert('end', tipo)
            tipo_var.set("")
    
    def remove_tipo(self, listbox):
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])
    
    def confirm_tipos_config(self, window):
        listbox = self.tipos_listbox_ref
        self.tipos_bienes = [listbox.get(i) for i in range(listbox.size())]
        
        if not self.tipos_bienes:
            messagebox.showerror("Error", "Debe configurar al menos un tipo de bien")
            return
        
        self.tipos_configurados = True
        self.estado_tipos.config(text="✅ Configurado", foreground='green')
        self._dirty = True

        content_enabled = self.empresa.configurada and self.tipos_configurados
        self.toggle_main_content(content_enabled)
        if content_enabled:
            self.status_var.set("Sistema listo para usar")
        else:
            self.status_var.set("Configure primero los datos de la empresa")
        
        window.destroy()
        messagebox.showinfo("Éxito", f"Configurados {len(self.tipos_bienes)} tipos de bienes")
    
    def new_bien(self):
        """Crear nuevo bien"""
        if not self.tipos_configurados:
            messagebox.showwarning("Advertencia", "Configure primero los tipos de bienes")
            return
        
        # Ventana para nuevo bien
        bien_window = tk.Toplevel(self.root)
        bien_window.title("Nuevo Bien de Uso")
        bien_window.geometry("600x600")
        bien_window.transient(self.root)
        
        main_frame = ttk.Frame(bien_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Crear Nuevo Bien", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Variables
        desc_var = tk.StringVar()
        tipo_var = tk.StringVar()
        amort_var = tk.BooleanVar(value=True)
        anos_var = tk.StringVar(value="5")
        ejercicio_var = tk.StringVar(value="2024")
        fecha_ing_var = tk.StringVar()
        fecha_baja_var = tk.StringVar()
        valor_var = tk.StringVar()
        
        # Formulario
        form_frame = ttk.Frame(main_frame, padding=(0, 0, 0, 10))
        form_frame.pack(fill='both', expand=True)
        form_frame.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(form_frame, text="Descripción:*").grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(form_frame, textvariable=desc_var, width=40).grid(row=row, column=1, sticky='ew', padx=(10, 0))

        row += 1
        ttk.Label(form_frame, text="Tipo de Bien:*").grid(row=row, column=0, sticky='w', pady=2)
        tipo_combo = ttk.Combobox(form_frame, textvariable=tipo_var, values=self.tipos_bienes, state='readonly')
        tipo_combo.grid(row=row, column=1, sticky='ew', padx=(10, 0))

        row += 1
        ttk.Checkbutton(form_frame, text="Es amortizable", variable=amort_var).grid(
            row=row, column=0, columnspan=2, sticky='w', pady=(5, 5))

        row += 1
        ttk.Label(form_frame, text="Años de amortización:").grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(form_frame, textvariable=anos_var, width=10).grid(row=row, column=1, sticky='w', padx=(10, 0))

        row += 1
        ttk.Label(form_frame, text="Ejercicio alta:").grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(form_frame, textvariable=ejercicio_var, width=10).grid(row=row, column=1, sticky='w', padx=(10, 0))

        row += 1
        ttk.Label(form_frame, text="Fecha ingreso (DD/MM/AAAA):*").grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(form_frame, textvariable=fecha_ing_var, width=15).grid(row=row, column=1, sticky='w', padx=(10, 0))

        row += 1
        ttk.Label(form_frame, text="Fecha baja (DD/MM/AAAA):").grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(form_frame, textvariable=fecha_baja_var, width=15).grid(row=row, column=1, sticky='w', padx=(10, 0))

        row += 1
        ttk.Label(form_frame, text="Valor origen (use , para decimales):*").grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(form_frame, textvariable=valor_var, width=20).grid(row=row, column=1, sticky='w', padx=(10, 0))

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="✅ Crear Bien",
                   command=lambda: self.save_new_bien(bien_window, desc_var, tipo_var, amort_var,
                                                     anos_var, ejercicio_var, fecha_ing_var, fecha_baja_var,
                                                     valor_var)).pack(side='left', padx=(0, 10))

        ttk.Button(button_frame, text="❌ Cancelar",
                   command=bien_window.destroy).pack(side='left')
        
        bien_window.focus()
    
    def save_new_bien(self, window, desc_var, tipo_var, amort_var, anos_var, ejercicio_var,
                      fecha_ing_var, fecha_baja_var, valor_var):
        try:
            # Validaciones
            descripcion = desc_var.get().strip()
            if not descripcion:
                messagebox.showerror("Error", "La descripción es obligatoria")
                return
            
            tipo_bien = tipo_var.get()
            if not tipo_bien:
                messagebox.showerror("Error", "Seleccione un tipo de bien")
                return
            
            fecha_ingreso = fecha_ing_var.get().strip()
            if not Validators.validar_fecha(fecha_ingreso):
                messagebox.showerror("Error", "Fecha de ingreso debe tener formato DD/MM/AAAA")
                return
            
            valor_origen_str = valor_var.get().strip()
            if not valor_origen_str:
                messagebox.showerror("Error", "El valor origen es obligatorio")
                return
            
            valor_origen = Validators.parse_decimal_argentino(valor_origen_str)
            if valor_origen <= 0:
                messagebox.showerror("Error", "El valor origen debe ser mayor a cero")
                return
            
            # Campos opcionales
            es_amortizable = amort_var.get()

            anos_amortizacion_str = anos_var.get().strip()
            if anos_amortizacion_str:
                try:
                    anos_amortizacion = int(anos_amortizacion_str)
                except ValueError:
                    messagebox.showerror("Error", "Los años de amortización deben ser un número entero")
                    return
            else:
                anos_amortizacion = 5

            if es_amortizable and anos_amortizacion < 1:
                messagebox.showerror("Error", "Los años de amortización deben ser al menos 1")
                return

            ejercicio_var_str = ejercicio_var.get().strip()
            if ejercicio_var_str:
                try:
                    ejercicio_alta = int(ejercicio_var_str)
                except ValueError:
                    messagebox.showerror("Error", "Ejercicio de alta debe ser un número entero")
                    return
            else:
                ejercicio_alta = 2024
            
            fecha_baja = fecha_baja_var.get().strip() if fecha_baja_var.get().strip() else None
            if fecha_baja and not Validators.validar_fecha(fecha_baja):
                messagebox.showerror("Error", "Fecha de baja debe tener formato DD/MM/AAAA")
                return

            cierre_empresa = (self.empresa.fecha_cierre or self.cierre_var.get().strip())
            if cierre_empresa and Validators.validar_fecha(cierre_empresa):
                ingreso_dt = datetime.strptime(fecha_ingreso, '%d/%m/%Y')
                cierre_dt = datetime.strptime(cierre_empresa, '%d/%m/%Y')
                if ingreso_dt > cierre_dt:
                    messagebox.showerror(
                        "Error",
                        "La fecha de ingreso debe ser anterior o igual a la fecha de cierre del ejercicio"
                    )
                    return
            
            # Crear bien
            nuevo_bien = Bien(
                id=self.next_id,
                descripcion=descripcion,
                tipo_bien=tipo_bien,
                es_amortizable=es_amortizable,
                anos_amortizacion=anos_amortizacion,
                ejercicio_alta=ejercicio_alta,
                fecha_ingreso=fecha_ingreso,
                fecha_baja=fecha_baja,
                valor_origen=valor_origen
            )
            
            self.bienes[self.next_id] = nuevo_bien
            self.next_id += 1
            self._dirty = True
            
            self.refresh_table()
            window.destroy()
            
            messagebox.showinfo("Éxito", f"Bien '{descripcion}' creado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando bien: {str(e)}")
    
    def refresh_table(self):
        """Actualizar tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar bienes si es necesario
        bienes_mostrar = list(self.bienes.values())
        
        # Aplicar filtro de texto
        filtro_texto = self.filter_var.get().strip().lower()
        if filtro_texto:
            bienes_mostrar = [b for b in bienes_mostrar 
                            if filtro_texto in b.descripcion.lower() or 
                               filtro_texto in b.tipo_bien.lower()]
        
        # Aplicar filtro de ejercicio
        ejercicio_liquidacion = self.ejercicio_liquidacion_var.get().strip()
        if ejercicio_liquidacion and Validators.validar_fecha(ejercicio_liquidacion):
            bienes_mostrar = self.filtro_ejercicio.filtrar_bienes_por_ejercicio(
                bienes_mostrar, ejercicio_liquidacion)
        
        # Calcular amortizaciones si hay ejercicio válido
        if ejercicio_liquidacion and Validators.validar_fecha(ejercicio_liquidacion):
            amortizaciones = self.amort_calculator.calcular_amortizaciones_lote(
                bienes_mostrar, ejercicio_liquidacion)
        else:
            amortizaciones = {}
        
        # Llenar tabla
        for bien in sorted(bienes_mostrar, key=lambda x: x.id):
            amort_data = amortizaciones.get(bien.id, {})
            
            values = (
                bien.id,
                bien.descripcion,
                bien.tipo_bien,
                'SI' if bien.es_amortizable else 'NO',
                bien.anos_amortizacion,
                bien.ejercicio_alta,
                bien.fecha_ingreso,
                bien.fecha_baja or '',
                Validators.format_decimal_argentino(bien.valor_origen),
                Validators.format_decimal_argentino(amort_data.get('amort_inicio', 0)),
                Validators.format_decimal_argentino(amort_data.get('amort_ejercicio', 0)),
                Validators.format_decimal_argentino(amort_data.get('amort_acumulada', 0)),
                Validators.format_decimal_argentino(amort_data.get('valor_residual', bien.valor_origen))
            )
            
            self.tree.insert('', 'end', values=values)
        
        # Actualizar contador
        self.status_var.set(f"Mostrando {len(bienes_mostrar)} bienes de {len(self.bienes)} totales")
    
    def import_csv(self):
        """Importar CSV"""
        if not self.tipos_configurados:
            messagebox.showwarning("Advertencia", "Configure primero los tipos de bienes")
            return
        
        file_path = filedialog.askopenfilename(
            title="Importar Bienes desde CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            bienes_importados = self.csv_handler.import_from_file(file_path, self.tipos_bienes)
            
            # Agregar bienes con nuevos IDs
            for bien in bienes_importados:
                bien.id = self.next_id
                self.bienes[self.next_id] = bien
                self.next_id += 1
            
            self.refresh_table()
            if bienes_importados:
                self._dirty = True
            messagebox.showinfo("Éxito", f"{len(bienes_importados)} bienes importados correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error importando CSV: {str(e)}")
    
    def export_csv_basico(self):
        """Exportar CSV básico"""
        if not self.bienes:
            messagebox.showwarning("Advertencia", "No hay bienes para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Bienes (Básico)",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            self.csv_handler.export_to_file(list(self.bienes.values()), file_path)
            messagebox.showinfo("Éxito", f"Bienes exportados a {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando: {str(e)}")
    
    def export_csv_completo(self):
        """Exportar CSV completo con amortizaciones"""
        if not self.bienes:
            messagebox.showwarning("Advertencia", "No hay bienes para exportar")
            return
        
        if not self.ejercicio_liquidacion_var.get().strip():
            messagebox.showwarning("Advertencia", "Configure el ejercicio a liquidar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Bienes (Completo)",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            # Calcular amortizaciones
            ejercicio = self.ejercicio_liquidacion_var.get().strip()
            amortizaciones = self.amort_calculator.calcular_amortizaciones_lote(
                list(self.bienes.values()), ejercicio)
            
            # Agregar datos de amortización a los bienes
            for bien_id, bien in self.bienes.items():
                bien.amortizacion_data = amortizaciones.get(bien_id, {})
            
            self.csv_handler.export_to_file(list(self.bienes.values()), file_path, include_amortizacion=True)
            messagebox.showinfo("Éxito", f"Bienes con amortizaciones exportados a {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando: {str(e)}")
    
    def _ensure_db(self):
        if self.db_con is None:
            try:
                self.db_con = duck_connect(self.db_path)
                duck_init(self.db_con)
            except Exception as e:
                messagebox.showerror("Error de base", f"No se pudo abrir DuckDB: {e}")
                self.db_con = None
        return self.db_con is not None

    def _mark_dirty_indices(self):
        self._dirty = True

    def save_current_company(self) -> bool:
        if not self._ensure_db():
            return False

        cuit_actual = (self.empresa.cuit or "").strip()
        if not Validators.validar_cuit(cuit_actual):
            messagebox.showwarning("Falta CUIT", "Ingrese un C.U.I.T. válido antes de guardar.")
            return False

        if not self.empresa.configurada:
            messagebox.showwarning("Datos incompletos", "Confirme los datos de la empresa antes de guardar.")
            return False

        try:
            save_company_state(self.db_con, self.empresa, self.tipos_bienes, self.bienes, self.gestor_indices)
            self._dirty = False
            self.status_var.set(f"Datos guardados en {self.db_path}")
            return True
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return False

    def save_to_duckdb(self):
        if self.save_current_company():
            messagebox.showinfo("Guardado", f"Datos guardados correctamente en {self.db_path}")

    def backup_duckdb(self):
        if not self._ensure_db():
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path("backups") / f"export_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)

            destination = backup_dir.as_posix().replace("'", "''")
            self.db_con.execute(f"EXPORT DATABASE '{destination}' (FORMAT PARQUET)")

            self.status_var.set(f"Backup exportado a {backup_dir}")
            messagebox.showinfo("Backup", f"Exportado a {backup_dir}")
        except Exception as e:
            messagebox.showerror("Error de backup", str(e))

    def lookup_by_cuit(self):
        cuit = self.cuit_var.get().strip()
        if not Validators.validar_cuit(cuit):
            messagebox.showerror("CUIT inválido", "El C.U.I.T. debe contener 11 dígitos válidos.")
            return

        if not self._ensure_db():
            return

        try:
            empresa, tipos, bienes, gestor = load_by_cuit(self.db_con, cuit)

            if not empresa:
                crear = messagebox.askyesno(
                    "CUIT no encontrado",
                    "No existen datos guardados para este C.U.I.T. ¿Desea inicializar un conjunto vacío usando los datos del panel izquierdo?"
                )
                if not crear:
                    return

                self.empresa = EmpresaData()
                self.empresa.razon_social = self.razon_var.get().strip()
                self.empresa.cuit = cuit
                self.empresa.fecha_inicio = self.inicio_var.get().strip()
                self.empresa.fecha_cierre = self.cierre_var.get().strip()
                self.empresa.ejercicio_anterior = self.ejercicio_anterior_var.get().strip()
                self.empresa.ejercicio_liquidacion = self.cierre_var.get().strip()
                self.empresa.configurada = True

                self.tipos_bienes = list(self.tipos_bienes)
                self.tipos_configurados = bool(self.tipos_bienes)
                self.bienes = {}
                self.next_id = 1
                self._dirty = True

                self._hydrate_empresa_panel()

                self.estado_empresa.config(text="✅ Configurado", foreground='green')
                self.estado_tipos.config(
                    text="✅ Configurado" if self.tipos_configurados else "❌ Pendiente",
                    foreground='green' if self.tipos_configurados else 'red'
                )

                self.toggle_main_content(self.empresa.configurada and self.tipos_configurados)
                self.refresh_table()
                self.status_var.set(f"Dataset inicializado para CUIT {cuit}")
                messagebox.showinfo("Listo", "Se creó un dataset vacío para este C.U.I.T.")
                return

            self.empresa = empresa
            self.tipos_bienes = tipos
            self.bienes = bienes
            self.gestor_indices = gestor
            self.inflacion_calculator = InflacionCalculator(self.gestor_indices)
            self.next_id = (max(self.bienes.keys()) + 1) if self.bienes else 1

            if self.vista_ajustada_window and hasattr(self.vista_ajustada_window, 'window'):
                try:
                    if self.vista_ajustada_window.window.winfo_exists():
                        self.vista_ajustada_window.window.destroy()
                except Exception:
                    pass
            self.vista_ajustada_window = None

            self._hydrate_empresa_panel()

            self.tipos_configurados = bool(self.tipos_bienes)
            self.estado_tipos.config(
                text="✅ Configurado" if self.tipos_configurados else "❌ Pendiente",
                foreground='green' if self.tipos_configurados else 'red'
            )

            self.estado_empresa.config(
                text="✅ Configurado" if self.empresa.configurada else "❌ Pendiente",
                foreground='green' if self.empresa.configurada else 'red'
            )

            content_enabled = self.empresa.configurada and self.tipos_configurados
            self.toggle_main_content(content_enabled)

            self.filter_var.set("")
            self.refresh_table()
            self._dirty = False

            self.status_var.set(f"Datos cargados para el C.U.I.T. {cuit}")
            messagebox.showinfo("Carga completada", f"Se cargaron datos para el C.U.I.T. {cuit}")
        except Exception as e:
            messagebox.showerror("Error al consultar", str(e))

    def load_from_duckdb(self):
        self.lookup_by_cuit()

    def _hydrate_empresa_panel(self):
        valores = {
            'razon': self.empresa.razon_social or "",
            'cuit': self.empresa.cuit or "",
            'inicio': self.empresa.fecha_inicio or "",
            'cierre': self.empresa.fecha_cierre or "",
            'anterior': self.empresa.ejercicio_anterior or "",
        }

        self.razon_var.set(valores['razon'])
        self.cuit_var.set(valores['cuit'])
        self.inicio_var.set(valores['inicio'])
        self.cierre_var.set(valores['cierre'])
        self.ejercicio_anterior_var.set(valores['anterior'])

        cierre_liquidacion = self.empresa.ejercicio_liquidacion or self.empresa.fecha_cierre or ""
        self.ejercicio_liquidacion_var.set(cierre_liquidacion)

        self.config_tipos_btn.config(state='normal')

        entries = [
            self.razon_entry,
            self.cuit_entry,
            self.inicio_entry,
            self.cierre_entry,
            self.ejercicio_anterior_entry,
        ]

        if self.empresa.configurada:
            for entry in entries:
                entry.config(state='readonly')
            self.confirm_empresa_btn.config(state='disabled')
        else:
            for entry in entries:
                entry.config(state='normal')
            self.validate_empresa_data()
            self.focus_cuit_entry()

    def on_close(self):
        if self._dirty:
            respuesta = messagebox.askyesnocancel(
                "Cambios sin guardar",
                "¿Desea guardar los cambios en DuckDB antes de salir?"
            )
            if respuesta is None:
                return
            if respuesta:
                if not self.save_current_company():
                    return
        self.root.destroy()

    def abrir_gestion_indices(self):
        """Abre la ventana de gestión de índices FACPCE"""
        GestionIndices(self.gestor_indices, self.root, on_change=self._mark_dirty_indices)
    
    def crear_template_csv(self):
        """Crea un template CSV de ejemplo"""
        if not self.tipos_configurados:
            messagebox.showwarning("Advertencia", "Primero configure los tipos de bienes")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Crear Template CSV de Bienes",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            self.csv_handler.create_template_csv(file_path, self.tipos_bienes)
            messagebox.showinfo("Éxito", f"Template creado en {file_path}\n\n" +
                              "Formato: CSV con punto y coma (;)\n" +
                              "Decimales: formato argentino (1.234.567,89)")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando template: {str(e)}")
    
    def abrir_vista_ajustada(self):
        """Abre la vista ajustada por inflación"""
        if not self.tipos_configurados:
            messagebox.showwarning("Advertencia", "Primero configure los tipos de bienes")
            return
        
        if not self.empresa.ejercicio_anterior:
            messagebox.showwarning("Advertencia", "Configure el ejercicio anterior en los datos de empresa")
            return
        
        # Verificar si ya existe una ventana
        if self.vista_ajustada_window and hasattr(self.vista_ajustada_window, 'window') and self.vista_ajustada_window.window.winfo_exists():
            self.vista_ajustada_window.window.lift()  # Traer al frente
        else:
            # Crear nueva ventana
            self.vista_ajustada_window = VistaAjustada(
                self, 
                self.bienes.copy(),  # Pasar copia de bienes
                self.empresa.ejercicio_liquidacion,
                self.empresa.ejercicio_anterior,
                self.amort_calculator,
                self.inflacion_calculator
            )
    
    # Métodos auxiliares
    def on_filter_change(self, *args):
        self.refresh_table()
    
    def on_ejercicio_change(self, *args):
        self.refresh_table()
    
    def on_item_double_click(self, event):
        if self.tipos_configurados:
            self.edit_selected()
    
    def on_right_click(self, event):
        if not self.tipos_configurados:
            return
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def edit_selected(self):
        if not self.tipos_configurados:
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un bien para editar")
            return
        
        # Obtener ID del bien seleccionado
        item = selection[0]
        bien_id = int(self.tree.item(item)['values'][0])
        bien = self.bienes.get(bien_id)
        
        if not bien:
            messagebox.showerror("Error", "Bien no encontrado")
            return
        
        # Abrir ventana de edición (similar a nuevo bien pero con datos precargados)
        messagebox.showinfo("Funcionalidad", "Edición de bienes - Por implementar en versión completa")
    
    def delete_selected(self):
        if not self.tipos_configurados:
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un bien para eliminar")
            return
        
        item = selection[0]
        bien_id = int(self.tree.item(item)['values'][0])
        bien = self.bienes.get(bien_id)
        
        if not bien:
            messagebox.showerror("Error", "Bien no encontrado")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el bien '{bien.descripcion}'?"):
            del self.bienes[bien_id]
            self._dirty = True
            self.refresh_table()
            messagebox.showinfo("Éxito", "Bien eliminado correctamente")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AmortizacionApp()
    app.run()