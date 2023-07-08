import http.client
"""
 * Send sms API reference: https://www.infobip.com/docs/api#channels/sms/send-sms-message
"""
def sendSMS(userName, contactNumber):
    BASE_URL = "4mydg6.api.infobip.com"
    API_KEY = "App 9138726fb0818699953c54fb6021ae72-fd46a2e1-feeb-4c5d-a50f-77afdff22fe2"

    SENDER = "AI Pet Nova"
    RECIPIENT = contactNumber#"447879333740"
    USERNAME = userName#"Henry"
    MESSAGE_TEXT = "Hello, please check on {}. I haven't heard from them in a while".format(USERNAME)

    conn = http.client.HTTPSConnection(BASE_URL)

    payload1 = "{\"messages\":" \
              "[{\"from\":\"" + SENDER + "\"" \
              ",\"destinations\":" \
              "[{\"to\":\"" + RECIPIENT + "\"}]," \
              "\"text\":\"" + MESSAGE_TEXT + "\"}]}"

    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/sms/2/text/advanced", payload1, headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))