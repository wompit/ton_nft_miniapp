from flask import Blueprint, request

from controllers.card_page import CardPageController
from controllers.final import FinalPageController
from controllers.generate_nft import GenerateNFTController
from controllers.mint_nft import MintNFTController
from controllers.pay_check import PayCheckController
from controllers.save_transaction import SaveTransactionController
from controllers.start_page import StartPageController
from controllers.submit_controller import SubmitController
from controllers.wait_page import WaitPageController
from controllers.wallet_connect import WalletConnectController
from controllers.nft_check import NFTCheckController
from controllers.nft_config import NFTConfigController

blueprint = Blueprint("main", __name__)


@blueprint.route("/", methods=["GET"])
def index():
    return StartPageController(request).call()


@blueprint.route("/buy_page/<mode>", methods=["GET"])
def buy_page(mode="default"):
    return CardPageController(request).call(mode)


@blueprint.route("/wait_page", methods=["GET"])
def wait_page():
    return WaitPageController(request).call()


@blueprint.route("/mint_nft", methods=["GET"])
def mint_nft():
    return MintNFTController(request).call()


@blueprint.route("/generate_nft", methods=["POST"])
def generate_nft():
    return GenerateNFTController(request).call()


@blueprint.route("/wait_nft", methods=["GET"])
def wait_nft():
    return WaitPageController(request, is_nft=True).call()


@blueprint.route("/connect_wallet", methods=["POST"])
def connect_wallet():
    return WalletConnectController(request).call()


@blueprint.route("/submit", methods=["POST"])
def submit():
    return SubmitController(request).call()


@blueprint.route("/check_payment", methods=["POST"])
def check_payment():
    return PayCheckController(request).call()


@blueprint.route("/check_nft", methods=["POST"])
def check_nft():
    return NFTCheckController(request).call()


@blueprint.route("/save_transaction", methods=["POST"])
def save_transaction():
    return SaveTransactionController(request).call()


@blueprint.route("/nft/<nft_name>", methods=["GET"])
def nft_config(nft_name):
    return NFTConfigController(request).call(nft_name)


@blueprint.route("/final/<nft_address>", methods=["GET"])
def final(nft_address):
    return FinalPageController(request).call(nft_address)
