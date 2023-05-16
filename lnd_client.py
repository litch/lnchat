# Import lnd api tooling
import codecs
import os
import sys
import vendor.lightning_pb2 as ln
import vendor.lightning_pb2_grpc as lnrpc

import grpc

import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

import logging
import configparser
import datetime
import codecs

class LndClient():
    def __init__(self):
        self._client = LndClientSubstitute()
        self._logger = logging.getLogger(__name__)


    def build(lnd_config):
        instance = LndClient()
        
        instance._logger.info(f"Opening CLN connection to {lnd_config['host']}:{lnd_config['port']}")
        instance._client = instance._build_client(lnd_config)

        return instance

    def _build_client(self, lnd_config):
        # self._logger.debug(f"Building gRPC client for {self._host}:{self._port}")

        host = lnd_config['host']
        port = lnd_config['port']
        tls_cert_path = lnd_config['tls_cert_path']
        macaroon_path = lnd_config['macaroon_path']
        tls_cert = open(tls_cert_path, "rb").read()
        macaroon = codecs.encode(open(macaroon_path, "rb").read(), "hex")
        cert_creds = grpc.ssl_channel_credentials(tls_cert)
        auth_creds = grpc.metadata_call_credentials(self._macaroon_call(macaroon))
        creds = grpc.composite_channel_credentials(cert_creds, auth_creds)
        channel = grpc.secure_channel(f"{host}:{port}", creds)
        return lnrpc.LightningStub(channel)

    def _macaroon_call(self, macaroon):
        def metadata_callback(context, callback):
            callback([('macaroon', macaroon)], None)
        return metadata_callback

    def check_connection(self, pubkey):
        self._logger.debug(f"Checking connection for peer (Pubkey: {pubkey})")
        try:
            # res = self._client.ListPeers(ln.ListPeersRequest())
            res = self._client.ListPeers(ln.ListPeersRequest())
            for peer in res.peers:
                if peer.pub_key == pubkey:
                    return True
        except Exception as e:
            print("Error during peer check")
            return False
        except grpc.RpcError as e:
            self._logger.error(f"Failed to check connection for peer (Pubkey: {pubkey})")
            self._logger.error(f"Error: {e}")
            return None
        return False
        
    def getinfo(self):
        try:
            res = self._client.GetInfo(ln.GetInfoRequest())
            return res
        except grpc.RpcError as e:
            self._logger.error(f"Failed to get info")
            self._logger.error(f"Error: {e}")
            return None

    def connect(self, connection_string):
        try:
            res = self._client.ConnectPeer(ln.ConnectPeerRequest(addr=ln.LightningAddress(pubkey=connection_string)))
            return True
        except grpc.RpcError as e:
            self._logger.error(f"Failed to connect to peer (Pubkey: {connection_string})")
            self._logger.error(f"Error: {e}")
            return False

    def open_channel(self, pubkey, size):
        try:
            res = self._client.OpenChannelSync(ln.OpenChannelRequest(node_pubkey=pubkey, local_funding_amount=size))
            return res
        except grpc.RpcError as e:
            self._logger.error(f"Failed to open channel to peer (Pubkey: {pubkey})")
            self._logger.error(f"Error: {e}")
            return False

    def generate_invoice(self, id, external_id, amount):
        try: 
            # Amount is in millisats
            res = self._client.AddInvoice(ln.Invoice(value_msat=amount*1000, memo=f"magma-{id}-{datetime.datetime.now()}", expiry=3600, r_preimage=external_id))

            # We want to return just the bolt11 invoice
            return res.payment_request
        except grpc.RpcError as e:
            self._logger.error(f"Failed to generate invoice")
            self._logger.error(f"Error: {e}")
            return None
        except Exception as e:
            print("Problemo: ", e)
            self._logger.error(f"Failed to generate invoice")
            self._logger.error(f"Error: {e}")
            return False         
    
    def call(self, query):
        self._logger.info(f"Calling {query}")
        try:
            namespace = {'self': self}
            exec(f"result = {query}", globals(), namespace)
            return namespace['result']
        except Exception as e:
            print("Error: ", e)
            raise e


class LndClientSubstitute():
    def __init__(self):
        self._executeds = []
        self._responses = []

    def execute(self, query, *params):
        self._executeds.append({'query': query})
        if len(self._responses) > 0:
            return self._responses.pop()

    def was_executed(self):
        return len(self._executeds) > 0

    def query(self, query):
        if len(self._responses) > 0:
            return MagicMock(return_value=self._responses.pop())
        else:
            return MagicMock()

    def add_response(self, response):
        self._responses.append(response)

    def commit(self):
        pass




if __name__ == '__main__':
    import asyncio
    client = LndClient.build()
    async def test():
        info = client.getinfo()
        print("Info: ", info)

    async def test_connection():
        voltage = client.check_connection("031f2669adab71548fad4432277a0d90233e3bc07ac29cfb0b3e01bd3fb26cb9fa")
        print("Voltage: ", voltage)
        geyser = client.check_connection("0272e8731c6feda7fb7e2b8dbe0fbf1322f9e3b60cc2727f4ee4ca0f820b9cd169")
        print("Geyser: ", geyser)
    asyncio.run(test())
    asyncio.run(test_connection())
    