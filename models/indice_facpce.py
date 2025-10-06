from datetime import datetime

class IndiceFACPCE:
    def __init__(self, fecha, indice, observaciones=""):
        self.fecha = fecha  # formato DD/MM/AAAA
        self.indice = float(indice)
        self.observaciones = observaciones
        self.fecha_carga = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def get_mes_año_key(self):
        """Retorna clave MM/AAAA para búsquedas"""
        try:
            fecha_obj = datetime.strptime(self.fecha, '%d/%m/%Y')
            return f"{fecha_obj.month:02d}/{fecha_obj.year}"
        except ValueError:
            return None
    
    def get_año(self):
        """Retorna el año del índice"""
        try:
            fecha_obj = datetime.strptime(self.fecha, '%d/%m/%Y')
            return fecha_obj.year
        except ValueError:
            return None
    
    def to_dict(self):
        return {
            'fecha': self.fecha,
            'indice': self.indice,
            'observaciones': self.observaciones,
            'fecha_carga': self.fecha_carga
        }
    
    # Métodos preparados para SQLite
    def to_sql_dict(self):
        return {
            'fecha': self.fecha,
            'indice': self.indice,
            'observaciones': self.observaciones,
            'fecha_carga': self.fecha_carga
        }
    
    @classmethod
    def from_sql_dict(cls, data):
        indice = cls(data['fecha'], data['indice'], data['observaciones'])
        indice.fecha_carga = data['fecha_carga']
        return indice

class GestorIndicesFACPCE:
    def __init__(self):
        self.indices = {}  # Key: "MM/AAAA", Value: IndiceFACPCE
    
    def agregar_indice(self, fecha, indice, observaciones=""):
        """Agrega un índice FACPCE"""
        indice_obj = IndiceFACPCE(fecha, indice, observaciones)
        key = indice_obj.get_mes_año_key()
        if key:
            self.indices[key] = indice_obj
            return True
        return False
    
    def get_indice(self, fecha_str):
        """Obtiene índice para una fecha específica (DD/MM/AAAA)"""
        try:
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            key = f"{fecha_obj.month:02d}/{fecha_obj.year}"
            return self.indices.get(key)
        except ValueError:
            return None
    
    def get_coeficiente(self, fecha_origen, fecha_destino):
        """Calcula coeficiente entre dos fechas"""
        indice_origen = self.get_indice(fecha_origen)
        indice_destino = self.get_indice(fecha_destino)
        
        if not indice_origen or not indice_destino:
            return None, f"Falta índice para {fecha_origen if not indice_origen else fecha_destino}"
        
        if indice_origen.indice == 0:
            return None, f"Índice origen es cero para {fecha_origen}"
        
        coeficiente = indice_destino.indice / indice_origen.indice
        return coeficiente, None
    
    def get_fechas_faltantes(self, fechas_necesarias):
        """Identifica qué fechas no tienen índices"""
        faltantes = []
        for fecha in fechas_necesarias:
            if not self.get_indice(fecha):
                faltantes.append(fecha)
        return faltantes
    
    def cargar_desde_csv(self, archivo_csv):
        """Carga índices desde archivo CSV con separador punto y coma"""
        import csv
        from utils.validators import Validators
        
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as file:
                # Detectar separador automáticamente
                sample = file.read(1024)
                file.seek(0)
                delimiter = ';' if ';' in sample else ','
                
                csv_reader = csv.reader(file, delimiter=delimiter)
                count = 0
                for row in csv_reader:
                    if len(row) >= 2:
                        fecha = row[0].strip()
                        indice_str = row[1].strip()
                        observaciones = row[2].strip() if len(row) > 2 else ""
                        
                        # Usar parser decimal argentino
                        indice_float = Validators.parse_decimal_argentino(indice_str)
                        
                        if self.agregar_indice(fecha, indice_float, observaciones):
                            count += 1
                return count, None
        except Exception as e:
            return 0, str(e)
    
    def exportar_a_csv(self, archivo_csv):
        """Exporta índices a archivo CSV con formato argentino"""
        import csv
        from utils.validators import Validators
        
        try:
            with open(archivo_csv, 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file, delimiter=';')  # Usar punto y coma
                csv_writer.writerow(['Fecha', 'Indice', 'Observaciones', 'Fecha_Carga'])
                
                # Ordenar por fecha
                indices_ordenados = sorted(self.indices.values(), 
                                         key=lambda x: datetime.strptime(x.fecha, '%d/%m/%Y'))
                
                for indice in indices_ordenados:
                    csv_writer.writerow([
                        indice.fecha, 
                        Validators.format_decimal_argentino(indice.indice, 6),  # 6 decimales para índices
                        indice.observaciones, 
                        indice.fecha_carga
                    ])
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_todos_indices(self):
        """Retorna todos los índices ordenados por fecha"""
        return sorted(self.indices.values(), 
                     key=lambda x: datetime.strptime(x.fecha, '%d/%m/%Y'))
