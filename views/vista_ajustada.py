import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from utils.validators import Validators

class VistaAjustada:
    def __init__(self, parent_app, bienes, ejercicio_actual, ejercicio_anterior, 
                 amort_calculator, inflacion_calculator):
        self.parent_app = parent_app
        self.bienes = bienes
        self.ejercicio_actual = ejercicio_actual
        self.ejercicio_anterior = ejercicio_anterior
        self.amort_calculator = amort_calculator
        self.inflacion_calculator = inflacion_calculator
        
        self.window = None
        self.tree = None
        self.status_var = None
        self.is_calculating = False
        
        self.create_window()
    
    def create_window(self):
        """Crea la ventana de vista ajustada"""
        self.window = tk.Toplevel()
        self.window.title("Vista Ajustada por Inflación FACPCE")
        self.window.geometry("1600x800")
        if hasattr(self.parent_app, 'root'):
            self.window.transient(self.parent_app.root)
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="Valores Ajustados por Inflación FACPCE", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Información de ejercicios
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Ejercicio Actual: {self.ejercicio_actual}", 
                 font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 20))
        ttk.Label(info_frame, text=f"Ejercicio Anterior: {self.ejercicio_anterior}", 
                 font=('Arial', 10, 'bold')).pack(side='left')
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        self.calcular_btn = ttk.Button(button_frame, text="🔄 Calcular Ajustes", 
                                     command=self.calcular_ajustes)
        self.calcular_btn.pack(side='left', padx=(0, 10))
        
        self.export_btn = ttk.Button(button_frame, text="📊 Exportar CSV", 
                                   command=self.export_csv, state='disabled')
        self.export_btn.pack(side='left', padx=(0, 10))
        
        self.indices_btn = ttk.Button(button_frame, text="📈 Gestionar Índices FACPCE", 
                                    command=self.abrir_gestion_indices)
        self.indices_btn.pack(side='left')
        
        # Tabla
        self.setup_table(main_frame)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para calcular ajustes")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                             relief='sunken', anchor='w')
        status_bar.pack(fill='x', side='bottom')
        
        # Protocolo de cierre
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_table(self, parent):
        """Configura la tabla de valores ajustados"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)

        # Columnas para vista ajustada
        columns = (
            'ID', 'Descripción', 'Tipo de Bien', 'F.Ingreso',
            'Valor Origen Histórico', 'V.O. Ajust. Anterior', 'V.O. Ajust. Actual',
            'Ajuste Infl. V.O.', 'Amort.Inicio Ajust.Ant.', 'Amort.Inicio Ajust.Act.',
            'Ajuste Infl. Amort.Inicio', 'Amort.Ejercicio Ajust.',
            'Amort.Acum. Cierre Ajust.', 'Valor Residual Ajustado'
        )
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        column_widths = {
            'ID': 50, 'Descripción': 150, 'Tipo de Bien': 120,
            'F.Ingreso': 80, 'Valor Origen Histórico': 120,
            'V.O. Ajust. Anterior': 120, 'V.O. Ajust. Actual': 120,
            'Ajuste Infl. V.O.': 110, 'Amort.Inicio Ajust.Ant.': 130,
            'Amort.Inicio Ajust.Act.': 130, 'Ajuste Infl. Amort.Inicio': 140,
            'Amort.Ejercicio Ajust.': 130, 'Amort.Acum. Cierre Ajust.': 140,
            'Valor Residual Ajustado': 140
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
    
    def calcular_ajustes(self):
        """Calcula los ajustes por inflación en hilo separado"""
        if self.is_calculating:
            return
        
        self.is_calculating = True
        self.calcular_btn.config(state='disabled')
        self.status_var.set("Calculando ajustes por inflación...")
        
        # Ejecutar cálculo en hilo separado
        thread = threading.Thread(target=self._calcular_ajustes_thread)
        thread.daemon = True
        thread.start()
    
    def _calcular_ajustes_thread(self):
        """Hilo para calcular ajustes"""
        try:
            # Primero calcular amortizaciones históricas
            amortizaciones = self.amort_calculator.calcular_amortizaciones_lote(
                list(self.bienes.values()), self.ejercicio_actual)
            
            # Luego calcular ajustes por inflación
            inflaciones = self.inflacion_calculator.calcular_inflacion_lote(
                list(self.bienes.values()), self.ejercicio_actual, 
                self.ejercicio_anterior, amortizaciones)
            
            # Actualizar interfaz en hilo principal
            self.window.after(0, self._actualizar_tabla, inflaciones, amortizaciones)
            
        except Exception as e:
            self.window.after(0, self._mostrar_error, str(e))
    
    def _actualizar_tabla(self, inflaciones, amortizaciones):
        """Actualiza la tabla con los resultados"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Procesar resultados
        errores_indices = []
        bienes_procesados = 0
        
        for bien_id, bien in self.bienes.items():
            inflacion_data = inflaciones.get(bien_id, {})
            
            if inflacion_data.get('error', False):
                errores_indices.append(inflacion_data)
                continue
            
            # Guardar datos en el bien para exportación
            bien.inflacion_data = inflacion_data
            
            values = (
                bien.id,
                bien.descripcion,
                bien.tipo_bien,
                bien.fecha_ingreso,
                Validators.format_decimal_argentino(inflacion_data.get('valor_origen_historico', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('vo_ajustado_anterior', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('vo_ajustado_actual', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('ajuste_infl_vo_ejercicio', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('amort_acum_inicio_ajustada_anterior', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('amort_acum_inicio_ajustada_actual', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('ajuste_infl_amort_inicio_ejercicio', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('amort_ejercicio_ajustada', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('amort_acum_cierre_ajustada', 0)),
                Validators.format_decimal_argentino(inflacion_data.get('valor_residual_ajustado', 0))
            )
            
            self.tree.insert('', 'end', values=values)
            bienes_procesados += 1
        
        # Manejar errores de índices faltantes
        if errores_indices:
            self._manejar_errores_indices(errores_indices)
        
        # Actualizar estado
        self.is_calculating = False
        self.calcular_btn.config(state='normal')
        self.export_btn.config(state='normal' if bienes_procesados > 0 else 'disabled')
        self.status_var.set(f"✅ {bienes_procesados} bienes procesados. "
                          f"{len(errores_indices)} errores por índices faltantes.")
    
    def _manejar_errores_indices(self, errores):
        """Maneja errores de índices faltantes"""
        fechas_faltantes = set()
        for error in errores:
            fechas_faltantes.update(error.get('fechas_faltantes', []))
        
        if fechas_faltantes:
            mensaje = f"Faltan índices FACPCE para las siguientes fechas:\n"
            mensaje += "\n".join(sorted(fechas_faltantes))
            mensaje += f"\n\nPuede encontrar los índices en:\n{errores[0].get('link_facpce', '')}"
            
            self.window.after(0, messagebox.showwarning, "Índices Faltantes", mensaje)
    
    def _mostrar_error(self, error_msg):
        """Muestra error en hilo principal"""
        self.is_calculating = False
        self.calcular_btn.config(state='normal')
        self.status_var.set(f"❌ Error: {error_msg}")
        messagebox.showerror("Error", f"Error calculando ajustes: {error_msg}")
    
    def abrir_gestion_indices(self):
        """Abre ventana de gestión de índices"""
        from views.gestion_indices import GestionIndices
        GestionIndices(self.parent_app.gestor_indices, self.window)
    
    def export_csv(self):
        """Exporta vista ajustada a CSV con formato argentino"""
        file_path = filedialog.asksaveasfilename(
            title="Exportar Vista Ajustada",
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            bienes_con_inflacion = [bien for bien in self.bienes.values() 
                                  if hasattr(bien, 'inflacion_data') and bien.inflacion_data]
            
            self.parent_app.csv_handler.export_to_file(
                bienes_con_inflacion, file_path, include_inflacion=True)
            
            self.status_var.set(f"✅ Vista ajustada exportada a {file_path}")
            messagebox.showinfo("Éxito", f"Vista ajustada exportada correctamente\n\nFormato: CSV con punto y coma (;) y decimales argentinos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando: {str(e)}")
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        if self.is_calculating:
            if messagebox.askokcancel("Calculando", "¿Cancelar cálculo en progreso?"):
                self.window.destroy()
        else:
            self.window.destroy()
