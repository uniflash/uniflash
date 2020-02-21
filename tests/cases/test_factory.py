from pytest import raises
from web3.contract import ConciseContract
from eth_tester.exceptions import TransactionFailed

def test_factory(w3, eth_flash_template, factory, pad_bytes32, eth_flash_abi, assert_fail):
    a0, a1 = w3.eth.accounts[:2]
    # Can't call initializeFactory on factory twice
    with raises(TransactionFailed):
        factory.init_factory(eth_flash_template.address)
    # Factory initial state
    assert factory.eth_flash_template() == eth_flash_template.address
    assert factory.get_eth_flash() == None
    # Create ETH flash loan
    factory.create_eth_flash(transact={})
    eth_flash_address = factory.get_eth_flash()
    assert eth_flash_address != None
    eth_flash = ConciseContract(w3.eth.contract(address=eth_flash_address, abi=eth_flash_abi))
    # Exchange already exists
    with raises(TransactionFailed):
        factory.create_eth_flash()
    # Can't call setup on exchange
    assert_fail(lambda: eth_flash.setup())
    # Exchange initial state
    assert eth_flash.factoryAddress() == factory.address
    assert eth_flash.name() == pad_bytes32('Uniflash for ETH V1')
    assert eth_flash.symbol() == pad_bytes32('UFO-V1')
    assert eth_flash.totalSupply() == 0
    assert eth_flash.subsidy_factor() == 8
    assert w3.eth.getBalance(eth_flash.address) == 0