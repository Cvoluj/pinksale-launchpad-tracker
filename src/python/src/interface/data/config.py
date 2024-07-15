from scrapy.utils.project import get_project_settings
project_settings = get_project_settings()

token = project_settings.get("BOT_TOKEN")
urls = {
    "Dexscreener": "https://dexscreener.com/",
    "Pinksale": "https://www.pinksale.finance/",
    "GeckoTerminal": "https://www.geckoterminal.com/uk",
    "Dextools": "https://www.dextools.io/app/en/ether/pool-explorer",
    "Itch.io": "https://itch.io/"
}

administrators = [123]
logs = -project_settings.getint("LOGS_CHAT")
