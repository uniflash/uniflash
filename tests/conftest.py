import os
from pathlib import Path
import pytest
from pytest import raises

from web3 import Web3
import eth_tester
from eth_tester import EthereumTester, PyEVMBackend
from eth_tester.exceptions import TransactionFailed
from vyper import compiler
from vyper.cli.vyper_compile import compile_files

from tests.constants import *

setattr(eth_tester.backends.pyevm.main, 'GENESIS_GAS_LIMIT', 10**9)
setattr(eth_tester.backends.pyevm.main, 'GENESIS_DIFFICULTY', 1)

@pytest.fixture
def tester():
    return EthereumTester(backend=PyEVMBackend())

@pytest.fixture
def w3(tester):
    w3 = Web3(Web3.EthereumTesterProvider(tester))
    w3.eth.setGasPriceStrategy(lambda web3, params: 0)
    w3.eth.defaultAccount = w3.eth.accounts[0]
    return w3

@pytest.fixture
def pad_bytes32():
    def pad_bytes32(instr):
        bstr = instr.encode()
        return bstr + (32 - len(bstr)) * b'\x00'
    return pad_bytes32

def create_contract(w3, path):
    wd = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(wd, os.pardir, path)) as f:
        source = f.read()
    root_path = os.path.join(wd, os.pardir)
    source_path = os.path.join(root_path, path)
    out = compile_files([source_path], ['abi', 'bytecode'], root_path)[path]
    return w3.eth.contract(abi=out['abi'], bytecode=out['bytecode'])

@pytest.fixture
def eth_flash_template(w3):
    deploy = create_contract(w3, 'contracts/uniflash_eth.vy')
    tx_hash = deploy.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    )

@pytest.fixture
def erc20_flash_template(w3):
    deploy = create_contract(w3, 'contracts/uniflash_erc20.vy')
    tx_hash = deploy.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    )


@pytest.fixture
def factory(w3, eth_flash_template, erc20_flash_template):
    deploy = create_contract(w3, 'contracts/uniflash_factory.vy')
    tx_hash = deploy.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contract = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    )
    contract.functions.initFactory(eth_flash_template.address, erc20_flash_template.address).transact()
    return contract

@pytest.fixture
def eth_flash(w3, factory, eth_flash_template):
    eth_flash_address = factory.caller.getEthFlash(INTEREST_FACTOR)
    return w3.eth.contract(
        address=eth_flash_address,
        abi=eth_flash_template.abi
    )

@pytest.fixture
def erc20_flash(w3, factory, erc20_flash_template, HAY_token):
    factory.functions.createErc20Flash(HAY_token.address).transact()
    erc20_flash_address = factory.caller.getErc20Flash(HAY_token.address, INTEREST_FACTOR)
    return w3.eth.contract(
        address=erc20_flash_address,
        abi=erc20_flash_template.abi
    )

@pytest.fixture
def HAY_token(w3):
    deploy = create_contract(w3, 'contracts/test_contracts/ERC20.vy')
    tx_hash = deploy.constructor(b'HAY Token', b'HAY', 18, TOTAL_HAY).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    )

def lender_template(w3, malicious, HAY_token):
    deploy = create_contract(w3, 'contracts/test_contracts/Borrower.vy')
    tx_hash = deploy.constructor(malicious, HAY_token.address).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi
    )

@pytest.fixture
def good_lender(w3, HAY_token):
    return lender_template(w3, False, HAY_token)

@pytest.fixture
def bad_lender(w3, HAY_token):
    return lender_template(w3, True, HAY_token)

@pytest.fixture
def assert_fail():
    def assert_fail(func):
        with raises(Exception):
            func()
    return assert_fail