class RoleHierarchy:
    def __init__(self, hierarchy):
        self.hierarchy = hierarchy
        self.map = {}
        self.build_role_map()

    def build_role_map(self):
        for main, roles in self.hierarchy.items():
            self.map[main] = roles
            visited = []
            additional_roles = roles.copy()

            while additional_roles:
                role = additional_roles.pop(0)
                if role not in self.hierarchy:
                    continue

                visited.append(role)

                for role_to_add in self.hierarchy[role]:
                    self.map[main].append(role_to_add)

                for additional_role in set(self.hierarchy[role]) - set(visited):
                    additional_roles.append(additional_role)

    def get_reachable_role_names(self, roles):
        reachable_roles = roles.copy()
        for role in roles:
            if role not in self.map:
                continue

            for sub_role in self.map[role]:
                reachable_roles.append(sub_role)

        # unique list
        return list(set(reachable_roles))
