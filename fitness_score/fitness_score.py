from iconservice import *

TAG = 'FitnessScore'


# * Important console commands for testnet
# $ docker container start -a local-tbears
# $ docker container attach local-tbears
# $ tbears balance [account] -u https://bicon.net.solidwallet.io/api/v3
# $ tbears deploy fitness_score/ -k wallets/test1_Account -u https://bicon.net.solidwallet.io/api/v3


class FitnessScore(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        # Wie viele Punkte jemand hat
        self._myPoints = DictDB('myPoints', db, value_type=int)
        # Person die du herausgefordert hast
        self._myTarget = DictDB('myTarget', db, value_type=Address)
        # Person die dich herausfordert
        self._myChallenger = DictDB('myChallengers', db, value_type=Address)
        self._myChallengerStartTime = DictDB('myChallengerStartTime', db, value_type=int)
        self._myChallengerDuration = DictDB('myChallengerDuration', db, value_type=int)
        self._myChallengersBet = DictDB('myChallengersBet', db, value_type=str)
        self._myChallengerAccepted = DictDB('myChallengerAccepted', db, value_type=bool)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello"

    @payable
    def fallback(self):
        if self.msg.value > 0:
            self.icx.send(self.msg.sender, self.msg.value)

    # Returns your current challenger (if there exists one)
    @external(readonly=True)
    def get_my_challengers(self) -> str:

        challenger = self._myChallenger[self.msg.sender]

        if challenger is None:
            return str(None)

        bet = self._myChallengersBet[self.msg.sender]

        return str(bet) + ":" + str(challenger) + ":" + str(self._myChallengerStartTime[self.msg.sender]) + ":" + str(self._myChallengerDuration[self.msg.sender])

    @external(readonly=True)
    def has_my_challenger_accepted(self) -> str:
        my_target = self._myTarget[self.msg.sender]
        return str(self._myChallengerAccepted[my_target]).lower() + ":"+str(self._myChallengerStartTime[my_target]) + ":"+str(self._myChallengerDuration[my_target])



    @external
    @payable
    def accept(self):

        if self._myChallengerAccepted[self.msg.sender]:
            self.refund("You already have accepted this challenge.")

        if self._myChallenger[self.msg.sender] is None:
            self.refund("You do not have any challenger.")

        if self._myChallengerStartTime[self.msg.sender] <= self.currentTimeSeconds():
            self.clear_my_challenger(self.msg.sender)
            self.refund("You haven't accepted fast enough. The challenge already should have began.")

        if self.msg.value != self._myChallengersBet[self.msg.sender]:
            self.refund("You haven't transferred the bet of " + str(self._myChallengersBet[self.msg.sender])+ ".")

        self._myChallengerAccepted[self.msg.sender] = True

    @external
    @payable
    def deny(self):

        if self._myChallengerAccepted[self.msg.sender]:
            self.refund("You have already accept this challenge. Don't be a coward.")

        self.clear_my_challenger(self.msg.sender)

    @external
    @payable
    def challenge(self, target: Address, startTime: int, duration: int):

        if str(self.msg.sender) == str(target):
            self.refund("You can not challenge yourself.")

        if self.msg.value <= 0:
            self.refund("Bet must be grater than zero.")

        if self._myTarget[self.msg.sender] is not None:
            self.refund("You have already challanged someone.")

        if startTime <= self.currentTimeSeconds():
            self.refund("Start time must be in the future! ")

        if self._myChallenger[target] is not None:

            # If the challenge starts time has already passed and wasn't accepted...
            if self._myChallengerStartTime[target] > self.currentTimeSeconds() and not self._myChallengerAccepted[target]:

                self.clear_my_challenger(target)

            else:
                self.refund(
                    "This person has already a challenger. He must first accept/deny the request, before you can challenge.")

        self._challenge(target, startTime, duration)

    def _challenge(self, target: Address, startTime: int, duration: int):
        sender = self.msg.sender
        bet = self.msg.value

        self._myTarget[sender] = target
        self._myChallenger[target] = sender
        self._myChallengerStartTime[target] = startTime
        self._myChallengerDuration[target] = duration
        self._myChallengersBet[target] = str(bet)
        self._myChallengerAccepted[target] = False

    def clear_my_challenger(self, target: Address):

        self._myPoints.remove(self._myChallenger[target])
        self._myPoints.remove(target)

        self._myTarget.remove(self._myChallenger[target])
        self._myChallenger.remove(target)
        self._myChallengerStartTime.remove(target)
        self._myChallengerDuration.remove(target)
        self._myChallengersBet.remove(target)
        self._myChallengerAccepted.remove(target)


    def refund(self, message: str):

        if self.msg.value > 0:
            self.icx.send(self.msg.sender, self.msg.value)
            message += " You got your " + str(self.msg.value) + " ICX refunded."

        revert(message)

    def currentTimeSeconds(self) -> int:
        return int(round(self.tx.timestamp / 1000000000))
