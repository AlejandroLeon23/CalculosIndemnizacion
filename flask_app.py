from datetime import datetime
from flask import Flask, render_template, request, send_file  # Asegúrate de incluir send_file aquí
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from reportlab.lib import utils



app = Flask(__name__)

def calcular_prima_antiguedad(salario_diario, años_servicio):
    salario_maximo = 749.78
    nota = ""

    if salario_diario > salario_maximo:
        salario_diario = salario_maximo
        nota = f"Nota: El salario diario se limitó a ${salario_maximo} MXN para el cálculo de la prima de antigüedad."

    prima_antiguedad = round(años_servicio * 12 * salario_diario, 2)
    calculo = f"{años_servicio:.2f} años * 12 días * {salario_diario} salario diario"
    
    return prima_antiguedad, calculo, nota

def calcular_indemnizacion(salario_diario):
    # Indemnización de 90 días (3 meses)
    indemnizacion_90_dias = round(salario_diario * 90, 2)
    calculo_90 = f"{salario_diario} salario diario * 90 días"
    
    # Indemnización de 45 días (para conciliación)
    indemnizacion_45_dias = round(salario_diario * 45, 2)
    calculo_45 = f"{salario_diario} salario diario * 45 días"
    
    return indemnizacion_90_dias, calculo_90, indemnizacion_45_dias, calculo_45

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

    # Determinar los días de vacaciones según el año en curso (año + 1)
    if años_completos == 0:
        dias_vacaciones = 12
    elif años_completos == 1:
        dias_vacaciones = 14
    elif años_completos == 2:
        dias_vacaciones = 16
    elif años_completos == 3:
        dias_vacaciones = 18
    elif años_completos == 4:
        dias_vacaciones = 20
    elif años_completos >= 5 and años_completos < 10:
        dias_vacaciones = 22
    elif años_completos >= 10 and años_completos < 15:
        dias_vacaciones = 24
    elif años_completos >= 15 and años_completos < 20:
        dias_vacaciones = 26
    elif años_completos >= 20:
        # 26 días base y 2 días adicionales por cada 5 años después de los 20 años
        dias_vacaciones = 28 + ((años_completos - 20) // 5) * 2
    
    # Calcular proporcionalmente los días de vacaciones en función del año en curso
    fraccion_año = años_servicio - años_completos
    dias_vacaciones_proporcionales = round(dias_vacaciones * fraccion_año, 2)

    # Elaboración detallada del cálculo
    calculo = (
        f"{años_servicio:.2f} años de servicio:\n"
        f"- Años completos: {años_completos} años -> Días de vacaciones según año en curso: {dias_vacaciones} días\n"
        f"- Fracción del año actual: {fraccion_año:.2f} años del {años_completos + 1}° año -> {dias_vacaciones_proporcionales:.2f} días de vacaciones proporcionales"
    )
    return round(dias_vacaciones_proporcionales, 2), calculo




def calcular_monto_vacaciones(salario_diario, dias_vacaciones):
    monto_vacaciones = round(salario_diario * dias_vacaciones, 2)
    calculo = f"{dias_vacaciones:.2f} días * {salario_diario} salario diario"
    return monto_vacaciones, calculo

def calcular_prima_vacacional(monto_vacaciones, porcentaje_prima=0.25):
    prima_vacacional = round(monto_vacaciones * porcentaje_prima, 2)
    calculo = f"{monto_vacaciones:.2f} monto de vacaciones * {porcentaje_prima * 100}%"
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

def calcular_suma_total(prima_antiguedad, monto_vacaciones, prima_vacacional, indemnizacion):
    # Incluir la Prima de Antigüedad en la suma total
    return prima_antiguedad + monto_vacaciones + prima_vacacional + indemnizacion

def generar_pdf(nombre_archivo, datos):
    ancho_pagina, alto_pagina = letter
    margen_izquierdo = 50
    margen_derecho = 50
    ancho_utilizable = ancho_pagina - margen_izquierdo - margen_derecho

    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Título centrado
    titulo = "Desglose de Prestaciones"
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(ancho_pagina / 2, alto_pagina - 50, titulo)

    c.setFont("Helvetica", 12)
    
    # Nota de advertencia centrada
    if 'nota_antiguedad' in datos:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(1, 0, 0)  # Color rojo
        c.drawCentredString(ancho_pagina / 2, alto_pagina - 70, datos['nota_antiguedad'])
        c.setFillColorRGB(0, 0, 0)  # Volver al color negro

    # Posición inicial del texto
    y = alto_pagina - 100

    detalles = [
        f"Años de servicio: {datos['años_completos']} años y {datos['dias_proporcionales']} días",
        f"Prima de Antigüedad: {datos['prima_antiguedad']} (Cálculo: {datos['calc_antiguedad']})",
        f"Indemnización (90 días): {datos['indemnizacion_90_dias']} (Cálculo: {datos['calc_indemnizacion_90']})",
        f"Indemnización (45 días para Conciliación): {datos['indemnizacion_45_dias']} (Cálculo: {datos['calc_indemnizacion_45']})",
        f"Aguinaldo Proporcional: {datos['aguinaldo_proporcional']} (Cálculo: {datos['calc_aguinaldo']})",
        f"Días de Vacaciones: {datos['dias_vacaciones']} días (Cálculo: {datos['calc_vacaciones']})",
        f"Monto Total de Vacaciones: {datos['monto_vacaciones']} (Cálculo: {datos['calc_monto_vacaciones']})",
        f"Prima Vacacional: {datos['prima_vacacional']} (Cálculo: {datos['calc_prima_vacacional']})",
    ]
    
    for detalle in detalles:
        # Alinear el texto a la izquierda dentro del margen izquierdo
        c.drawString(margen_izquierdo, y, detalle)
        y -= 20

    # Suma Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen_izquierdo, y - 10, f"Suma Total (Indemnización 90 días): {datos['suma_total']}")
    c.drawString(margen_izquierdo, y - 30, f"Suma Total (Indemnización 45 días - Conciliación): {datos['suma_conciliacion']}")

    c.save()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        salario_diario = float(request.form['salario_diario'])
        fecha_ingreso = request.form['fecha_ingreso']
        fecha_salida = request.form['fecha_salida']

        años_servicio = calcular_anos_servicio(fecha_ingreso, fecha_salida)
        años_completos, dias_proporcionales = desglose_anos_dias(años_servicio)

        prima_antiguedad, calc_antiguedad, nota_antiguedad = calcular_prima_antiguedad(salario_diario, años_servicio)
        indemnizacion_90_dias, calc_indemnizacion_90, indemnizacion_45_dias, calc_indemnizacion_45 = calcular_indemnizacion(salario_diario)
        aguinaldo_proporcional, calc_aguinaldo = calcular_aguinaldo_proporcional(salario_diario, fecha_ingreso, fecha_salida)
        dias_vacaciones, calc_vacaciones = calcular_dias_vacaciones(años_servicio)
        
        monto_vacaciones, calc_monto_vacaciones = calcular_monto_vacaciones(salario_diario, dias_vacaciones)
        prima_vacacional, calc_prima_vacacional = calcular_prima_vacacional(monto_vacaciones)

        suma_total = calcular_suma_total(prima_antiguedad, monto_vacaciones, prima_vacacional, indemnizacion_90_dias)
        suma_conciliacion = calcular_suma_total(prima_antiguedad, monto_vacaciones, prima_vacacional, indemnizacion_45_dias)

        datos = {
            'años_completos': años_completos,
            'dias_proporcionales': dias_proporcionales,
            'prima_antiguedad': formatear_moneda(prima_antiguedad),
            'calc_antiguedad': calc_antiguedad,
            'indemnizacion_90_dias': formatear_moneda(indemnizacion_90_dias),
            'calc_indemnizacion_90': calc_indemnizacion_90,
            'indemnizacion_45_dias': formatear_moneda(indemnizacion_45_dias),
            'calc_indemnizacion_45': calc_indemnizacion_45,
            'aguinaldo_proporcional': formatear_moneda(aguinaldo_proporcional),
            'calc_aguinaldo': calc_aguinaldo,
            'dias_vacaciones': dias_vacaciones,
            'calc_vacaciones': calc_vacaciones,
            'monto_vacaciones': formatear_moneda(monto_vacaciones),
            'calc_monto_vacaciones': calc_monto_vacaciones,
            'prima_vacacional': formatear_moneda(prima_vacacional),
            'calc_prima_vacacional': calc_prima_vacacional,
            'suma_total': formatear_moneda(suma_total),
            'suma_conciliacion': formatear_moneda(suma_conciliacion),
            'nota_antiguedad': nota_antiguedad if nota_antiguedad else ""
        }
       # Full path to save the PDF
        pdf_dir = '/home/aleonlomeli/mysite/'
        nombre_pdf = os.path.join(pdf_dir, "prestaciones.pdf")

        # Generate the PDF and save it to the specified location
        generar_pdf(nombre_pdf, datos)
        # Generar el PDF y guardar en el servidor
        nombre_pdf = "prestaciones.pdf"
        generar_pdf(nombre_pdf, datos)

        # Renderizar la página HTML con la opción de descargar el PDF
        return render_template('index.html', resultado=True,
                               nombre_pdf=nombre_pdf,
                               **datos)
    return render_template('index.html', resultado=False)



@app.route('/descargar/<filename>')
def descargar_pdf(filename):
    # Make sure to provide the full path to the file
    pdf_dir = '/home/aleonlomeli/mysite/'
    file_path = os.path.join(pdf_dir, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
