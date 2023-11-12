import os,re

import openai
from blinker import Signal
from dotenv import load_dotenv
from flask import render_template, Flask, request, Response, stream_with_context,jsonify,url_for,session
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')
app.secret_key = 'your_very_secret_key_here'  # 设置一个安全的密钥
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

        # session['var'] = length_token


    return Response(stream_response(), mimetype='text/html')
def get_question(term_str):
    button_texts = {
        "1-1": "请你构造一个问题使模型的回答是一字不差的“1+1=3”（不需要引号）。 请在下面的输入框内填写你的构造并点击按钮提交。",
        "1-2": "请你输入三个字（及）以内的问题，使模型的回答在30个字以上。 请在下面的输入框内填写你的问题并点击按钮提交。",
        "1-3": "请你输入一个字的问题，使模型的回答在100个字以上。 请在下面的输入框内填写你的问题并点击按钮提交。",
        "1-4": "请输入一个字的问题，使模型的回答字数小于20个字。 请在下面的输入框内填写你的问题并点击按钮提交。",
        "2-1": "你需要提出一个字数是质数的问题，使回答的长度刚好是它的下一个质数。",
        "2-2": "请输入一个大于一的正整数作为问题，使回答里包含至少比它大一千的数。",
        "2-3": "请输入一个大于一的正整数作为问题，使回答里包含至少10个不同的至少比它小一千的自然数。",
        "2-4": "请在不提及1,4,5这三个字符的情况下让模型回答114514，不要有多余的字符。",
        "2-5": "请输入一个大于一的平方数作为问题，使回答里包含它的平方根对应的数。",
        "2-6": "请提一个不包含“狗”这个字的10个字以内的问题，使回答中“狗”这个字出现的次数至少是问题字数的2倍。",
        "3-1": "请你输入一个至少10个字的提问，使模型的回答和提问完全一样。 请在下面的输入框内填写你的提问并点击按钮提交。",
        "3-2": "请你输入一个至少10个字的提问，使模型的回答是问题的反序。 请在下面的输入框内填写你的提问并点击按钮提交。",
        "3-3": "请你输入一个不包含“1”和“3”的提问，使模型的回答是一字不差的“1+1=3”（不需要引号）。 请在下面的输入框内填写你的提问并点击按钮提交。",
        "4-3": "请输入一个大于一的正整数作为问题，使回答里包含和它刚好相差1的数。 请在下面的输入框内填写你构造并点击按钮提交。",
        "5-1": "请构造一个不少于十个字的问题，使得回答中不包含问题中的任意字符。 请在下面的输入框内填写你的提问并点击按钮提交。"
    }

    return button_texts[term_str]
def is_prime(n):
    """Check if a number is a prime number."""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
def input_judge(term_str,input_str):
    if term_str == "1-1":
        return True
    elif term_str == "1-2":
        if len(input_str)<=3:
            return True
        else:
            return False
    elif term_str == "1-3":
        if len(input_str)==1:
            return True
        else:
            return False
    elif term_str == "1-4":
        if len(input_str)==1:
            return True
        else:
            return False
    elif term_str == "2-1":
        if is_prime(len(input_str)):
            return True
        else:
            return False
    elif term_str == "2-2":
        s=input_str
        try:
            num = int(s)
            return num > 1
        except:
            # Not a valid integer
            return False
    elif term_str == "2-3":
        s = input_str
        try:
            num = int(s)
            return num > 1
        except:
            # Not a valid integer
            return False
    elif term_str == "2-4":
        invalid_str=["1","4","5"]
        for i in invalid_str:
            if i in input_str:
                return False
        return True
    elif term_str == "2-5":
        try:
            num = int(input_str)
            if num <= 1:
                return False

            # Calculate the square root and check if it's an integer
            sqrt_num = num ** 0.5
            return sqrt_num.is_integer()
        except ValueError:
            # Not a valid integer
            return False

    elif term_str == "2-6":
        if "狗" not in input_str and len(input_str)<=10:
            return True
        else:
            return False
    elif term_str == "3-1":
        if len(input_str)>=10:
            return True
    elif term_str == "3-2":
        if len(input_str)>=10:
            return True
    elif term_str == "3-3":
        invalid_str=["1","3"]
        for i in invalid_str:
            if i in input_str:
                return False
        return True
    elif term_str == "4-3":
        s = input_str
        try:
            num = int(s)
            return num > 1
        except:
            # Not a valid integer
            return False
    elif term_str == "5-1":
        if len(input_str)>=10:
            return True
        else:
            return False


@app.route('/judge', methods=['POST'])
def judge():
    data = request.json
    caption = data['caption']
    print(caption)
    # Process the caption as needed
    session['term'] = judge_term(caption)#明确现在的关卡
    return jsonify(result="关卡：" + caption,question=get_question(session['term']))
def judge_term(text):
    term_str=text[:3]
    return term_str
def judge_token(text):
    # 将文本按空格分割，计算分割后的元素数量
    if re.search("[\u4e00-\u9fff]", text):
        # 中文文本，返回字符长度
        return len(text)
    else:
        # 非中文文本，按空格分割计算token数量
        tokens = text.split()
        return len(tokens)
@app.route('/process_data', methods=['POST'])
def process_data():
    print("process")
    data = request.json #response全文
    length=judge_token(data['value'])
    # 对数据进行处理，例如仅返回原样的值
    return jsonify({'response': 'Received: ' + data['value']+" length:"+str(length)})

@app.route('/stop', methods=['GET'])
def stop_streaming():
    print("stopped")
    streaming_stopped.send()
    return "Streaming stop signal sent"


if __name__ == '__main__':
    app.run(debug=True)
