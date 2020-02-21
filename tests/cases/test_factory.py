from pytest import raises

from web3.contract import ConciseContract
from eth_tester.exceptions import TransactionFailed

from tests.contants import *

def test_init(w3, eth_flash_template, erc20_flash_template, factory, pad_bytes32, eth_flash_abi, assert_fail):
    assert_fail(lambda: factory.initFactory(eth_flash_template.address, erc20_flash_template.address))
    assert factory.ethFlashTemplate() == eth_flash_template.address
    assert factory.getEthFlash(SUBSIDY_FACTOR) == None

def test_factory_for_eth(w3, eth_flash_template, factory, pad_bytes32, eth_flash_abi, assert_fail):
    assert factory.getEthFlash(SUBSIDY_FACTOR) == None
    factory.createEthFlash(transact={})
    assert_fail(lambda: factory.createEthFlash(transact={}))
    assert_fail(lambda: factory.getEthFlash(MAX_SUBSIDY_FACTOR + 1))
    assert_fail(lambda: eth_flash.setup(SUBSIDY_FACTOR))
    eth_flash_address = factory.getEthFlash(SUBSIDY_FACTOR)
    assert eth_flash_address != None
    eth_flash = ConciseContract(w3.eth.contract(address=eth_flash_address, abi=eth_flash_abi))

    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.factoryAddress() == factory.address
    assert eth_flash.name() == pad_bytes32('Uniflash for ETH V1')
    assert eth_flash.symbol() == pad_bytes32('UFO-V1')
    assert eth_flash.totalSupply() == 0
    assert eth_flash.subsidyFactor() == SUBSIDY_FACTOR

def test_factory_for_erc20(w3, erc20_flash_template, HAY_token, factory, pad_bytes32, erc20_flash_abi, assert_fail):
    assert factory.getErc20Flash(HAY_token.address, SUBSIDY_FACTOR) == None
    factory.createErc20Flash(HAY_token.address, transact={})
    assert_fail(lambda: factory.createErc20Flash(HAY_token.address, transact={}))
    assert_fail(lambda: factory.getErc20Flash(MAX_SUBSIDY_FACTOR + 1))
    assert_fail(lambda: eth_flash.setup(SUBSIDY_FACTOR))
    erc20_flash_address = factory.getErc20Flash(HAY_token.address, SUBSIDY_FACTOR)
    assert erc20_flash_address != None
    erc20_flash = ConciseContract(w3.eth.contract(address=erc20_flash_address, abi=erc20_flash_abi))

    assert w3.eth.getBalance(erc20_flash.address) == 0
    assert erc20_flash.factoryAddress() == factory.address
    assert erc20_flash.token() == HAY_token.address
    assert erc20_flash.name() == pad_bytes32('Uniflash for ETH V1')
    assert erc20_flash.symbol() == pad_bytes32('UFO-V1')
    assert erc20_flash.totalSupply() == 0
    assert erc20_flash.subsidyFactor() == SUBSIDY_FACTOR