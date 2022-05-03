import argparse
import pandas as pd
import sys
import re
import csv

def print_error(err_str):
    print("ERROR: {}".format(err_str), file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="""Genera dos archivos csv que
            el generador de horarios puede procesar.""")

    parser.add_argument("archivo", type=argparse.FileType('rb'),
            metavar="ARCHIVO",help="Archivo Excel que contiene una plantilla" )

    parser.add_argument("--indice-nombre-prof", type=int, required=True,
            metavar="P", dest="idx_prof", help="Índice de la columna que contiene el nombre del profesor")

    parser.add_argument("--indice-clave-materia", type=int, required=True,
            metavar="C", dest="idx_clave_mat", help="Índice de la columna que contiene la clave única de la asignatura")

    parser.add_argument("--indice-nombre-materia", type=int, required=True,
            metavar="M", dest="idx_nom_mat", help="Índice de la columna que contiene el nombre de la asignatura")

    parser.add_argument("--indice-grupo", type=int, required=True,
            metavar="G", dest="idx_grupo", help="Índice de la columna que contiene el grupo")

    parser.add_argument("--indices-ini-fin",type=int,
            required=True,metavar="L",dest="idxs_dias" , nargs=6,help="Índice de las columnas que contienen las horas de inicio de las asignaturas. Se asume que la hora fin le sigue inmediatamente")

    parser.add_argument("--inicio", type=int,
            required=True,metavar="INICIO", dest="inicio", help="Número de filas para saltar inicialmente.")

    parser.add_argument("--saltar-filas", type=int,
            required=False,nargs="+", metavar="X", dest="skip",
            help="Índices(s) de filas para saltar. Comienza a partir de INICIO Y corresponde al mismo número visualizado en excel")

    parser.add_argument("-o",type=argparse.FileType('w'),metavar="OUT",default=None,dest="outfile",help="Archivo de salida")

    args = parser.parse_args()

    if args.skip:
        for idx in args.skip:
            if idx < args.inicio:
                print_error("El índice especificado para saltar ({}) es menor que el inicio de los datos ({})".format(idx,args.inicio))
                sys.exit(-1)

    datos_plantilla = pd.read_excel(args.archivo, skiprows=args.inicio-1)

    # Queremos agregar únicamente los siguientes datos al nuevo DataFrame:
    #   * Nombre del profesor
    #   * Nombre de la materia que imparte
    #   * Clave
    #   * Hora de inicio y hora fin de lunes-domingo

    columnas = [
            "NOMBRE PROF", 
            "CLAVE",
            "NOMBRE MATERIA", 
            "GRUPO",
            "INI LUNES",
            "FIN LUNES",
            "INI MARTES", 
            "FIN MARTES",
            "INI MIERCOLES", 
            "FIN MIERCOLES",
            "INI JUEVES", 
            "FIN JUEVES",
            "INI VIERNES", 
            "FIN VIERNES",
            "INI SÁBADO", 
            "FIN SÁBADO",
            "INI DOMINGO", 
            "FIN DOMINGO",
        ]

    idxs_dias_etqs = [4, 6, 8, 10, 12, 14]

    datos_filtrados = pd.DataFrame(columns=columnas)

    datos_filtrados["NOMBRE PROF"] = datos_plantilla.iloc[:,args.idx_prof]
    datos_filtrados["CLAVE"] = [re.sub(r"\s+", "", s) for s in  datos_plantilla.iloc[:,args.idx_clave_mat]]
    datos_filtrados["NOMBRE MATERIA"] = datos_plantilla.iloc[:,args.idx_nom_mat]
    datos_filtrados["GRUPO"] = datos_plantilla.iloc[:,args.idx_grupo]

    for i in range(6):
        idx_etq_ini = idxs_dias_etqs[i]
        idx_etq_fin= idx_etq_ini + 1

        etq_ini = columnas[idx_etq_ini]
        etq_fin = columnas[idx_etq_fin]

        idx_ini_datos = args.idxs_dias[i]
        idx_fin_datos = idx_ini_datos + 1
        #  print("({},{})".format(idx_ini_datos,idx_fin_datos))

        datos_filtrados[etq_ini] = datos_plantilla.iloc[:,idx_ini_datos]
        datos_filtrados[etq_fin] = datos_plantilla.iloc[:,idx_fin_datos]

    if args.skip:
        # Eliminar filas que no queremos
        # Si queremos que sea el mismo número que en el Excel, entonces
        # tenemos que tomar en cuenta el número de inicio y el índice que
        # comienza en 0
        real_nums = [idx - args.inicio - 1 for idx in args.skip] 
        datos_filtrados.drop(real_nums,axis=0, inplace=True)

    if args.outfile is None:
        str_csv = datos_filtrados.to_csv(index=True,quoting=csv.QUOTE_MINIMAL,quotechar="'")
        print(str_csv)
    else:
        datos_filtrados.to_csv(path_or_buf=args.outfile,
                index=True,quotechar="'")


if __name__ == "__main__":
    main()
