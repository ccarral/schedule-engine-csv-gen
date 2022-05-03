import argparse
import pandas as pd
import sys

def print_error(err_str):
    print("ERROR: {}".format(err_str), file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="""Toma la salida de
            extrae_plantilla.py y la transforma en una lista de materias
            con identificadores""")

    parser.add_argument("archivo", metavar="ARCHIVO" 
            ,type=argparse.FileType('r'))

    args = parser.parse_args()

    input = pd.read_csv(args.archivo)

    clave_nombre = dict()

    for idx,row in input.iterrows():
        nueva_clave = row[2].lstrip()
        nueva_clave = nueva_clave.rstrip()
        nuevo_nombre = row[3].lstrip()
        nuevo_nombre = nuevo_nombre.rstrip()

        if nueva_clave not in clave_nombre.keys():
            clave_nombre[nueva_clave] = nuevo_nombre
        else:
            viejo_nombre = clave_nombre[nueva_clave]
            if viejo_nombre != nuevo_nombre:
                print_error("Se encontraron diferentes nombres para la clave '{}': ['{}','{}']".format(nueva_clave, viejo_nombre, nuevo_nombre))

    claves = clave_nombre.keys()
    nombres = clave_nombre.values()

    datos = pd.DataFrame(data={'CLAVE':claves,'NOMBRE':nombres})
    print(datos.to_csv(index=False))


if __name__ == "__main__":
    main()
