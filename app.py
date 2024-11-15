from flask import Flask, render_template, request, redirect, url_for, session
import ell
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Obtener SECRET_KEY desde .env

# Inicializar ell con la API Key de OpenAI
ell.init(verbose=True, store='./logdir', autocommit=True)

# Cargar la base de conocimiento desde texto_especifico.txt
with open('texto_especifico.txt', 'r', encoding='utf-8') as f:
    knowledge_base = f.read()

# Definir el chatbot LMP usando ell
@ell.simple(model='gpt-4o-mini')
def chatbot(conversation):
    """Eres un asistente experto en Inteligencia Artificial. Utiliza la base de conocimiento proporcionada para responder preguntas con precisión."""
    # Combinar la conversación en una cadena de texto
    conversation_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in conversation])
    return f"{conversation_text}\n\nBasado en la conversación anterior y utilizando la siguiente base de conocimiento:\n{knowledge_base}\n\nProporciona una respuesta adecuada."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form['user_input']
        # Recuperar el historial de la conversación de la sesión
        if 'conversation' not in session:
            session['conversation'] = []
        conversation = session['conversation']

        # Añadir el mensaje del usuario a la conversación
        conversation.append({'sender': 'User', 'message': user_input})

        # Obtener la respuesta del chatbot
        response = chatbot(conversation)

        # Añadir la respuesta del chatbot a la conversación
        conversation.append({'sender': 'Assistant', 'message': response})

        # Actualizar la sesión
        session['conversation'] = conversation

        return redirect(url_for('chat'))

    else:
        # Recuperar el historial de la conversación de la sesión
        conversation = session.get('conversation', [])
        return render_template('chat.html', conversation=conversation)

@app.route('/reset')
def reset():
    # Limpiar el historial de la conversación
    session.pop('conversation', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
