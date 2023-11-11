import os,re

import openai
from blinker import Signal
from dotenv import load_dotenv
from flask import render_template, Flask, request, Response, stream_with_context,redirect,url_for
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

streaming_state = {'value': True}
streaming_stopped = Signal()


def stop_streaming_handler(sender):
    streaming_state['value'] = False


streaming_stopped.connect(stop_streaming_handler)


@app.route('/', methods=['GET', 'POST'])
@stream_with_context
def landing():

    if request.method == 'GET':
        return render_template('chat.html')

    streaming_state['value'] = True
    data = request.form or request.json
    prompt = data.get('prompt')

    if not prompt:
        return Response('Prompt is required', status=400)

    def stream_response():
        response_list=[]
        response = openai.ChatCompletion.create(messages=[{"role": "user", "content": f'{prompt}'}, ], temperature=0,
                                                model='gpt-3.5-turbo',
                                                stream=True)
        for chunk in response:
            if not streaming_state['value']:
                print("Streaming Stopped")
                break
            response_str=chunk['choices'][0]['delta']['content'] if 'content' in chunk['choices'][0]['delta'] else ""
            response_list.append(response_str)
            print(response_str)
            yield response_str
        print('finished')
        print(response_list)
        whole_response="".join(response_list)
        length_token=judge_token(whole_response)
        print(length_token)
        show_str(length_token)


    return Response(stream_response(), mimetype='text/html')

def judge_token(text):
    # 将文本按空格分割，计算分割后的元素数量
    if re.search("[\u4e00-\u9fff]", text):
        # 中文文本，返回字符长度
        return len(text)
    else:
        # 非中文文本，按空格分割计算token数量
        tokens = text.split()
        return len(tokens)
def show_str(length_token):
    print(length_token)
    return render_template('chat.html', my_string=length_token)
@app.route('/stream_finished')
def stream_finished():
    # 流式处理完成后重定向
    return redirect(url_for('show_result'))
@app.route('/stop', methods=['GET'])
def stop_streaming():
    print("stopped")
    streaming_stopped.send()
    return "Streaming stop signal sent"


if __name__ == '__main__':
    app.run(debug=True)
