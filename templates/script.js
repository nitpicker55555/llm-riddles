window.onload = function() {
    // 这里放置您希望在页面加载完成后执行的代码
    console.log("页面加载完成！");
    fetch('/api/min_time')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('timer2').innerHTML = 'No data found';
            } else {
                console.log(`Time: ${data.time}, Speak: ${data.speak}`)
                document.getElementById('timer2').innerHTML =
                    `最佳成绩: ${convertToMinAndSec(data.time)}, 冠军留言: ${data.speak}`;
            }
        })
        .catch(error => console.error('Error:', error));
    // 其他功能或逻辑
};
var timer; // 用于存储计时器
var seconds = 0; // 设置初始时间

function startTimer() {
    // 获取h1标签
    var timerElement = document.getElementById("timer");
    var timerElement2 = document.getElementById("timer2");
    // 显示计时器
    timerElement.style.display = 'block';
    // timerElement2.style.display='block';
    // 防止多次点击创建多个计时器
    if (timer) {
        // clearInterval(timer);
    }else{
        // 每秒更新时间
        timer = setInterval(function() {
            seconds++;
            var minutes = Math.floor(seconds / 60); // 计算分钟
            var remainingSeconds = seconds % 60;    // 计算剩余秒数

            // 格式化显示
            timerElement.innerHTML = minutes + " 分 " + remainingSeconds + " 秒";
        }, 1000);

    }


}
function stopTimer() {
    if (timer) {
        clearInterval(timer); // 清除计时器
    }
}
function convertToSeconds(timeStr) {
    // 分割字符串以获取分钟和秒数
    const parts = timeStr.match(/(\d+)\s*分\s*(\d+)\s*秒/);
    if (parts && parts.length === 3) {
        const minutes = parseInt(parts[1], 10);
        const seconds = parseInt(parts[2], 10);
        return minutes * 60 + seconds; // 将分钟转换为秒并加上秒数
    } else {
        return 0; // 如果格式不匹配，则返回 0 或错误处理
    }
}
function convertToMinAndSec(seconds) {
    // 分割字符串以获取分钟和秒数

    var minutes = Math.floor(seconds / 60); // 计算分钟
    var remainingSeconds = seconds % 60;    // 计算剩余秒数
    return minutes + " 分 " + remainingSeconds + " 秒";


}
// 示例使用

function submitData() {
    // 获取文本框和时间标签的值
    var speakValue = document.getElementById('speakInput').value;
    // var timeValue = "20 分 10 秒";
    var timeValue = document.getElementById('timer').innerHTML;

    const totalSeconds = convertToSeconds(timeValue);
    console.log("totalSeconds",totalSeconds); // 应该输出 1210（即 20*60 + 10）
    // 发送数据到 Flask 后端
    fetch('/api/add_entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ speak: speakValue, time: totalSeconds })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data['message']);
            if (data['champion']!==""){
                alert(data['champion']);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}


document.addEventListener("DOMContentLoaded", function() {
    var buttons = document.querySelectorAll("#judge_form button");
    buttons.forEach(function(button) {
        button.classList.add("m-2", "bg-gray-400", "hover:bg-gray-900", "text-white", "rounded-lg");
        button.addEventListener('click', function() {

            var caption = this.getAttribute('data-caption');
            sendCaption(caption);

            buttons.forEach(function(button) {
                button.classList.remove("bg-gray-900");

            });
            this.classList.add('bg-gray-900');
            document.getElementById('resultContainer').innerHTML ='';
            document.getElementById("flaskResponse").value ='';

        });


// 遍历这些按钮

    });


});
var promptForm = document.getElementById('prompt_form');
var resultContainer = document.getElementById('resultContainer');
var buttons = document.querySelectorAll("#judge_form button");
function sendCaption(caption) {
    // Initialize a new AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/judge', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

    // Set up what happens when the request is successful
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 400) {
            // Handle success
            var response = JSON.parse(xhr.responseText);
            console.log(response.result);
            document.getElementById("question").textContent  = response.result;
            document.getElementById("wholequestion").textContent  = response.question;
        } else {
            // Handle error
            console.error('Error from server');
        }
    };

    // Set up what happens in case of error
    xhr.onerror = function () {
        // Handle network errors
        console.error('Network error');
    };

    // Send the AJAX request with the caption as data
    xhr.send(JSON.stringify({caption: caption}));
}

function addUserChat(prompt, mode = "You") {
    var userMessageElement = document.createElement("p");
    if (mode === "You") {
        userMessageElement.classList.add("border-dashed", "bg-gray-200", "p-2");
    }
    else{
        userMessageElement.classList.add("border-dashed", "bg-red-200", "p-2");
    }
    userMessageElement.innerHTML = "<strong>" + mode + ":</strong> " + prompt;
    resultContainer.innerHTML = userMessageElement.outerHTML;
}

