from pytest import raises

from eth_tester.exceptions import TransactionFailed

from tests.constants import *

def test_init(w3, eth_flash_template, erc20_flash_template, factory, pad_bytes32, assert_fail):
    assert_fail(lambda: factory.functions.initFactory(eth_flash_template.address, erc20_flash_template.address).transact())
    assert factory.caller.ethFlashTemplate() == eth_flash_template.address
    assert factory.caller.getEthFlash(INTEREST_FACTOR) != None

def test_factory_for_eth(w3, eth_flash_template, factory, pad_bytes32, assert_fail):
    assert factory.caller.getEthFlash(INTEREST_FACTOR) != None
    assert_fail(lambda: factory.caller.getEthFlash(MAX_INTEREST_FACTOR + 1))
    assert_fail(lambda: eth_flash.functions.setup(INTEREST_FACTOR).transact())
    eth_flash_address = factory.caller.getEthFlash(INTEREST_FACTOR)
    assert eth_flash_address != None
    eth_flash = w3.eth.contract(address=eth_flash_address, abi=eth_flash_template.abi)

    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.caller.factoryAddress() == factory.address
    assert eth_flash.caller.name() == pad_bytes32('Uniflash for ETH V1')
    assert eth_flash.caller.symbol() == pad_bytes32('UFO-V1')
    assert eth_flash.caller.totalSupply() == 0
    assert eth_flash.caller.interestFactor() == INTEREST_FACTOR

def test_factory_for_erc20(w3, erc20_flash_template, HAY_token, factory, pad_bytes32, assert_fail):
    assert factory.caller.getErc20Flash(HAY_token.address, INTEREST_FACTOR) == ZERO_ADDRESS
    factory.functions.createErc20Flash(HAY_token.address).transact()
    assert_fail(lambda: factory.functions.createErc20Flash(HAY_token.address).transact())
    assert_fail(lambda: factory.caller.getErc20Flash(MAX_INTEREST_FACTOR + 1))
    assert_fail(lambda: eth_flash.caller.setup(INTEREST_FACTOR))
    erc20_flash_address = factory.caller.getErc20Flash(HAY_token.address, INTEREST_FACTOR)
    assert erc20_flash_address != None
    erc20_flash = w3.eth.contract(address=erc20_flash_address, abi=erc20_flash_template.abi)

    assert w3.eth.getBalance(erc20_flash.address) == 0
    assert erc20_flash.caller.factoryAddress() == factory.address
    assert erc20_flash.caller.token() == HAY_token.address
    assert erc20_flash.caller.name() == pad_bytes32('Uniflash for ETH V1')
    assert erc20_flash.caller.symbol() == pad_bytes32('UFO-V1')
    assert erc20_flash.caller.totalSupply() == 0
    assert erc20_flash.caller.interestFactor() == INTEREST_FACTOR