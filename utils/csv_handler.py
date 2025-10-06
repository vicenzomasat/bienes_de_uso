import csv
from models.bien import Bien
from utils.validators import Validators

class CsvHandler:
    def __init__(self):
        # Usar punto y coma como separador estándar para evitar conflictos con decimales
        self.csv_delimiter = ';'
    
    def import_from_file(self, file_path, tipos_bienes):
        """Importa bienes desde CSV (histórico). Ignora columnas extra como fecha diferida."""
        bienes = []
        errores = []
        
        try:
            # Intentar diferentes encodings
            encodings = ['utf-8', 'latin1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        # Auto-detectar separador (priorizar punto y coma)
                        sample = file.read(1024)
                        file.seek(0)
                        
                        delimiter = ';' if ';' in sample else ','
                        
                        csv_reader = csv.reader(file, delimiter=delimiter)
                        
                        for row_num, row in enumerate(csv_reader, 1):
                            try:
                                if len(row) >= 9:  # Mínimo requerido
                                    # Campos básicos
                                    id_bien = int(row[0].strip()) if row[0].strip() else row_num
                                    descripcion = row[1].strip()
                                    tipo_bien = row[2].strip()
                                    
                                    if not descripcion:
                                        errores.append(f"Fila {row_num}: Descripción vacía")
                                        continue
                                    
                                    if tipo_bien not in tipos_bienes:
                                        errores.append(f"Fila {row_num}: Tipo '{tipo_bien}' no válido")
                                        continue
                                    
                                    # Campos boolean/int
                                    es_amortizable = row[3].upper().strip() in ['SI', 'SÍ', 'S', 'YES', 'Y', '1']
                                    anos_amortizacion = int(row[4].strip()) if row[4].strip() else 5
                                    ejercicio_alta = int(row[5].strip()) if row[5].strip() else 2024
                                    
                                    # Fechas
                                    fecha_ingreso = row[6].strip()
                                    fecha_baja = row[7].strip() if row[7].strip() else None
                                    
                                    # DECIMALES CON FORMATO ARGENTINO
                                    valor_origen = Validators.parse_decimal_argentino(row[8])

                                    # Crear bien solo con datos históricos
                                    bien = Bien(
                                        id=id_bien,
                                        descripcion=descripcion,
                                        tipo_bien=tipo_bien,
                                        es_amortizable=es_amortizable,
                                        anos_amortizacion=anos_amortizacion,
                                        ejercicio_alta=ejercicio_alta,
                                        fecha_ingreso=fecha_ingreso,
                                        fecha_baja=fecha_baja,
                                        valor_origen=valor_origen
                                    )
                                    
                                    bienes.append(bien)
                                
                                else:
                                    errores.append(f"Fila {row_num}: Faltan columnas (mínimo 9)")
                            
                            except (ValueError, IndexError) as e:
                                errores.append(f"Fila {row_num}: Error - {str(e)}")
                                continue
                    
                    break  # Encoding exitoso
                    
                except UnicodeDecodeError:
                    if encoding == encodings[-1]:
                        raise Exception("No se pudo leer el archivo con ningún encoding")
                    continue
            
            # Reportar errores si existen pero no bloquear
            if errores:
                print(f"Advertencias en importación: {len(errores)} filas con errores")
            
            return bienes
            
        except Exception as e:
            raise Exception(f"Error importando CSV: {str(e)}")
    
    def export_to_file(self, bienes, file_path, include_amortizacion=False, include_inflacion=False):
        """Exporta a CSV con separador punto y coma y formato argentino"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file, delimiter=self.csv_delimiter)
                
                # Encabezados
                if include_inflacion:
                    headers = [
                        'ID', 'Descripción', 'TipoBien', 'F.Ingreso',
                        'Valor_Origen_Historico', 'VO_Ajustado_Anterior', 'VO_Ajustado_Actual',
                        'Ajuste_Infl_VO', 'Amort_Inicio_Ajust_Ant', 'Amort_Inicio_Ajust_Act',
                        'Ajuste_Infl_Amort_Inicio', 'Amort_Ejercicio_Ajust', 
                        'Amort_Acum_Cierre_Ajust', 'Valor_Residual_Ajustado'
                    ]
                elif include_amortizacion:
                    headers = [
                        'ID', 'Descripción', 'TipoBien', 'Amortizable', 'Años',
                        'Ejercicio', 'FechaIngreso', 'FechaBaja', 'ValorOrigen',
                        'AmortizacionInicio', 'AmortizacionEjercicio', 
                        'AmortizacionAcumulada', 'ValorResidual'
                    ]
                else:
                    headers = [
                        'ID', 'Descripción', 'TipoBien', 'Amortizable', 'Años',
                        'Ejercicio', 'FechaIngreso', 'FechaBaja', 'ValorOrigen'
                    ]
                
                csv_writer.writerow(headers)
                
                # Datos con formato argentino
                bienes_ordenados = sorted(bienes, key=lambda x: x.id)
                for bien in bienes_ordenados:
                    if include_inflacion and hasattr(bien, 'inflacion_data'):
                        data = bien.inflacion_data
                        row = [
                            bien.id, bien.descripcion, bien.tipo_bien,
                            bien.fecha_ingreso,
                            Validators.format_decimal_argentino(data.get('valor_origen_historico', 0)),
                            Validators.format_decimal_argentino(data.get('vo_ajustado_anterior', 0)),
                            Validators.format_decimal_argentino(data.get('vo_ajustado_actual', 0)),
                            Validators.format_decimal_argentino(data.get('ajuste_infl_vo_ejercicio', 0)),
                            Validators.format_decimal_argentino(data.get('amort_acum_inicio_ajustada_anterior', 0)),
                            Validators.format_decimal_argentino(data.get('amort_acum_inicio_ajustada_actual', 0)),
                            Validators.format_decimal_argentino(data.get('ajuste_infl_amort_inicio_ejercicio', 0)),
                            Validators.format_decimal_argentino(data.get('amort_ejercicio_ajustada', 0)),
                            Validators.format_decimal_argentino(data.get('amort_acum_cierre_ajustada', 0)),
                            Validators.format_decimal_argentino(data.get('valor_residual_ajustado', 0))
                        ]
                    else:
                        # Datos básicos o con amortización
                        row = [
                            bien.id, bien.descripcion, bien.tipo_bien,
                            'SI' if bien.es_amortizable else 'NO',
                            bien.anos_amortizacion, bien.ejercicio_alta,
                            bien.fecha_ingreso, bien.fecha_baja or '',
                            Validators.format_decimal_argentino(bien.valor_origen)
                        ]
                        
                        if include_amortizacion and hasattr(bien, 'amortizacion_data'):
                            row.extend([
                                Validators.format_decimal_argentino(bien.amortizacion_data['amort_inicio']),
                                Validators.format_decimal_argentino(bien.amortizacion_data['amort_ejercicio']),
                                Validators.format_decimal_argentino(bien.amortizacion_data['amort_acumulada']),
                                Validators.format_decimal_argentino(bien.amortizacion_data['valor_residual'])
                            ])
                    
                    csv_writer.writerow(row)
            
        except Exception as e:
            raise Exception(f"Error escribiendo CSV: {str(e)}")
    
    def create_template_csv(self, file_path, tipos_bienes):
        """Crea un archivo CSV de ejemplo con el formato correcto"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file, delimiter=self.csv_delimiter)
                
                # Encabezados
                csv_writer.writerow([
                    'ID', 'Descripción', 'TipoBien', 'Amortizable', 'Años',
                    'Ejercicio', 'FechaIngreso', 'FechaBaja', 'ValorOrigen'
                ])
                
                # Ejemplos con formato argentino
                primer_tipo = tipos_bienes[0] if tipos_bienes else "Maquinaria"
                csv_writer.writerow([
                    '1', 'Ejemplo Máquina Industrial', primer_tipo, 'SI', '10',
                    '2020', '15/03/2020', '', '1.250.000,00'
                ])
        
        except Exception as e:
            raise Exception(f"Error creando template: {str(e)}")
