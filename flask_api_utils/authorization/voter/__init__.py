ABSTAIN = 'abstain'
DENIED = 'denied'
GRANTED = 'granted'


class Voter:
    def __init__(self):
        pass

    def vote(self, user, subject, attributes):
        """
        Returns the vote for the given parameters.
        :param user:
        :param subject:
        :param attributes:
        :return: either
        """
        vote = ABSTAIN

        for attribute in attributes:
            if not self.supports(attribute, subject):
                continue

            vote = DENIED

            if self.vote_on_attribute(attribute, subject, user):
                return GRANTED

        return vote

    def supports(self, attribute, subject):
        """
        Determine if the attribute and subject are supported by this voter.
        :param attribute: An attribute
        :param subject: The subject to secure, e.g an object the user wants to access or any other type
        :return: bool True if the attribute and subject are supported, False otherwise
        """
        raise NotImplementedError

    def vote_on_attribute(self, attribute, subject, user):
        """
        Perform a single access check operation on a given attribute, subject and token.
        :param attribute:
        :param subject:
        :param user:
        :return:
        """
        raise NotImplementedError
