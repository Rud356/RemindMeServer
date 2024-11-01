import asyncio
import tomllib

from src import main
from src.models import initialize_connector
from src.models.initialize_connector import (
    create_engine, initialize_session_maker
)

with open("config.toml", "rb") as cfg:
    config = tomllib.load(cfg)["RemindMe"]
    host = config["host"]
    port = config["port"]
    debug_run = config["debug"]
    engine_conn_str = config["engine_connection"]

    if debug_run:
        engine = create_engine(engine_conn_str)
        asyncio.run(initialize_connector.reinitialize_db(engine))
        del engine

    session_factory = initialize_session_maker(engine_conn_str)
    asyncio.run(main(host, port, session_factory))