promptForm.addEventListener('submit', async function(event) {
    startTimer();
    event.preventDefault();
    var processed_error_indication

    var prompt = promptForm.elements.prompt.value;


    //

    //




    try {
        const response = await fetch('/judge-route', {  //判断input
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt }),
        });

        const result = await response.json();

        if (result.success) {
            // Do something if the judge function returns true
            addUserChat(prompt);

            var formData = new FormData(promptForm);
            formData.append('prompt', prompt);

            promptForm.elements.prompt.value = "";

            try {
                const response = await fetch('{{url_for('landing')}}', {
                    method: 'POST',
                    body: formData
                });
                const reader = response.body.getReader();

                var aiMessageElement = document.createElement("p");
                var ai_raw_message=""
                aiMessageElement.classList.add("border", "p-2", "whitespace-pre-line", "py-2", "bg-green-100");
                aiMessageElement.innerHTML = "<strong>AI:</strong>" + " ";
                resultContainer.appendChild(aiMessageElement);

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const text = new TextDecoder().decode(value);
                    aiMessageElement.textContent += text;
                    ai_raw_message+=text;
                }
                console.log('ai_raw_message', ai_raw_message);
                fetch('/process_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ value: ai_raw_message })
                })
                    .then(response => response.json())
                    .then(data => {
                        // 处理从 Flask 返回的数据
                        console.log('data.response', data.response);
                        processed_error_indication= data.response
                        // document.getElementById("flaskResponse").value = data.response;

                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });

            } catch (error) {
                console.error(error);
            }
            try {
                const response =await  fetch('/judge-route', {  //判断output
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ response:  ai_raw_message }),
                });
                console.log("response",response)

                const response_result =  await response.json();
                console.log("response_result",response_result)

                if (response_result.success) {
                    document.getElementById("flaskResponse").value="成功！"
                    buttons.forEach(function(button) {
                        // 检查按钮的类名是否包含'bg-gray-900'
                        if(button.classList.contains('bg-gray-900')) {
                            // 输出按钮的文本（caption）
                            button.classList.add("bg-green-900");
                            console.log(button);
                        }

                    });
                    var passed_num=0;

                    buttons.forEach(function(button) {
                        // 检查按钮的类名是否包含'bg-gray-900'
                        if(button.classList.contains('bg-green-900')) {
                            // 输出按钮的文本（caption）
                            passed_num+=1;
                            console.log('passed_num ', passed_num);

                        }


                    });
                    document.getElementById('passed_num').innerHTML =
                        '<span style="color: green;">过关：' + passed_num.toString() + '</span>' +
                        '<span style="color: gray;">' + "/15" + '</span>';
                    if (passed_num===15){
                        stopTimer();

                        document.getElementById("championship").style.display='block';
                        document.getElementById("speakInput").style.display='block';
                        document.getElementById("flaskResponse").value="通关！！！！"
                        alert("恭喜通关！！！填写你的通关留言吧！")
                        var colors = ["DodgerBlue", "OliveDrab", "Gold", "Pink", "SlateBlue", "LightBlue", "Violet", "PaleGreen", "SteelBlue", "SandyBrown", "Chocolate", "Crimson"];

                        startConfetti(3600,1,colors,5000);

                    }else {
                        // var colors = ["PaleGreen", "OliveDrab","PaleGreen"];
                        var colors = ["DodgerBlue", "OliveDrab", "Gold", "Pink", "SlateBlue", "LightBlue", "Violet", "PaleGreen", "SteelBlue", "SandyBrown", "Chocolate", "Crimson"];

                        startConfetti(300,1,colors,2500);
                    }

                } else {
                    // addUserChat("输出结果不符合当前关卡要求！","error")
                    console.log("processed_error_indication",processed_error_indication)
                    document.getElementById("flaskResponse").value="输出结果不符合当前关卡要求(注意空格也算作字数)！以下是QA的分析，也许对你有帮助：\n"+processed_error_indication
                    console.log('output judge not success:', response_result.message);
                    buttons.forEach(function(button) {
                        // 检查按钮的类名是否包含'bg-gray-900'
                        if(button.classList.contains('bg-gray-900')) {
                            // 输出按钮的文本（caption）
                            button.classList.add("bg-gray-600");
                            console.log(button);
                        }

                    });
                    console.log("run canvas")
                    var colors = ["PaleGreen", "OliveDrab","PaleGreen"];
                    // var colors = ["DodgerBlue", "OliveDrab", "Gold", "Pink", "SlateBlue", "LightBlue", "Violet", "PaleGreen", "SteelBlue", "SandyBrown", "Chocolate", "Crimson"];

                    startConfetti(300,1,colors);
                }
            } catch (error) {
                console.log('output judge Error:', error);
            }

        } else {
            document.getElementById("flaskResponse").value="输入格式不符合当前关卡要求！(注意空格也算作字数)"
            addUserChat("输入格式不符合当前关卡要求！(注意空格也算作字数)","error")
            console.log('judge not success:', result.message);

            buttons.forEach(function(button) {
                // 检查按钮的类名是否包含'bg-gray-900'
                if(button.classList.contains('bg-gray-900')) {
                    // 输出按钮的文本（caption）
                    button.classList.add("bg-gray-600");
                    console.log(button);
                }
                else {
                    // console.log('按钮，标题为:', button.caption);
                }
            });
            console.log("run canvas")
            var colors = [ "Violet","Crimson"];
            // var colors = ["DodgerBlue", "OliveDrab", "Gold", "Pink", "SlateBlue", "LightBlue", "Violet", "PaleGreen", "SteelBlue", "SandyBrown", "Chocolate", "Crimson"];

            startConfetti(300,1,colors);




            // 将script元素添加到文档中




        }
    } catch (error) {
        console.log('judge Error:', error);
    }




});



