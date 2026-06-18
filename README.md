# TRABAJO PRÁCTICO INTEGRADOR - Bot de Soporte Técnico Nivel 1

Chatbot desarrollado en Python para automatizar la gestión de solicitudes de soporte técnico Nivel 1 a través de Telegram. El bot clasifica el problema reportado por el usuario, busca una solución en una base de conocimiento, y deriva el caso a Nivel 2 cuando no encuentra una respuesta adecuada o la solución ofrecida no resuelve el inconveniente.

Este proyecto fue desarrollado como Trabajo Práctico Integrador de la materia Organización Empresarial, Tecnicatura Universitaria en Programación, Universidad Tecnológica Nacional.

## Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **Plataforma:** Telegram, mediante la librería `python-telegram-bot`
- **Persistencia:** Archivos JSON (base de conocimiento y registro de tickets)

## Estructura del Proyecto

```
proyecto/
├── bot/
│   └── main.py
├── docs/
│   └── base_conocimiento.json
├── data/
│   └── tickets.json
├── requirements.txt
└── README.md
```

Las carpetas `docs/` y `data/` se generan automáticamente la primera vez que se ejecuta el bot, junto con sus archivos JSON por defecto.

## Instalación y Despliegue

1. Clonar el repositorio:

```bash
git clone <url-del-repositorio>
cd proyecto
```

2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Si no se cuenta con un archivo `requirements.txt`, instalar manualmente:

```bash
pip install python-telegram-bot
```

3. Obtener un token de bot a través de [@BotFather](https://t.me/BotFather) en Telegram.

4. Reemplazar el valor de la variable `TOKEN` en `bot/main.py` por el token generado:

```python
TOKEN = "TU_TOKEN_AQUI"
```

5. Ejecutar el bot:

```bash
python bot/main.py
```

Si la consola muestra el mensaje `Bot de soporte tecnico iniciado. Esperando mensajes...`, el bot quedó activo y disponible para recibir interacciones desde Telegram.

## Comandos Disponibles

| Comando      | Función                                            |
|--------------|-----------------------------------------------------|
| `/start`     | Inicia una nueva solicitud de soporte                |
| `/cancelar`  | Cancela la solicitud en curso                         |

## Flujo de Funcionamiento

1. El usuario inicia la conversación con `/start`.
2. Describe su problema con el mayor detalle posible.
3. El bot clasifica la solicitud en una de tres categorías: software, hardware o acceso.
4. Si encuentra una solución en la base de conocimiento (y la categoría no es hardware), la sugiere y espera confirmación del usuario.
5. Si la solución funciona, el ticket se cierra automáticamente. Si no funciona, no se encuentra solución, o el problema es de hardware, el caso se deriva a Nivel 2 y se genera el ticket correspondiente.

Todas las solicitudes, hayan sido resueltas o derivadas, quedan registradas en `data/tickets.json`.

## Manejo de Errores

El bot valida las entradas del usuario en cada paso del flujo (descripciones demasiado cortas, respuestas no reconocidas, categorías no identificadas) y cuenta con un manejador de errores global que evita que fallos inesperados interrumpan el servicio.

## Autor

de la Peña, Juan Cruz — Tecnicatura Universitaria en Programación, UTN
