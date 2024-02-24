var index = 0.0;
var choosen_num = 0;

var spin = new Audio("/static/spin.wav")
var win = new Audio("/static/win.wav")

function setToNumber(){
    var number = parseFloat(choosen_num);
    if(index.toFixed(2) === number.toFixed(2)){
        clearInterval(window.setNumberInterval);
        index = 0;
        spin.pause()
        if(number >= document.getElementById("anticipated_multiplier").value) {
            document.getElementById("multiplier").style.color = "green"
        }else{
            document.getElementById("multiplier").style.color = "red"
        }
        return;
    }
    index += 0.01;
    document.getElementById("multiplier").innerHTML = index.toFixed(2) + "x"
}

function playLimbo(){
    document.getElementById("multiplier").style.color = "white"
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/limbo_guess_multiplier', true);

    //Send the proper header information along with the request
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Inadequate Balance"){
                alert("Bakiyeniz yetersiz")
                document.location = "/limbo"
            }
            if(!window.timeout_play){
                choosen_num = this.responseText;
                spin.play()
                spin.loop = true;
                window.setNumberInterval = setInterval(setToNumber, 10);
            }else{
                document.getElementById("multiplier").innerHTML = this.responseText + "x"
            }
            if(parseFloat(this.responseText) >= document.getElementById("anticipated_multiplier").value){
                if(!window.timeout_play){
                    setTimeout(stopConfetti, 3000)
                }
            }
        }
    }
    xhr.send("multiplier=" + document.getElementById("anticipated_multiplier").value +
        "&bet_amount=" + document.getElementById("betting_amount").value);
}

function stopConfetti(){
    document.getElementById("confetti-wrapper").style.display = "none";
}

function setAutoPlay(){
    window.timeout_play = setInterval(startAutoPlay, 1000);
}


function startAutoPlay(){
    playLimbo();
    document.getElementById("pause-play-button").style.display = "block";
    document.getElementById("start-play-button").style.display = "none";
}

function stopAutoPlay(){
    document.getElementById("pause-play-button").style.display = "none";
    document.getElementById("start-play-button").style.display = "block";
    clearInterval(window.timeout_play);
    window.timeout_play = undefined;
}
