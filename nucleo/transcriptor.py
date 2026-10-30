from config import IDIOMA_WHISPER, MODELO_WHISPER

# Con muletillas en el prompt, Whisper las transcribe en lugar de omitirlas
PROMPT_MULETILLAS = "Hola, eh, um, ah, este, o sea, bueno, mhm. Sí, ehhh, mm."


class Transcriptor:
    def __init__(self, nombre_modelo=MODELO_WHISPER):
        self.nombre_modelo = nombre_modelo
        self.modelo = None

    # La primera vez descarga el modelo, por eso se carga solo cuando hace falta
    def cargar_modelo(self):
        if self.modelo is None:
            import whisper

            self.modelo = whisper.load_model(self.nombre_modelo)

    def transcribir(self, audio):
        self.cargar_modelo()
        resultado = self.modelo.transcribe(
            audio,
            language=IDIOMA_WHISPER,
            initial_prompt=PROMPT_MULETILLAS,
            temperature=0.0,
            fp16=False,
        )
        segmentos = [
            {"inicio": segmento["start"], "fin": segmento["end"], "texto": segmento["text"].strip()}
            for segmento in resultado["segments"]
        ]
        return {"texto": resultado["text"].strip(), "segmentos": segmentos}
