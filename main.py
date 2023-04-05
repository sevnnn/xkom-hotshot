import json
from urllib.request import Request, urlopen
from configparser import ConfigParser

XKOM_API_URL = "https://mobileapi.x-kom.pl/api/v1/xkom/hotShots/current?onlyHeader=true"
XKOM_API_AUTH = "jfsTOgOL23CN2G8Y"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 "
    "Safari/537.36 RuxitSynthetic/1.0 v6630565191794278100t3234796395378176538 ath259cea6f altpriv cvcv=2 "
    "smf=0"
)


def get_webhook_link_from_config() -> str:
    config = ConfigParser()
    config.read("./config.ini")
    try:
        webhook_url = config["discord"]["webhook_url"]
    except KeyError:
        with open("./config.ini", "w") as config_file:
            config_file.write("[discord]\nwebhook_url = PASTE YOUR WEBHOOK URL HERE\n")
        print(
            "no config.ini file found, created one for you - please configure it before you run this script again"
        )
        exit(1)

    return webhook_url


def request_xkom_hotshot() -> dict:
    with urlopen(
        Request(XKOM_API_URL, headers={"x-api-key": XKOM_API_AUTH})
    ) as response:
        return json.loads(response.read())


def build_and_send_embed(xkom_data: dict) -> None:
    payload = {
        # you can set contents to "<@YOUR DISCORD ID HERE>" to get pinged every time this is executed
        "content": None,
        "embeds": [
            {
                "title": xkom_data["PromotionName"],
                "description": f"~~%.2f PLN~~ => **%.2f PLN**"
                % (xkom_data["OldPrice"], xkom_data["Price"]),
                "url": "https://www.x-kom.pl/goracy_strzal",
                "footer": {
                    "text": f"Pozostało {xkom_data['PromotionTotalCount'] - xkom_data['SaleCount']} na"
                    f" {xkom_data['PromotionTotalCount']} produktów "
                },
                "image": {"url": xkom_data["PromotionPhoto"]["Url"]},
            }
        ],
    }
    urlopen(
        Request(
            get_webhook_link_from_config(),
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"},
        )
    )


if __name__ == "__main__":
    build_and_send_embed(request_xkom_hotshot())
