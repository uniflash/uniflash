contract EthFlash():
    def setup(subsidy_factor: uint256): modifying

contract ERC20Flash():
    def setup(token_addr: address): modifying

eth_flash_template: public(address)
eth_flash: public(address)
erc20_flash_tempalte: public(address)
erc20_to_flash: map(address, address)
flash_to_erc20: map(address, address)

@public
def init_factory(eth_template: address):
    assert self.eth_flash_template == ZERO_ADDRESS
    self.eth_flash_template = eth_template

@public
def create_eth_flash() -> address:
    assert self.eth_flash_template != ZERO_ADDRESS
    assert self.eth_flash == ZERO_ADDRESS
    self.eth_flash = create_forwarder_to(self.eth_flash_template)
    EthFlash(self.eth_flash).setup(8)
    return self.eth_flash

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
def get_eth_flash() -> address:
    return self.eth_flash

@public
@constant
def get_erc20_flash(erc20: address) -> address:
    return self.erc20_to_flash[erc20]

@public
@constant
def get_erc20_addr(flash: address) -> address:
    return self.flash_to_erc20[flash]