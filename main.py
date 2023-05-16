from dotenv import load_dotenv
import sys
import os
import ast
import openai
import tiktoken


from logging_config import configure as configure_logging
from lnd_client import LndClient
import logging

# load secrets from .env
load_dotenv()

# get the open api key from the secrets
open_api_key = os.getenv("OPENAI_API_KEY")

# openai_model = "gpt-3.5-turbo"
openai_model = "gpt-4"
openai_model_max_tokens = 2000
openai.api_key = open_api_key

lnd_config = {
    "host": os.getenv("LND_HOST"),
    "port": os.getenv("LND_PORT"),
    "tls_cert_path": os.getenv("LND_TLS_CERT_PATH"),
    "macaroon_path": os.getenv("LND_MACAROON_PATH")
}

lnd_client = LndClient.build(lnd_config)

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()


messages = []
def setup_openai():
        # Read the lnd_client.py
    lnd_client = read_file("lnd_client.py")
    
    system_prompt = f"""
        You are an AI assistant that is going to help people manage their lightning nodes
        You will interact with their lightning node through the provided interface

        You will be able to:
        - send payments
        - receive payments
        - open channels
        - close channels
        - manage channels
        - manage invoices
        - manage peers
        - manage the node itself
        - manage the wallet
        - generate reports
        - find active and inactive channels
        - rank channels by activity

        and other things that the user may prompt you to do

        You will be able to do all of this through the provided interface

        The interface is defined here:

        {lnd_client}

        -----------------------------
        Your response will be executed directly as such:

        lnd_client.call(<your-response>)

        -----------------------------

        If you want to do a GetInfo on the node, you would respond simply:

        self._client.GetInfo(ln.GetInfoRequest())

        -----------------------------

        Please supress any intermediate output during the code generation, and if the code is going to return something like a table, please print that table in a human readable format
        Also please make any large numbers human-readable by putting in commas, etc

        --------------------------

        print all responses to the screen yourself, and do not return any information to the user.  the user will not have access to your returned values
        
        ---

        Every character you respond will be used to call to the interface, so only respond with valid python code and no delimiters
        do not add any other explanation, only return valid code
    """
    
    messages.append({"role": "system", "content": system_prompt})


def query_openai(query):
    query_logger = logging.getLogger("query_logger")
    query_logger.info(f"Query: {query}")    
    messages.append({"role": "user", "content": query})

    params = {
        "model": openai_model,
        "messages": messages,
        "max_tokens": openai_model_max_tokens,
        "temperature": 0,
    }

    response = openai.ChatCompletion.create(**params)

    reply = response.choices[0]["message"]["content"]

    messages.append({"role": "assistant", "content": reply})
    return reply

def try_query(query, logger):
    print("Current message count: ", len(messages))
    response = query_openai(query)
    try:
        node_response = lnd_client.call(response)
        return node_response
    except Exception as e:
        exception_string = str(e)
        logger.info(f"Exception, replaying the error to chatgpt: {exception_string}")
        error_message = f"Your previous response returned an error when I tried to execute it: {exception_string}.  Please try again."
        try_query(error_message, logger)
    

def main_loop():
    # let's do a getinfo on the node and see what we get
    configure_logging({"logging": {"log_dir": "./logs"}})
    logger = logging.getLogger(__name__)
    logger.info("Getting info from LND node")

    info = lnd_client.getinfo()
    logger.info("Got info from LND node")
    logger.info(info.identity_pubkey)

    response = lnd_client.call("self._client.GetInfo(ln.GetInfoRequest())")
    logger.info(response)

    setup_openai()

    # Sample prompt
    # sample = "Please tell me how many peers I have connected to my node"
    # logger.info(f"Sample: {sample}")
    # response = query_openai(sample)
    # logger.info(f"Response: {response}")
    # node_response = lnd_client.call(response)
    # print(node_response)

    # Now prompt the user for a query
    print("Example query: Please tell me how many peers I have connected to my node")
    while True:
        query = input("Please enter a query: ")
        # Trap control-c and return to this prompt
        try:
            try_query(query, logger)
        except KeyboardInterrupt:
            continue

        
        # print(node_response)
        