//
// function startConfetti(a,b,c,d){
//
// }




var maxParticleCount = 150;
// var particleSpeed = 2;
var startConfetti;
var stopConfetti;
var toggleConfetti;
var removeConfetti;

// (function() {
startConfetti = startConfettiInner;
stopConfetti = stopConfettiInner;
toggleConfetti = toggleConfettiInner;
removeConfetti = removeConfettiInner;

// var colors = ["DodgerBlue", "OliveDrab", "Gold", "Pink", "SlateBlue", "LightBlue", "Violet", "PaleGreen", "SteelBlue", "SandyBrown", "Chocolate", "Crimson"];
var streamingConfetti = false;
var animationTimer = null;
var particles = [];
var waveAngle = 0;

function resetParticle(particle, width, height,colors) {
    particle.color = colors[(Math.random() * colors.length) | 0];
    particle.x = Math.random() * width;
    particle.y = Math.random() * height - height;
    particle.diameter = Math.random() * 10 + 5;
    particle.tilt = Math.random() * 10 - 10;
    particle.tiltAngleIncrement = Math.random() * 0.07 + 0.05;
    particle.tiltAngle = 0;
    return particle;
}

function startConfettiInner(maxParticleCount,particleSpeed,colors,tt=1000) {
    var container = document.getElementById('myConfettiContainer');
    var width = window.innerWidth;
    var height = window.innerHeight;
    window.requestAnimFrame = (function() {
        return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function(callback) {
            return window.setTimeout(callback, 16.6666667);
        };
    })();
    var canvas = document.getElementById("confetti-canvas");
    if (canvas === null) {
        canvas = document.createElement("canvas");
        canvas.setAttribute("id", "confetti-canvas");
        canvas.setAttribute("style", "display:block;z-index:999999;pointer-events:none");
        container.appendChild(canvas);
        canvas.width = width;
        canvas.height = height;
        window.addEventListener("resize", function() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }, true);
    }
    var context = canvas.getContext("2d");
    while (particles.length < maxParticleCount)
        particles.push(resetParticle({}, width, height,colors));
    streamingConfetti = true;
    if (animationTimer === null) {
        (function runAnimation() {
            context.clearRect(0, 0, window.innerWidth, window.innerHeight);
            if (particles.length === 0)
                animationTimer = null;
            else {
                updateParticles(maxParticleCount,particleSpeed,colors);
                drawParticles(context);
                animationTimer = requestAnimFrame(runAnimation);
            }
        })();
    }
    setTimeout(stopConfettiInner, tt);
}

function stopConfettiInner() {
    streamingConfetti = false;
}

function removeConfettiInner() {
    stopConfetti();
    particles = [];
}

function toggleConfettiInner() {
    if (streamingConfetti)
        stopConfettiInner();
    else
        startConfettiInner();
}

function drawParticles(context) {
    var particle;
    var x;
    for (var i = 0; i < particles.length; i++) {
        particle = particles[i];
        context.beginPath();
        context.lineWidth = particle.diameter;
        context.strokeStyle = particle.color;
        x = particle.x + particle.tilt;
        context.moveTo(x + particle.diameter / 2, particle.y);
        context.lineTo(x, particle.y + particle.tilt + particle.diameter / 2);
        context.stroke();
    }
}

function updateParticles(maxParticleCount,particleSpeed,colors) {
    var width = window.innerWidth;
    var height = window.innerHeight;
    var particle;
    waveAngle += 0.01;
    for (var i = 0; i < particles.length; i++) {
        particle = particles[i];
        if (!streamingConfetti && particle.y < -15)
            particle.y = height + 100;
        else {
            particle.tiltAngle += particle.tiltAngleIncrement;
            particle.x += Math.sin(waveAngle);
            particle.y += (Math.cos(waveAngle) + particle.diameter + particleSpeed) * 0.5;
            particle.tilt = Math.sin(particle.tiltAngle) * 15;
        }
        if (particle.x > width + 20 || particle.x < -20 || particle.y > height) {
            if (streamingConfetti && particles.length <= maxParticleCount)
                resetParticle(particle, width, height,colors);
            else {
                particles.splice(i, 1);
                i--;
            }
        }
    }
}
