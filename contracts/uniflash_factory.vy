# @title Uniflash V1
# @notice Source code found at https://github.com/uniflash
# @notice Use at your own risk

contract EthFlash():
    def setup(interest_factor: uint256): modifying

contract ERC20Flash():
    def setup(token_addr: address, interest_factor: uint256): modifying

NewETHFlash: event({interest_factor: uint256, flash_pool: indexed(address)})
NewERC20Flash: event({token_address: indexed(address), interest_factor: uint256, flash_pool: indexed(address)})

# @notice The interest rate for loan x is: interest_factor / 10000
MAX_SUBSIDY_FACTOR: constant(uint256) = 10

ethFlashTemplate: public(address)
erc20FlashTempalte: public(address)
eth_flash_addresses: address[MAX_SUBSIDY_FACTOR]
erc20_flash_addresses: map(address, address[MAX_SUBSIDY_FACTOR])

@private
def createEthFlash():
    assert self.ethFlashTemplate != ZERO_ADDRESS and self.eth_flash_addresses[0] == ZERO_ADDRESS
    for i in range(MAX_SUBSIDY_FACTOR):
        eth_flash_address: address = create_forwarder_to(self.ethFlashTemplate)
        self.eth_flash_addresses[i] = eth_flash_address
        interest_factor: uint256 = convert(i + 1, uint256)
        EthFlash(eth_flash_address).setup(interest_factor)       # interest rate: (i + 1) / 10000
        log.NewETHFlash(interest_factor, eth_flash_address)

@public
def initFactory(eth_template: address, erc20_tempalte: address):
    assert self.ethFlashTemplate == ZERO_ADDRESS and eth_template != ZERO_ADDRESS and \
             self.erc20FlashTempalte == ZERO_ADDRESS and erc20_tempalte != ZERO_ADDRESS
    self.ethFlashTemplate = eth_template
    self.erc20FlashTempalte = erc20_tempalte
    self.createEthFlash()

@public
def createErc20Flash(erc20: address):
    assert self.erc20FlashTempalte != ZERO_ADDRESS and self.erc20_flash_addresses[erc20][0] == ZERO_ADDRESS and erc20 != ZERO_ADDRESS
    for i in range(MAX_SUBSIDY_FACTOR):
        erc20_flash_address: address = create_forwarder_to(self.erc20FlashTempalte)
        self.erc20_flash_addresses[erc20][i] = erc20_flash_address
        interest_factor: uint256 = convert(i + 1, uint256)
        ERC20Flash(erc20_flash_address).setup(erc20, interest_factor)
        log.NewERC20Flash(erc20, interest_factor, erc20_flash_address)

@public
@constant
def getEthFlash(interest_factor: uint256) -> address:
    return self.eth_flash_addresses[interest_factor - 1]

@public
@constant
def getErc20Flash(erc20: address, interest_factor: uint256) -> address:
    return self.erc20_flash_addresses[erc20][interest_factor - 1]