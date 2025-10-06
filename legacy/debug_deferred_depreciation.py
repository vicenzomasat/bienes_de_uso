#!/usr/bin/env python3
"""
Debug script for deferred date depreciation calculations
Run this from the project root directory (where main.py is located)
"""

import sys
from datetime import datetime

# Import project modules
from models.bien import Bien
from models.empresa import EmpresaData
from models.indice_facpce import GestorIndicesFACPCE
from modules.amortizaciones import AmortizacionCalculator
from modules.inflacion_calculator import InflacionCalculator
from utils.validators import Validators

def create_test_asset_with_deferred_date():
    """Create a test asset similar to the example provided"""
    # Based on the example showing:
    # - Value at previous period (31/12/2023): 1,256,925.44
    # - Depreciation at previous period: 1,005,540.35
    # - Should have 5 periods remaining
    
    # We'll assume this is a 10-year asset acquired in 2018
    # with deferred date at 31/12/2022
    test_bien = Bien(
        id=1,
        descripcion="TEST ASSET - DEFERRED DATE",
        tipo_bien="Maquinaria",
        es_amortizable=True,
        anos_amortizacion=10,  # 10 years total
        ejercicio_alta=2018,    # Acquired in 2018
        fecha_ingreso="01/01/2018",
        fecha_baja=None,
        valor_origen=2000000.00,  # 2 million original value
        fecha_diferida="31/12/2022",  # Deferred date after 5 years
        valor_fecha_diferida=1256925.44,  # Value at deferred date
        amort_acum_fecha_diferida=1005540.35  # Accumulated depreciation at deferred date
    )
    return test_bien

def debug_depreciation_calculation(bien, ejercicio_liquidacion):
    """Debug the depreciation calculation step by step"""
    print("\n" + "="*70)
    print("DEPRECIATION CALCULATION DEBUG")
    print("="*70)
    
    print(f"\nAsset Details:")
    print(f"  Description: {bien.descripcion}")
    print(f"  Original Value: {Validators.format_decimal_argentino(bien.valor_origen)}")
    print(f"  Acquisition Year: {bien.ejercicio_alta}")
    print(f"  Total Depreciation Years: {bien.anos_amortizacion}")
    print(f"  Acquisition Date: {bien.fecha_ingreso}")
    
    if bien.tiene_fecha_diferida():
        print(f"\nDeferred Date Information:")
        print(f"  Deferred Date: {bien.fecha_diferida}")
        print(f"  Value at Deferred Date: {Validators.format_decimal_argentino(bien.valor_fecha_diferida)}")
        print(f"  Accum. Depreciation at Deferred Date: {Validators.format_decimal_argentino(bien.amort_acum_fecha_diferida)}")
        
        # Calculate periods
        año_diferida = Validators.extraer_año_ejercicio(bien.fecha_diferida)
        periodos_ya_depreciados = año_diferida - bien.ejercicio_alta if año_diferida else 0
        periodos_restantes = bien.anos_amortizacion - periodos_ya_depreciados
        
        print(f"\nPeriod Calculations:")
        print(f"  Year of Deferred Date: {año_diferida}")
        print(f"  Periods Already Depreciated: {periodos_ya_depreciados}")
        print(f"  Remaining Periods: {periodos_restantes}")
    
    # Calculate depreciation
    calculator = AmortizacionCalculator()
    result = calculator.calcular_amortizacion(bien, ejercicio_liquidacion)
    
    print(f"\nDepreciation Results for {ejercicio_liquidacion}:")
    print(f"  Beginning Depreciation: {Validators.format_decimal_argentino(result['amort_inicio'])}")
    print(f"  Period Depreciation: {Validators.format_decimal_argentino(result['amort_ejercicio'])}")
    print(f"  Accumulated Depreciation: {Validators.format_decimal_argentino(result['amort_acumulada'])}")
    print(f"  Residual Value: {Validators.format_decimal_argentino(result['valor_residual'])}")
    
    if 'periodos_restantes' in result:
        print(f"  Remaining Periods in Result: {result['periodos_restantes']}")
    
    return result

