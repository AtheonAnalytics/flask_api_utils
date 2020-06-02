from flask_api_utils.authorization.voter import ABSTAIN, DENIED, GRANTED


class RoleVoter:
    def vote(self, user, subject, attributes):
        result = ABSTAIN
        roles = self.extract_roles(user)

        for attribute in attributes:
            if not isinstance(attribute, str):
                continue

            result = DENIED
            if attribute in roles:
                return GRANTED

        return result

    def extract_roles(self, user):
        return user.roles
