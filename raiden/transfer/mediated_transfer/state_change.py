# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods,too-many-arguments,too-many-instance-attributes

from raiden.transfer.architecture import StateChange
from raiden.transfer.state import RouteState
from raiden.transfer.mediated_transfer.state import (
    LockedTransferSignedState,
    TransferDescriptionWithSecretState,
)
from raiden.utils import pex, sha3, typing


# Note: The init states must contain all the required data for trying doing
# useful work, ie. there must /not/ be an event for requesting new data.


class ActionInitInitiator(StateChange):
    """ Initial state of a new mediated transfer.

    Args:
        transfer: A state object containing the transfer details.
        routes: A list of possible routes provided by a routing service.
        secret: The secret that must be used with the transfer.
    """

    def __init__(self, payment_network_identifier, transfer_description, routes):
        if not isinstance(transfer_description, TransferDescriptionWithSecretState):
            raise ValueError('transfer must be an TransferDescriptionWithSecretState instance.')

        self.payment_network_identifier = payment_network_identifier
        self.transfer = transfer_description
        self.routes = routes

    def __repr__(self):
        return '<ActionInitInitiator network:{} transfer:{}>'.format(
            self.payment_network_identifier,
            self.transfer,
        )

    def __eq__(self, other):
        return (
            isinstance(other, ActionInitInitiator) and
            self.payment_network_identifier == other.payment_network_identifier and
            self.transfer == other.transfer and
            self.routes == other.routes
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class ActionInitMediator(StateChange):
    """ Initial state for a new mediator.

    Args:
        routes: A list of possible routes provided by a routing service.
        from_route: The payee route.
        from_transfer: The payee transfer.
    """

    def __init__(
            self,
            payment_network_identifier,
            routes: typing.List[RouteState],
            from_route: RouteState,
            from_transfer: LockedTransferSignedState):

        if not isinstance(from_route, RouteState):
            raise ValueError('from_route must be a RouteState instance')

        if not isinstance(from_transfer, LockedTransferSignedState):
            raise ValueError('from_transfer must be a LockedTransferSignedState instance')

        self.payment_network_identifier = payment_network_identifier
        self.routes = routes
        self.from_route = from_route
        self.from_transfer = from_transfer

    def __repr__(self):
        return '<ActionInitMediator network:{} from_route:{} from_transfer:{}>'.format(
            self.payment_network_identifier,
            self.from_route,
            self.from_transfer,
        )

    def __eq__(self, other):
        return (
            isinstance(other, ActionInitMediator) and
            self.payment_network_identifier == other.payment_network_identifier and
            self.routes == other.routes and
            self.from_route == other.from_route and
            self.from_transfer == other.from_transfer
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class ActionInitTarget(StateChange):
    """ Initial state for a new target.

    Args:
        route: The payee route.
        transfer: The payee transfer.
    """

    def __init__(self, payment_network_identifier, route, transfer):
        if not isinstance(route, RouteState):
            raise ValueError('route must be a RouteState instance')

        if not isinstance(transfer, LockedTransferSignedState):
            raise ValueError('transfer must be a LockedTransferSignedState instance')

        self.payment_network_identifier = payment_network_identifier
        self.route = route
        self.transfer = transfer

    def __repr__(self):
        return '<ActionInitTarget network:{} route:{} transfer:{}>'.format(
            self.payment_network_identifier,
            self.route,
            self.transfer,
        )

    def __eq__(self, other):
        return (
            isinstance(other, ActionInitTarget) and
            self.payment_network_identifier == other.payment_network_identifier and
            self.route == other.route and
            self.transfer == other.transfer
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class ActionCancelRoute(StateChange):
    """ Cancel the current route.
    Notes:
        Used to cancel a specific route but not the transfer. May be used for
        timeouts.
    """

    def __init__(self, identifier, routes):
        self.identifier = identifier
        self.routes = routes

    def __repr__(self):
        return '<ActionCancelRoute id:{}>'.format(
            self.identifier,
        )

    def __eq__(self, other):
        return (
            isinstance(other, ActionCancelRoute) and
            self.identifier == other.identifier and
            self.routes == other.routes
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class ReceiveSecretRequest(StateChange):
    """ A SecretRequest message received. """

    def __init__(self, identifier, amount, hashlock, sender):
        self.identifier = identifier
        self.amount = amount
        self.hashlock = hashlock
        self.sender = sender
        self.revealsecret = None

    def __repr__(self):
        return '<ReceiveSecretRequest id:{} amount:{} hashlock:{} sender:{}>'.format(
            self.identifier,
            self.amount,
            pex(self.hashlock),
            pex(self.sender),
        )

    def __eq__(self, other):
        return (
            isinstance(other, ReceiveSecretRequest) and
            self.identifier == other.identifier and
            self.amount == other.amount and
            self.hashlock == other.hashlock and
            self.sender == other.sender and
            self.revealsecret == other.revealsecret
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class ReceiveSecretReveal(StateChange):
    """ A SecretReveal message received. """
    def __init__(self, secret, sender):
        hashlock = sha3(secret)

        self.secret = secret
        self.hashlock = hashlock
        self.sender = sender

    def __repr__(self):
        return '<ReceiveSecretReveal hashlock:{} sender:{}>'.format(
            pex(self.hashlock),
            pex(self.sender),
        )

    def __eq__(self, other):
        return (
            isinstance(other, ReceiveSecretReveal) and
            self.secret == other.secret and
            self.hashlock == other.hashlock and
            self.sender == other.sender
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class ReceiveTransferRefundCancelRoute(StateChange):
    """ A RefundTransfer message received by initiator will cancel the current
    route.
    """

    def __init__(self, sender, routes, transfer, secret):
        if not isinstance(transfer, LockedTransferSignedState):
            raise ValueError('transfer must be an instance of LockedTransferSignedState')

        hashlock = sha3(secret)

        self.sender = sender
        self.transfer = transfer
        self.routes = routes
        self.hashlock = hashlock
        self.secret = secret

    def __str__(self):
        return '<ReceiveTransferRefundCancelRoute sender:{} transfer:{}>'.format(
            pex(self.sender),
            self.transfer
        )

    def __eq__(self, other):
        return (
            isinstance(other, ReceiveTransferRefundCancelRoute) and
            self.sender == other.sender and
            self.transfer == other.transfer and
            self.routes == other.routes and
            self.secret == other.secret and
            self.hashlock == other.hashlock
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class ReceiveTransferRefund(StateChange):
    """ A RefundTransfer message received. """
    def __init__(self, sender, transfer: LockedTransferSignedState):
        if not isinstance(transfer, LockedTransferSignedState):
            raise ValueError('transfer must be an instance of LockedTransferSignedState')

        self.sender = sender
        self.transfer = transfer


class ReceiveBalanceProof(StateChange):
    """ A balance proof `identifier` was received. """
    def __init__(self, identifier, node_address, balance_proof):
        self.identifier = identifier
        self.node_address = node_address
        self.balance_proof = balance_proof


class ContractReceiveWithdraw(StateChange):
    """ A lock was withdrawn via the blockchain.

    Used when a hash time lock was withdrawn and a log ChannelSecretRevealed is
    emited by the netting channel.

    Note:
        For this state change the contract caller is not important but only the
        receiving address. `receiver` is the address to which the lock's token
        was transferred, this may be either of the channel participants.

        If the channel was used for a mediated transfer that was refunded, this
        event must be used twice, once for each receiver.
    """
    def __init__(self, channel_address, secret, receiver):
        self.channel_address = channel_address
        self.secret = secret
        self.receiver = receiver


class ContractReceiveClosed(StateChange):
    def __init__(self, channel_address, closing_address, block_number):
        self.channel_address = channel_address
        self.closing_address = closing_address
        self.block_number = block_number  # TODO: rename to closed_block


class ContractReceiveSettled(StateChange):
    def __init__(self, channel_address, block_number):
        self.channel_address = channel_address
        self.block_number = block_number  # TODO: rename to settle_block_number


class ContractReceiveBalance(StateChange):
    def __init__(
            self,
            channel_address,
            token_address,
            participant_address,
            balance,
            block_number):

        self.channel_address = channel_address
        self.token_address = token_address
        self.participant_address = participant_address
        self.balance = balance
        self.block_number = block_number


class ContractReceiveNewChannel(StateChange):
    def __init__(
            self,
            manager_address,
            channel_address,
            participant1,
            participant2,
            settle_timeout):

        self.manager_address = manager_address
        self.channel_address = channel_address
        self.participant1 = participant1
        self.participant2 = participant2
        self.settle_timeout = settle_timeout


class ContractReceiveTokenAdded(StateChange):
    def __init__(self, registry_address, token_address, manager_address):
        self.registry_address = registry_address
        self.token_address = token_address
        self.manager_address = manager_address
