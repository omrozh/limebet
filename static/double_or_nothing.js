window.gameID = ""
var win = new Audio("/static/win.wav")

function stopConfetti(){
    document.getElementById("confetti-wrapper").style.display = "none"
}

function confetti(){
    win.play()
    document.getElementById("confetti-wrapper").style.display = "block"
    setTimeout(stopConfetti, 1500)
}

function endGame(){
    document.location = "/win_double_or_nothing/" + window.gameID
}

function doubleDoubleOrNothing() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/double_double_or_nothing', true);

    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Nothing"){
                window.location = "/lose_double_or_nothing"
            }
            if(this.responseText === "Double"){
                confetti()
                document.getElementById("offer").innerText =
                    (parseFloat(document.getElementById("offer").innerText) * 2).toString() + "TRY"
            }
        }
    }
    xhr.send("&game_id=" + window.gameID);
}


function initiateDoubleOrNothing() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/create_double_or_nothing', true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            if(this.responseText === "Inadequate Balance"){
                alert("Yetersiz bakiye")
                document.location = '/double'
            }
            document.getElementById("betting_amount").style.display = "none"
            document.getElementById("betting").style.display = "none"
            window.gameID = this.responseText
            document.getElementById("game").style.display = "block";
            document.getElementById("offer").innerText = document.getElementById("betting_amount").value + "TRY"
        }
    }
    xhr.send("&bet_amount=" + document.getElementById("betting_amount").value);
}
