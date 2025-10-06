from datetime import datetime


class Validators:
    _CUIT_WEIGHTS = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)

    @staticmethod
    def validar_fecha(fecha_str):
        try:
            datetime.strptime(fecha_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_cuit(cuit):
        if not cuit:
            return False

        cuit_clean = ''.join(ch for ch in cuit if ch.isdigit())
        if len(cuit_clean) != 11:
            return False

        try:
            digits = [int(ch) for ch in cuit_clean]
        except ValueError:
            return False

        acumulado = sum(peso * digito for peso, digito in zip(Validators._CUIT_WEIGHTS, digits[:-1]))
        resto = acumulado % 11
        verificador = 11 - resto

        if verificador == 11:
            verificador = 0
        elif verificador == 10:
            verificador = 9

        return digits[-1] == verificador
    
    @staticmethod
    def extraer_año_ejercicio(fecha_cierre):
        try:
            return datetime.strptime(fecha_cierre, '%d/%m/%Y').year
        except ValueError:
            return None
    
    @staticmethod
    def parse_decimal_argentino(value_str):
        """Convierte formato decimal argentino (1.234,56) a float"""
        if not value_str or not value_str.strip():
            return 0.0
        
        value_clean = value_str.strip().replace(' ', '')
        
        # Formato argentino completo: 1.234.567,89
        if '.' in value_clean and ',' in value_clean:
            value_clean = value_clean.replace('.', '').replace(',', '.')
        # Solo decimal: 1234,56
        elif ',' in value_clean and '.' not in value_clean:
            value_clean = value_clean.replace(',', '.')
        # Ya en formato internacional: 1234.56 (no cambiar)
        
        try:
            return float(value_clean)
        except ValueError:
            return 0.0
    
    @staticmethod
    def format_decimal_argentino(value, decimals=2):
        """Formatea número al formato argentino 1.234.567,89"""
        if value is None:
            return "0,00"
        
        try:
            # Formatear con separadores
            formatted = f"{value:,.{decimals}f}"
            # Intercambiar puntos y comas para formato argentino
            return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return str(value)
    
    @staticmethod
    def validar_indice_facpce(indice_str):
        """Valida índice FACPCE con formato argentino"""
        try:
            indice = Validators.parse_decimal_argentino(indice_str)
            if indice <= 0:
                return False, "El índice debe ser mayor a cero"
            return True, ""
        except:
            return False, "El índice debe ser un número válido (use coma para decimales)"
    
    @staticmethod
    def validar_ejercicio_anterior(ejercicio_anterior, ejercicio_actual):
        """Valida que el ejercicio anterior sea anterior al actual"""
        if not Validators.validar_fecha(ejercicio_anterior):
            return False, "Ejercicio anterior debe tener formato DD/MM/AAAA"
        
        if not Validators.validar_fecha(ejercicio_actual):
            return False, "Ejercicio actual debe tener formato DD/MM/AAAA"
        
        try:
            fecha_anterior = datetime.strptime(ejercicio_anterior, '%d/%m/%Y')
            fecha_actual = datetime.strptime(ejercicio_actual, '%d/%m/%Y')
            
            if fecha_anterior >= fecha_actual:
                return False, "Ejercicio anterior debe ser anterior al actual"
            
            return True, ""
        except ValueError:
            return False, "Error validando ejercicios"
    
    @staticmethod
    def validar_decimal_positivo(value_str, nombre_campo="valor"):
        """Valida que un string sea un decimal positivo válido"""
        try:
            valor = Validators.parse_decimal_argentino(value_str)
            if valor < 0:
                return False, f"El {nombre_campo} no puede ser negativo"
            return True, ""
        except:
            return False, f"El {nombre_campo} debe ser un número válido"
