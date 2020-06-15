from flask_api_utils.authorization.voter import Voter


class InternalClientVoter(Voter):
    def supports(self, attribute, subject):
        return True

    def vote_on_attribute(self, attribute, subject, user):
        sub = user.get('sub')

        return sub and '@clients' in sub
