contract EthFlash():
    def setup(subsidy_factor: uint256): modifying

contract ERC20Flash():
    def setup(token_addr: address): modifying

# @notice The subsidy rate for loan x is: subsidy_factor / 10000
MAX_SUBSIDY_FACTOR: constant(uint256) = 10

eth_flash_template: public(address)
eth_flash_addresses: address[MAX_SUBSIDY_FACTOR]
erc20_flash_tempalte: public(address)
erc20_to_flash: map(address, address)
flash_to_erc20: map(address, address)

@public
def init_factory(eth_template: address):
    assert self.eth_flash_template == ZERO_ADDRESS and eth_template != ZERO_ADDRESS
    self.eth_flash_template = eth_template

@public
def create_eth_flash():
    assert self.eth_flash_template != ZERO_ADDRESS and self.eth_flash_addresses[0] == ZERO_ADDRESS
    for i in range(MAX_SUBSIDY_FACTOR):
        eth_flash_address: address = create_forwarder_to(self.eth_flash_template)
        self.eth_flash_addresses[i] = eth_flash_address
        subsidy_factor: uint256 = convert(i + 1, uint256)
        EthFlash(eth_flash_address).setup(subsidy_factor)       # subsidy rate: (i + 1) / 10000

@public
def create_erc20_flash(erc20: address) -> address:
    assert erc20 != ZERO_ADDRESS
    assert self.erc20_flash_tempalte != ZERO_ADDRESS
    assert self.erc20_to_flash[erc20] == ZERO_ADDRESS
    flash: address = create_forwarder_to(self.erc20_flash_tempalte)
    ERC20Flash(flash).setup(erc20)
    self.erc20_to_flash[erc20] = flash
    self.flash_to_erc20[flash] = erc20
    return flash

@public
@constant
def get_eth_flash(subsidy_factor: uint256) -> address:
    return self.eth_flash_addresses[subsidy_factor - 1]

@public
@constant
def get_erc20_flash(erc20: address) -> address:
    return self.erc20_to_flash[erc20]

@public
@constant
def get_erc20_addr(flash: address) -> address:
    return self.flash_to_erc20[flash]