def debug_inflation_calculation(bien, ejercicio_actual, ejercicio_anterior, amortizacion_data):
    """Debug the inflation adjustment calculation"""
    print("\n" + "="*70)
    print("INFLATION ADJUSTMENT DEBUG")
    print("="*70)
    
    # Setup inflation calculator with sample indices
    gestor_indices = GestorIndicesFACPCE()
    
    # Add sample indices (you should replace with your actual indices)
    sample_indices = [
        ("31/12/2022", 1234.567890),  # Deferred date
        ("31/12/2023", 1593.401850),  # Previous period
        ("31/12/2024", 2737.126430),  # Current period
    ]
    
    print("\nSample Indices Used:")
    for fecha, indice in sample_indices:
        gestor_indices.agregar_indice(fecha, indice)
        print(f"  {fecha}: {Validators.format_decimal_argentino(indice, 6)}")
    
    # Calculate coefficients
    fecha_origen = bien.get_fecha_origen_bien()
    coef_anterior, error_ant = gestor_indices.get_coeficiente(fecha_origen, ejercicio_anterior)
    coef_actual, error_act = gestor_indices.get_coeficiente(fecha_origen, ejercicio_actual)
    
    print(f"\nCoefficients:")
    print(f"  Origin Date for Calculation: {fecha_origen}")
    if coef_anterior:
        print(f"  Previous Period Coefficient: {coef_anterior:.6f}")
    else:
        print(f"  Previous Period Coefficient Error: {error_ant}")
    
    if coef_actual:
        print(f"  Current Period Coefficient: {coef_actual:.6f}")
    else:
        print(f"  Current Period Coefficient Error: {error_act}")
    
    if not coef_anterior or not coef_actual:
        print("\n❌ Cannot proceed with inflation calculation due to missing indices")
        return None
    
    # Calculate inflation adjustment
    inflacion_calc = InflacionCalculator(gestor_indices)
    result = inflacion_calc.calcular_ajuste_inflacion(
        bien, ejercicio_actual, ejercicio_anterior, amortizacion_data
    )
    
    if not result.get('error'):
        print(f"\nInflation Adjustment Results:")
        print(f"  Historical Origin Value: {Validators.format_decimal_argentino(result['valor_origen_historico'])}")
        print(f"  Adjusted Value (Previous): {Validators.format_decimal_argentino(result['vo_ajustado_anterior'])}")
        print(f"  Adjusted Value (Current): {Validators.format_decimal_argentino(result['vo_ajustado_actual'])}")
        print(f"  Value Inflation Adjustment: {Validators.format_decimal_argentino(result['ajuste_infl_vo_ejercicio'])}")
        
        print(f"\n  Beginning Depreciation (Previous Adjusted): {Validators.format_decimal_argentino(result['amort_acum_inicio_ajustada_anterior'])}")
        print(f"  Beginning Depreciation (Current Adjusted): {Validators.format_decimal_argentino(result['amort_acum_inicio_ajustada_actual'])}")
        print(f"  Depreciation Inflation Adjustment: {Validators.format_decimal_argentino(result['ajuste_infl_amort_inicio_ejercicio'])}")
        
        print(f"\n  Period Depreciation (Adjusted): {Validators.format_decimal_argentino(result['amort_ejercicio_ajustada'])}")
        print(f"  Accumulated Depreciation at Close (Adjusted): {Validators.format_decimal_argentino(result['amort_acum_cierre_ajustada'])}")
        print(f"  Residual Value (Adjusted): {Validators.format_decimal_argentino(result['valor_residual_ajustado'])}")
        
        # Check for the issue mentioned
        if result['amort_acum_cierre_ajustada'] >= result['vo_ajustado_actual']:
            print(f"\n⚠️  WARNING: Adjusted depreciation equals or exceeds adjusted asset value!")
            print(f"    This indicates the asset appears fully depreciated after inflation adjustment.")
    else:
        print(f"\n❌ Inflation Calculation Error: {result.get('mensaje', 'Unknown error')}")
    
    return result

def main():
    """Main debug function"""
    print("\n" + "="*70)
    print("DEFERRED DATE DEPRECIATION DEBUG SCRIPT")
    print("="*70)
    print("This script tests depreciation calculations for assets with deferred dates")
    
    # Create test asset
    test_asset = create_test_asset_with_deferred_date()
    
    # Define periods
    ejercicio_anterior = "31/12/2023"
    ejercicio_actual = "31/12/2024"
    
    print(f"\nTest Periods:")
    print(f"  Previous Period: {ejercicio_anterior}")
    print(f"  Current Period: {ejercicio_actual}")
    
    # Test depreciation calculation
    amort_data = debug_depreciation_calculation(test_asset, ejercicio_actual)
    
    # Test inflation adjustment
    if amort_data:
        inflacion_data = debug_inflation_calculation(
            test_asset, ejercicio_actual, ejercicio_anterior, amort_data
        )
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if amort_data and inflacion_data and not inflacion_data.get('error'):
        print("\nKey Findings:")
        print(f"1. Asset acquired in {test_asset.ejercicio_alta} with {test_asset.anos_amortizacion}-year depreciation")
        print(f"2. Deferred date at {test_asset.fecha_diferida} shows {Validators.format_decimal_argentino(test_asset.amort_acum_fecha_diferida)} accumulated depreciation")
        
        if 'periodos_restantes' in amort_data:
            print(f"3. Remaining depreciation periods: {amort_data['periodos_restantes']}")
        
        print(f"4. Historical residual value: {Validators.format_decimal_argentino(amort_data['valor_residual'])}")
        print(f"5. Inflation-adjusted residual value: {Validators.format_decimal_argentino(inflacion_data['valor_residual_ajustado'])}")
        
        # Check if the issue is present
        if inflacion_data['amort_acum_cierre_ajustada'] >= inflacion_data['vo_ajustado_actual']:
            print("\n❗ ISSUE DETECTED: The inflation-adjusted depreciation equals or exceeds the adjusted asset value.")
            print("   This might indicate:")
            print("   - The asset was already highly depreciated at the deferred date")
            print("   - The inflation coefficient is causing the depreciation to scale beyond the asset value")
            print("   - A logic issue in how deferred date depreciation is calculated")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n\nDebug script completed. Please share the output for analysis.")