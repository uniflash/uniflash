from pytest import raises

from web3.contract import ConciseContract
from eth_tester.exceptions import TransactionFailed

from tests.contants import *

def test_init(w3, eth_flash_template, erc20_flash_template, factory, pad_bytes32, eth_flash_abi, assert_fail):
    assert_fail(lambda: factory.init_factory(eth_flash_template.address, erc20_flash_template.address))
    assert factory.eth_flash_template() == eth_flash_template.address
    assert factory.get_eth_flash(SUBSIDY_FACTOR) == None

def test_factory(w3, eth_flash_template, factory, pad_bytes32, eth_flash_abi, assert_fail):
    factory.create_eth_flash(transact={})
    assert_fail(lambda: factory.get_eth_flash(MAX_SUBSIDY_FACTOR + 1))
    eth_flash_address = factory.get_eth_flash(SUBSIDY_FACTOR)
    assert eth_flash_address != None
    eth_flash = ConciseContract(w3.eth.contract(address=eth_flash_address, abi=eth_flash_abi))
    assert_fail(lambda: factory.create_eth_flash())
    assert_fail(lambda: eth_flash.setup())

    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.factoryAddress() == factory.address
    assert eth_flash.name() == pad_bytes32('Uniflash for ETH V1')
    assert eth_flash.symbol() == pad_bytes32('UFO-V1')
    assert eth_flash.totalSupply() == 0
    assert eth_flash.subsidyFactor() == SUBSIDY_FACTOR