import datetime
import json
import os,re
import requests
# import openai
from blinker import Signal
from dotenv import load_dotenv
from flask import render_template, Flask, request, Response, stream_with_context,jsonify,url_for,session
load_dotenv()

app = Flask(__name__)
# openai.api_key = os.getenv('OPENAI_API_KEY')
app.secret_key = 'your_very_secret_key_here'  # 设置一个安全的密钥
streaming_state = {'value': True}
streaming_stopped = Signal()
app.config.from_pyfile('settings.py')
apiKey = app.config['OPENAI_API_KEY']
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
    headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {apiKey}",
    }
    json_format={'role': 'user', 'content': prompt}
    openai_data = {
        "messages": [json_format],
        "model": "gpt-3.5-turbo",
        "max_tokens": 256,
        "temperature": 0.5,
        "top_p": 1,
        "n": 1,
        "stream": True,
    }

    resp = requests.post(
        url=app.config["URL"],
        headers=headers,
        json=openai_data,
        stream=True,
        timeout=(10, 10)  # 连接超时时间为10秒，读取超时时间为10秒
    )
    def stream_response():
        response_list=[]
        # response = openai.ChatCompletion.create(messages=[{"role": "user", "content": f'{prompt}'}, ], temperature=0,
        #                                         model='gpt-3.5-turbo',
        #                                         max_tokens=256,
        #                                         stream=True)
        # for chunk in response:
        #     if not streaming_state['value']:
        #         print("Streaming Stopped")
        #         break
        #     response_str=chunk['choices'][0]['delta']['content'] if 'content' in chunk['choices'][0]['delta'] else ""
        #     response_list.append(response_str)
        #     print(response_str)
        #     yield response_str




        errorStr = ""
        response_str=""

        for chunk in resp.iter_lines():
            if chunk:
                streamStr = chunk.decode("utf-8").replace("data: ", "")
                print(streamStr)
                try:
                    streamDict = json.loads(streamStr)  # 说明出现返回信息不是正常数据,是接口返回的具体错误信息
                except:
                    errorStr += streamStr.strip()  # 错误流式数据累加
                    continue
                delData = streamDict["choices"][0]
                if delData["finish_reason"] != None :
                    break
                else:
                    if "content" in delData["delta"]:
                        respStr = delData["delta"]["content"]
                        print(respStr)
                        response_list.append(respStr)
                        response_str+=respStr

                        yield respStr

        print('finished')
        # print(response_list)
        # whole_response="".join(response_list)
        # length_token=judge_token(whole_response)
        # print(length_token)

        # session['var'] = length_token


    return Response(stream_response(), content_type='application/octet-stream')
    # return Response(stream_response(), mimetype='text/html')
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
def next_prime(n):
    """Find the next prime number greater than n."""
    def is_prime(k):
        """Check if a number is a prime number."""
        if k <= 1:
            return False
        for i in range(2, int(k**0.5) + 1):
            if k % i == 0:
                return False
        return True

    next_num = n + 1
    while not is_prime(next_num):
        next_num += 1
    return next_num
def extract_numbers(s):
    """Extract all numbers from a string."""
    result_list=[]
    try:
        result_list=re.findall(r'\d+', s)
    except:
        pass
    return result_list


def is_square_root_of_square(num1, num2):
    """
    Check if num2 is the square root of num1, where num1 is a square of a number greater than 1.
    """
    # Check if num1 is a square of a number greater than 1
    if num1 <= 1 or (num1 ** 0.5).is_integer() == False:
        return False

    # Check if num2 is the square root of num1
    return num2 == num1 ** 0.5
def have_common_chars(str1, str2):
    # 遍历第一个字符串中的每个字符
    for char in str1:
        # 如果字符出现在第二个字符串中，则返回True
        if char in str2:
            return True
    # 如果没有找到重复字符，则返回False
    return False

def input_judge(input_str):
    term_str=session['term']
    print("input_judge: ",input_str)

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
def response_judge(input_str):

    term_str = session['term']
    prompt_str = session['prompt']
    print("response_judge",prompt_str,input_str)
    if term_str == "1-1":
        if input_str=="1+1=3":
            return True
    elif term_str == "1-2":
        if len(input_str)>=30:
            return True
    elif term_str == "1-3":
        if len(input_str)>=100:
            return True
    elif term_str == "1-4":
        if len(input_str) <= 20:
            return True
    elif term_str == "2-1":
        if is_prime(len(input_str)):
            return next_prime(len(prompt_str)) == len(input_str)
    elif term_str == "2-2":

        num_list=extract_numbers(input_str)
        pre_num=int(prompt_str)
        for i in num_list:
            if int(i)-pre_num>=1000:
                return True
    elif term_str == "2-3":
        num_list = extract_numbers(input_str)
        pre_num = int(prompt_str)
        result_list=set()
        for i in num_list:
            if int(i)-pre_num<=-1000:
                result_list.add(int(i))
        if len(result_list)>=10:
            return True
    elif term_str == "2-4":
        if (input_str)=="114514":
            return True
    elif term_str == "2-5":
        num_list = extract_numbers(input_str)
        pre_num = int(prompt_str)
        for i in num_list:
            if is_square_root_of_square(pre_num,int(i)):
                return True
    elif term_str == "2-6":
        num_len_pre=len(prompt_str)
        gou_count=input_str.count("狗")
        if gou_count>=2*num_len_pre:
            return True

    elif term_str == "3-1":
        if prompt_str==input_str:
            return True
    elif term_str == "3-2":
        return input_str[::-1]==prompt_str
    elif term_str == "3-3":
        return input_str=="1+1=3"
    elif term_str == "4-3":
        pre_num = int(prompt_str)
        num_list = extract_numbers(input_str)
        for i in num_list:
            if abs(i - pre_num) == 1:
                return True

    elif term_str == "5-1":
        return have_common_chars(input_str,prompt_str)


@app.route('/judge-route', methods=['POST'])
def handle_prompt():
    data = request.json
    user_ip = request.headers.get('X-Real-IP')
    now = datetime.datetime.now()
    print(data)
    success=False
    if "prompt" in data:
        prompt = data['prompt']
        session['prompt']=prompt

        if input_judge(prompt):
            success=True
            # return jsonify(success=True)
        # else:
        #     return jsonify(success=False, message="Error message")
    elif "response" in data:
        response = data['response']
        session['response'] = response

        if response_judge(response):
            success=True
            # return jsonify(success=True)
        # else:
        #     return jsonify(success=False, message="Error message")
    if "response" in data:
        with open("static/data3.txt", "a",encoding='utf-8') as f:
            f.write(f"‘success:’，{success}  ‘time:’，  {now}, ‘ip:’，  {user_ip}  'prompt:'  {str( session['prompt'])},  'response:'  {str( session['response'])}  \n")
    if success:
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Error message")
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

        return len(text)
@app.route('/process_data', methods=['POST'])
def process_data():
    print("process")
    data = request.json #response全文
    length=str(judge_token(data['value']))
    num_list=str(extract_numbers(data['value']))

    result="string length: "+length+"\n"+"number list in string: "+num_list

    # 对数据进行处理，例如仅返回原样的值
    return jsonify({'response': result })

@app.route('/stop', methods=['GET'])
def stop_streaming():
    print("stopped")
    streaming_stopped.send()
    return "Streaming stop signal sent"


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5002)
