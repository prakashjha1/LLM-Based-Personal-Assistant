import streamlit as st
from ctransformers import AutoModelForCausalLM
import os
import speech_recognition as sr
import pyttsx3



css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}

.chat-message.bot {
    background-color: #475063
}

.chat-message .message {
  width: 90%;
  padding: 0 1.5rem;
  color: #fff;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="message">{{MSG1}}<br><br>{{MSG2}}</div>
</div>
'''

msg_template = '''
<div class="chat-message bot">
    <div class="message">{{MSG1}}</div>
</div>
'''


def load_llm(model):
    llm = AutoModelForCausalLM.from_pretrained( model_path_or_repo_id=model,
                                                model_type="llama",
                                                temperature = 1,
                                               context_length = 10000,
                                                max_new_tokens = 10000,
                                                
                                                )
    return llm


def change_llm(model):
    st.session_state.llm = load_llm(model)
    st.write("Model changed")


file_name = "output.txt"
def update_history(data,mode):
    with open(file_name, mode,encoding='utf-8') as file:
        file.write(data+ "\n\n")
        file.close()




def recognize_speech():
    r = sr.Recognizer()
    listening = st.empty()
    with sr.Microphone() as source:
        listening.markdown("I am listening....")
        audio_text = r.listen(source)
        listening.markdown("Time over, thanks")
        
        
    try:
        # using google speech recognition
        st.write("You: "+r.recognize_google(audio_text))
        return r.recognize_google(audio_text)
    except:
        st.write("Sorry, I did not get that")
        return "Not recognized"


def download_history():
    try:
             
        if os.path.exists(file_name):

            with open(file_name) as file:
                file_data = file.read()
                file.close()

        st.download_button(
            label="Download data",
            data=file_data,
            file_name='history.txt',
            mime='text')
    except:
        st.write("No history to download")

def clear_history():

    st.session_state.history = []
        
    if os.path.exists(file_name):
        os.remove(file_name)
        st.write("Cleared history")
    else:
        st.write("No history to clear")    



def text_to_speech(text):

    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 1)   # Volume (0.0 to 1.0)
        engine.say(text)
        engine.runAndWait()
    except: 
        st.write("No Response to Read")


def stream_response(prompt):
    placeholder = st.empty()
    full_response = ''
    print(prompt)
    print()
    for item in st.session_state.llm(prompt, stream = True):
        full_response += item
        placeholder.markdown(msg_template.replace("{{MSG1}}",full_response), unsafe_allow_html=True)

        
    update_history("You : " +user_input,'a')
    update_history("AI Assistant : " + full_response,'a')
    
    st.session_state.history.append(f"<b>User: </b> <br>{user_input}<br>")
    st.session_state.history.append(f"<b>AI Assistant:</b><br>{full_response}<br>")
    placeholder.markdown('')
    if len(st.session_state.history) > 15:
        st.session_state.history = st.session_state.history[-15:]
    
    st.session_state.response = full_response
    

def display_history():
    
    for i in range(len(st.session_state.history)-1,-1,-2):
        user_msg = st.session_state.history[i-1]
        bot_msg = st.session_state.history[i]
        st.write(bot_template.replace("{{MSG1}}",user_msg).replace("{{MSG2}}",bot_msg), unsafe_allow_html=True)



st.set_page_config(page_title="Chat with llm",
                       page_icon=":alien:")
st.write(css, unsafe_allow_html=True)

st.header("My AI Assistant :alien:")




models = {
          "Mistral-7B-OpenOrca-Q8":"Models/mistral-7b-openorca.Q8_0.gguf",
          "Mistral-7B-Instruct-Q8":"Models/mistral-7b-instruct-v0.1.Q8_0.gguf",
          "llama-2-13b-chat-Q5":"Models/llama-2-13b-chat.Q5_K_M.gguf",
          "llama-2-13b-chat-Q6":"Models/llama-2-13b-chat.Q6_K.gguf",
          "codellama-13b-instruct-Q5":"Models/codellama-13b-instruct.Q5_K_M.gguf"

          }



st.session_state.selected = st.selectbox("Select Model", list(models.keys()))
st.session_state.llm = load_llm(models[st.session_state.selected])
st.write("selected model : "+st.session_state.selected)
user_input = st.text_area('Ask me anything!')


col1, col2, col3, col4 = st.columns(4)

with col1:
    talk = st.button('Talk',key="talk",use_container_width=True)

with col2: 
    clear = st.button("Clear History",key="clear",use_container_width=True)

with col3:
   download  = st.button("Download History",key="download",use_container_width=True)
with col4:
   read  = st.button("Read Response",key="read",use_container_width=True)




if talk:
    user_input = recognize_speech()
    user_input = user_input.lower()
elif clear:
    user_input = "clear history"
elif download:
    user_input = "download history"
elif read:
    user_input = "read response"


try:
    if st.session_state.history:
        pass
except:
    st.session_state.llm = load_llm(models[st.session_state.selected])
    print("model loaded....")
    st.session_state.history = []
    

prompt = f"""
INSTRUCTIONS :
You are the assistant.
I can ask you anything.
First understand the user's input and then answer.
Chat History:
{st.session_state.history}
User Input:
{user_input}
Don't repeat or rephrase the user input.

AI Assistant:
"""

if user_input:

    if user_input == "not recognized":
        st.write("Try Again")

    elif user_input == 'clear history':
        clear_history()
        
    elif user_input == "download history":
        download_history()

    elif user_input == "read response":
        try:
            text_to_speech(st.session_state.response)
            display_history()
        except:
            st.write("No response to Read")
    else:   
        stream_response(prompt)
        display_history()


