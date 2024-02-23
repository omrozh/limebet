window.gameID = ""


function stopConfetti(){
    document.getElementById("confetti-wrapper").style.display = "none"
}

function confetti(){
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
                alert("Your balance is insufficient you will be redirected to the deposit page.")
            }
            document.getElementById("betting_amount").style.display = "none"
            document.getElementById("betting").style.display = "none"
            window.gameID = this.responseText
            document.getElementById("game").style.display = "block";
            document.getElementById("offer").innerText = document.getElementById("betting_amount").value + "PLT"
        }
    }
    xhr.send("&bet_amount=" + document.getElementById("betting_amount").value);
}

function getBalance(){
    function reqListenerMoney () {
      document.getElementById("account_balance").innerHTML = this.responseText
    }

    var oReqMoney = new XMLHttpRequest();
    oReqMoney.addEventListener("load", reqListenerMoney);
    oReqMoney.open("GET", "/refresh-balance");
    oReqMoney.send();
}

getBalance();
