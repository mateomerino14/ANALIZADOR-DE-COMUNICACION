# Uso: python main.py                     abre la interfaz
#      python main.py --texto "..."       analiza un texto en la terminal
#      python main.py --audio charla.mp3  transcribe y analiza un audio en la terminal

import argparse
import sys

from nucleo.almacen import reporte_a_texto


def leer_argumentos():
    parser = argparse.ArgumentParser(description="EXPRESA: análisis de comunicación oral y escrita")
    entrada = parser.add_mutually_exclusive_group()
    entrada.add_argument("--texto", help="texto a analizar")
    entrada.add_argument("--audio", help="archivo de audio a transcribir y analizar")
    return parser.parse_args()


def abrir_interfaz():
    from interfaz.app import Aplicacion

    Aplicacion().ejecutar()


def main():
    argumentos = leer_argumentos()
    if argumentos.texto is None and argumentos.audio is None:
        abrir_interfaz()
        return

    from nucleo import flujo

    try:
        if argumentos.texto is not None:
            reporte = flujo.analizar_texto(argumentos.texto)
        else:
            from nucleo.transcriptor import Transcriptor

            reporte = flujo.analizar_audio(argumentos.audio, Transcriptor(), aviso=print)
    except (ValueError, RuntimeError) as error:
        sys.exit(f"Error: {error}")
    print(reporte_a_texto(reporte))


if __name__ == "__main__":
    main()
