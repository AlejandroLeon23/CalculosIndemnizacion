from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

def calcular_prima_antiguedad(salario_diario, años_servicio):
    prima_antiguedad = round(años_servicio * 12 * salario_diario, 2)
    calculo = f"{años_servicio:.2f} años * 12 días * {salario_diario} salario diario"
    return prima_antiguedad, calculo

def calcular_indemnizacion_por_dia(salario_diario):
    dias_por_mes = 30
    total_dias = dias_por_mes * 3
    indemnizacion = round(salario_diario * total_dias, 2)
    calculo = f"{salario_diario} salario diario * {total_dias} días (3 meses)"
    return indemnizacion, calculo

def calcular_aguinaldo_proporcional(salario_diario, fecha_ingreso, fecha_salida, dias_aguinaldo=15):
    fecha_ingreso = datetime.strptime(fecha_ingreso, '%Y-%m-%d')
    fecha_salida = datetime.strptime(fecha_salida, '%Y-%m-%d')
    
    inicio_año = datetime(year=fecha_salida.year, month=1, day=1)
    if fecha_ingreso > inicio_año:
        dias_trabajados = (fecha_salida - fecha_ingreso).days
    else:
        dias_trabajados = (fecha_salida - inicio_año).days
    
    aguinaldo_proporcional = round((dias_trabajados / 365) * dias_aguinaldo * salario_diario, 2)
    calculo = f"{dias_trabajados} días trabajados / 365 días * {dias_aguinaldo} días de aguinaldo * {salario_diario} salario diario"
    return aguinaldo_proporcional, calculo

def calcular_dias_vacaciones(años_servicio):
    años_completos = int(años_servicio)
    dias_vacaciones = 0

    if años_completos == 0:
        dias_vacaciones = round(12 * años_servicio, 2)  # Proporcional si menos de 1 año
    elif años_completos == 1:
        dias_vacaciones = 12
    elif años_completos == 2:
        dias_vacaciones = 14
    elif años_completos == 3:
        dias_vacaciones = 16
    elif años_completos == 4:
        dias_vacaciones = 18
    elif años_completos >= 5 and años_completos < 10:
        dias_vacaciones = 20
    elif años_completos >= 10 and años_completos < 15:
        dias_vacaciones = 22
    elif años_completos >= 15 and años_completos < 20:
        dias_vacaciones = 24
    elif años_completos >= 20:
        dias_vacaciones = 26 + ((años_completos - 20) // 5) * 2
    
    if años_completos >= 1:
        dias_vacaciones += (años_servicio - años_completos) * (dias_vacaciones / años_completos)
    
    calculo = f"{años_servicio:.2f} años -> {dias_vacaciones:.2f} días de vacaciones"
    return round(min(dias_vacaciones, 30), 2), calculo

def calcular_prima_vacacional(salario_diario, dias_vacaciones, porcentaje_prima=0.25):
    salario_vacacional = salario_diario * dias_vacaciones
    prima_vacacional = round(salario_vacacional * porcentaje_prima, 2)
    calculo = f"{dias_vacaciones:.2f} días * {salario_diario} salario diario * {porcentaje_prima * 100}%"
    return prima_vacacional, calculo

def calcular_anos_servicio(fecha_ingreso, fecha_salida):
    fecha_ingreso = datetime.strptime(fecha_ingreso, '%Y-%m-%d')
    fecha_salida = datetime.strptime(fecha_salida, '%Y-%m-%d')
    delta = fecha_salida - fecha_ingreso
    años_servicio = delta.days / 360.0
    return años_servicio

def desglose_anos_dias(años_servicio):
    años_completos = int(años_servicio)
    dias_proporcionales = round((años_servicio - años_completos) * 360)
    return años_completos, dias_proporcionales

def formatear_moneda(valor):
    return f"${valor:,.2f} MXN"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        salario_diario = float(request.form['salario_diario'])
        fecha_ingreso = request.form['fecha_ingreso']
        fecha_salida = request.form['fecha_salida']

        años_servicio = calcular_anos_servicio(fecha_ingreso, fecha_salida)
        años_completos, dias_proporcionales = desglose_anos_dias(años_servicio)

        prima_antiguedad, calc_antiguedad = calcular_prima_antiguedad(salario_diario, años_servicio)
        indemnizacion, calc_indemnizacion = calcular_indemnizacion_por_dia(salario_diario)
        aguinaldo_proporcional, calc_aguinaldo = calcular_aguinaldo_proporcional(salario_diario, fecha_ingreso, fecha_salida)
        dias_vacaciones, calc_vacaciones = calcular_dias_vacaciones(años_servicio)
        prima_vacacional, calc_prima_vacacional = calcular_prima_vacacional(salario_diario, dias_vacaciones)

        return render_template('index.html', resultado=True,
                               años_completos=años_completos, dias_proporcionales=dias_proporcionales,
                               prima_antiguedad=formatear_moneda(prima_antiguedad), calc_antiguedad=calc_antiguedad,
                               indemnizacion=formatear_moneda(indemnizacion), calc_indemnizacion=calc_indemnizacion,
                               aguinaldo_proporcional=formatear_moneda(aguinaldo_proporcional), calc_aguinaldo=calc_aguinaldo,
                               dias_vacaciones=dias_vacaciones, calc_vacaciones=calc_vacaciones,
                               prima_vacacional=formatear_moneda(prima_vacacional), calc_prima_vacacional=calc_prima_vacacional)
    return render_template('index.html', resultado=False)

if __name__ == '__main__':
    app.run(debug=True)
