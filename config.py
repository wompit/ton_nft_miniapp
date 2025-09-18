from environs import Env

env = Env()

env.read_env()

with env.prefixed("RUZZIA_"):
    BOT_TOKEN = env.str("BOT_TOKEN")
    TON_API_KEY = env.str("TON_API_KEY")
    TON_WALLET_ADDRESS = env.str("TON_WALLET_ADDRESS")
    TON_WALLET_MNEMO = env.str("TON_WALLET_MNEMO").split(" ")
    ZOOBLE_ADDRESS = env.str(
        "ZOOBLE_ADDRESS", "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"
    )
    ZOOBLE_AMOUNT = env.int("ZOOBLE_AMOUNT", 999000000000)
    NFT_COLLECTION_ADDRESS = env.str(
        "NFT_COLLECTION_ADDRESS", "EQC6x1x5_S16Gacftl2v-3Uyc79dL7fhp0atOIgdtVa1EpKI"
    )
    SECRET_KEY = env.str("SECRET_KEY")
    MAIN_PATH = env.str("MAIN_PATH", "/opt/deploy/nft_bot/")

    PORT = env.int("PORT", 80)
    HOST = env.str("HOST", "127.0.0.1")
    BASE_PATH = env.str("BASE_PATH", "/opt/deploy/nft_bot/")

    FILEBASE_SECRET = env.str("FILEBASE_SECRET")
    FILEBASE_KEY = env.str("FILEBASE_KEY")

    with env.prefixed("DB_"):
        DB_CONFIG = dict(
            database=env.str("NAME"),
            user=env.str("USER"),
            password=env.str("PASSWORD"),
            host=env.str("HOST"),
            port=env.int("PORT"),
            max_connections=env.int("MAX_CONNECTIONS", 50),
            stale_timeout=env.int("STALE_TIMEOUT", 600),
            register_hstore=False,
            server_side_cursors=False,
        )
