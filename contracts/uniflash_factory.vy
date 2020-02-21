contract EthFlash():
    def setup(subsidy_factor: uint256): modifying

contract ERC20Flash():
    def setup(token_addr: address, subsidy_factor: uint256): modifying

# @notice The subsidy rate for loan x is: subsidy_factor / 10000
MAX_SUBSIDY_FACTOR: constant(uint256) = 10

ethFlashTemplate: public(address)
erc20FlashTempalte: public(address)
eth_flash_addresses: address[MAX_SUBSIDY_FACTOR]
erc20_flashes_addresses: map(address, address[MAX_SUBSIDY_FACTOR])

@public
def initFactory(eth_template: address, erc20_tempalte: address):
    assert self.ethFlashTemplate == ZERO_ADDRESS and eth_template != ZERO_ADDRESS and \
             self.erc20FlashTempalte == ZERO_ADDRESS and erc20_tempalte != ZERO_ADDRESS
    self.ethFlashTemplate = eth_template
    self.erc20FlashTempalte = erc20_tempalte

@public
def createEthFlash():
    assert self.ethFlashTemplate != ZERO_ADDRESS and self.eth_flash_addresses[0] == ZERO_ADDRESS
    for i in range(MAX_SUBSIDY_FACTOR):
        eth_flash_address: address = create_forwarder_to(self.ethFlashTemplate)
        self.eth_flash_addresses[i] = eth_flash_address
        subsidy_factor: uint256 = convert(i + 1, uint256)
        EthFlash(eth_flash_address).setup(subsidy_factor)       # subsidy rate: (i + 1) / 10000

@public
def createErc20Flash(erc20: address):
    assert self.erc20FlashTempalte != ZERO_ADDRESS and self.erc20_flashes_addresses[erc20][0] == ZERO_ADDRESS and erc20 != ZERO_ADDRESS
    for i in range(MAX_SUBSIDY_FACTOR):
        flash: address = create_forwarder_to(self.erc20FlashTempalte)
        self.erc20_flashes_addresses[erc20][i] = flash
        subsidy_factor: uint256 = convert(i + 1, uint256)
        ERC20Flash(flash).setup(erc20, subsidy_factor)

@public
@constant
def getEthFlash(subsidy_factor: uint256) -> address:
    return self.eth_flash_addresses[subsidy_factor - 1]

@public
@constant
def getErc20Flash(erc20: address, subsidy_factor: uint256) -> address:
    index: uint256 = subsidy_factor - 1
    return self.erc20_flashes_addresses[erc20][index]