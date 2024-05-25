import requests

kralpay_site_id = "643"
kralpay_merchant_key = "9cj4aj2b53jmk6c534c2sufrop750ab39407e34jnh04bic07l9cyd2ziuytmn6kchka"

vevopay_firma_key = "c800e21052a99ac4e8bf349487721db1"

deposit_types = {
    "kralpay_papara": "Kralpay Papara",
    "kralpay_crypto": "Kralpay Kripto",
    "kralpay_mft": "Kralpay Mefete",
    "kralpay_banka": "Kralpay Banka Transferi",
    "kralpay_creditCard": "Kralpay Kredi Kartı",
    "vevopay_papara": "Vevopay Papara",
    "vevopay_havale": "Vevopay Havale",
    "vevopay_mefete": "Vevopay Mefete",
    "vevopay_payfix": "Vevopay Payfix",
    "vevopay_parazula": "Vevopay Parazula",
    "vevopay_fups": "Vevopay Fups",
    "vevopay_pep": "Vevopay PeP",
    "vevopay_cmt": "Vevopay CMT"
}

withdraw_types_kralpay = {
    "auto_kralpay_papara": "Papara",
    "auto_kralpay_mft": "MFT",
    "auto_kralpay_crypto": "Crypto",
    "auto_kralpay_banka": "BankTransfer"
}


def get_iframe_url_kralpay(transaction, method, base_url, bank_id):
    user = transaction.user
    url = f"https://hizliyatir.com/next/{method.replace('kralpay_', '')}?sid={kralpay_site_id}&username={user.user_uuid}&userID={user.id}&fullname={user.user_information.name}&trx={transaction.id}&amount={transaction.transaction_amount}&return_url={base_url.replace('/profile', '')}/transaction_return"
    if bank_id:
        url += f"&bankId={bank_id}"
    return url


def get_available_banks_kralpay():
    url = f"https://kralpy.com/api/v1/available-banks/?sid={kralpay_site_id}"
    r = requests.get(url, verify=False)
    bank_list = {}
    for i in r.json().get("banks"):
        bank_list[i.get("isim")] = i.get("id")
    return bank_list


def get_iframe_vevopay(transaction, method):
    user = transaction.user
    data = {
            "islem": "iframeolustur",
            "firma_key": vevopay_firma_key,
            "kullanici_isim": user.user_information.name,
            "kullanici_id": user.id,
            "referans": transaction.id,
            "yontem": method.replace("vevopay_", "")
        }
    return requests.post("https://management.vevopay.com/api/veri", data=data, verify=False).json().get("iframe_bilgileri", {}).get("link", None)


def withdraw_vevopay(withdrawal_request):
    user = withdrawal_request.user
    data = {
        "Process": "Withdrawal",
        "firma_key": vevopay_firma_key,
        "UserID": user.id,
        "NameSurname": user.user_information.name,
        "BankAccountNo": withdrawal_request.withdraw_to,
        "Amount": withdrawal_request.withdrawal_amount,
        "Method": withdrawal_request.withdraw_type.replace("auto_vevopay_", ""),
        "Reference": withdrawal_request.id
    }

    r = requests.post("https://management.vevopay.com/api/veri", data=data, verify=False)
    return r.json().get("apistatus") == "ok"


def withdraw_kralpay(withdrawal_request):
    data = {
        "sid": kralpay_site_id,
        "merchant_key": kralpay_merchant_key,
        "method": withdraw_types_kralpay.get(withdrawal_request.withdraw_type),
        "user_id": withdrawal_request.user.id,
        "username": withdrawal_request.user.user_uuid,
        "trx": withdrawal_request.id,
        "fullname": withdrawal_request.user.user_information.name,
        "amount": withdrawal_request.withdrawal_amount,
        "account": withdrawal_request.withdraw_to
    }
    r = requests.post("https://kralpy.com/api/v1/cekim", data=data, verify=False)
    return int(r.json().get("status")) == 1
